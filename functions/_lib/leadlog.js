/**
 * Lead log in Cloudflare D1 (binding LEADS_DB). One database can be bound to every site, so the dashboard shows all of them.
 *   leads    one row per lead (winner, price, source, contact)
 *   attempts one row per buyer answer (skip / ping / post) with the exact request we sent and the raw response
 *   spend    ad spend per day / site / channel (entered on the dashboard)
 * Tables are created on first use. If LEADS_DB isn't bound, logging is skipped (the lead still goes to the buyers).
 */
let ready = null;
export function init(db) {
  if (!ready) ready = db.batch([
    db.prepare(`CREATE TABLE IF NOT EXISTS leads (id TEXT PRIMARY KEY, ts INTEGER NOT NULL, site TEXT, vertical TEXT, test INTEGER DEFAULT 0,
      source TEXT, campaign TEXT, page TEXT, zip TEXT, city TEXT, state TEXT, material TEXT, project TEXT,
      first_name TEXT, last_name TEXT, phone TEXT, email TEXT, address TEXT, tf TEXT, jornaya TEXT,
      buyer TEXT, ping_status TEXT, ping_id TEXT, ping_price REAL, ping_error TEXT, post_status TEXT, post_price REAL, post_error TEXT,
      sold INTEGER DEFAULT 0, revenue REAL DEFAULT 0, payout REAL DEFAULT 0, publisher TEXT, reason TEXT,
      ping_req TEXT, ping_res TEXT, post_req TEXT, post_res TEXT)`),
    db.prepare("CREATE INDEX IF NOT EXISTS leads_ts ON leads (ts)"),
    db.prepare(`CREATE TABLE IF NOT EXISTS attempts (id INTEGER PRIMARY KEY AUTOINCREMENT, lead_id TEXT NOT NULL, ts INTEGER NOT NULL, buyer TEXT, live INTEGER DEFAULT 0,
      stage TEXT, status TEXT, price REAL DEFAULT 0, token TEXT, error TEXT, ms INTEGER, won INTEGER DEFAULT 0, req TEXT, res TEXT)`),
    db.prepare("CREATE INDEX IF NOT EXISTS attempts_lead ON attempts (lead_id)"),
    db.prepare("CREATE INDEX IF NOT EXISTS attempts_ts ON attempts (ts)"),
    db.prepare(`CREATE TABLE IF NOT EXISTS settings (k TEXT PRIMARY KEY, v TEXT)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS publishers (id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT, key TEXT UNIQUE NOT NULL, mode TEXT DEFAULT 'test',
      share REAL DEFAULT 0.7, fixed REAL DEFAULT 0, verticals TEXT DEFAULT 'roofing', daily_cap INTEGER DEFAULT 0, created INTEGER, note TEXT)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS pubpings (id TEXT PRIMARY KEY, pub_id TEXT NOT NULL, ts INTEGER NOT NULL, test INTEGER DEFAULT 1, lead TEXT, offers TEXT,
      top REAL DEFAULT 0, payout REAL DEFAULT 0, status TEXT, reason TEXT, lead_id TEXT, sold INTEGER DEFAULT 0)`),
    db.prepare("CREATE INDEX IF NOT EXISTS pubpings_pub ON pubpings (pub_id, ts)"),
    db.prepare(`CREATE TABLE IF NOT EXISTS spend (day TEXT NOT NULL, site TEXT NOT NULL, channel TEXT NOT NULL, amount REAL NOT NULL, note TEXT, PRIMARY KEY (day, site, channel))`),
    // pre-pings: cheap yes/no checks that never reach a buyer (used for rate limits and publisher stats)
    db.prepare(`CREATE TABLE IF NOT EXISTS prepings (id INTEGER PRIMARY KEY AUTOINCREMENT, pub_id TEXT NOT NULL, ts INTEGER NOT NULL, test INTEGER DEFAULT 1,
      vertical TEXT, zip TEXT, state TEXT, ok INTEGER DEFAULT 0, reason TEXT)`),
    db.prepare("CREATE INDEX IF NOT EXISTS prepings_pub ON prepings (pub_id, ts)"),
    // opt-outs: SHA-256 of the 10-digit phone or lowercase email. Checked on every publisher lead.
    db.prepare(`CREATE TABLE IF NOT EXISTS suppress (hash TEXT PRIMARY KEY, kind TEXT, ts INTEGER, source TEXT)`),
    // consent proof, kept 5 years (FTC TSR). Phone is stored as a hash, plus AES-GCM encrypted when DATA_KEY is set.
    db.prepare(`CREATE TABLE IF NOT EXISTS consent (lead_id TEXT PRIMARY KEY, ts INTEGER NOT NULL, site TEXT, publisher TEXT, vertical TEXT, test INTEGER DEFAULT 0,
      phone_hash TEXT, email_hash TEXT, contact_enc TEXT, tf TEXT, jornaya TEXT, consent_text TEXT, page TEXT, ip TEXT, user_agent TEXT, submitted_at TEXT, sold_to TEXT)`),
    db.prepare("CREATE INDEX IF NOT EXISTS consent_phone ON consent (phone_hash)"),
  ]).then(async () => {
    // columns added after launch (ignore "duplicate column" on later runs)
    for (const sql of ["ALTER TABLE publishers ADD COLUMN rpm INTEGER DEFAULT 60", "ALTER TABLE publishers ADD COLUMN hourly_cap INTEGER DEFAULT 0",
      "ALTER TABLE publishers ADD COLUMN paused_reason TEXT", "ALTER TABLE leads ADD COLUMN phone_hash TEXT"]) { try { await db.prepare(sql).run(); } catch {} }
    try { await db.prepare("CREATE INDEX IF NOT EXISTS leads_phash ON leads (phone_hash, ts)").run(); } catch {}
  }).catch((e) => { ready = null; throw e; });
  return ready;
}

/** SHA-256 hex. Phones are hashed as 10 digits, emails lowercase. */
export async function sha(s) {
  const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(String(s)));
  return [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, "0")).join("");
}
export const normPhone = (p) => String(p || "").replace(/\D/g, "").replace(/^1(?=\d{10}$)/, "");
export const phoneHash = (p) => { const n = normPhone(p); return n.length === 10 ? sha(n) : Promise.resolve(""); };
export const emailHash = (e) => { const n = String(e || "").trim().toLowerCase(); return n.includes("@") ? sha(n) : Promise.resolve(""); };

/** AES-GCM encrypt with the DATA_KEY secret (any long random string). Returns "" when DATA_KEY isn't set. */
async function enc(env, text) {
  if (!env.DATA_KEY || !text) return "";
  const k = await crypto.subtle.importKey("raw", await crypto.subtle.digest("SHA-256", new TextEncoder().encode(env.DATA_KEY)), "AES-GCM", false, ["encrypt"]);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const c = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv }, k, new TextEncoder().encode(text)));
  const all = new Uint8Array(12 + c.length); all.set(iv); all.set(c, 12);
  return btoa(String.fromCharCode(...all));
}
export async function dec(env, b64) {
  if (!env.DATA_KEY || !b64) return "";
  const all = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
  const k = await crypto.subtle.importKey("raw", await crypto.subtle.digest("SHA-256", new TextEncoder().encode(env.DATA_KEY)), "AES-GCM", false, ["decrypt"]);
  return new TextDecoder().decode(await crypto.subtle.decrypt({ name: "AES-GCM", iv: all.slice(0, 12) }, k, all.slice(12)));
}
const FIVE_YEARS = (5 * 365 + 30) * 86400000;

/** Is this phone or email on the opt-out list? */
export async function suppressed(db, ph, eh) {
  const hs = [ph, eh].filter(Boolean); if (!hs.length) return false;
  const r = await db.prepare(`SELECT hash FROM suppress WHERE hash IN (${hs.map((_, i) => "?" + (i + 1)).join(",")}) LIMIT 1`).bind(...hs).first();
  return !!r;
}

/** Where the visitor came from, from click IDs and UTM tags. */
export function sourceOf(l) {
  if (l.gclid || l.gbraid || l.wbraid) return "google";
  if (l.msclkid) return "bing";
  if (l.fbclid) return "meta";
  if (l.utm_source) return String(l.utm_source).toLowerCase().slice(0, 30);
  return "organic/direct";
}

const J = (v) => (v == null ? null : typeof v === "string" ? v.slice(0, 8000) : JSON.stringify(v).slice(0, 8000));

/** lead: normalized lead; sale: result of buyers.sell() (or null); extra: { test, source, publisher, payout } */
export async function logLead(env, lead, sale, extra = {}) {
  if (!env.LEADS_DB) return false;
  const db = env.LEADS_DB;
  try {
    await init(db);
    const at = (sale && sale.attempts) || [];
    const win = at.find((a) => a.stage === "post" && a.ok) || null;
    const wp = win ? at.find((a) => a.stage === "ping" && a.buyer === win.buyer) : (at.filter((a) => a.stage === "ping").sort((x, y) => (y.price || 0) - (x.price || 0))[0] || null);
    const lastPost = win || [...at].reverse().find((a) => a.stage === "post") || null;
    const now = Date.now();
    const stmts = [db.prepare(`INSERT OR REPLACE INTO leads (id, ts, site, vertical, test, source, campaign, page, zip, city, state, material, project,
      first_name, last_name, phone, email, address, tf, jornaya, buyer, ping_status, ping_id, ping_price, ping_error, post_status, post_price, post_error,
      sold, revenue, payout, publisher, reason, ping_req, ping_res, post_req, post_res)
      VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12,?13,?14,?15,?16,?17,?18,?19,?20,?21,?22,?23,?24,?25,?26,?27,?28,?29,?30,?31,?32,?33,?34,?35,?36,?37)`).bind(
      lead.lead_id, now, lead.source_site || "", lead.vertical || "", extra.test ? 1 : 0, extra.source || lead.source || sourceOf(lead), lead.utm_campaign || "",
      String(lead.landing_page || "").slice(0, 300), lead.zip || "", lead.city || "", lead.state || "", lead.material || "", lead.project || "",
      lead.first_name || "", lead.last_name || "", lead.phone || "", lead.email || "", lead.address || "", lead.xxTrustedFormCertUrl || "", lead.universal_leadid || "",
      win ? win.name : (wp ? wp.name : ""), wp ? (wp.ok ? "Match" : (wp.status || "")) : "", (wp && wp.token) || "", (wp && wp.price) || 0, (wp && wp.error) || "",
      lastPost ? (lastPost.ok ? "Accepted" : (lastPost.status || "")) : "", (lastPost && lastPost.price) || 0, (lastPost && lastPost.error) || "",
      sale && sale.sold ? 1 : 0, sale && sale.sold ? sale.price : 0, extra.payout || 0, extra.publisher || "",
      sale ? (sale.sold ? "" : (sale.reason || "")) : "no buyer connected",
      J(wp && wp.req), J(wp && wp.raw), J(lastPost && lastPost.req), J(lastPost && lastPost.raw))];
    const ph = await phoneHash(lead.phone), eh = await emailHash(lead.email);
    stmts.push(db.prepare("UPDATE leads SET phone_hash=?2 WHERE id=?1").bind(lead.lead_id, ph));
    if (lead.phone || lead.email) stmts.push(db.prepare(`INSERT OR REPLACE INTO consent (lead_id, ts, site, publisher, vertical, test, phone_hash, email_hash, contact_enc, tf, jornaya,
      consent_text, page, ip, user_agent, submitted_at, sold_to) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12,?13,?14,?15,?16,?17)`).bind(
      lead.lead_id, now, lead.source_site || "", extra.publisher || "", lead.vertical || "", extra.test ? 1 : 0, ph, eh,
      await enc(env, JSON.stringify({ first_name: lead.first_name, last_name: lead.last_name, phone: lead.phone, email: lead.email, address: lead.address, zip: lead.zip })),
      lead.xxTrustedFormCertUrl || "", lead.universal_leadid || "", String(lead.consent_text || "").slice(0, 3000), String(lead.landing_page || "").slice(0, 400),
      lead.ip_address || "", String(lead.user_agent || "").slice(0, 400), lead.submitted_at || new Date(now).toISOString(), win ? win.name : ""));
    if (Math.random() < 0.01) stmts.push(db.prepare("DELETE FROM consent WHERE ts<?1").bind(now - FIVE_YEARS));   // records older than 5 years + 30 days
    for (const a of at) stmts.push(db.prepare(`INSERT INTO attempts (lead_id, ts, buyer, live, stage, status, price, token, error, ms, won, req, res) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12,?13)`)
      .bind(lead.lead_id, now, a.name || a.buyer, a.live ? 1 : 0, a.stage, a.ok ? (a.stage === "post" ? "Accepted" : "Match") : (a.status || ""), a.price || 0, a.token || "", a.error || "", a.ms || 0,
        win && a === win ? 1 : 0, J(a.req), J(a.raw)));
    await db.batch(stmts);
    return true;
  } catch (e) { console.log("leadlog", String(e)); return false; }
}

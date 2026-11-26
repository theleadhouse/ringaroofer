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
    db.prepare(`CREATE TABLE IF NOT EXISTS spend (day TEXT NOT NULL, site TEXT NOT NULL, channel TEXT NOT NULL, amount REAL NOT NULL, note TEXT, PRIMARY KEY (day, site, channel))`),
  ]).catch((e) => { ready = null; throw e; });
  return ready;
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
    for (const a of at) stmts.push(db.prepare(`INSERT INTO attempts (lead_id, ts, buyer, live, stage, status, price, token, error, ms, won, req, res) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12,?13)`)
      .bind(lead.lead_id, now, a.name || a.buyer, a.live ? 1 : 0, a.stage, a.ok ? (a.stage === "post" ? "Accepted" : "Match") : (a.status || ""), a.price || 0, a.token || "", a.error || "", a.ms || 0,
        win && a === win ? 1 : 0, J(a.req), J(a.raw)));
    await db.batch(stmts);
    return true;
  } catch (e) { console.log("leadlog", String(e)); return false; }
}

/**
 * Lead log in Cloudflare D1 (binding LEADS_DB). One database can be bound to every site, so the dashboard shows all of them.
 * Tables are created on first use. If LEADS_DB isn't bound, logging is skipped (the lead still goes to the buyer).
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

const J = (v) => (v == null ? null : typeof v === "string" ? v.slice(0, 6000) : JSON.stringify(v).slice(0, 6000));

/** lead: normalized lead from /api/quote (or the test runner); r: result of pingPost() (may be null). */
export async function logLead(env, lead, r, extra = {}) {
  if (!env.LEADS_DB) return false;
  try {
    await init(env.LEADS_DB);
    const ping = (r && r.ping) || {}, post = (r && r.post) || {};
    await env.LEADS_DB.prepare(`INSERT OR REPLACE INTO leads (id, ts, site, vertical, test, source, campaign, page, zip, city, state, material, project,
      first_name, last_name, phone, email, address, tf, jornaya, buyer, ping_status, ping_id, ping_price, ping_error, post_status, post_price, post_error,
      sold, revenue, payout, publisher, reason, ping_req, ping_res, post_req, post_res)
      VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11,?12,?13,?14,?15,?16,?17,?18,?19,?20,?21,?22,?23,?24,?25,?26,?27,?28,?29,?30,?31,?32,?33,?34,?35,?36,?37)`).bind(
      lead.lead_id, Date.now(), lead.source_site || "", lead.vertical || "", extra.test ? 1 : 0, extra.source || sourceOf(lead), lead.utm_campaign || "",
      String(lead.landing_page || "").slice(0, 300), lead.zip || "", lead.city || "", lead.state || "", lead.material || "", lead.project || "",
      lead.first_name || "", lead.last_name || "", lead.phone || "", lead.email || "", lead.address || "", lead.xxTrustedFormCertUrl || "", lead.universal_leadid || "",
      r ? (extra.buyer || "LoanBright") : "", ping.status || "", ping.id || "", ping.price || 0, ping.error || "", post.status || "", post.price || 0, post.error || "",
      r && r.sold ? 1 : 0, r && r.sold ? r.price : 0, extra.payout || 0, extra.publisher || "", (r && r.reason) || (r ? "" : "no buyer connected"),
      J(ping.req), J(ping.raw), J(post.req), J(post.raw)).run();
    return true;
  } catch (e) { console.log("leadlog", String(e)); return false; }
}

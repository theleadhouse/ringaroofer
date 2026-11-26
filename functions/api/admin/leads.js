/**
 * Private lead dashboard data. Header "X-Admin-Key" must match ADMIN_PASS (or SBB_TEST_TOKEN).
 *   GET  /api/admin/leads?days=7&test=0|1|all&site=   overview, by day, by buyer, by source (with spend + margin), latest leads, buyer status
 *   GET  /api/admin/leads?id=<lead id>                one lead + every buyer attempt (exact request + raw response)
 *   POST /api/admin/leads {spend:{day,site,channel,amount}}   save ad spend (amount 0 deletes)
 */
import { init } from "../../_lib/leadlog.js";
import { BUYERS } from "../../_lib/buyers.js";
const J = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
const r2 = (v) => Math.round((+v || 0) * 100) / 100;
function authed(request, env) { const k = request.headers.get("X-Admin-Key") || ""; const want = env.ADMIN_PASS || env.SBB_TEST_TOKEN; return !!want && k === want; }
const CH = (src) => (/google/.test(src) ? "google" : /meta|facebook|fb|instagram/.test(src) ? "meta" : /bing|microsoft/.test(src) ? "bing" : /organic|direct/.test(src) ? "organic" : "other");

export async function onRequestGet({ request, env }) {
  if (!authed(request, env)) return J({ error: "locked" }, 401);
  const buyers = BUYERS.map((b) => ({ id: b.id, name: b.name, verticals: b.verticals, connected: b.configured(env), live: b.live(env), paused: env[`${b.id.toUpperCase()}_OFF`] === "1",
    min: parseFloat(env[`${b.id.toUpperCase()}_MIN_PRICE`] || "0") || 0 }));
  if (!env.LEADS_DB) return J({ error: "no_db", message: "Add the D1 binding LEADS_DB to this Pages project.", buyers }, 503);
  const db = env.LEADS_DB; await init(db);
  const u = new URL(request.url), id = u.searchParams.get("id");
  if (id) {
    const lead = await db.prepare("SELECT * FROM leads WHERE id=?1").bind(id).first();
    let attempts = (await db.prepare("SELECT * FROM attempts WHERE lead_id=?1 ORDER BY id").bind(id).all()).results;
    if (!attempts.length && lead && lead.ping_status) {   // leads saved before per-buyer logging: rebuild from the lead row
      attempts = [{ buyer: lead.buyer || "LoanBright", stage: "ping", status: lead.ping_status, price: lead.ping_price, error: lead.ping_error, ts: lead.ts, live: lead.test ? 0 : 1, req: lead.ping_req, res: lead.ping_res, won: 0 }];
      if (lead.post_status) attempts.push({ buyer: lead.buyer || "LoanBright", stage: "post", status: lead.post_status, price: lead.post_price, error: lead.post_error, ts: lead.ts, live: lead.test ? 0 : 1, req: lead.post_req, res: lead.post_res, won: lead.sold });
    }
    return J({ lead, attempts });
  }
  const days = Math.min(Math.max(parseInt(u.searchParams.get("days") || "7", 10) || 7, 1), 365);
  const since = Date.now() - days * 86400000, test = u.searchParams.get("test") || "all", site = u.searchParams.get("site") || "";
  const where = ["l.ts > ?1"], args = [since];
  if (test === "0" || test === "1") { where.push(`l.test = ?${args.length + 1}`); args.push(+test); }
  if (site) { where.push(`l.site = ?${args.length + 1}`); args.push(site); }
  const W = where.join(" AND ");
  const q = async (sql) => (await db.prepare(sql).bind(...args).all()).results;
  const tot = (await q(`SELECT COUNT(*) leads, SUM(l.ping_status<>'') pinged, SUM(l.ping_status='Match' OR l.ping_status='Matched') matched, SUM(l.sold) sold,
    SUM(l.revenue) revenue, SUM(l.payout) payouts, SUM(l.test) tests FROM leads l WHERE ${W}`))[0] || {};
  const byDay = await q(`SELECT date(l.ts/1000,'unixepoch') day, COUNT(*) leads, SUM(l.sold) sold, SUM(l.revenue) revenue, SUM(l.payout) payouts FROM leads l WHERE ${W} GROUP BY day ORDER BY day DESC`);
  const bySourceRaw = await q(`SELECT l.site, l.source, l.publisher, COUNT(*) leads, SUM(l.sold) sold, SUM(l.revenue) revenue, SUM(l.payout) payouts FROM leads l WHERE ${W} GROUP BY l.site, l.source, l.publisher ORDER BY leads DESC`);
  const byBuyer = await q(`SELECT a.buyer, SUM(a.stage='ping') pings, SUM(a.stage='ping' AND a.status IN ('Match','Matched')) matched,
    AVG(CASE WHEN a.stage='ping' AND a.status IN ('Match','Matched') THEN a.price END) avg_bid, MAX(CASE WHEN a.stage='ping' THEN a.price END) max_bid,
    SUM(a.stage='post') posts, SUM(a.stage='post' AND a.status='Accepted') accepted, SUM(CASE WHEN a.won=1 THEN a.price ELSE 0 END) revenue, SUM(a.stage='skip') skipped,
    AVG(CASE WHEN a.stage='ping' THEN a.ms END) avg_ms FROM attempts a JOIN leads l ON l.id=a.lead_id WHERE ${W} GROUP BY a.buyer ORDER BY revenue DESC`);
  const buyerReasons = await q(`SELECT a.buyer, a.stage, a.error reason, COUNT(*) n FROM attempts a JOIN leads l ON l.id=a.lead_id WHERE ${W} AND a.error<>'' GROUP BY a.buyer, a.stage, a.error ORDER BY n DESC LIMIT 30`);
  const reasons = await q(`SELECT l.reason, COUNT(*) n FROM leads l WHERE ${W} AND l.sold=0 AND l.reason<>'' GROUP BY l.reason ORDER BY n DESC LIMIT 10`);
  const sinceDay = new Date(since).toISOString().slice(0, 10);
  const spend = (await db.prepare(`SELECT day, site, channel, amount, note FROM spend WHERE day >= ?1 ${site ? "AND site = ?2" : ""} ORDER BY day DESC, site`).bind(...(site ? [sinceDay, site] : [sinceDay])).all()).results;
  // sources: our sites by channel (cost = ad spend), publishers (cost = payouts)
  const src = {};
  for (const r of bySourceRaw) {
    const k = r.publisher ? `pub|${r.publisher}` : `${r.site}|${CH(r.source)}`;
    const s = src[k] || (src[k] = { kind: r.publisher ? "publisher" : "own", site: r.site, channel: r.publisher ? "publisher" : CH(r.source), name: r.publisher || `${r.site} · ${CH(r.source)}`, leads: 0, sold: 0, revenue: 0, cost: 0 });
    s.leads += r.leads; s.sold += r.sold || 0; s.revenue += r.revenue || 0; s.cost += r.payouts || 0;
  }
  for (const sp of spend) { const k = `${sp.site}|${sp.channel}`; const s = src[k] || (src[k] = { kind: "own", site: sp.site, channel: sp.channel, name: `${sp.site} · ${sp.channel}`, leads: 0, sold: 0, revenue: 0, cost: 0 }); s.cost += sp.amount || 0; }
  const sources = Object.values(src).map((s) => ({ ...s, revenue: r2(s.revenue), cost: r2(s.cost), margin: r2(s.revenue - s.cost), per_lead: s.leads ? r2(s.cost / s.leads) : 0 })).sort((a, b) => b.leads - a.leads);
  const spendTotal = spend.reduce((a, r) => a + (r.amount || 0), 0);
  const rows = await q(`SELECT l.id, l.ts, l.site, l.vertical, l.test, l.source, l.campaign, l.zip, l.city, l.state, l.material, l.project, l.first_name, l.last_name, l.phone, l.email,
    l.buyer, l.ping_status, l.ping_price, l.post_status, l.post_price, l.sold, l.revenue, l.payout, l.publisher, l.reason,
    (SELECT COUNT(*) FROM attempts a WHERE a.lead_id=l.id AND a.stage='ping') bids FROM leads l WHERE ${W} ORDER BY l.ts DESC LIMIT 500`);
  const sites = (await db.prepare("SELECT DISTINCT site FROM leads ORDER BY site").all()).results.map((r) => r.site);
  const totals = { ...tot, revenue: r2(tot.revenue), payouts: r2(tot.payouts), spend: r2(spendTotal) };
  totals.margin = r2(totals.revenue - totals.payouts - totals.spend);
  return J({ days, test, site, sites, buyers, totals, byDay: byDay.map((d) => ({ ...d, revenue: r2(d.revenue) })),
    byBuyer: byBuyer.map((b) => ({ ...b, avg_bid: r2(b.avg_bid), max_bid: r2(b.max_bid), revenue: r2(b.revenue), avg_ms: Math.round(b.avg_ms || 0) })), buyerReasons, reasons, sources, spend, rows });
}

export async function onRequestPost({ request, env }) {
  if (!authed(request, env)) return J({ error: "locked" }, 401);
  if (!env.LEADS_DB) return J({ error: "no_db" }, 503);
  const db = env.LEADS_DB; await init(db);
  let d; try { d = await request.json(); } catch { return J({ error: "bad json" }, 400); }
  const s = d.spend || {};
  if (!/^\d{4}-\d{2}-\d{2}$/.test(s.day || "") || !s.site || !s.channel) return J({ error: "need day, site, channel" }, 400);
  const amt = r2(parseFloat(s.amount) || 0);
  if (amt <= 0) await db.prepare("DELETE FROM spend WHERE day=?1 AND site=?2 AND channel=?3").bind(s.day, String(s.site).slice(0, 60), String(s.channel).slice(0, 30)).run();
  else await db.prepare("INSERT OR REPLACE INTO spend (day, site, channel, amount, note) VALUES (?1,?2,?3,?4,?5)").bind(s.day, String(s.site).slice(0, 60), String(s.channel).slice(0, 30), amt, String(s.note || "").slice(0, 200)).run();
  return J({ ok: true });
}

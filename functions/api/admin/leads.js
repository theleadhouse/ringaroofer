/**
 * Private lead dashboard data. Header "X-Admin-Key" must match the ADMIN_PASS secret (or SBB_TEST_TOKEN until ADMIN_PASS is set).
 *   GET  /api/admin/leads?days=7&test=0|1|all&site=   -> totals, by day, latest 300 leads
 *   GET  /api/admin/leads?id=<lead id>                -> one lead with exact requests sent and buyer responses
 *   POST /api/admin/leads {spend:{day,site,channel,amount,note}}  -> save ad spend for a day (amount 0 deletes)
 */
import { init } from "../../_lib/leadlog.js";
const J = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
function authed(request, env) { const k = request.headers.get("X-Admin-Key") || ""; const want = env.ADMIN_PASS || env.SBB_TEST_TOKEN; return !!want && k === want; }

export async function onRequestGet({ request, env }) {
  if (!authed(request, env)) return J({ error: "locked" }, 401);
  if (!env.LEADS_DB) return J({ error: "no_db", message: "Add the D1 binding LEADS_DB to this Pages project." }, 503);
  const db = env.LEADS_DB; await init(db);
  const u = new URL(request.url), id = u.searchParams.get("id");
  if (id) { const row = await db.prepare("SELECT * FROM leads WHERE id=?1").bind(id).first(); return J({ lead: row }); }
  const days = Math.min(Math.max(parseInt(u.searchParams.get("days") || "7", 10) || 7, 1), 365);
  const since = Date.now() - days * 86400000, test = u.searchParams.get("test") || "all", site = u.searchParams.get("site") || "";
  const where = ["ts > ?1"], args = [since];
  if (test === "0" || test === "1") { where.push(`test = ?${args.length + 1}`); args.push(+test); }
  if (site) { where.push(`site = ?${args.length + 1}`); args.push(site); }
  const W = where.join(" AND ");
  const tot = await db.prepare(`SELECT COUNT(*) leads, SUM(ping_status<>'') pinged, SUM(ping_status IN ('Match','Matched')) matched, SUM(sold) sold,
    ROUND(SUM(revenue),2) revenue, ROUND(SUM(payout),2) payouts FROM leads WHERE ${W}`).bind(...args).first();
  const byDay = (await db.prepare(`SELECT date(ts/1000,'unixepoch') day, COUNT(*) leads, SUM(ping_status IN ('Match','Matched')) matched, SUM(sold) sold,
    ROUND(SUM(revenue),2) revenue, ROUND(SUM(payout),2) payouts FROM leads WHERE ${W} GROUP BY day ORDER BY day DESC`).bind(...args).all()).results;
  const bySource = (await db.prepare(`SELECT source, COUNT(*) leads, SUM(sold) sold, ROUND(SUM(revenue),2) revenue FROM leads WHERE ${W} GROUP BY source ORDER BY leads DESC`).bind(...args).all()).results;
  const reasons = (await db.prepare(`SELECT reason, COUNT(*) n FROM leads WHERE ${W} AND sold=0 AND reason<>'' GROUP BY reason ORDER BY n DESC LIMIT 10`).bind(...args).all()).results;
  const sinceDay = new Date(since).toISOString().slice(0, 10);
  const sp = (await db.prepare(`SELECT day, site, channel, amount, note FROM spend WHERE day >= ?1 ${site ? "AND site = ?2" : ""} ORDER BY day DESC`).bind(...(site ? [sinceDay, site] : [sinceDay])).all()).results;
  const spendTotal = sp.reduce((a, r) => a + (r.amount || 0), 0);
  const rows = (await db.prepare(`SELECT id, ts, site, vertical, test, source, campaign, zip, city, state, material, project, first_name, last_name, phone,
    buyer, ping_status, ping_price, post_status, post_price, sold, revenue, payout, publisher, reason FROM leads WHERE ${W} ORDER BY ts DESC LIMIT 300`).bind(...args).all()).results;
  const sites = (await db.prepare("SELECT DISTINCT site FROM leads ORDER BY site").all()).results.map((r) => r.site);
  const t = { ...tot, spend: Math.round(spendTotal * 100) / 100 };
  t.margin = Math.round(((t.revenue || 0) - (t.payouts || 0) - t.spend) * 100) / 100;
  return J({ days, test, site, sites, totals: t, byDay, bySource, reasons, spend: sp, rows });
}

export async function onRequestPost({ request, env }) {
  if (!authed(request, env)) return J({ error: "locked" }, 401);
  if (!env.LEADS_DB) return J({ error: "no_db" }, 503);
  const db = env.LEADS_DB; await init(db);
  let d; try { d = await request.json(); } catch { return J({ error: "bad json" }, 400); }
  const s = d.spend || {};
  if (!/^\d{4}-\d{2}-\d{2}$/.test(s.day || "") || !s.site || !s.channel) return J({ error: "need day, site, channel" }, 400);
  const amt = Math.round((parseFloat(s.amount) || 0) * 100) / 100;
  if (amt <= 0) await db.prepare("DELETE FROM spend WHERE day=?1 AND site=?2 AND channel=?3").bind(s.day, String(s.site).slice(0, 60), String(s.channel).slice(0, 30)).run();
  else await db.prepare("INSERT OR REPLACE INTO spend (day, site, channel, amount, note) VALUES (?1,?2,?3,?4,?5)").bind(s.day, String(s.site).slice(0, 60), String(s.channel).slice(0, 30), amt, String(s.note || "").slice(0, 200)).run();
  return J({ ok: true });
}

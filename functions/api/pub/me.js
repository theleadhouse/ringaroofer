/** GET /api/pub/me (also /v1/me) — a publisher's own account: limits, daily stats, recent leads and monthly statements. Used by the publisher portal. */
import { J, auth } from "../../_lib/pubs.js";
import { currentUser } from "../../_lib/session.js";
export const onRequestOptions = () => new Response(null, { headers: { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Authorization, Content-Type", "Access-Control-Allow-Methods": "GET" } });
const r2 = (n) => Math.round((n || 0) * 100) / 100;
export async function onRequestGet({ request, env }) {
  if (!request.headers.get("Authorization")) {   // logged in to the portal with email + password
    const u = await currentUser(request, env), p = u && u.role === "publisher" && u.pub_id && await env.LEADS_DB.prepare("SELECT * FROM publishers WHERE id=?1").bind(u.pub_id).first();
    if (!p) return J({ status: "error", reason: "not signed in" }, 401);
    return build(env.LEADS_DB, p);
  }
  const { pub, err } = await auth(env, request, null);
  if (err) {   // a paused publisher can still see their numbers
    const h = (request.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "").trim();
    const p = h && env.LEADS_DB && await env.LEADS_DB.prepare("SELECT * FROM publishers WHERE key=?1").bind(h).first();
    if (!p) return err; return build(env.LEADS_DB, p);
  }
  return build(env.LEADS_DB, pub);
}
async function build(db, pub) {
  const since = Date.now() - 30 * 86400000, all = async (sql, ...b) => (await db.prepare(sql).bind(...b).all()).results;
  const days = await all(`SELECT date(ts/1000,'unixepoch') day, COUNT(*) pings, SUM(payout>0) bids, SUM(lead_id IS NOT NULL) posts, SUM(sold) sold,
    SUM(CASE WHEN sold=1 THEN payout ELSE 0 END) payout, SUM(returned) returned FROM pubpings WHERE pub_id=?1 AND ts>?2 GROUP BY day ORDER BY day DESC`, pub.id, since);
  const pre = await all(`SELECT date(ts/1000,'unixepoch') day, COUNT(*) n, SUM(ok) ok FROM prepings WHERE pub_id=?1 AND ts>?2 GROUP BY day`, pub.id, since);
  const P = Object.fromEntries(pre.map((r) => [r.day, r]));
  const rows = await all(`SELECT id, ts, test, lead, top, payout, status, reason, sold, returned FROM pubpings WHERE pub_id=?1 ORDER BY ts DESC LIMIT 200`, pub.id);
  const leads = rows.map((r) => { let l = {}; try { l = JSON.parse(r.lead || "{}"); } catch {}
    return { ts: r.ts, ping_id: r.id, test: !!r.test, vertical: l.vertical, zip: l.zip, state: l.state, project: l.project, sub_id: l.sub_id || "",
      status: r.returned ? "returned" : r.status, payout: r2(r.sold ? r.payout : 0), offered: r2(r.payout), reason: r.reason || "" }; });
  const statements = (await all(`SELECT strftime('%Y-%m', ts/1000, 'unixepoch') month, SUM(sold) sold, SUM(returned) returned, SUM(CASE WHEN sold=1 THEN payout ELSE 0 END) payable
    FROM pubpings WHERE pub_id=?1 AND test=0 AND sold=1 GROUP BY month ORDER BY month DESC LIMIT 12`, pub.id)).map((s) => ({ ...s, payable: r2(s.payable) }));
  const t = days.reduce((a, d) => { for (const k of ["pings", "bids", "posts", "sold", "payout", "returned"]) a[k] = (a[k] || 0) + (d[k] || 0); return a; }, {});
  t.prepings = pre.reduce((a, r) => a + r.n, 0); t.payout = r2(t.payout);
  return J({ publisher: { name: pub.name, mode: pub.mode, paused_reason: pub.mode === "paused" ? pub.paused_reason || "" : "", verticals: (pub.verticals || "").split(","),
      payout_rule: pub.fixed > 0 ? `$${pub.fixed} per sold lead` : `${Math.round((pub.share || 0.7) * 100)}% of the winning bid`,
      limits: { requests_per_minute: pub.rpm == null ? 60 : pub.rpm, hourly_cap: pub.hourly_cap || 0, daily_cap: pub.daily_cap || 0 } },
    totals_30d: t, days: days.map((d) => ({ ...d, payout: r2(d.payout), prepings: (P[d.day] || {}).n || 0 })), leads, statements });
}

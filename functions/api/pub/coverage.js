/** GET /api/pub/coverage (also /v1/coverage) — what you can send us right now, and how much of your limits is left. */
import { J, auth } from "../../_lib/pubs.js";
import { coverage } from "../../_lib/guard.js";
export const onRequestOptions = () => new Response(null, { headers: { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Authorization, Content-Type", "Access-Control-Allow-Methods": "GET" } });
export async function onRequestGet({ request, env }) {
  const { pub, err } = await auth(env, request, null); if (err) return err;
  const db = env.LEADS_DB, test = pub.mode !== "live", now = Date.now(), d0 = new Date(); d0.setUTCHours(0, 0, 0, 0);
  const cats = [];
  for (const v of (pub.verticals || "roofing").split(",").filter(Boolean)) {
    const projects = v === "roofing" ? ["replace", "new", "repair"] : ["replace", "repair"], open = [];
    for (const p of projects) {
      const label = { roofing: { replace: "Roof replacement", new: "New roof", repair: "Roof repair" }, windows: { replace: "Window replacement", repair: "Window repair" } }[v]?.[p];
      if (label && (await coverage(env, { vertical: v, zip: "10001", project: label, city: "New York", state: "NY", homeowner: "yes" }, test)).buyers) open.push(p);
    }
    cats.push({ vertical: v, open: open.length > 0, projects: open });
  }
  const n = async (sql, ...b) => ((await db.prepare(sql).bind(...b).first()) || {}).n || 0;
  return J({ publisher: pub.name, mode: pub.mode, test, categories: cats, geography: "US lower 48 + AK/HI ZIPs; confirm per lead with /v1/preping",
    limits: { requests_per_minute: pub.rpm == null ? 60 : pub.rpm,
      hourly_cap: pub.hourly_cap || 0, sold_last_hour: await n("SELECT COUNT(*) n FROM pubpings WHERE pub_id=?1 AND ts>?2 AND sold=1", pub.id, now - 3600000),
      daily_cap: pub.daily_cap || 0, sold_today_utc: await n("SELECT COUNT(*) n FROM pubpings WHERE pub_id=?1 AND ts>?2 AND sold=1", pub.id, d0.getTime()) } });
}

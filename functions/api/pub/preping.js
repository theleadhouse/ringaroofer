/**
 * POST /api/pub/preping (also /v1/preping) — the free, instant yes/no before a ping.
 * Send only category + ZIP (+ project, + optional SHA-256 of the phone). No name, phone or email. No buyer is contacted.
 * "accepted" = we have a buyer for it right now, it isn't a duplicate and you're within your limits → go ahead and ping.
 */
import { J, S, body, auth } from "../../_lib/pubs.js";
import { rate, coverage, dupe } from "../../_lib/guard.js";
import { zipPlace } from "../../_lib/sbb.js";
export const onRequestOptions = () => new Response(null, { headers: { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Authorization, Content-Type", "Access-Control-Allow-Methods": "POST" } });
const PRJ = { roofing: { replace: "Roof replacement", replacement: "Roof replacement", new: "New roof", repair: "Roof repair" },
              windows: { replace: "Window replacement", replacement: "Window replacement", new: "Window replacement", repair: "Window repair" } };
export async function onRequestPost({ request, env }) {
  const d = await body(request); if (!d) return J({ status: "error", reason: "send JSON" }, 400);
  const { pub, err } = await auth(env, request, d); if (err) return err;
  const db = env.LEADS_DB, test = pub.mode !== "live";
  const vertical = S(d.vertical, 20).toLowerCase() || "roofing", zip = S(d.zip, 5);
  const no = async (reason, extra = {}, code = 200) => {
    await db.prepare("INSERT INTO prepings (pub_id, ts, test, vertical, zip, state, ok, reason) VALUES (?1,?2,?3,?4,?5,?6,0,?7)").bind(pub.id, Date.now(), test ? 1 : 0, vertical, zip, extra.state || "", reason).run();
    const { state, ...rest } = extra; return J({ status: "rejected", reason, ...rest, test }, code);
  };
  const lim = await rate(db, pub); if (lim) return no(lim.reason, { retry_after: lim.retry_after }, lim.code || 200);
  if (!PRJ[vertical]) return no(`vertical must be one of: ${Object.keys(PRJ).join(", ")}`);
  if (!(pub.verticals || "roofing").split(",").includes(vertical)) return no(`not approved for ${vertical}`);
  if (!/^\d{5}$/.test(zip)) return no("zip must be 5 digits");
  const project = PRJ[vertical][S(d.project, 20).toLowerCase() || "replace"]; if (!project) return no(`project must be one of: ${Object.keys(PRJ[vertical]).join(", ")}`);
  const pl = await zipPlace(zip); if (!pl) return no("unknown zip");
  const ph = /^[a-f0-9]{64}$/i.test(S(d.phone_hash, 64)) ? S(d.phone_hash, 64).toLowerCase() : "", eh = /^[a-f0-9]{64}$/i.test(S(d.email_hash, 64)) ? S(d.email_hash, 64).toLowerCase() : "";
  const dp = await dupe(db, ph, eh, test); if (dp) return no(dp, { state: pl.state });
  const cov = await coverage(env, { vertical, zip, project, city: pl.city, state: pl.state, homeowner: "yes" }, test);
  if (!cov.buyers) return no(test ? `${cov.why} (test)` : "no buyer for this lead", { state: pl.state });
  await db.prepare("INSERT INTO prepings (pub_id, ts, test, vertical, zip, state, ok, reason) VALUES (?1,?2,?3,?4,?5,?6,1,'')").bind(pub.id, Date.now(), test ? 1 : 0, vertical, zip, pl.state).run();
  return J({ status: "accepted", city: pl.city, state: pl.state, next: "send the ping", test });
}

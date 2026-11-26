/** POST /api/pub/ping — publisher sends a lead without name/phone/email; we ask our buyers and answer with our bid. See /publisher-spec/. */
import { J, S, body, auth, normPing, payoutFor } from "../../_lib/pubs.js";
import { pingAll } from "../../_lib/buyers.js";
import { zipPlace } from "../../_lib/sbb.js";
import { rate, dupe } from "../../_lib/guard.js";
export const onRequestOptions = () => new Response(null, { headers: { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Authorization, Content-Type", "Access-Control-Allow-Methods": "POST" } });
export async function onRequestPost({ request, env }) {
  const d = await body(request); if (!d) return J({ status: "error", reason: "send JSON" }, 400);
  const { pub, err } = await auth(env, request, d); if (err) return err;
  const n = normPing(d); if (n.reason) return J({ status: "rejected", reason: n.reason }, 200);
  const lead = n.lead, db = env.LEADS_DB, test = pub.mode !== "live";
  if (!(pub.verticals || "roofing").split(",").includes(lead.vertical)) return J({ status: "rejected", reason: `not approved for ${lead.vertical}` });
  const lim = await rate(db, pub); if (lim) return J({ status: "rejected", reason: lim.reason, retry_after: lim.retry_after }, lim.code || 200);
  const ph = /^[a-f0-9]{64}$/i.test(S(d.phone_hash, 64)) ? S(d.phone_hash, 64).toLowerCase() : "";
  const dp = await dupe(db, ph, "", test); if (dp) return J({ status: "rejected", reason: dp });
  if (!lead.city || !lead.state) { const pl = await zipPlace(lead.zip); if (pl) { lead.city = lead.city || pl.city; lead.state = lead.state || pl.state; } }
  if (!lead.state) return J({ status: "rejected", reason: "unknown zip" });
  lead.source = "publisher"; lead.source_site = `pub:${pub.name}`; lead.pub_id = pub.id;
  const P = await pingAll(env, lead, test ? { only: "demo", testOnly: true, demo: true } : { liveOnly: true });   // test publishers only ever reach the Demo Buyer
  const top = P.offers.length ? P.offers[0].price : 0, payout = top ? payoutFor(pub, top) : 0;
  const id = "P-" + crypto.randomUUID().replace(/-/g, "").slice(0, 20);
  const accepted = P.offers.length > 0 && payout > 0;
  const reason = accepted ? "" : P.offers.length ? "below your fixed payout" : (P.attempts.map((a) => a.error || a.status).filter(Boolean)[0] || "no buyer for this lead");
  await db.prepare(`INSERT INTO pubpings (id, pub_id, ts, test, lead, offers, top, payout, status, reason) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10)`)
    .bind(id, pub.id, Date.now(), test ? 1 : 0, JSON.stringify(lead), JSON.stringify(P.attempts.map((a) => ({ ...a, req: a.req, raw: a.raw }))), top, payout, accepted ? "open" : "rejected", reason).run();
  if (!accepted) return J({ status: "rejected", ping_id: id, reason: test ? `${reason} (test)` : "no buyer for this lead" });
  return J({ status: "accepted", ping_id: id, payout, currency: "USD", expires_in: 120, test });
}

/** POST /api/pub/post — publisher sends the full lead for an accepted ping; we sell it to the best buyer and answer accepted/rejected. */
import { J, S, body, auth } from "../../_lib/pubs.js";
import { postBest, loadModes, envWith } from "../../_lib/buyers.js";
import { logLead, phoneHash, emailHash, suppressed } from "../../_lib/leadlog.js";
import { quality } from "../../_lib/guard.js";
export const onRequestOptions = () => new Response(null, { headers: { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Authorization, Content-Type", "Access-Control-Allow-Methods": "POST" } });
export async function onRequestPost({ request, env }) {
  const d = await body(request); if (!d) return J({ status: "error", reason: "send JSON" }, 400);
  const { pub, err } = await auth(env, request, d); if (err) return err;
  const db = env.LEADS_DB, pid = S(d.ping_id, 40);
  const pp = pid && await db.prepare("SELECT * FROM pubpings WHERE id=?1 AND pub_id=?2").bind(pid, pub.id).first();
  if (!pp) return J({ status: "rejected", reason: "unknown ping_id" });
  if (pp.status !== "open") return J({ status: "rejected", reason: `ping already ${pp.status}` });
  if (Date.now() - pp.ts > 150000) { await db.prepare("UPDATE pubpings SET status='expired' WHERE id=?1").bind(pid).run(); return J({ status: "rejected", reason: "ping expired (post within 2 minutes)" }); }
  const phone = S(d.phone, 20).replace(/\D/g, "").replace(/^1(?=\d{10}$)/, ""), email = S(d.email, 120).toLowerCase();
  const fn = S(d.first_name, 60), ln = S(d.last_name, 60);
  const bad = !fn || !ln ? "first_name and last_name are required" : !/^[2-9]\d{2}[2-9]\d{6}$/.test(phone) ? "phone must be a valid 10-digit US number"
    : !/^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i.test(email) ? "email is invalid" : "";
  if (bad) return J({ status: "rejected", reason: bad });
  const dup = await db.prepare("SELECT id FROM leads WHERE phone=?1 AND ts>?2 AND test=?3 LIMIT 1").bind(phone, Date.now() - 30 * 86400000, pp.test).first();
  const lead = { ...JSON.parse(pp.lead), first_name: fn, last_name: ln, phone, email, address: S(d.address, 120), lead_id: crypto.randomUUID(), publisher: pub.name };
  if (d.trustedform_cert_url) lead.xxTrustedFormCertUrl = S(d.trustedform_cert_url, 300);
  const pingAttempts = JSON.parse(pp.offers || "[]");
  const finish = async (sale, payout, reason) => {
    await logLead(env, lead, { ...sale, attempts: [...pingAttempts, ...(sale.attempts || []).filter((a) => a.stage === "post")], reason }, { test: !!pp.test, source: "publisher", publisher: pub.name, payout });
    await db.prepare("UPDATE pubpings SET status=?2, sold=?3, lead_id=?4, reason=?5 WHERE id=?1").bind(pid, sale.sold ? "sold" : "rejected", sale.sold ? 1 : 0, lead.lead_id, reason || "").run();
    try { await quality(db, pub); } catch (e) { console.log("quality", String(e)); }
  };
  if (await suppressed(db, await phoneHash(phone), await emailHash(email))) { await finish({ sold: false, attempts: [] }, 0, "consumer opted out"); return J({ status: "rejected", reason: "consumer opted out" }); }
  if (dup) { await finish({ sold: false, attempts: [] }, 0, "duplicate phone in last 30 days"); return J({ status: "rejected", reason: "duplicate phone in last 30 days" }); }
  const offers = pingAttempts.filter((a) => a.stage === "ping" && a.ok).sort((x, y) => y.price - x.price);
  const env2 = envWith(env, await loadModes(env));
  const sale = await postBest(env2, lead, offers, []);
  if (sale.sold) { await finish(sale, pp.payout, ""); return J({ status: "accepted", payout: pp.payout, currency: "USD", lead_id: lead.lead_id, test: !!pp.test }); }
  const why = sale.attempts.map((a) => a.error).filter(Boolean)[0] || "rejected by buyer";
  await finish(sale, 0, why);
  return J({ status: "rejected", reason: pp.test ? `${why} (test)` : why });
}

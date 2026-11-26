/**
 * GET /api/sbb-test?token=...  — runs sample leads through the LoanBright/SBBnet ping-post on the UAT TEST server only.
 * Locked: needs the SBB_TEST_TOKEN secret, and refuses to run when SBB_LIVE=1. Test leads are never used in production (per the spec).
 */
import { pingPost, roofFields } from "../_lib/sbb.js";
const J = (o, s = 200) => new Response(JSON.stringify(o, null, 2), { status: s, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
export async function onRequestGet({ request, env }) {
  const u = new URL(request.url);
  if (!env.SBB_TEST_TOKEN || u.searchParams.get("token") !== env.SBB_TEST_TOKEN) return J({ error: "locked" }, 403);
  if (env.SBB_LIVE === "1") return J({ error: "live mode: test runner disabled" }, 403);
  const tenv = { ...env, SBB_SRC: "Test" };   // always the Test SRC here
  const base = { homeowner: "yes", first_name: "Test", last_name: "Lead", email: "test.lead@example.com", phone: "2065550147", address: "123 Test St",
    ip_address: request.headers.get("CF-Connecting-IP") || "198.51.100.20", landing_page: "https://ringaroofer.com/get-a-quote/", consent_text: "Test consent", lead_id: crypto.randomUUID(),
    xxTrustedFormCertUrl: "https://cert.trustedform.com/0000000000000000000000000000000000000000", universal_leadid: "" };
  const cases = [
    { name: "Seattle WA, asphalt, replace", city: "Seattle", state: "WA", zip: "98103", material: "Asphalt shingle", project: "Roof replacement" },
    { name: "Denver CO, metal, repair", city: "Denver", state: "CO", zip: "80205", material: "Metal", project: "Roof repair" },
    { name: "Cairo IL (spec example), tile, repair", city: "Cairo", state: "IL", zip: "62914", material: "Tile", project: "Roof repair" },
    { name: "Houston TX, asphalt, storm", city: "Houston", state: "TX", zip: "77002", material: "Asphalt shingle", project: "Storm or hail repair" },
  ];
  const only = u.searchParams.get("case");
  const results = [];
  for (const c of cases) {
    if (only && !c.name.toLowerCase().includes(only.toLowerCase())) continue;
    const lead = { ...base, ...c, lead_id: crypto.randomUUID(), email: `test.${Date.now()}@example.com` };
    const r = await pingPost(tenv, lead);
    results.push({ case: c.name, roof: roofFields(c.material, c.project), sold: r.sold, stage: r.stage, price: r.price, reason: r.reason,
      ping: r.ping && { status: r.ping.status, id: r.ping.id, price: r.ping.price, error: r.ping.error, raw: r.ping.raw },
      post: r.post && { status: r.post.status, id: r.post.id, price: r.post.price, error: r.post.error, raw: r.post.raw } });
  }
  return J({ server: "UAT (test)", ran_at: new Date().toISOString(), results });
}

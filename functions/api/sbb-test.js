/**
 * GET /api/sbb-test?token=...&buyer=loanbright|connatria|alpine&case=...  — sends sample leads to a buyer's TEST system and logs them.
 * Locked: token must match ADMIN_PASS (or SBB_TEST_TOKEN). Refuses to run for any buyer that is switched to live.
 */
import { sell, byId, ALL_BUYERS, loadModes } from "../_lib/buyers.js";
import { logLead } from "../_lib/leadlog.js";
const J = (o, s = 200) => new Response(JSON.stringify(o, null, 2), { status: s, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
const CASES = {
  roofing: [
    { name: "Seattle WA, asphalt, replace", city: "Seattle", state: "WA", zip: "98103", material: "Asphalt shingle", project: "Roof replacement" },
    { name: "Denver CO, metal, new roof", city: "Denver", state: "CO", zip: "80205", material: "Metal", project: "New roof" },
    { name: "Houston TX, asphalt, storm repair", city: "Houston", state: "TX", zip: "77002", material: "Asphalt shingle", project: "Storm or hail repair" },
  ],
  windows: [
    { name: "Lakewood CO, 4 windows, replace", city: "Lakewood", state: "CO", zip: "80226", material: "Vinyl", project: "Window replacement", windows_count: "4" },
  ],
};
export async function onRequestGet({ request, env }) {
  const u = new URL(request.url), tok = u.searchParams.get("token") || "";
  if (!tok || (tok !== env.SBB_TEST_TOKEN && tok !== env.ADMIN_PASS)) return J({ error: "locked" }, 403);
  const bid = (u.searchParams.get("buyer") || "loanbright").toLowerCase(), b = byId(bid);
  if (!b) return J({ error: "unknown buyer", buyers: ALL_BUYERS.map((x) => x.id) }, 400);
  if (!b.configured(env)) return J({ error: `${b.name} is not connected yet (keys missing in Cloudflare)` }, 400);
  const modes = await loadModes(env);
  if (modes[bid] === "live") return J({ error: `${b.name} is LIVE: test leads are blocked` }, 403);
  if (modes[bid] === "paused") return J({ error: `${b.name} is paused: switch it to Test to send a test lead` }, 403);
  const vert = u.searchParams.get("vertical") || (b.verticals.includes("roofing") && bid !== "alpine" ? "roofing" : "windows");
  const only = (u.searchParams.get("case") || "").toLowerCase(), n = Math.min(+u.searchParams.get("n") || 1, 3);
  const cases = (CASES[vert] || []).filter((c) => !only || c.name.toLowerCase().includes(only)).slice(0, n);
  const results = [];
  for (const c of cases) {
    const uid = crypto.randomUUID().replace(/-/g, "");
    const lead = { vertical: vert, homeowner: "yes", first_name: "Test", last_name: "Lead", email: `test.${uid.slice(0, 10)}@theleadhouse.com`, phone: "2065550147", address: "123 Test St",
      ip_address: request.headers.get("CF-Connecting-IP") || "198.51.100.20", user_agent: request.headers.get("User-Agent") || "Mozilla/5.0", source_site: u.hostname.replace(/^www\./, ""), source: "test-runner",
      landing_page: `https://${u.hostname}/get-a-quote/`, submitted_at: new Date().toISOString(), lead_id: crypto.randomUUID(),
      consent_text: "By clicking Get my quote, I agree to the Terms and Privacy Policy and give my express written consent to be contacted about my project (TEST LEAD).",
      xxTrustedFormCertUrl: `https://cert.trustedform.com/${uid}${uid.slice(0, 8)}`, universal_leadid: u.searchParams.get("leadid") || (bid === "alpine" ? "00000000-0000-0000-0000-000000000000" : ""), ...c };
    const r = await sell(env, lead, bid, { modes, testOnly: true });
    await logLead(env, lead, r, { test: true, source: "test-runner" });
    results.push({ case: c.name, buyer: b.name, sold: r.sold, price: r.price, reason: r.reason || "", attempts: r.attempts.map((a) => ({ stage: a.stage, status: a.status, ok: !!a.ok, price: a.price, error: a.error, ms: a.ms, raw: a.raw })) });
  }
  return J({ buyer: b.name, server: "TEST", ran_at: new Date().toISOString(), results });
}

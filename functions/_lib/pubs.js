/** Publisher (traffic source) helpers: auth by API key, field mapping, payout. */
import { init } from "./leadlog.js";
export const J = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "Content-Type": "application/json", "Cache-Control": "no-store", "Access-Control-Allow-Origin": "*" } });
export const S = (v, n = 120) => String(v == null ? "" : v).trim().slice(0, n);
export async function body(request) {
  const ct = request.headers.get("Content-Type") || "";
  if (/json/i.test(ct)) { try { return await request.json(); } catch { return null; } }
  try { const f = await request.formData(); return Object.fromEntries(f.entries()); } catch { return null; }
}
export async function auth(env, request, d) {
  if (!env.LEADS_DB) return { err: J({ status: "error", reason: "service not ready" }, 503) };
  await init(env.LEADS_DB);
  const h = request.headers.get("Authorization") || "";
  const key = (h.replace(/^Bearer\s+/i, "") || (d && d.api_key) || "").trim();
  if (!key) return { err: J({ status: "error", reason: "missing API key (Authorization: Bearer <key>)" }, 401) };
  const pub = await env.LEADS_DB.prepare("SELECT * FROM publishers WHERE key=?1").bind(key).first();
  if (!pub) return { err: J({ status: "error", reason: "invalid API key" }, 401) };
  if (pub.mode === "paused") return { err: J({ status: "rejected", reason: "publisher paused" }, 200) };
  return { pub };
}
const MAT = { asphalt: "Asphalt shingle", asphalt_shingle: "Asphalt shingle", shingle: "Asphalt shingle", metal: "Metal", tile: "Clay tile", clay_tile: "Clay tile", cement_tile: "Cement tile",
  flat: "Flat", wood_shake: "Wood shake", wood: "Wood shake", shake: "Wood shake", slate: "Slate", other: "Not sure", unknown: "Not sure" };
const PRJ = { roofing: { replace: "Roof replacement", replacement: "Roof replacement", new: "New roof", repair: "Roof repair" },
              windows: { replace: "Window replacement", replacement: "Window replacement", new: "Window replacement", repair: "Window repair" } };
/** Validate + normalize a ping. Returns { lead } or { reason }. */
export function normPing(d) {
  const vertical = S(d.vertical, 20).toLowerCase() || "roofing";
  if (!PRJ[vertical]) return { reason: `vertical must be one of: ${Object.keys(PRJ).join(", ")}` };
  const zip = S(d.zip, 5); if (!/^\d{5}$/.test(zip)) return { reason: "zip must be 5 digits" };
  const ho = d.homeowner === true || /^(true|yes|1)$/i.test(String(d.homeowner)); if (!ho) return { reason: "homeowner must be true" };
  const project = PRJ[vertical][S(d.project, 20).toLowerCase()]; if (!project) return { reason: `project must be one of: ${Object.keys(PRJ[vertical]).join(", ")}` };
  const tf = S(d.trustedform_cert_url, 300); if (!/^https:\/\/cert\.trustedform\.com\/[a-f0-9]{20,}/i.test(tf)) return { reason: "trustedform_cert_url is required (https://cert.trustedform.com/...)" };
  const consent = S(d.tcpa_consent_text, 3000); if (consent.length < 30) return { reason: "tcpa_consent_text is required" };
  const lp = S(d.landing_page_url, 400); if (!/^https?:\/\//.test(lp)) return { reason: "landing_page_url is required" };
  const ip = S(d.ip_address, 45); if (!/^[0-9a-f.:]{7,45}$/i.test(ip)) return { reason: "ip_address is required" };
  const material = vertical === "roofing" ? (MAT[S(d.roof_material, 30).toLowerCase()] || "Not sure") : S(d.window_material || "", 30);
  return { lead: { vertical, zip, city: S(d.city, 60), state: S(d.state, 2).toUpperCase(), homeowner: "yes", project, material, windows_count: S(d.windows_count, 3),
    xxTrustedFormCertUrl: tf, universal_leadid: S(d.jornaya_leadid, 100), consent_text: consent, landing_page: lp, ip_address: ip, user_agent: S(d.user_agent, 400),
    sub_id: S(d.sub_id, 60), best_time_to_call: S(d.best_time_to_call, 12).toLowerCase(), submitted_at: S(d.lead_created_at, 40) || new Date().toISOString() } };
}
export function payoutFor(pub, top) {
  if (pub.fixed > 0) return top >= pub.fixed ? Math.round(pub.fixed * 100) / 100 : 0;
  return Math.round(top * (pub.share || 0.7) * 100) / 100;
}

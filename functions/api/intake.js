/**
 * POST /api/intake (also /v1/intake) — form leads from our other homeowner sites (first: housefirecleanup.com).
 * Saved to the Lead Desk (leads + 5-year consent record). No buyer is connected for these categories yet, so nothing is sold or shared automatically.
 * Allowed sites are listed in SITES; add a domain there to accept its form.
 */
import { logLead, init, phoneHash, emailHash, suppressed } from "../_lib/leadlog.js";
import { sendMail } from "../_lib/session.js";
const SITES = { "housefirecleanup.com": "fire" };
const host = (o) => { try { return new URL(o).hostname.replace(/^www\./, ""); } catch { return ""; } };
const H = (o) => ({ "Content-Type": "application/json", "Cache-Control": "no-store", "Access-Control-Allow-Origin": SITES[host(o)] || /\.pages\.dev$/.test(host(o)) ? o : "https://housefirecleanup.com", "Vary": "Origin" });
const S = (v, n = 200) => String(v == null ? "" : v).replace(/[\u0000-\u001f]/g, " ").trim().slice(0, n);
export const onRequestOptions = ({ request }) => new Response(null, { headers: { ...H(request.headers.get("Origin") || ""), "Access-Control-Allow-Headers": "Content-Type", "Access-Control-Allow-Methods": "POST" } });
export async function onRequestPost({ request, env }) {
  const o = request.headers.get("Origin") || "", J = (x, s = 200) => new Response(JSON.stringify(x), { status: s, headers: H(o) });
  const site = host(o), pagesPreview = /^[a-z0-9-]+\.housefirecleanup\.pages\.dev$|^housefirecleanup\.pages\.dev$/.test(site);
  const vertical = SITES[site] || (pagesPreview ? "fire" : "");
  if (!vertical) return J({ error: "This form isn't connected yet." }, 403);
  if (!env.LEADS_DB) return J({ error: "Please try again shortly." }, 503);
  let d; try { d = await request.json(); } catch { return J({ error: "Invalid request." }, 400); }
  if (d.company_website) return J({ ok: true });                                   // honeypot
  if ((+d.elapsed_ms || 0) < 3000) return J({ error: "Please take a moment to review the form, then submit again." }, 400);
  const phone = S(d.phone, 30).replace(/\D/g, "").replace(/^1(?=\d{10}$)/, ""), email = S(d.email, 254).toLowerCase(), zip = S(d.zip, 10).slice(0, 5);
  if (!S(d.first_name) || !S(d.last_name)) return J({ error: "Please enter your first and last name." }, 400);
  if (!/^[2-9]\d{2}[2-9]\d{6}$/.test(phone)) return J({ error: "Please enter a valid 10-digit US phone number." }, 400);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return J({ error: "Please enter a valid email address." }, 400);
  if (!/^\d{5}$/.test(zip)) return J({ error: "Please enter a valid US ZIP code." }, 400);
  if (d.consent_share !== "yes") return J({ error: "Please check the consent box so we can respond to your request." }, 400);
  const db = env.LEADS_DB; await init(db);
  const ip = request.headers.get("CF-Connecting-IP") || "";
  const recent = await db.prepare("SELECT COUNT(*) n FROM leads WHERE site=?1 AND ts>?2 AND page LIKE ?3").bind(site || "housefirecleanup.com", Date.now() - 3600000, "%").first();
  if (recent && recent.n > 200) return J({ error: "Please try again later." }, 429);
  const lead = { vertical, source_site: pagesPreview ? "housefirecleanup.com (preview)" : site, lead_id: crypto.randomUUID(),
    first_name: S(d.first_name, 80), last_name: S(d.last_name, 80), phone, email, zip, address: S(d.address, 120),
    project: S(d.service, 100), material: "", homeowner: "yes", consent_text: S(d.consent_text, 3000) + (d.consent_sms === "yes" ? " | SMS: " + S(d.sms_text, 500) : ""),
    xxTrustedFormCertUrl: S(d.xxTrustedFormCertUrl, 300), landing_page: S(d.page_url, 400), ip_address: ip, user_agent: S(request.headers.get("User-Agent"), 300),
    submitted_at: new Date().toISOString(), utm_source: S(d.utm_source, 200), utm_campaign: S(d.utm_campaign, 200), details: S(d.details, 2000) };
  const optedOut = await suppressed(db, await phoneHash(phone), await emailHash(email));
  await logLead(env, lead, { sold: false, attempts: [], reason: (optedOut ? "consumer previously opted out" : "no buyer connected for " + vertical + " yet · follow up manually") + (lead.details ? " · Details: " + lead.details.slice(0, 400) : "") + (d.consent_sms === "yes" ? " · SMS ok" : "") },
    { test: pagesPreview ? 1 : 0, source: S(d.utm_source, 40) || "organic/direct" });
  if (env.LEAD_ALERT_TO) await sendMail(env, env.LEAD_ALERT_TO, `New ${vertical} lead · ${zip} · ${lead.project}`,
    `New request from ${site}\n\nName: ${lead.first_name} ${lead.last_name}\nPhone: ${phone}\nEmail: ${email}\nZIP: ${zip}\nService: ${lead.project}\nDetails: ${lead.details}\nSMS consent: ${d.consent_sms === "yes" ? "yes" : "no"}\n\nOpen the Lead Desk: https://app.homeproradar.com/app/admin/`);
  return J({ ok: true });
}

/**
 * POST /api/lead — RingaRoofer callback form.
 * Validates, blocks bots, then delivers the lead to every destination you configure
 * (Cloudflare Pages → Settings → Variables and Secrets):
 *   LEAD_WEBHOOK_URL   any URL that accepts JSON (TrackDrive lead post URL, Zapier, Make, Google Apps Script)
 *   LEAD_WEBHOOK_TOKEN optional token, sent as ?token= and header X-Token
 *   RESEND_API_KEY + LEAD_EMAIL_TO (+ LEAD_EMAIL_FROM)   email copy of each lead via Resend
 * At least one destination must be set, or the form returns an error and asks people to call.
 */
const J = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });

export async function onRequestPost({ request, env }) {
  const origin = request.headers.get("Origin") || "";
  if (origin && !/^https:\/\/(www\.)?ringaroofer\.com$|\.pages\.dev$/.test(origin)) return J({ error: "origin" }, 403);
  let d; try { d = await request.json(); } catch { return J({ error: "bad request" }, 400); }
  if (d.website) return J({ ok: true });                       // honeypot: pretend success
  if ((+d.elapsed_ms || 0) < 3000) return J({ error: "too fast" }, 400);
  const phone = String(d.phone || "").replace(/\D/g, "").replace(/^1(?=\d{10}$)/, "");
  if (phone.length !== 10 || /^(\d)\1{9}$/.test(phone) || /^[01]/.test(phone)) return J({ error: "phone" }, 400);
  if (!/^\d{5}$/.test(String(d.zip || ""))) return J({ error: "zip" }, 400);
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(String(d.email || ""))) return J({ error: "email" }, 400);
  const lead = {
    first_name: String(d.first_name || "").slice(0, 60), last_name: String(d.last_name || "").slice(0, 60), phone, email: String(d.email).slice(0, 120),
    zip: d.zip, service: String(d.service || "").slice(0, 60), roof_type: String(d.roof_type || "").slice(0, 60), timing: String(d.timing || "").slice(0, 40),
    details: String(d.details || "").slice(0, 1000), trustedform_cert_url: String(d.xxTrustedFormCertUrl || ""),
    consent_text: String(d.consent_text || "").slice(0, 1200), page: String(d.page || "").slice(0, 300),
    ip: request.headers.get("CF-Connecting-IP") || "", user_agent: (request.headers.get("User-Agent") || "").slice(0, 300),
    submitted_at: new Date().toISOString(), source: "ringaroofer.com",
  };
  for (const k of ["gclid", "gbraid", "wbraid", "msclkid", "fbclid", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"]) if (d[k]) lead[k] = String(d[k]).slice(0, 200);
  const jobs = [];
  if (env.LEAD_WEBHOOK_URL) {
    const u = new URL(env.LEAD_WEBHOOK_URL); if (env.LEAD_WEBHOOK_TOKEN) u.searchParams.set("token", env.LEAD_WEBHOOK_TOKEN);
    jobs.push(fetch(u, { method: "POST", headers: { "Content-Type": "application/json", "X-Token": env.LEAD_WEBHOOK_TOKEN || "" }, body: JSON.stringify(lead) }).then((r) => r.ok));
  }
  if (env.RESEND_API_KEY && env.LEAD_EMAIL_TO) {
    const rows = Object.entries(lead).map(([k, v]) => `<tr><td><b>${k}</b></td><td>${String(v).replace(/[<>&]/g, "")}</td></tr>`).join("");
    jobs.push(fetch("https://api.resend.com/emails", { method: "POST", headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, "Content-Type": "application/json" },
      body: JSON.stringify({ from: env.LEAD_EMAIL_FROM || "RingaRoofer <leads@ringaroofer.com>", to: env.LEAD_EMAIL_TO.split(","), subject: `New roofing lead: ${lead.service} · ${lead.zip}`, html: `<table>${rows}</table>` }) }).then((r) => r.ok));
  }
  if (!jobs.length) return J({ error: "not configured" }, 503);
  const res = await Promise.allSettled(jobs);
  return res.some((r) => r.status === "fulfilled" && r.value) ? J({ ok: true }) : J({ error: "delivery" }, 502);
}

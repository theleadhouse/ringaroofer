/**
 * POST /api/quote — smart quote form (/get-a-quote/) (RingaRoofer roofing, BathVisionary bathroom).
 * Validates + bot-checks the lead, then sends it to your ping tree and/or email. Configure in Cloudflare Pages →
 * Settings → Variables and Secrets (no code changes needed when the buyer's spec arrives):
 *   QUOTE_POST_URL     ping tree / lead platform POST URL (required to sell leads)
 *   QUOTE_POST_FORMAT  "json" (default) or "form" (application/x-www-form-urlencoded)
 *   QUOTE_FIELD_MAP    optional JSON renaming our fields to theirs, e.g. {"first_name":"FirstName","phone":"Phone","xxTrustedFormCertUrl":"TrustedFormURL"}
 *   QUOTE_EXTRA        optional JSON of fixed fields the platform needs, e.g. {"lp_campaign_id":"123","lp_campaign_key":"abc"}
 *   QUOTE_TEST         "1" adds test=1 to every post (for buyer testing)
 *   RESEND_API_KEY + LEAD_EMAIL_TO (+ LEAD_EMAIL_FROM)  email copy of every lead
 *   LEADS              optional KV binding: keeps a 90-day backup log of every lead + the platform's response
 */
const J = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
const S = (v, n = 120) => String(v == null ? "" : v).trim().slice(0, n);
const ALLOWED = /^https:\/\/(www\.)?(ringaroofer|bathvisionary)\.com$|\.pages\.dev$/;

export async function onRequestPost({ request, env }) {
  const origin = request.headers.get("Origin") || "";
  if (origin && !ALLOWED.test(origin)) return J({ error: "origin" }, 403);
  let d; try { d = await request.json(); } catch { return J({ error: "bad request" }, 400); }
  if (d.website) return J({ ok: true });                                  // honeypot
  if ((+d.elapsed_ms || 0) < 4000) return J({ error: "too fast" }, 400);  // humans need > 4s for 3 steps
  const phone = S(d.phone).replace(/\D/g, "").replace(/^1(?=\d{10}$)/, "");
  if (!/^[2-9]\d{2}[2-9]\d{6}$/.test(phone) || /^(\d)\1{9}$/.test(phone)) return J({ error: "phone" }, 400);
  if (!/^\d{5}$/.test(S(d.zip))) return J({ error: "zip" }, 400);
  if (!/^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i.test(S(d.email))) return J({ error: "email" }, 400);
  if (d.consent !== "yes") return J({ error: "consent" }, 400);
  if (!S(d.first_name) || !S(d.last_name)) return J({ error: "missing" }, 400);
  const host = new URL(request.url).hostname.replace(/^www\./, "");
  const lead = {
    vertical: S(d.vertical, 20), source_site: host, first_name: S(d.first_name, 60), last_name: S(d.last_name, 60), phone, email: S(d.email).toLowerCase(),
    address: S(d.address, 120), city: S(d.city, 60), state: S(d.state, 2).toUpperCase(), zip: S(d.zip, 5),
    homeowner: S(d.homeowner, 10), project: S(d.project, 60), material: S(d.material, 60), property_type: S(d.property_type, 40), timeframe: S(d.timeframe, 40),
    stories: S(d.stories, 20), xxTrustedFormCertUrl: S(d.xxTrustedFormCertUrl, 300), consent: "yes", consent_text: S(d.consent_text, 2000),
    landing_page: S(d.page, 400), ip_address: request.headers.get("CF-Connecting-IP") || "", user_agent: S(request.headers.get("User-Agent"), 300),
    submitted_at: new Date().toISOString(),
  };
  for (const k of ["gclid", "gbraid", "wbraid", "msclkid", "fbclid", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"]) if (d[k]) lead[k] = S(d[k], 200);

  const jobs = [], log = { lead, platform: null };
  if (env.QUOTE_POST_URL) {
    let map = {}, extra = {}; try { map = JSON.parse(env.QUOTE_FIELD_MAP || "{}"); } catch {} try { extra = JSON.parse(env.QUOTE_EXTRA || "{}"); } catch {}
    const out = { ...extra }; for (const [k, v] of Object.entries(lead)) out[map[k] || k] = v; if (env.QUOTE_TEST === "1") out.test = 1;
    const form = (env.QUOTE_POST_FORMAT || "json").toLowerCase() === "form";
    jobs.push(fetch(env.QUOTE_POST_URL, { method: "POST", headers: { "Content-Type": form ? "application/x-www-form-urlencoded" : "application/json", Accept: "application/json, text/plain, */*" },
      body: form ? new URLSearchParams(out).toString() : JSON.stringify(out) })
      .then(async (r) => { log.platform = { status: r.status, body: (await r.text()).slice(0, 2000) }; return r.ok; }).catch((e) => { log.platform = { error: String(e) }; return false; }));
  }
  if (env.RESEND_API_KEY && env.LEAD_EMAIL_TO) {
    const rows = Object.entries(lead).map(([k, v]) => `<tr><td><b>${k}</b></td><td>${String(v).replace(/[<>&]/g, "")}</td></tr>`).join("");
    jobs.push(fetch("https://api.resend.com/emails", { method: "POST", headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, "Content-Type": "application/json" },
      body: JSON.stringify({ from: env.LEAD_EMAIL_FROM || `Leads <leads@${host}>`, to: env.LEAD_EMAIL_TO.split(","), subject: `New ${lead.vertical} lead · ${lead.zip} · ${lead.project}`, html: `<table>${rows}</table>` }) })
      .then((r) => r.ok).catch(() => false));
  }
  if (!jobs.length) return J({ error: "not configured" }, 503);
  const res = await Promise.allSettled(jobs);
  if (env.LEADS) { try { await env.LEADS.put(`lead:${lead.submitted_at}:${phone}`, JSON.stringify(log), { expirationTtl: 90 * 86400 }); } catch {} }
  return res.some((r) => r.status === "fulfilled" && r.value) ? J({ ok: true }) : J({ error: "delivery" }, 502);
}

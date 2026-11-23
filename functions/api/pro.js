/**
 * POST /api/pro — "For Plumbing Pros" application form (ringaroofer.com/for-roofing-pros/).
 * Validates and bot-checks, then sends the application to (Cloudflare Pages → Settings → Variables and Secrets):
 *   PRO_WEBHOOK_URL    Google Apps Script web app URL (appends a row to your Google Sheet) — or any URL that accepts JSON
 *   PRO_WEBHOOK_TOKEN  optional shared token, sent as "token" in the JSON body
 * No secrets live in this file.
 */
const J = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
const S = (v, n = 120) => String(v == null ? "" : v).trim().slice(0, n);
const ALLOWED = /^https:\/\/(www\.)?ringaroofer\.com$|\.pages\.dev$/;

export async function onRequestPost({ request, env }) {
  const origin = request.headers.get("Origin") || "";
  if (origin && !ALLOWED.test(origin)) return J({ error: "origin" }, 403);
  let d; try { d = await request.json(); } catch { return J({ error: "bad request" }, 400); }
  if (d.website) return J({ ok: true });                                   // honeypot
  if ((+d.elapsed_ms || 0) < 4000) return J({ error: "too fast" }, 400);
  const phone = S(d.phone).replace(/\D/g, "").replace(/^1(?=\d{10}$)/, "");
  if (!/^[2-9]\d{2}[2-9]\d{6}$/.test(phone)) return J({ error: "phone" }, 400);
  if (!/^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i.test(S(d.email))) return J({ error: "email" }, 400);
  if (!S(d.company) || !S(d.contact)) return J({ error: "missing" }, 400);
  if (d.agree !== "yes") return J({ error: "agree" }, 400);
  if (!env.PRO_WEBHOOK_URL) return J({ error: "not configured" }, 503);
  const row = {
    token: env.PRO_WEBHOOK_TOKEN || "", submitted_at: new Date().toISOString(), source: "ringaroofer.com/for-roofing-pros",
    company: S(d.company, 120), contact: S(d.contact, 80), phone, email: S(d.email, 120).toLowerCase(), website: S(d.site, 200),
    states: S(d.states, 200), areas: S(d.areas, 600), services: S(d.services, 600), emergency: S(d.emergency, 40), capacity: S(d.capacity, 40),
    state_number: S(d.state_number, 80), years: S(d.years, 20), notes: S(d.notes, 1000),
    ip: request.headers.get("CF-Connecting-IP") || "", user_agent: S(request.headers.get("User-Agent"), 300),
  };
  try {
    const r = await fetch(env.PRO_WEBHOOK_URL, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(row), redirect: "follow" });
    return r.ok ? J({ ok: true }) : J({ error: "delivery" }, 502);
  } catch { return J({ error: "delivery" }, 502); }
}

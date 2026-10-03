// GET  /api/reviews?pest=Roof%20leak&limit=6  -> published reviews (all ratings, newest first) + summary
// POST /api/reviews                          -> submit a review (held for moderation; nothing is published automatically)
import { json, clean, pub, listPrefix, PESTS, STATES } from "./_rv.js";

export async function onRequestGet({ request, env }) {
  if (!env.REVIEWS) return json({ reviews: [], count: 0, note: "reviews storage not connected" });
  const u = new URL(request.url), pest = u.searchParams.get("pest"), limit = Math.min(+u.searchParams.get("limit") || 50, 200);
  let all = await listPrefix(env.REVIEWS, "approved:");
  if (pest) all = all.filter((r) => r.pest === pest);
  const count = all.length, avg = count ? Math.round((all.reduce((s, r) => s + r.rating, 0) / count) * 10) / 10 : 0;
  const dist = [5, 4, 3, 2, 1].map((n) => all.filter((r) => r.rating === n).length);
  return json({ count, avg, dist, reviews: all.slice(0, limit).map(pub) }, 200, { "cache-control": "public, max-age=120" });
}

export async function onRequestPost({ request, env }) {
  if (!env.REVIEWS) return json({ ok: false, error: "Reviews aren't switched on yet." }, 503);
  let b; try { b = await request.json(); } catch { return json({ ok: false, error: "Bad request." }, 400); }
  if (b.website) return json({ ok: true }); // honeypot: bots fill hidden fields
  const ip = request.headers.get("cf-connecting-ip") || "0";
  // Optional bot check (Cloudflare Turnstile) when TURNSTILE_SECRET is set.
  if (env.TURNSTILE_SECRET) {
    const fd = new FormData(); fd.append("secret", env.TURNSTILE_SECRET); fd.append("response", b.turnstile || ""); fd.append("remoteip", ip);
    const v = await (await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", { method: "POST", body: fd })).json();
    if (!v.success) return json({ ok: false, error: "Please complete the check and try again." }, 400);
  }
  // Simple rate limit: 3 reviews per IP per day.
  const rk = "rl:" + ip, n = +(await env.REVIEWS.get(rk) || 0);
  if (n >= 3) return json({ ok: false, error: "Thanks, we've already received your review." }, 429);
  const r = {
    name: clean(b.name, 40), city: clean(b.city, 40), state: STATES.includes(b.state) ? b.state : "", pest: PESTS.includes(b.pest) ? b.pest : "",
    rating: Math.max(1, Math.min(5, parseInt(b.rating, 10) || 0)), title: clean(b.title, 80), text: clean(b.text, 1500),
    callDate: /^\d{4}-\d{2}-\d{2}$/.test(b.callDate || "") ? b.callDate : "", last4: String(b.last4 || "").replace(/\D/g, "").slice(-4),
    email: clean(b.email, 120), consent: b.consent === true,
  };
  if (!r.name || !r.state || !r.pest || !b.rating || r.text.length < 20 || !r.consent)
    return json({ ok: false, error: "Please fill in your name, state, the roofing job, star rating, at least a couple of sentences, and tick the box." }, 400);
  r.id = Date.now().toString(36) + Math.random().toString(36).slice(2, 7); r.created = new Date().toISOString(); r.verified = false; r.ip = ip;
  await env.REVIEWS.put("pending:" + r.id, JSON.stringify(r));
  await env.REVIEWS.put(rk, String(n + 1), { expirationTtl: 86400 });
  if (env.RESEND_API_KEY && env.REVIEW_NOTIFY_TO) {
    try {
      await fetch("https://api.resend.com/emails", { method: "POST", headers: { authorization: "Bearer " + env.RESEND_API_KEY, "content-type": "application/json" },
        body: JSON.stringify({ from: env.REVIEW_NOTIFY_FROM || "Reviews <reviews@ringaroofer.com>", to: env.REVIEW_NOTIFY_TO,
          subject: `New ${r.rating}-star review to check (${r.pest}, ${r.state})`, text: `${r.name}, ${r.city} ${r.state}\nCall date: ${r.callDate}  Phone last 4: ${r.last4}\n\n${r.title}\n${r.text}\n\nApprove at /review-admin/` }) });
    } catch (e) {}
  }
  return json({ ok: true });
}

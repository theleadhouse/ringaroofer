/** POST /api/access (also /v1/access) — "Request access" form on homeproradar.com/exchange/. Saved to D1 (shown on the Lead Desk). */
import { init } from "../_lib/leadlog.js";
const ORIGINS = /^https:\/\/(www\.)?homeproradar\.com$|^https:\/\/(www\.)?housefirecleanup\.com$|\.pages\.dev$|^https:\/\/ringaroofer\.com$/;
const H = (o) => ({ "Content-Type": "application/json", "Cache-Control": "no-store", "Access-Control-Allow-Origin": o && ORIGINS.test(o) ? o : "https://homeproradar.com", "Vary": "Origin" });
const S = (v, n = 200) => String(v == null ? "" : v).replace(/[\u0000-\u001f]/g, " ").trim().slice(0, n);
export const onRequestOptions = ({ request }) => new Response(null, { headers: { ...H(request.headers.get("Origin")), "Access-Control-Allow-Headers": "Content-Type", "Access-Control-Allow-Methods": "POST" } });
export async function onRequestPost({ request, env }) {
  const o = request.headers.get("Origin") || "", J = (x, s = 200) => new Response(JSON.stringify(x), { status: s, headers: H(o) });
  if (o && !ORIGINS.test(o)) return J({ ok: false, error: "origin" }, 403);
  if (!env.LEADS_DB) return J({ ok: false, error: "not ready" }, 503);
  let d; try { d = await request.json(); } catch { return J({ ok: false, error: "bad json" }, 400); }
  if (d.website_url) return J({ ok: true });                                   // honeypot
  if ((+d.elapsed || 0) < 3000) return J({ ok: false, error: "too fast" }, 400);
  const name = S(d.name, 80), company = S(d.company, 100), email = S(d.email, 120).toLowerCase();
  if (!name || !company || !/^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i.test(email)) return J({ ok: false, error: "Please add your name, company and a valid email." }, 400);
  const db = env.LEADS_DB; await init(db);
  await db.prepare(`CREATE TABLE IF NOT EXISTS access_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, ts INTEGER, name TEXT, company TEXT, email TEXT, phone TEXT,
    role TEXT, verticals TEXT, volume TEXT, website TEXT, message TEXT, ip TEXT, status TEXT DEFAULT 'new')`).run();
  const recent = await db.prepare("SELECT COUNT(*) n FROM access_requests WHERE ip=?1 AND ts>?2").bind(request.headers.get("CF-Connecting-IP") || "", Date.now() - 3600000).first();
  if (recent && recent.n >= 5) return J({ ok: false, error: "Too many requests. Please email us instead." }, 429);
  await db.prepare("INSERT INTO access_requests (ts, name, company, email, phone, role, verticals, volume, website, message, ip) VALUES (?1,?2,?3,?4,?5,?6,?7,?8,?9,?10,?11)")
    .bind(Date.now(), name, company, email, S(d.phone, 30), S(d.role, 40), S(Array.isArray(d.verticals) ? d.verticals.join(", ") : d.verticals, 120), S(d.volume, 40), S(d.website, 200), S(d.message, 1500),
      request.headers.get("CF-Connecting-IP") || "").run();
  return J({ ok: true });
}

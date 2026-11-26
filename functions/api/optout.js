/** POST /api/optout {phone?, email?} — consumer opt-out. Stored only as a SHA-256 hash; blocks future publisher leads for that phone/email. */
import { init, phoneHash, emailHash } from "../_lib/leadlog.js";
const J = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "Content-Type": "application/json", "Cache-Control": "no-store", "Access-Control-Allow-Origin": "*" } });
export const onRequestOptions = () => new Response(null, { headers: { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type", "Access-Control-Allow-Methods": "POST" } });
export async function onRequestPost({ request, env }) {
  if (!env.LEADS_DB) return J({ ok: false, error: "not ready" }, 503);
  let d = {}; try { d = /json/i.test(request.headers.get("Content-Type") || "") ? await request.json() : Object.fromEntries((await request.formData()).entries()); } catch {}
  const ph = await phoneHash(d.phone), eh = await emailHash(d.email);
  if (!ph && !eh) return J({ ok: false, error: "Enter a 10-digit US phone number or an email address." }, 400);
  const db = env.LEADS_DB; await init(db); const now = Date.now(), src = String(d.source || "web").slice(0, 40);
  const st = []; if (ph) st.push(db.prepare("INSERT OR IGNORE INTO suppress (hash, kind, ts, source) VALUES (?1,'phone',?2,?3)").bind(ph, now, src));
  if (eh) st.push(db.prepare("INSERT OR IGNORE INTO suppress (hash, kind, ts, source) VALUES (?1,'email',?2,?3)").bind(eh, now, src));
  await db.batch(st);
  return J({ ok: true, message: "Done. We have recorded your opt-out and will stop sharing your request. Partners who already received it are told within 10 business days." });
}

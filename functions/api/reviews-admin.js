// Moderation API. Header: Authorization: Bearer <ADMIN_TOKEN>
// GET  -> pending reviews (with call date + phone last 4 so you can match the call in TrackDrive)
// POST {id, action: "approve"|"reject"|"unpublish", verified: true|false, reply: "optional public reply"}
import { json, clean, listPrefix } from "./_rv.js";
const ok = (request, env) => env.ADMIN_TOKEN && (request.headers.get("authorization") || "") === "Bearer " + env.ADMIN_TOKEN;

export async function onRequestGet({ request, env }) {
  if (!ok(request, env)) return json({ error: "Not allowed" }, 401);
  return json({ pending: await listPrefix(env.REVIEWS, "pending:"), published: (await listPrefix(env.REVIEWS, "approved:")).slice(0, 50) });
}
export async function onRequestPost({ request, env }) {
  if (!ok(request, env)) return json({ error: "Not allowed" }, 401);
  const b = await request.json().catch(() => ({})), id = String(b.id || "").replace(/[^a-z0-9]/g, "");
  if (!id) return json({ error: "Missing id" }, 400);
  if (b.action === "unpublish") { await env.REVIEWS.delete("approved:" + id); return json({ ok: true }); }
  const r = await env.REVIEWS.get("pending:" + id, "json");
  if (!r) return json({ error: "Not found" }, 404);
  await env.REVIEWS.delete("pending:" + id);
  if (b.action === "approve") {
    r.verified = !!b.verified; r.reply = clean(b.reply, 600); r.approved = new Date().toISOString();
    delete r.last4; delete r.ip; delete r.email; // keep personal details out of published storage
    await env.REVIEWS.put("approved:" + id, JSON.stringify(r));
  }
  return json({ ok: true });
}

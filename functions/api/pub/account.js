/** /api/pub/account — for a publisher signed in to the portal: GET shows their API key, POST {action:"rotate"} makes a new one. */
import { J } from "../../_lib/pubs.js";
import { currentUser, audit } from "../../_lib/session.js";
export async function onRequest({ request, env }) {
  const u = await currentUser(request, env);
  if (!u || u.role !== "publisher" || !u.pub_id) return J({ error: "not signed in" }, 401);
  const db = env.LEADS_DB, p = await db.prepare("SELECT id, name, key FROM publishers WHERE id=?1").bind(u.pub_id).first();
  if (!p) return J({ error: "no publisher" }, 404);
  if (request.method === "POST") {
    let d = {}; try { d = await request.json(); } catch {}
    if (d.action !== "rotate") return J({ error: "unknown action" }, 400);
    const key = "rx_" + crypto.randomUUID().replace(/-/g, "") + crypto.randomUUID().replace(/-/g, "").slice(0, 8);
    await db.prepare("UPDATE publishers SET key=?2 WHERE id=?1").bind(p.id, key).run(); await audit(db, request, u, "api key rotated", p.name);
    return J({ ok: true, key });
  }
  return J({ key: p.key, name: p.name });
}

/**
 * Dashboard settings (X-Admin-Key). GET: buyers with mode + publishers with stats.
 * POST {action}: buyer_mode {id, mode: paused|test|live} · buyer_min {id, min} ·
 *   pub_create {name, email, share, fixed, verticals, daily_cap} · pub_update {id, mode, share, fixed, daily_cap, verticals} · pub_rotate {id}
 */
import { init } from "../../_lib/leadlog.js";
import { BUYERS, loadModes, liveBlock, byId } from "../../_lib/buyers.js";
const J = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
function authed(request, env) { const k = request.headers.get("X-Admin-Key") || ""; const want = env.ADMIN_PASS || env.SBB_TEST_TOKEN; return !!want && k === want; }
const newKey = () => "tlh_" + crypto.randomUUID().replace(/-/g, "") + crypto.randomUUID().replace(/-/g, "").slice(0, 8);
async function state(env) {
  const db = env.LEADS_DB, modes = await loadModes(env);
  const buyers = BUYERS.map((b) => ({ id: b.id, name: b.name, verticals: b.verticals, connected: b.configured(env), mode: b.configured(env) ? modes[b.id] : "off",
    live_block: liveBlock(b, env), min: parseFloat(modes["min:" + b.id] || env[`${b.id.toUpperCase()}_MIN_PRICE`] || "0") || 0 }));
  const pubs = (await db.prepare("SELECT * FROM publishers ORDER BY created DESC").all()).results;
  const since = Date.now() - 30 * 86400000;
  const st = (await db.prepare(`SELECT pub_id, COUNT(*) pings, SUM(status<>'rejected' OR lead_id IS NOT NULL) bids, SUM(lead_id IS NOT NULL) posts, SUM(sold) sold,
    SUM(CASE WHEN sold=1 AND test=0 THEN payout ELSE 0 END) owed, SUM(CASE WHEN sold=1 THEN payout ELSE 0 END) payout_all, AVG(CASE WHEN payout>0 THEN payout END) avg_bid
    FROM pubpings WHERE ts>?1 GROUP BY pub_id`).bind(since).all()).results;
  const S = Object.fromEntries(st.map((r) => [r.pub_id, r]));
  return { buyers, publishers: pubs.map((p) => ({ ...p, key_hint: p.key.slice(0, 8) + "…" + p.key.slice(-4), stats: S[p.id] || {} })) };
}
export async function onRequestGet({ request, env }) {
  if (!authed(request, env)) return J({ error: "locked" }, 401);
  if (!env.LEADS_DB) return J({ error: "no_db" }, 503);
  await init(env.LEADS_DB); return J(await state(env));
}
export async function onRequestPost({ request, env }) {
  if (!authed(request, env)) return J({ error: "locked" }, 401);
  if (!env.LEADS_DB) return J({ error: "no_db" }, 503);
  const db = env.LEADS_DB; await init(db);
  let d; try { d = await request.json(); } catch { return J({ error: "bad json" }, 400); }
  const set = (k, v) => db.prepare("INSERT OR REPLACE INTO settings (k, v) VALUES (?1, ?2)").bind(k, String(v)).run();
  if (d.action === "buyer_mode") {
    const b = byId(d.id); if (!b || b.internal) return J({ error: "unknown buyer" }, 400);
    if (!["paused", "test", "live"].includes(d.mode)) return J({ error: "mode must be paused, test or live" }, 400);
    if (d.mode === "live") { const why = liveBlock(b, env); if (why) return J({ error: `${b.name} can't go live yet: ${why}` }, 400); }
    await set(`mode:${b.id}`, d.mode);
  } else if (d.action === "buyer_min") {
    const b = byId(d.id); if (!b) return J({ error: "unknown buyer" }, 400); await set(`min:${b.id}`, Math.max(0, parseFloat(d.min) || 0));
  } else if (d.action === "pub_create") {
    const name = String(d.name || "").trim().slice(0, 60); if (!name) return J({ error: "name required" }, 400);
    const id = "pub_" + crypto.randomUUID().slice(0, 8), key = newKey();
    await db.prepare(`INSERT INTO publishers (id, name, email, key, mode, share, fixed, verticals, daily_cap, created, note) VALUES (?1,?2,?3,?4,'test',?5,?6,?7,?8,?9,?10)`)
      .bind(id, name, String(d.email || "").slice(0, 120), key, Math.min(0.95, Math.max(0.05, parseFloat(d.share) || 0.7)), Math.max(0, parseFloat(d.fixed) || 0),
        String(d.verticals || "roofing").toLowerCase().replace(/[^a-z,]/g, "") || "roofing", Math.max(0, parseInt(d.daily_cap, 10) || 0), Date.now(), String(d.note || "").slice(0, 200)).run();
    return J({ ok: true, id, key, ...(await state(env)) });
  } else if (d.action === "pub_update") {
    const p = await db.prepare("SELECT * FROM publishers WHERE id=?1").bind(d.id).first(); if (!p) return J({ error: "unknown publisher" }, 400);
    const mode = ["paused", "test", "live"].includes(d.mode) ? d.mode : p.mode;
    await db.prepare("UPDATE publishers SET mode=?2, share=?3, fixed=?4, daily_cap=?5, verticals=?6 WHERE id=?1").bind(p.id, mode,
      d.share != null ? Math.min(0.95, Math.max(0.05, parseFloat(d.share) || p.share)) : p.share, d.fixed != null ? Math.max(0, parseFloat(d.fixed) || 0) : p.fixed,
      d.daily_cap != null ? Math.max(0, parseInt(d.daily_cap, 10) || 0) : p.daily_cap, d.verticals ? String(d.verticals).toLowerCase().replace(/[^a-z,]/g, "") : p.verticals).run();
  } else if (d.action === "pub_rotate") {
    const key = newKey(); await db.prepare("UPDATE publishers SET key=?2 WHERE id=?1").bind(d.id, key).run(); return J({ ok: true, key, ...(await state(env)) });
  } else if (d.action === "pub_key") {
    const p = await db.prepare("SELECT key FROM publishers WHERE id=?1").bind(d.id).first(); return J({ ok: true, key: p && p.key });
  } else return J({ error: "unknown action" }, 400);
  return J({ ok: true, ...(await state(env)) });
}

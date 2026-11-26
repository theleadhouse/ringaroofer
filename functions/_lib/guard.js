/**
 * Volume guard for publisher traffic — the cheap checks that run BEFORE any buyer is contacted.
 *   rate()      requests per minute per key (pre-pings + pings), hourly + daily sold caps
 *   coverage()  is there any buyer that could take this category + ZIP + project right now (no buyer is called)
 *   dupe()      same phone already sold in the last 30 days, or on the opt-out list
 *   quality()   auto-pause a live publisher whose posts keep getting rejected
 */
import { pick, loadModes, envWith } from "./buyers.js";
import { suppressed } from "./leadlog.js";

const MIN = 60000, HOUR = 3600000;
export const Q = { window: 50, minPosts: 20, maxReject: 0.6 };   // last 50 posts; pause when >60% rejected (once 20+ posts)

export async function rate(db, pub) {
  const now = Date.now(), rpm = pub.rpm == null ? 60 : pub.rpm;
  if (rpm > 0) {
    const r = await db.prepare(`SELECT (SELECT COUNT(*) FROM prepings WHERE pub_id=?1 AND ts>?2) + (SELECT COUNT(*) FROM pubpings WHERE pub_id=?1 AND ts>?2) n`).bind(pub.id, now - MIN).first();
    if (r && r.n >= rpm) return { reason: `rate limit: max ${rpm} requests per minute`, retry_after: 60, code: 429 };
  }
  if (pub.hourly_cap > 0) {
    const r = await db.prepare("SELECT COUNT(*) n FROM pubpings WHERE pub_id=?1 AND ts>?2 AND sold=1").bind(pub.id, now - HOUR).first();
    if (r && r.n >= pub.hourly_cap) return { reason: "hourly cap reached", retry_after: 600 };
  }
  if (pub.daily_cap > 0) {
    const d0 = new Date(); d0.setUTCHours(0, 0, 0, 0);
    const r = await db.prepare("SELECT COUNT(*) n FROM pubpings WHERE pub_id=?1 AND ts>?2 AND sold=1").bind(pub.id, d0.getTime()).first();
    if (r && r.n >= pub.daily_cap) return { reason: "daily cap reached", retry_after: Math.ceil((d0.getTime() + 86400000 - now) / 1000) };
  }
  return null;
}

/** Which buyers could take it, without calling any of them. test publishers only ever see the Demo Buyer. */
export async function coverage(env, lead, test) {
  const modes = await loadModes(env), e = envWith(env, modes), skipped = [];
  const active = pick(e, lead, test ? { only: "demo", testOnly: true, demo: true, modes } : { liveOnly: true, modes }, skipped);
  return { buyers: active.length, why: active.length ? "" : (skipped.map((a) => a.error).filter(Boolean)[0] || "no buyer for this category right now") };
}

export async function dupe(db, ph, eh, test) {
  if (await suppressed(db, ph, eh)) return "consumer opted out";
  if (ph) {
    const r = await db.prepare("SELECT id FROM leads WHERE phone_hash=?1 AND ts>?2 AND test=?3 AND sold=1 LIMIT 1").bind(ph, Date.now() - 30 * 86400000, test ? 1 : 0).first();
    if (r) return "duplicate phone in last 30 days";
  }
  return "";
}

/** After each post: pause a LIVE publisher when too many of its recent posts were rejected by buyers. */
export async function quality(db, pub) {
  if (pub.mode !== "live") return null;
  const rows = (await db.prepare("SELECT sold FROM pubpings WHERE pub_id=?1 AND lead_id IS NOT NULL ORDER BY ts DESC LIMIT ?2").bind(pub.id, Q.window).all()).results;
  if (rows.length < Q.minPosts) return null;
  const rej = rows.filter((r) => !r.sold).length / rows.length;
  if (rej <= Q.maxReject) return null;
  const why = `auto-paused ${new Date().toISOString().slice(0, 16).replace("T", " ")} UTC: ${Math.round(rej * 100)}% of last ${rows.length} posts rejected`;
  await db.prepare("UPDATE publishers SET mode='paused', paused_reason=?2 WHERE id=?1").bind(pub.id, why).run();
  return why;
}

/** Publisher quality numbers for the dashboard (last 30 days). */
export async function scores(db) {
  const since = Date.now() - 30 * 86400000;
  const pre = (await db.prepare("SELECT pub_id, COUNT(*) n, SUM(ok) ok FROM prepings WHERE ts>?1 GROUP BY pub_id").bind(since).all()).results;
  const post = (await db.prepare("SELECT pub_id, COUNT(*) posts, SUM(sold) sold FROM pubpings WHERE ts>?1 AND lead_id IS NOT NULL GROUP BY pub_id").bind(since).all()).results;
  const out = {};
  for (const r of pre) out[r.pub_id] = { prepings: r.n, preping_ok: r.ok || 0 };
  for (const r of post) { const o = (out[r.pub_id] = out[r.pub_id] || {}); o.posts = r.posts; o.post_sold = r.sold || 0; o.reject_rate = r.posts ? Math.round((1 - (r.sold || 0) / r.posts) * 100) : 0; }
  return out;
}

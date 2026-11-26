/**
 * /api/auth/<action> — accounts for the Radar Exchange app.
 *   GET  me                          who is logged in (+ whether first-time setup is needed)
 *   POST setup   {admin_pass, name, email, password}   first admin only, proven with the ADMIN_PASS secret
 *   POST login   {email, password}   -> session cookie, or {step:"code"} when an email code is required
 *   POST verify  {ticket, code}      -> session cookie
 *   POST logout
 *   POST invite  {email, name, role, pub_id}  (admin) -> invite link (also emailed when email is set up)
 *   POST accept  {token, password}   set a password from an invite / reset link -> session cookie
 *   POST forgot  {email}             emails a reset link (always answers ok)
 *   POST password {current, password}
 *   GET  users                       (admin) list accounts · POST user_status {id, status} (admin)
 */
import { initAuth, currentUser, startSession, endSession, setCookie, hashPassword, safeEq, pwProblem, randomToken, sendMail, mailReady, appUrl, audit } from "../../_lib/session.js";
import { sha } from "../../_lib/leadlog.js";

const J = (o, s = 200, h = {}) => new Response(JSON.stringify(o), { status: s, headers: { "Content-Type": "application/json", "Cache-Control": "no-store", ...h } });
const S = (v, n = 200) => String(v == null ? "" : v).trim().slice(0, n);
const okEmail = (e) => /^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i.test(e);
const LOCK = { max: 8, win: 15 * 60000 };

async function tooMany(db, k) {
  const r = await db.prepare("SELECT COUNT(*) n FROM login_fails WHERE k=?1 AND ts>?2").bind(k, Date.now() - LOCK.win).first();
  return r && r.n >= LOCK.max;
}
const fail = (db, k) => db.prepare("INSERT INTO login_fails (k, ts) VALUES (?1, ?2)").bind(k, Date.now()).run();
const pub = (u) => u && ({ id: u.id, email: u.email, name: u.name, role: u.role, pub_id: u.pub_id, two_step: !!u.two_step });

async function issueCode(env, db, u) {
  const code = String(100000 + (crypto.getRandomValues(new Uint32Array(1))[0] % 900000)), ticket = randomToken(24);
  await db.prepare("INSERT INTO login_codes (ticket_hash, user_id, code_hash, exp, tries) VALUES (?1,?2,?3,?4,0)").bind(await sha(ticket), u.id, await sha(code), Date.now() + 10 * 60000).run();
  const sent = await sendMail(env, u.email, `Your sign-in code: ${code}`, `Your Radar Exchange sign-in code is ${code}\n\nIt expires in 10 minutes. If you didn't try to sign in, change your password.`);
  return { ticket, sent };
}

export async function onRequest({ request, env, params }) {
  const db = env.LEADS_DB; if (!db) return J({ error: "not ready" }, 503);
  await initAuth(db);
  const a = params.action, m = request.method, ip = request.headers.get("CF-Connecting-IP") || "";
  let d = {}; if (m === "POST") { try { d = await request.json(); } catch { return J({ error: "bad json" }, 400); } }
  const me = await currentUser(request, env);

  if (a === "me" && m === "GET") {
    const n = await db.prepare("SELECT COUNT(*) n FROM users WHERE role='admin'").first();
    return J({ user: pub(me), needs_setup: !n || !n.n, email_ready: mailReady(env) });
  }
  if (a === "setup" && m === "POST") {
    const n = await db.prepare("SELECT COUNT(*) n FROM users WHERE role='admin'").first(); if (n && n.n) return J({ error: "Setup is already done. Sign in instead." }, 400);
    if (await tooMany(db, "setup:" + ip)) return J({ error: "Too many tries. Wait 15 minutes." }, 429);
    if (!env.ADMIN_PASS || !safeEq(S(d.admin_pass, 200), env.ADMIN_PASS)) { await fail(db, "setup:" + ip); return J({ error: "The setup password is wrong." }, 401); }
    const email = S(d.email, 120).toLowerCase(), pw = String(d.password || ""); if (!okEmail(email)) return J({ error: "Enter a valid email." }, 400);
    const bad = pwProblem(pw); if (bad) return J({ error: bad }, 400);
    const { hash, salt } = await hashPassword(pw), id = "u_" + randomToken(9);
    await db.prepare("INSERT INTO users (id, email, name, role, pw_hash, pw_salt, status, two_step, created) VALUES (?1,?2,?3,'admin',?4,?5,'active',1,?6)").bind(id, email, S(d.name, 80) || "Admin", hash, salt, Date.now()).run();
    const u = await db.prepare("SELECT * FROM users WHERE id=?1").bind(id).first(); await audit(db, request, u, "setup");
    return J({ ok: true, user: pub(u) }, 200, { "Set-Cookie": setCookie(await startSession(db, u, request)) });
  }
  if (a === "login" && m === "POST") {
    const email = S(d.email, 120).toLowerCase(), k = "login:" + email;
    if (await tooMany(db, k) || await tooMany(db, "ip:" + ip)) return J({ error: "Too many tries. Wait 15 minutes, or reset your password." }, 429);
    const u = await db.prepare("SELECT * FROM users WHERE email=?1").bind(email).first();
    const { hash } = u && u.pw_salt ? await hashPassword(String(d.password || ""), u.pw_salt) : await hashPassword("x");
    if (!u || u.status !== "active" || !safeEq(hash, u.pw_hash)) { await fail(db, k); await fail(db, "ip:" + ip); return J({ error: "Email or password is wrong." }, 401); }
    if (u.two_step && mailReady(env)) {
      const { ticket, sent } = await issueCode(env, db, u);
      if (sent) return J({ step: "code", ticket, to: u.email.replace(/^(.).*(@.*)$/, "$1•••$2") });
    }
    await audit(db, request, u, "login", u.two_step && !mailReady(env) ? "email code skipped: email not set up" : "");
    return J({ ok: true, user: pub(u), warn: u.two_step && !mailReady(env) ? "Email codes are not switched on yet (email sending isn't set up)." : "" }, 200, { "Set-Cookie": setCookie(await startSession(db, u, request)) });
  }
  if (a === "verify" && m === "POST") {
    const th = await sha(S(d.ticket, 100)), row = await db.prepare("SELECT * FROM login_codes WHERE ticket_hash=?1").bind(th).first();
    if (!row || row.exp < Date.now() || row.tries >= 5) return J({ error: "That code expired. Sign in again." }, 401);
    if (!safeEq(await sha(S(d.code, 10).replace(/\D/g, "")), row.code_hash)) { await db.prepare("UPDATE login_codes SET tries=tries+1 WHERE ticket_hash=?1").bind(th).run(); return J({ error: "Wrong code." }, 401); }
    await db.prepare("DELETE FROM login_codes WHERE ticket_hash=?1 OR exp<?2").bind(th, Date.now()).run();
    const u = await db.prepare("SELECT * FROM users WHERE id=?1").bind(row.user_id).first(); await audit(db, request, u, "login", "with email code");
    return J({ ok: true, user: pub(u) }, 200, { "Set-Cookie": setCookie(await startSession(db, u, request)) });
  }
  if (a === "logout" && m === "POST") { await endSession(request, env); return J({ ok: true }, 200, { "Set-Cookie": setCookie("", 0) }); }
  if (a === "invite" && m === "POST") {
    if (!me || me.role !== "admin") return J({ error: "locked" }, 401);
    const email = S(d.email, 120).toLowerCase(), role = ["admin", "publisher"].includes(d.role) ? d.role : "publisher"; if (!okEmail(email)) return J({ error: "Enter a valid email." }, 400);
    if (role === "publisher" && !(await db.prepare("SELECT id FROM publishers WHERE id=?1").bind(S(d.pub_id, 40)).first())) return J({ error: "Pick the publisher this login belongs to." }, 400);
    const token = randomToken(), exp = Date.now() + 7 * 86400000, ex = await db.prepare("SELECT * FROM users WHERE email=?1").bind(email).first();
    if (ex) await db.prepare("UPDATE users SET invite_hash=?2, invite_exp=?3, role=?4, pub_id=?5, name=COALESCE(NULLIF(?6,''),name) WHERE id=?1").bind(ex.id, await sha(token), exp, role, role === "publisher" ? S(d.pub_id, 40) : null, S(d.name, 80)).run();
    else await db.prepare("INSERT INTO users (id, email, name, role, pub_id, status, invite_hash, invite_exp, two_step, created) VALUES (?1,?2,?3,?4,?5,'invited',?6,?7,?8,?9)")
      .bind("u_" + randomToken(9), email, S(d.name, 80), role, role === "publisher" ? S(d.pub_id, 40) : null, await sha(token), exp, role === "admin" ? 1 : 0, Date.now()).run();
    const link = `${appUrl(env, request)}/app/#invite=${token}`;
    const sent = await sendMail(env, email, "Your Radar Exchange account", `Hi${d.name ? " " + S(d.name, 80) : ""},\n\nYour Radar Exchange account is ready. Set your password here (link valid 7 days):\n${link}\n\nHomeProRadar`);
    await audit(db, request, me, "invite", `${email} as ${role}`);
    return J({ ok: true, link, emailed: sent });
  }
  if (a === "accept" && m === "POST") {
    const th = await sha(S(d.token, 100)), u = await db.prepare("SELECT * FROM users WHERE invite_hash=?1").bind(th).first();
    if (!u || u.invite_exp < Date.now() || u.status === "disabled") return J({ error: "This link has expired. Ask for a new one." }, 400);
    const bad = pwProblem(d.password); if (bad) return J({ error: bad }, 400);
    const { hash, salt } = await hashPassword(String(d.password));
    await db.batch([db.prepare("UPDATE users SET pw_hash=?2, pw_salt=?3, status='active', invite_hash=NULL, invite_exp=NULL WHERE id=?1").bind(u.id, hash, salt),
      db.prepare("DELETE FROM sessions WHERE user_id=?1").bind(u.id)]);
    await audit(db, request, u, "password set");
    return J({ ok: true, user: pub({ ...u, status: "active" }) }, 200, { "Set-Cookie": setCookie(await startSession(db, u, request)) });
  }
  if (a === "forgot" && m === "POST") {
    const email = S(d.email, 120).toLowerCase(), u = await db.prepare("SELECT * FROM users WHERE email=?1 AND status='active'").bind(email).first();
    if (u && mailReady(env) && !(await tooMany(db, "forgot:" + email))) {
      await fail(db, "forgot:" + email);
      const token = randomToken(); await db.prepare("UPDATE users SET invite_hash=?2, invite_exp=?3 WHERE id=?1").bind(u.id, await sha(token), Date.now() + 3600000).run();
      await sendMail(env, u.email, "Reset your Radar Exchange password", `Reset your password here (link valid 1 hour):\n${appUrl(env, request)}/app/#invite=${token}\n\nIf you didn't ask for this, ignore this email.`);
    }
    return J({ ok: true, email_ready: mailReady(env) });
  }
  if (a === "password" && m === "POST") {
    if (!me) return J({ error: "locked" }, 401);
    const { hash } = await hashPassword(String(d.current || ""), me.pw_salt); if (!safeEq(hash, me.pw_hash)) return J({ error: "Current password is wrong." }, 401);
    const bad = pwProblem(d.password); if (bad) return J({ error: bad }, 400);
    const n = await hashPassword(String(d.password)); await db.prepare("UPDATE users SET pw_hash=?2, pw_salt=?3 WHERE id=?1").bind(me.id, n.hash, n.salt).run();
    await audit(db, request, me, "password changed"); return J({ ok: true });
  }
  if (a === "users" && m === "GET") {
    if (!me || me.role !== "admin") return J({ error: "locked" }, 401);
    const users = (await db.prepare("SELECT id, email, name, role, pub_id, status, two_step, created, last_login FROM users ORDER BY created DESC").all()).results;
    const log = (await db.prepare("SELECT ts, email, action, detail, ip FROM audit ORDER BY ts DESC LIMIT 60").all()).results;
    return J({ users, audit: log, email_ready: mailReady(env) });
  }
  if (a === "user_status" && m === "POST") {
    if (!me || me.role !== "admin") return J({ error: "locked" }, 401);
    if (d.id === me.id) return J({ error: "You can't change your own account here." }, 400);
    const st = ["active", "disabled"].includes(d.status) ? d.status : null;
    if (st) await db.batch([db.prepare("UPDATE users SET status=?2 WHERE id=?1 AND status<>'invited'").bind(d.id, st), ...(st === "disabled" ? [db.prepare("DELETE FROM sessions WHERE user_id=?1").bind(d.id)] : [])]);
    if (d.two_step != null) await db.prepare("UPDATE users SET two_step=?2 WHERE id=?1").bind(d.id, d.two_step ? 1 : 0).run();
    await audit(db, request, me, "user updated", JSON.stringify(d)); return J({ ok: true });
  }
  return J({ error: "not found" }, 404);
}

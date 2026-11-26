/**
 * Accounts for the Radar Exchange app (app.homeproradar.com): admins and publishers log in with email + password.
 * Passwords: PBKDF2-SHA256, 100k rounds, random salt. Sessions: random token in an HttpOnly, Secure, SameSite=Lax cookie; only its SHA-256 is stored.
 * Admins also confirm a 6-digit code sent by email (needs RESEND_API_KEY + AUTH_FROM). Publishers can turn the same code on per account.
 * Machine access (the ping/post API) still uses API keys: keys are for servers, passwords are for people.
 */
import { init, sha } from "./leadlog.js";

export const COOKIE = "rx_s";
const HOURS = 12;
let ready = null;
export function initAuth(db) {
  if (!ready) ready = init(db).then(() => db.batch([
    db.prepare(`CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, email TEXT UNIQUE NOT NULL, name TEXT, role TEXT NOT NULL, pub_id TEXT, pw_hash TEXT, pw_salt TEXT,
      status TEXT DEFAULT 'invited', invite_hash TEXT, invite_exp INTEGER, two_step INTEGER DEFAULT 0, created INTEGER, last_login INTEGER)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS sessions (hash TEXT PRIMARY KEY, user_id TEXT NOT NULL, created INTEGER, expires INTEGER, ip TEXT, ua TEXT)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS login_codes (ticket_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL, code_hash TEXT, exp INTEGER, tries INTEGER DEFAULT 0)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS login_fails (k TEXT NOT NULL, ts INTEGER NOT NULL)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY AUTOINCREMENT, ts INTEGER, user_id TEXT, email TEXT, action TEXT, detail TEXT, ip TEXT)`),
  ])).catch((e) => { ready = null; throw e; });
  return ready;
}

const b64 = (u8) => btoa(String.fromCharCode(...u8)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
export const randomToken = (n = 32) => b64(crypto.getRandomValues(new Uint8Array(n)));
export async function hashPassword(pw, salt) {
  salt = salt || b64(crypto.getRandomValues(new Uint8Array(16)));
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(pw), "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits({ name: "PBKDF2", hash: "SHA-256", salt: new TextEncoder().encode(salt), iterations: 100000 }, key, 256);
  return { hash: b64(new Uint8Array(bits)), salt };
}
export function safeEq(a, b) { a = String(a || ""); b = String(b || ""); if (a.length !== b.length) return false; let d = 0; for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i); return d === 0; }
export const pwProblem = (pw) => (String(pw || "").length < 10 ? "Use at least 10 characters." : /^(.)\1+$/.test(pw) ? "Choose a less simple password." : "");

const cookieOf = (request) => { const m = (request.headers.get("Cookie") || "").match(new RegExp(`(?:^|;\\s*)${COOKIE}=([^;]+)`)); return m ? m[1] : ""; };
export const setCookie = (token, maxAge = HOURS * 3600) => `${COOKIE}=${token}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${maxAge}`;

/** The logged-in user for this request, or null. */
export async function currentUser(request, env) {
  const db = env.LEADS_DB, t = cookieOf(request); if (!db || !t) return null;
  await initAuth(db);
  const s = await db.prepare("SELECT u.*, s.expires FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.hash=?1").bind(await sha(t)).first();
  if (!s || s.expires < Date.now() || s.status !== "active") return null;
  return s;
}
export async function startSession(db, user, request) {
  const t = randomToken(); const now = Date.now();
  await db.batch([db.prepare("INSERT INTO sessions (hash, user_id, created, expires, ip, ua) VALUES (?1,?2,?3,?4,?5,?6)").bind(await sha(t), user.id, now, now + HOURS * 3600000,
      request.headers.get("CF-Connecting-IP") || "", (request.headers.get("User-Agent") || "").slice(0, 200)),
    db.prepare("UPDATE users SET last_login=?2 WHERE id=?1").bind(user.id, now),
    db.prepare("DELETE FROM sessions WHERE expires<?1").bind(now)]);
  return t;
}
export async function endSession(request, env) { const t = cookieOf(request); if (t && env.LEADS_DB) await env.LEADS_DB.prepare("DELETE FROM sessions WHERE hash=?1").bind(await sha(t)).run(); }

/** Admin check used by every /api/admin endpoint: a logged-in admin, or the X-Admin-Key header (kept for automated checks). */
export async function isAdmin(request, env) {
  const k = request.headers.get("X-Admin-Key") || "", want = env.ADMIN_PASS || env.SBB_TEST_TOKEN;
  if (k && want && safeEq(k, want)) return true;
  const u = await currentUser(request, env); return !!(u && u.role === "admin");
}

export async function audit(db, request, user, action, detail = "") {
  try { await db.prepare("INSERT INTO audit (ts, user_id, email, action, detail, ip) VALUES (?1,?2,?3,?4,?5,?6)").bind(Date.now(), user ? user.id : "", user ? user.email : "", action, String(detail).slice(0, 300), request.headers.get("CF-Connecting-IP") || "").run(); } catch {}
}

/** Email via Resend (RESEND_API_KEY + AUTH_FROM, e.g. "HomeProRadar <no-reply@homeproradar.com>"). Returns true when sent. */
export async function sendMail(env, to, subject, text) {
  if (!env.RESEND_API_KEY || !env.AUTH_FROM) return false;
  try {
    const r = await fetch("https://api.resend.com/emails", { method: "POST", headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, "Content-Type": "application/json" },
      body: JSON.stringify({ from: env.AUTH_FROM, to: [to], subject, text }) });
    return r.ok;
  } catch { return false; }
}
export const mailReady = (env) => !!(env.RESEND_API_KEY && env.AUTH_FROM);
export const appUrl = (env, request) => env.APP_URL || new URL(request.url).origin;

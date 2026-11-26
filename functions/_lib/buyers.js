/**
 * Lead buyers + auction. Every buyer has the same shape:
 *   id, name, verticals, configured(env), live(env), eligible(lead) -> "" or reason,
 *   ping(env, lead) -> { ok, price, token, status, error, req, raw },  post(env, lead, ping) -> { ok, price, status, error, req, raw }
 * sell() pings every eligible buyer at once, posts to the best price, and falls back to the next best if a post is rejected.
 * All keys come from Cloudflare secrets. Each buyer has its own test/live switch:
 *   LoanBright  SBB_USER, SBB_PASS, SBB_SRC, SBB_PUB_ID, SBB_LIVE=1
 *   Connatria   CONNATRIA_KEY, CONNATRIA_OFFER_ID, CONNATRIA_SOURCE_ID, CONNATRIA_LIVE=1
 *   Alpine      ALPINE_KEY, ALPINE_CAMPAIGN, ALPINE_LIVE=1, ALPINE_ROOFING=1 (also send roofing)
 *   Any buyer   <ID>_MIN_PRICE (e.g. LOANBRIGHT_MIN_PRICE=20). Pause / Test / Live is set on the dashboard (settings table), env flags are the fallback.
 */
import { roofFields, parseXml, BEST_TIME } from "./sbb.js";

const T = 12000;
async function jfetch(url, opt) {
  const r = await fetch(url, { ...opt, signal: AbortSignal.timeout(T) });
  const raw = await r.text(); let j = null; try { j = JSON.parse(raw); } catch {}
  return { http: r.status, raw: raw.slice(0, 2000), j };
}
const isRepair = (p) => /repair|leak|storm|hail/i.test(String(p || ""));
const isNewRoof = (p) => /new roof/i.test(String(p || ""));

// ------------------------------------------------------------------ LoanBright (SBBnet) — roofing
const LB_URL = { test: "https://uat.sbbnetinc.com/rest/api/roofing/submit-inquiry", live: "https://live.sbbnetinc.com/rest/api/roofing/submit-inquiry" };
const loanbright = {
  id: "loanbright", name: "LoanBright", verticals: ["roofing"],
  configured: (e) => !!(e.SBB_USER && e.SBB_PASS), live: (e) => e.SBB_LIVE === "1",
  eligible: (l) => (!l.city || !l.state ? "no city/state" : ""),   // street address is checked at post (form + publisher API require it for roofing)
  base(e, l) {
    return { API_Action: "pingPostLead", TYPE: "16", Return_Best_Price: 1, SRC: this.live(e) ? (e.SBB_SRC || "Test") : "Test", Pub_ID: (e.SBB_PUB_ID || "TLH-RR") + (l.pub_id ? "-" + l.pub_id.replace(/^pub_/, "") : ""),   // one Pub_ID per traffic source so LoanBright can price each
      Sub_ID: String(l.sub_id || l.utm_campaign || "").slice(0, 100),
      IP_Address: l.ip_address || "", Property_City: l.city, Property_State: l.state, Property_Zip: l.zip, Property_Owner: "Yes", Best_Time_To_Call: BEST_TIME(l.best_time_to_call),
      Landing_Page: String(l.landing_page || "").slice(0, 100), ...roofFields(l.material, l.project) };
  },
  async send(e, body) {
    const r = await fetch(this.live(e) ? LB_URL.live : LB_URL.test, { method: "POST", signal: AbortSignal.timeout(T),
      headers: { Authorization: "Basic " + btoa(`${e.SBB_USER}:${e.SBB_PASS}`), "Content-Type": "application/json", Accept: "application/xml, */*" }, body: JSON.stringify({ Request: body }) });
    const raw = await r.text(); return { ...parseXml(raw), raw: raw.trim().slice(0, 2000), req: body };
  },
  async ping(e, l) {
    const x = await this.send(e, { ...this.base(e, l), Mode: "ping", Lead_Cost: "0", NoSale: "Yes", Universal_Lead_ID: l.universal_leadid || "", Active_Prospect_URL: l.xxTrustedFormCertUrl || "" });
    return { ok: x.ok && !!x.id, price: x.price, token: x.id, status: x.status, error: x.error, req: x.req, raw: x.raw };
  },
  async post(e, l, p) {
    const x = await this.send(e, { ...this.base(e, l), Mode: "post", Lead_ID: p.token, Lead_Cost: "1", NoSale: "No",
      First_Name: l.first_name, Last_Name: l.last_name, Email: l.email, Primary_Phone: l.phone, Property_Address: l.address || "",
      Universal_Lead_ID: l.universal_leadid || "", Active_Prospect_URL: l.xxTrustedFormCertUrl || "",
      Tcpa_Language: String(l.consent_text || "").replace(/\s+/g, " ").slice(0, 255), vendor_lead_id: l.lead_id || "",
      Comments: [l.project, l.timeframe && "Timing: " + l.timeframe].filter(Boolean).join(" · ").slice(0, 255) });
    return { ok: /^accepted$/i.test(x.status), price: x.price || p.price, status: x.status, error: x.error, req: x.req, raw: x.raw };
  },
};

// ------------------------------------------------------------------ Connatria (Standard Information) — roofing, new/replace only
const CN = { test: ["https://exchange.standardinformation.io/ping_test", "https://exchange.standardinformation.io/post_test"],
             live: ["https://exchange.standardinformation.io/ping", "https://exchange.standardinformation.io/post"] };
const connatria = {
  id: "connatria", name: "Connatria", verticals: ["roofing"],
  configured: (e) => !!e.CONNATRIA_KEY, live: (e) => e.CONNATRIA_LIVE === "1",
  eligible: (l) => (isRepair(l.project) ? "buys new/replacement roofs only" : ""),
  body(e, l, full) {
    const contact = { city: l.city || "", state: l.state || "", zip_code: l.zip, ip_address: l.ip_address || "" };
    if (full) Object.assign(contact, { first_name: l.first_name, last_name: l.last_name, email: l.email, phone: l.phone, address: l.address || "" });
    return { data: { subid_1: l.source_site || "", subid_2: l.source || "", subid_3: l.lead_id || "", own_property: "yes", roof_project_type: isNewRoof(l.project) ? "new" : "replace" },
      meta: { offer_id: e.CONNATRIA_OFFER_ID || "", source_id: e.CONNATRIA_SOURCE_ID || "", user_agent: l.user_agent || "", lead_id_code: l.universal_leadid || "",
        landing_page_url: l.landing_page || "", tcpa_consent_text: String(l.consent_text || "").replace(/\s+/g, " "), originally_created: l.submitted_at || new Date().toISOString(),
        trusted_form_cert_url: l.xxTrustedFormCertUrl || "" },
      contact };
  },
  async call(e, i, body) {
    const u = (this.live(e) ? CN.live : CN.test)[i];
    const x = await jfetch(u, { method: "POST", headers: { Authorization: `Bearer ${e.CONNATRIA_KEY}`, "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(body) });
    const j = x.j || {}; const err = j.errors ? (typeof j.errors === "string" ? j.errors : JSON.stringify(j.errors)) : (x.http >= 400 ? `HTTP ${x.http}` : "");
    return { j, raw: x.raw, req: body, ok: String(j.status).toLowerCase() === "success", price: parseFloat(j.price) || 0, status: j.status || `HTTP ${x.http}`, error: err };
  },
  async ping(e, l) { const x = await this.call(e, 0, this.body(e, l, false)); return { ok: x.ok, price: x.price, token: x.j.auth_code || "", status: x.status, error: x.error, req: x.req, raw: x.raw }; },
  async post(e, l, p) { const b = { ...this.body(e, l, true), auth_code: p.token }; const x = await this.call(e, 1, b); return { ok: x.ok, price: x.price || p.price, status: x.status, error: x.error, req: x.req, raw: x.raw }; },
};

// ------------------------------------------------------------------ Alpine Digital Group (adgtrax) — windows (+ roofing when ALPINE_ROOFING=1)
const AL_URL = "https://adgtrax.com/submit/home-improvement";
const TIMEFRAME = { emergency: 1, immediately: 1, flexible: 2, "within 1 week": 3, "1-2 weeks": 4, "more than 2 weeks": 5, "within 1-3 months": 5, "just planning": 5 };
const alpine = {
  id: "alpine", name: "Alpine Digital", verticals: ["windows", "roofing"],
  configured: (e) => !!(e.ALPINE_KEY && e.ALPINE_CAMPAIGN), live: (e) => e.ALPINE_LIVE === "1",
  eligible(l, e) {
    if (l.vertical === "roofing" && (!e || e.ALPINE_ROOFING !== "1")) return "roofing not switched on for Alpine";
    return "";
  },
  projectType(l) {
    if (l.vertical === "windows") return isRepair(l.project) ? 12 : 4;
    return isRepair(l.project) ? 6 : 14;
  },
  body(e, l, method, extra) {
    const b = { product: "Home Improvement", method, campaignId: e.ALPINE_CAMPAIGN, key: e.ALPINE_KEY, projectType: this.projectType(l),
      timeframe: TIMEFRAME[String(l.timeframe || "").toLowerCase()] || (isRepair(l.project) ? 3 : 2),
      residential: true, homeowner: true, firstName: l.first_name, lastName: l.last_name, city: l.city || "", state: l.state || "", zipCode: l.zip,
      leadId: l.universal_leadid || "", xxTrustedFormCertUrl: l.xxTrustedFormCertUrl || "", consentLang: String(l.consent_text || "").replace(/\s+/g, " "),
      sourceIP: l.ip_address || "", userAgent: l.user_agent || "", leadBornOnDateTime: l.submitted_at || new Date().toISOString(),
      submissionURL: l.landing_page || "", s1: "TLH", s2: `${l.source_site || ""}|${l.source || ""}`.slice(0, 80), mobile: /Mobi|Android|iPhone/i.test(l.user_agent || ""), test: !this.live(e) };
    if (l.vertical === "windows" && +l.windows_count >= 1) b.windows = Math.min(15, +l.windows_count);
    return { ...b, ...extra };
  },
  async call(e, body) {
    const x = await jfetch(AL_URL, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(body) });
    const j = x.j || {}; const safe = { ...body, key: "(hidden)" };
    return { j, raw: x.raw, req: safe, ok: j.success === true, price: parseFloat(j.payout) || 0, status: j.success === true ? "success" : j.success === false ? "rejected" : `HTTP ${x.http}`,
      error: j.error ? String(j.error) : "" };
  },
  async ping(e, l) { const x = await this.call(e, this.body(e, l, "ping", { last4: String(l.phone || "").slice(-4) })); return { ok: x.ok && !!x.j.pingId, price: x.price, token: x.j.pingId || "", status: x.status, error: x.error, req: x.req, raw: x.raw }; },
  async post(e, l, p) {
    const x = await this.call(e, this.body(e, l, "post", { pingId: p.token, address: l.address || "", phone: l.phone, email: l.email }));
    return { ok: x.ok, price: x.price || p.price, status: x.status, error: x.error, req: x.req, raw: x.raw };
  },
};

// ------------------------------------------------------------------ Demo Buyer — answers TEST publisher traffic only, never a real company
const demo = {
  id: "demo", name: "Demo Buyer", verticals: ["roofing", "windows", "bath", "siding"], internal: true,
  configured: () => true, live: () => false, eligible: (l) => (/^000/.test(l.zip || "") ? "No coverage in this ZIP (demo)" : ""),
  async ping(e, l) {
    const base = { roofing: 38, windows: 30, bath: 28, siding: 55 }[l.vertical] || 25;
    if (/^000/.test(l.zip || "")) return { ok: false, price: 0, status: "rejected", error: "No coverage in this ZIP (demo)", req: { zip: l.zip }, raw: '{"status":"rejected"}' };
    const price = Math.round((base + (parseInt(String(l.zip).slice(-2), 10) % 7)) * 100) / 100;
    return { ok: true, price, token: "DEMO-" + crypto.randomUUID().slice(0, 8), status: "success", error: "", req: { vertical: l.vertical, zip: l.zip }, raw: JSON.stringify({ status: "success", price }) };
  },
  async post(e, l, p) {
    if (/reject/i.test(l.email || "")) return { ok: false, price: 0, status: "rejected", error: "Rejected on purpose (email contains 'reject')", req: { token: p.token }, raw: '{"status":"rejected"}' };
    return { ok: true, price: p.price, status: "success", error: "", req: { token: p.token }, raw: JSON.stringify({ status: "success", price: p.price }) };
  },
};

export const BUYERS = [loanbright, connatria, alpine];
export const ALL_BUYERS = [loanbright, connatria, alpine, demo];
export const byId = (id) => ALL_BUYERS.find((b) => b.id === id);
const FLAG = { loanbright: "SBB_LIVE", connatria: "CONNATRIA_LIVE", alpine: "ALPINE_LIVE" };

/** Can this buyer be switched to live? ("" = yes, otherwise the reason) */
export function liveBlock(b, env) {
  if (!b.configured(env)) return "keys missing in Cloudflare";
  if (b.id === "loanbright" && (!env.SBB_SRC || env.SBB_SRC === "Test")) return "set SBB_SRC to LoanBright's live SRC in Cloudflare first";
  return "";
}
/** Buyer modes from the dashboard (settings table): paused | test | live. Falls back to env flags. */
export async function loadModes(env) {
  const m = {};
  for (const b of BUYERS) m[b.id] = env[`${b.id.toUpperCase()}_OFF`] === "1" ? "paused" : env[FLAG[b.id]] === "1" ? "live" : "test";
  if (env.LEADS_DB) {
    try { const rows = (await env.LEADS_DB.prepare("SELECT k, v FROM settings WHERE k LIKE 'mode:%' OR k LIKE 'min:%'").all()).results;
      for (const r of rows) { const [t, id] = r.k.split(":"); if (t === "mode") m[id] = r.v; else m["min:" + id] = r.v; } } catch {}
  }
  for (const b of BUYERS) if (m[b.id] === "live" && liveBlock(b, env)) m[b.id] = "test";   // never live without what live needs
  return m;
}
/** env copy where each buyer's live flag matches its mode */
export function envWith(env, modes) {
  const E = { ...env };
  for (const b of BUYERS) { E[FLAG[b.id]] = modes[b.id] === "live" ? "1" : "0"; if (modes["min:" + b.id]) E[`${b.id.toUpperCase()}_MIN_PRICE`] = modes["min:" + b.id]; }
  return E;
}

/** Which buyers get this lead. opts: { only, modes, testOnly (test publisher), demo (include Demo Buyer) } */
export function pick(env, lead, opts, attempts) {
  const modes = opts.modes || {};
  let list = opts.only === "demo" ? [] : BUYERS.filter((b) => (!opts.only || b.id === opts.only) && b.configured(env) && b.verticals.includes(lead.vertical));
  list = list.filter((b) => {
    const m = modes[b.id] || "test";
    if (m === "paused") { attempts.push({ buyer: b.id, name: b.name, live: 0, stage: "skip", status: "skipped", price: 0, error: "paused on dashboard" }); return false; }
    if (opts.testOnly && m === "live") return false;             // test traffic never reaches a live buyer
    if (opts.liveOnly && m !== "live") return false;             // live publisher traffic only goes to live buyers
    return true;
  });
  if (opts.only === "demo" || (opts.demo && !opts.only)) list.push(demo);
  const active = [];
  for (const b of list) { const why = b.eligible(lead, env); if (why) attempts.push({ buyer: b.id, name: b.name, live: b.live(env) ? 1 : 0, stage: "skip", status: "skipped", price: 0, error: why }); else active.push(b); }
  return active;
}

/** Step 1 for everyone: ping all chosen buyers at once. Returns offers sorted best first. */
export async function pingAll(env0, lead, opts = {}) {
  const modes = opts.modes || await loadModes(env0), env = envWith(env0, modes), attempts = [];
  const active = pick(env, lead, { ...opts, modes }, attempts);
  const pings = await Promise.all(active.map(async (b) => {
    const t0 = Date.now(); let r;
    try { r = await b.ping(env, lead); } catch (e) { r = { ok: false, price: 0, status: "error", error: String(e).slice(0, 200) }; }
    const a = { buyer: b.id, name: b.name, live: b.live(env) ? 1 : 0, stage: "ping", ms: Date.now() - t0, ts: t0, ...r }; attempts.push(a); return a;
  }));
  const offers = pings.filter((a) => a.ok && a.price >= (parseFloat(env[`${a.buyer.toUpperCase()}_MIN_PRICE`] || "0") || 0)).sort((x, y) => y.price - x.price);
  for (const a of pings) if (a.ok && !offers.includes(a)) a.error = `bid ${a.price} below minimum`;
  return { env, modes, attempts, offers, active: active.length };
}

/** Step 2: post to the best offer; fall back to the next best on rejection. */
export async function postBest(env, lead, offers, attempts) {
  for (const a of offers) {
    const b = byId(a.buyer), t0 = Date.now(); let r;
    try { r = await b.post(env, lead, a); } catch (e) { r = { ok: false, price: 0, status: "error", error: String(e).slice(0, 200) }; }
    const p = { buyer: b.id, name: b.name, live: b.live(env) ? 1 : 0, stage: "post", ms: Date.now() - t0, ts: t0, ...r }; attempts.push(p);
    if (r.ok) return { sold: true, buyer: b.id, name: b.name, price: r.price || a.price, live: p.live, attempts };
  }
  return { sold: false, buyer: "", name: "", price: 0, live: 0, attempts, reason: offers.length ? "all posts rejected" : "" };
}

/** Our own forms: ping everyone, post to the best. (only = test runner for one buyer) */
export async function sell(env0, lead, only, opts = {}) {
  const P = await pingAll(env0, lead, { only, ...opts });
  if (!P.offers.length) {
    const reason = P.attempts.length ? P.attempts.map((a) => `${a.name}: ${a.error || a.status}`).join("; ") : "no buyer for this vertical";
    return { sold: false, buyer: "", name: "", price: 0, live: 0, attempts: P.attempts, reason };
  }
  return postBest(P.env, lead, P.offers, P.attempts);
}

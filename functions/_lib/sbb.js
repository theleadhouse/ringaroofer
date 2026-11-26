/**
 * LoanBright / SBBnet roofing ping-post (Roofing Supplier Delivery Guide, rev. 02/27/2026).
 *   1. PING  — no name/phone/email: ZIP, city, state, roof material, roof task, homeowner.  Reply: Match + id + price, or Unmatched.
 *   2. POST  — full lead + Lead_ID from the ping, within 3 minutes.                          Reply: Accepted + price, or Duplicate/Invalid/Error.
 * Credentials and IDs come from Cloudflare secrets/variables (never from code):
 *   SBB_USER, SBB_PASS   Basic auth from the buyer             (secret)
 *   SBB_SRC              SRC assigned by SBBnet ("Test" while testing)
 *   SBB_PUB_ID           our source identifier                  (default TLH-RR)
 *   SBB_LIVE             "1" = production URL; anything else = UAT test URL
 *   SBB_MIN_PRICE        optional: don't post if the ping price is below this (dollars)
 */
const URLS = { test: "https://uat.sbbnetinc.com/rest/api/roofing/submit-inquiry", live: "https://live.sbbnetinc.com/rest/api/roofing/submit-inquiry" };

// Our form answers -> SBBnet allowed values (exact strings from the spec).
const MATERIAL = { "asphalt shingle": "Asphalt Shingles", "asphalt shingles": "Asphalt Shingles", "metal": "Metal", "tile": "Clay Tile", "clay tile": "Clay Tile",
  "cement tile": "Cement Tile", "slate": "Slate", "wood shake": "Wood Shake", "flat": "Other or Unknown", "not sure": "Other or Unknown" };
const FAMILY = { "Asphalt Shingles": "Asphalt Shingle Roofing", "Metal": "Metal Roofing", "Clay Tile": "Traditional Tile Roofing", "Cement Tile": "Traditional Tile Roofing",
  "Slate": "Natural Slate Roofing", "Wood Shake": "Wood Shake or Composite Roofing" };
export function roofFields(material, project) {
  const m = String(material || "").trim().toLowerCase();
  const mat = MATERIAL[m] || "Other or Unknown";
  const repair = /repair|leak|storm|hail/i.test(String(project || ""));
  let task;
  if (m === "flat") task = repair ? "Flat, Foam or Single Ply Roofing - Repair" : "Flat, Foam, or Single Ply Roofing - Install or Replace";   // spec spells these two differently
  else task = `${FAMILY[mat] || "Asphalt Shingle Roofing"} - ${repair ? "Repair" : "Install or Replace"}`;
  return { Roof_Material: mat, Roof_Task: task };
}

// SBBnet answers in XML: <response><status>..</status><id>..</id><price>..</price><error><type>..</type><description>..</description></error></response>
export function parseXml(t) {
  const g = (tag) => { const m = String(t || "").match(new RegExp(`<${tag}>([\\s\\S]*?)</${tag}>`, "i")); return m ? m[1].trim() : ""; };
  const status = g("status");
  return { status, ok: /^match(ed)?$|^accepted$/i.test(status), id: g("id"), price: parseFloat(g("price")) || 0, error: g("description") || g("type") || "" };
}

async function send(env, body) {
  const url = env.SBB_LIVE === "1" ? URLS.live : URLS.test;
  const auth = "Basic " + btoa(`${env.SBB_USER}:${env.SBB_PASS}`);
  const r = await fetch(url, { method: "POST", headers: { Authorization: auth, "Content-Type": "application/json", Accept: "application/xml, text/xml, */*" },
    body: JSON.stringify({ Request: body }), signal: AbortSignal.timeout(15000) });
  const text = await r.text();
  return { http: r.status, ...parseXml(text), raw: text.slice(0, 1500), req: body };   // req = what we sent (no password: that's only in the header)
}

/** lead: our normalized lead (see /api/quote). Returns { sold, stage, price, ping, post, reason } — never throws. */
export async function pingPost(env, lead) {
  const out = { sold: false, stage: "skip", price: 0, ping: null, post: null, reason: "" };
  if (!env.SBB_USER || !env.SBB_PASS) { out.reason = "not configured"; return out; }
  if (!/^yes$/i.test(lead.homeowner || "")) { out.reason = "not a homeowner"; return out; }
  if (!lead.city || !lead.state) { out.reason = "no city/state"; return out; }
  const base = {
    API_Action: "pingPostLead", TYPE: "16", Return_Best_Price: 1, SRC: env.SBB_SRC || "Test", Pub_ID: env.SBB_PUB_ID || "TLH-RR",
    IP_Address: lead.ip_address || "", Property_City: lead.city, Property_State: lead.state, Property_Zip: lead.zip, Property_Owner: "Yes",
    Best_Time_To_Call: "Anytime", Landing_Page: String(lead.landing_page || "").slice(0, 100), ...roofFields(lead.material, lead.project),
  };
  try {
    out.stage = "ping";
    out.ping = await send(env, { ...base, Mode: "ping", Lead_Cost: "0", NoSale: "Yes", Universal_Lead_ID: lead.universal_leadid || "", Active_Prospect_URL: lead.xxTrustedFormCertUrl || "" });
    if (!out.ping.ok || !out.ping.id) { out.reason = out.ping.error || out.ping.status || "unmatched"; return out; }
    const min = parseFloat(env.SBB_MIN_PRICE || "0");
    if (min && out.ping.price < min) { out.reason = `price ${out.ping.price} below minimum ${min}`; return out; }
    out.stage = "post";
    out.post = await send(env, { ...base, Mode: "post", Lead_ID: out.ping.id, Lead_Cost: "1", NoSale: "No",
      First_Name: lead.first_name, Last_Name: lead.last_name, Email: lead.email, Primary_Phone: lead.phone, Property_Address: lead.address || "",
      Universal_Lead_ID: lead.universal_leadid || "", Active_Prospect_URL: lead.xxTrustedFormCertUrl || "",
      Tcpa_Language: String(lead.consent_text || "").replace(/\s+/g, " ").slice(0, 255), vendor_lead_id: lead.lead_id || "" });
    out.sold = /^accepted$/i.test(out.post.status);
    out.price = out.sold ? (out.post.price || out.ping.price) : 0;
    if (!out.sold) out.reason = out.post.error || out.post.status || "rejected";
  } catch (e) { out.reason = "error: " + String(e).slice(0, 200); }
  return out;
}

/** City + state from a ZIP (free public lookup), used when the form didn't send a city. */
export async function zipPlace(zip) {
  try {
    const r = await fetch(`https://api.zippopotam.us/us/${zip}`, { cf: { cacheTtl: 2592000, cacheEverything: true }, signal: AbortSignal.timeout(4000) });
    if (!r.ok) return null; const j = await r.json(); const p = (j.places || [])[0];
    return p ? { city: p["place name"], state: p["state abbreviation"] } : null;
  } catch { return null; }
}

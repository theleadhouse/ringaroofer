// Shared helpers for the reviews API (Cloudflare Pages Functions + KV binding "REVIEWS").
export const json = (data, status = 200, extra = {}) =>
  new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...extra } });
export const PESTS = ["Roof repair", "Roof leak", "Emergency repair or tarp", "Storm or wind", "Hail", "Roof replacement or new roof", "Roof inspection", "Flat roof", "Other roofing"];
export const STATES = ["AL","AK","AZ","AR","CA","CO","CT","DE","DC","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"];
export const clean = (s, max) => String(s || "").replace(/[<>]/g, "").replace(/\s+/g, " ").trim().slice(0, max);
// Public view: never expose the phone digits, IP or email.
export const pub = (r) => ({ id: r.id, name: r.name, city: r.city, state: r.state, pest: r.pest, rating: r.rating, title: r.title, text: r.text,
  month: r.callDate ? r.callDate.slice(0, 7) : "", verified: !!r.verified, reply: r.reply || "", created: r.created });
export async function listPrefix(kv, prefix) {
  const out = []; let cursor;
  do {
    const page = await kv.list({ prefix, cursor });
    for (const k of page.keys) { const v = await kv.get(k.name, "json"); if (v) out.push(v); }
    cursor = page.list_complete ? null : page.cursor;
  } while (cursor);
  return out.sort((a, b) => (b.created || "").localeCompare(a.created || ""));
}

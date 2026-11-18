// GET /api/where — the visitor's approximate location from Cloudflare (no third-party service, nothing stored).
export async function onRequestGet({ request }) {
  const cf = request.cf || {};
  const body = { country: cf.country || "", region: cf.region || "", regionCode: cf.regionCode || "", city: cf.city || "" };
  return new Response(JSON.stringify(body), { headers: { "Content-Type": "application/json", "Cache-Control": "private, no-store" } });
}

/** "/" — on api.* hosts answer with a small JSON index; everywhere else serve the normal home page. */
export async function onRequest(ctx) {
  const h = new URL(ctx.request.url).hostname;
  if (h.startsWith("app.")) return Response.redirect(new URL("/app/", ctx.request.url).toString(), 302);   // app.homeproradar.com -> sign-in
  if (!h.startsWith("api.")) return ctx.next();
  return new Response(JSON.stringify({ service: "Radar Exchange API", version: "v1", status: "ok",
    endpoints: { access: "POST /v1/access (public)", preping: "POST /v1/preping", ping: "POST /v1/ping", post: "POST /v1/post", coverage: "GET /v1/coverage", me: "GET /v1/me", optout: "POST /v1/optout" },
    auth: "Authorization: Bearer <your key>" }, null, 2), { headers: { "Content-Type": "application/json", "Cache-Control": "no-store", "X-Robots-Tag": "noindex" } });
}

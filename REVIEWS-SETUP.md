# RingaRoofer reviews: one-time setup (Cloudflare Pages project "ringaroofer")

1. Cloudflare → Storage & Databases → KV → Create namespace `rr-reviews`.
2. Pages project "ringaroofer" → Settings → Bindings → Add → KV namespace → Variable name `REVIEWS` → `rr-reviews` → Save.
3. Settings → Variables and Secrets → add `ADMIN_TOKEN` (long random password, type Secret). Optional: `TURNSTILE_SECRET`, `RESEND_API_KEY` + `REVIEW_NOTIFY_TO`.
4. Deployments → Retry latest deployment.
5. Moderate at https://ringaroofer.com/review-admin/ — match call date + last 4 digits in TrackDrive, tick "Verified caller", Publish.

Rules (FTC Consumer Reviews rule): publish every genuine review whatever the rating; reject only spam, abuse, personal details or non-callers.
Never write, buy or reward reviews. No review-star markup (Google doesn't show stars for a business's reviews of itself).

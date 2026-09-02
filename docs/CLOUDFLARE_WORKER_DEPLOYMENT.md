# Cloudflare Worker Deployment

This project is configured as a real Cloudflare Worker with Workers Static Assets, not a Pages-only deployment.

## 1. Create the Worker

Create a Worker named `lucky-river-ad40` in Cloudflare Workers & Pages.

## 2. Create / select KV

Create a Workers KV namespace and copy its namespace ID.

Replace this line in `wrangler.toml`:

    id = "REPLACE_WITH_YOUR_KV_ID"

with the real namespace ID.

KV namespace IDs are not secrets. Do not put passwords, API keys, or private keys in this file.

## 3. Authenticate Wrangler

From the project root:

    npx wrangler login

## 4. Test locally

    npx wrangler dev

## 5. Deploy

    npx wrangler deploy

The deployment contains both:

- Worker runtime: `src/index.ts`
- Public static assets: `website/`

The separate `admin-app/` directory is deliberately not included in the public asset directory.

## Important security note

Do not use `CF-Connecting-IP` or a `100.64.0.0/10` check as proof that a request came from Tailscale. Behind Cloudflare, the client IP is not a sufficient identity assertion for an admin security boundary.

For the admin application, use Cloudflare Access or another identity-aware access layer, with Tailscale as an additional private-network control if desired.

## KV binding

The Worker receives the KV namespace as `env.AUTH_KV`. The current public Worker does not store credentials in KV. Add authentication/session logic only in the Worker backend after defining the required security model.

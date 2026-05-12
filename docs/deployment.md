# Deployment Plan

Target: live demo URL for grading around 2026-05-16. Time budget: ~1 day (per `CLAUDE.md`).

## Recommended stack

| Layer    | Pick                           | Why |
|----------|--------------------------------|-----|
| Frontend | **Vercel**                     | Vite static deploy is one click; free tier sufficient |
| Backend  | **Render** (Web Service, free) | Native Python/Flask, env vars in UI, free TLS, no Docker needed |
| DB       | **MongoDB Atlas** (M0 free)    | Already what `CLAUDE.md` assumes; GridFS works unchanged |

Free tiers cover a grading demo. Render free dynos sleep after ~15 min idle (~30s cold start) — hit `/api/health` to wake it before presenting.

## Gotchas in current code

These will break a split-origin deploy until fixed.

### 1. Frontend uses relative `/api/...` paths

`frontend/src/api/client.ts` (and call sites in `api/auth.ts`, `api/items.ts`, `api/locations.ts`) assumes the Vite dev proxy. In production with a separate backend origin, requests must hit an absolute URL.

**Fix:** add a `VITE_API_BASE_URL` env var and prefix it in `api/client.ts`. Also covers `imageUrl()` in the same file and the hard-coded `window.location.href = "/api/auth/google"` in `auth/AuthContext.tsx:42`.

### 2. Session cookie is `SameSite=Lax`

`backend/app/config.py:19` sets `SESSION_COOKIE_SAMESITE = "Lax"`. With Vercel frontend → Render backend (different registrable domains), browsers will not send the cookie on cross-site XHR with credentials. `/api/auth/me` will look unauthenticated after the OAuth callback.

**Fix:** in `ProdConfig`, override to `SESSION_COOKIE_SAMESITE = "None"`. `SESSION_COOKIE_SECURE = True` is already set there, which `None` requires.

### Sidestep option: same-origin deploy

Host frontend + backend on a single Render service (Flask serves the built `dist/`). Removes both gotchas — no CORS, `SameSite=Lax` keeps working. Trade-off: no Vercel CDN, slightly slower static serving. Fine for a demo. **Decision pending.**

## Sequenced checklist

### Pre-work (teammate-owned, blocking)

- [ ] Add prod redirect URI to the Google Cloud OAuth client: `https://<backend>.onrender.com/api/auth/callback`
- [ ] Confirm OAuth consent screen is published (not "Testing"), or add grader emails as test users

### Backend → Render

- [ ] Add `gunicorn` to `backend/requirements.txt`
- [ ] Start command: `gunicorn "app:create_app()"`
- [ ] Env vars on Render:
  - `APP_ENV=prod`
  - `SESSION_SECRET=<long random>`
  - `MONGODB_URI=<Atlas connection string>`
  - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
  - `GOOGLE_REDIRECT_URI=https://<backend>.onrender.com/api/auth/callback`
  - `FRONTEND_ORIGIN=https://<frontend>.vercel.app`
- [ ] Flip `SESSION_COOKIE_SAMESITE` in `ProdConfig` (see gotcha #2)

### Frontend → Vercel

- [ ] Add `VITE_API_BASE_URL` and use it in `api/client.ts` (see gotcha #1)
- [ ] Build command: `npm run build`; output dir: `dist/`
- [ ] Env vars on Vercel:
  - `VITE_USE_MOCK=false`
  - `VITE_API_BASE_URL=https://<backend>.onrender.com`

### MongoDB Atlas

- [ ] Create M0 cluster
- [ ] Network access: allow `0.0.0.0/0` (Render free tier IPs are not static)
- [ ] DB user with read/write on the cufinder DB
- [ ] Seed `location_admin` / `web_admin` documents the same way as local

### Smoke test on live URL

- [ ] Google login round-trip lands authenticated
- [ ] Post a found item with an image; image renders via `/api/images/:id`
- [ ] Browse / search / filter returns results
- [ ] Admin can mark items claimed / disposed

## Open decisions

1. **Same-origin vs split-origin?** Same-origin avoids both gotchas; split-origin is the recommended stack above.
2. **Who registers the prod redirect URI in Google Cloud?** Needs to happen before the backend deploy is testable.
3. **Custom domain or `*.onrender.com` / `*.vercel.app`?** Free subdomains are fine for a demo.

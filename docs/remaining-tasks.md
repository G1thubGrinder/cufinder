# CUFinder — Remaining Tasks

Audit on **2026-05-15** (Day 5, demo dry-run day per `docs/backend-tasks.md`; demo 2026-05-16).

Method: walked every Day-1 → Day-4 deliverable in `docs/backend-tasks.md` and every endpoint in `docs/api.md` against the source under `backend/` and `frontend/src/`.

---

## TL;DR

The backend code surface is **functionally complete**: every endpoint in `docs/api.md` is implemented, the guards are wired up, the seed is idempotent, and `tests/` covers what the plan asked for. **Nothing in the Day-1 → Day-4 *coding* checklist is missing.**

What is missing is everything **after** the code: end-to-end integration testing against a real backend, deployment, demo-day artifacts, and a handful of small loose ends (one stale frontend function, prod cookie attrs, missing `gunicorn`).

---

## Implementation status by deliverable

Legend: ✅ done · ⚠️ done but with a follow-up · ❌ not done

### P — Foundation, Locations, Integration

| Deliverable | Status | Notes |
|---|---|---|
| Day 1 — `requirements.txt`, `.env.example`, `app/__init__.py`, `config.py`, `db.py`, `errors.py`, `GET /api/health` | ✅ | All present. Error handler maps `AppError`/`ValidationError`/`HTTPException` to the JSON shape in `docs/api.md`. |
| Day 2 — Locations CRUD (`GET`/`POST`/`PATCH`/`DELETE /api/locations`) | ✅ | Guards already use real `require_web_admin()` (stub gate already replaced). Soft-delete on `DELETE`. 409 on duplicate name (case-insensitive). |
| Day 3 — Swap stub gate to `require_web_admin()` | ✅ | Already in `app/locations/routes.py:7`. |
| Day 3 — Integration testing (walk every flow in `docs/api.md` against the running frontend) | ❌ | No evidence this happened. `frontend/.env.example` still has `VITE_USE_MOCK=true`. |
| Day 3 — CORS sanity check against the real frontend origin | ❌ | Not verified end-to-end. Config side looks right (`FRONTEND_ORIGIN` is read from env in `config.py:10` and applied in `__init__.py:18`). |
| Day 4 — Bug triage / fix assignment | ❌ | Depends on integration testing producing a bug list. |
| Day 4 — Deploy (Render + Atlas + Vercel) | ❌ | See "Deployment loose ends" below — three gating fixes still needed. |
| Day 5 — Demo script + slides + final bug-bash | ❌ | Today's work. |

### Guy — Auth + Items

| Deliverable | Status | Notes |
|---|---|---|
| Day 1 — `auth/schemas.py` (CU regex), `items/schemas.py` (discriminated `ItemCreate` with both mutex rules) | ✅ | Regex matches `docs/api.md` exactly. Both `lost` and `found` enforce the "exactly one of id/text" rules. |
| Day 1 — Empty route stubs for auth + items | ✅ | Filled in later. |
| Day 2 — `auth/guards.py` (`require_user`, `require_web_admin`, `require_any_admin`) | ✅ | Sessions cleared on stale/invalid `user_id`. Tests cover each failure mode. |
| Day 2 — Auth routes (`GET /api/auth/google`, `GET /api/auth/callback`, `POST /api/auth/logout`, `GET /api/auth/me`) | ✅ | State CSRF guard rejects empty-on-both-sides (`routes.py:58`). Email lowercased before regex. Upsert uses `$setOnInsert` so seeded admin roles survive. All failure modes redirect to `FRONTEND_ORIGIN/login?error=<code>` per `docs/api.md`. |
| Day 2 — Register `auth_bp` in `app/__init__.py` | ✅ | Done in `__init__.py:25-33`. |
| Day 3 — `GET /api/items` (filters + pagination), `GET /api/items/:id`, `POST /api/items` | ✅ | `_build_filter` regex-escapes the `q` param. `limit` capped at 100. `status` defaults to `open`; invalid values fall back to `open`. |
| Day 4 — `PATCH /api/items/:id/status`, `DELETE /api/items/:id` with role/location authz | ✅ | `_check_admin_authz` enforces "web_admin any, location_admin only `found` at their `admin_location_id`". TODO for orphaned-image GridFS cleanup on delete is intentional per `docs/backend.md` "Out of scope". |
| Day 4 — Walk every `frontend/src/api/items.ts` call to confirm shapes | ⚠️ | Shapes match at code level (`ItemDraft = Omit<…, "id"\|"posted_by"\|"posted_at"\|"status">` matches `ItemCreate`). Not yet verified against a running backend. |
| Day 5 — Bug bash | ❌ | Pending P's triage list. |

### Kie — Images, Seed, Validation, Tests

| Deliverable | Status | Notes |
|---|---|---|
| Day 1 — `images/schemas.py` constants, empty `images/routes.py` stubs, started `seed.py` | ✅ | |
| Day 2 — `seed.py` finished and idempotent (20 locations + 3 admins via `$setOnInsert`) | ✅ | Re-runs print "already present" counts. |
| Day 2 — `POST /api/images`, `GET /api/images/:id` | ✅ | Mime + size + empty + no-extension all rejected with `400 validation_failed`. `GET` is public. |
| Day 2 — Register `images_bp` in `app/__init__.py` | ✅ | |
| Day 3 — Swap stub gate to real `require_user()` in images routes | ✅ | Already imported from `app.auth.guards`. |
| Day 3 — Validation audit (location name bounds, title/description bounds, category in constants, image reject empty/no-extension) | ✅ | All bounds present in respective `schemas.py`/`routes.py`. |
| Day 3 — `tests/test_email_regex.py`, `tests/test_items_query.py` | ✅ | Items query test imports the real `_build_filter` so regressions are caught. |
| Day 4 — `tests/test_auth_guards.py`, `tests/test_images.py`, `backend/README.md` | ✅ | Auth-guard tests cover happy + every failure mode. Image tests use the in-memory GridFS stub from `conftest.py`. README mirrors `CLAUDE.md` "Running locally". |
| Day 5 — Bug bash | ❌ | Pending P's triage list. |

---

## Concrete remaining work

Ordered roughly by demo-day priority. Owners are guesses based on the folder ownership table in `docs/backend-tasks.md` — re-assign at the stand-up.

### P0 — must do before the demo

1. **Integration test pass against real backend** *(P)*
   - Flip `VITE_USE_MOCK=false` locally (set in `frontend/.env`, do not commit a change to `.env.example`).
   - Boot `flask --app app run --debug --port 5001` and `npm run dev` in parallel.
   - Walk the demo script: Google login → post lost item with photo → post found item → browse/filter → admin marks claimed → admin marks disposed → logout.
   - File one issue per bug. Don't fix non-trivial bugs yourself — hand to Guy (auth/items) or Kie (images/validation).

2. **Demo script + slides** *(P)*
   - Mirrors the Meeting 2 agenda in `docs/sprint-plan.md` §"Meeting 2".
   - Identify which seeded admin account will be logged in at each demo step.

3. **Dry-run with the team** *(all)*
   - Time-boxed run-through. Anything that breaks goes into the bug-bash slot.

### P1 — small code loose ends (fast)

4. **Remove stale `authApi.login(email)` from `frontend/src/api/auth.ts:5-6`** *(frontend, or whoever has the cycle)*
   - That endpoint (`POST /api/auth/login`) does not exist in the new OAuth flow and nothing calls it (`AuthContext.tsx` redirects to `/api/auth/google` directly).
   - Leaving it in misleads future readers and will 404 if anyone wires it up.

5. **CORS sanity check** *(P)*
   - With both servers running, confirm a real fetch from `http://localhost:5173` to `/api/auth/me` carries the session cookie and isn't blocked. The config looks correct (`supports_credentials=True` in `__init__.py:19`), but the plan explicitly calls for a manual check.

### P2 — deployment (optional per `CLAUDE.md`; drop if dry-run reveals a long bug list)

`docs/deployment.md` lists three gating fixes — all of these need to land **before** a split-origin deploy will work:

6. **Add `gunicorn` to `backend/requirements.txt`** *(P)* — Render's start command (`gunicorn "app:create_app()"`) won't run otherwise.

7. **Flip `SESSION_COOKIE_SAMESITE` in `ProdConfig`** *(P)* — `backend/app/config.py:29-31` currently only sets `SESSION_COOKIE_SECURE = True`. Add `SESSION_COOKIE_SAMESITE = "None"` so the cookie is sent on cross-site XHR from Vercel to Render. Without this, `/api/auth/me` will look unauthenticated after callback.

8. **Frontend `VITE_API_BASE_URL` prefix** *(frontend, or P if no one else has the cycle)* — `frontend/src/api/client.ts` uses relative `/api/…` paths that depend on the Vite dev proxy. For Vercel → Render, add `VITE_API_BASE_URL` and prefix it in `client.ts`, including `imageUrl()` and the `window.location.href = "/api/auth/google"` redirect in `AuthContext.tsx:42`.

9. **Register the prod redirect URI in Google Cloud Console** *(P, but anyone with console access)* — `https://<backend>.onrender.com/api/auth/callback` must be added before the deployed login flow works.

10. **Atlas + seed + smoke test** *(P)* — create M0 cluster, set `0.0.0.0/0` network access, point Render at the connection string, run `python seed.py` against Atlas, hit the live URL through the demo script.

### P3 — explicitly out of scope (do NOT do)

Per `CLAUDE.md` "Deferred to v2" and `docs/backend.md` "Out of scope":

- Auto-matching between lost/found
- Claim workflow with identity verification
- Notifications (in-app or email)
- Campus map view
- GridFS orphan cleanup on item delete (TODO already in `app/items/routes.py:213`)
- Rate limiting, audit logs, deeper pagination

If the dry-run surfaces something that *feels* like one of these, drop a `TODO` comment and move on.

---

## Cross-reference

- Wire contract: `docs/api.md` — authoritative for endpoints, shapes, status codes.
- Folder layout + decisions: `docs/backend.md`.
- Per-person Day-by-Day plan: `docs/backend-tasks.md`.
- Sprint goals + meeting agendas: `docs/sprint-plan.md`.
- Deployment gotchas + sequencing: `docs/deployment.md`.
- Project-wide rules: `CLAUDE.md`.

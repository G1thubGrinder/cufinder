# CUFinder — Backend Task Split

5-day push to demo on 2026-05-16. All three people on backend. Frontend is feature-complete and consuming the contract in `docs/api.md`.

> Read first: `docs/api.md` (wire contract — authoritative), `docs/backend.md` (stack + folder layout + build order), `CLAUDE.md` (project rules).

## How the split avoids overlap

The skeleton is a hard prerequisite for everything else, so **P owns Day 1 alone** for `app/__init__.py`, `db.py`, `errors.py`. Guy and Kie spend Day 1 writing pydantic schemas and route stubs in their own files — no shared module touched. From Day 2, all three work in parallel because each owns a disjoint blueprint folder.

The one cross-cutting piece is `app/auth/guards.py` (used by every protected route). Guy finishes it by **EOD Day 2**. Until then, P and Kie use the stub gate that `docs/backend.md` already calls out, then swap to real guards on Day 3.

Folder ownership at a glance:

| Folder / file | Owner | Co-readers (no edits) |
|---|---|---|
| `backend/app/__init__.py`, `config.py`, `db.py`, `errors.py` | P | Guy, Kie |
| `backend/app/locations/` | P | — |
| `backend/app/auth/` | Guy | P, Kie (import guards only) |
| `backend/app/items/` | Guy | — |
| `backend/app/images/` | Kie | — |
| `backend/seed.py` | Kie | — |
| `backend/tests/` | Kie | — |
| `backend/.env.example`, `requirements.txt` | P | Guy, Kie add deps via PR |

---

## P — Foundation, Locations, Integration

### Day 1 (Mon 2026-05-11) — skeleton, alone in shared files

1. `backend/requirements.txt` — pin `flask`, `pymongo`, `pydantic>=2`, `python-dotenv`, `flask-cors`, `pytest`. Use exact versions you've verified locally.
2. `backend/.env.example` — placeholders for `MONGODB_URI`, `SESSION_SECRET`, `FRONTEND_ORIGIN` (per `docs/backend.md` "Env vars").
3. `backend/app/__init__.py` — `create_app()` factory: load config, init Mongo, register blueprints (import each lazily to avoid circulars), register error handlers, configure CORS for `FRONTEND_ORIGIN`, set session cookie attrs (`HttpOnly`, `SameSite=Lax`, `Secure` in prod).
4. `backend/app/config.py` — env-var-loading config classes (`DevConfig`, `ProdConfig`).
5. `backend/app/db.py` — single `MongoClient` + `get_db()` helper + GridFS bucket handle.
6. `backend/app/errors.py` — central error registration. Exception classes: `Unauthenticated`, `Forbidden`, `NotFound`, `Conflict`. All map to the JSON error shape in `docs/api.md` ("Error response shape").
7. `GET /api/health` — returns `{"status":"ok"}`. Smoke endpoint to prove the server boots.
8. **Push to `feat/backend-skeleton` and merge by EOD.** Guy and Kie are blocked on this hitting `main`.

### Day 2 (Tue 2026-05-12) — locations CRUD

Files: `backend/app/locations/__init__.py`, `backend/app/locations/routes.py`, `backend/app/locations/schemas.py`.

Endpoints (full spec in `docs/api.md` §Locations):
- `GET /api/locations` — public, returns active only.
- `POST /api/locations` — `web_admin` only. Use the **stub gate** for now: a function in `app/locations/routes.py` that just checks a placeholder header until Guy's `require_web_admin()` lands. Leave a `TODO(Guy)` comment.
- `PATCH /api/locations/:id` — `web_admin` only. Partial body.
- `DELETE /api/locations/:id` — soft delete (`is_active=false`).

`schemas.py` — pydantic models for `LocationCreate`, `LocationPatch`. Duplicate-name check returns `409 conflict`.

### Day 3 (Wed 2026-05-13)

- Replace stub gate with `require_web_admin()` from Guy's `app/auth/guards.py`. One PR, small.
- **Begin integration testing.** Run frontend (`frontend/`) against backend. Walk every flow in `docs/api.md`. File issues per bug, don't fix them yourself unless trivial.
- CORS sanity check against the actual frontend origin.

### Day 4 (Thu 2026-05-14)

- Bug triage — assign fixes to Guy or Kie based on blueprint ownership.
- Deploy: Render (backend) + Atlas (DB) + Vercel (frontend). Update `FRONTEND_ORIGIN` in prod env. **Drop deployment if the integration test list is still long — demo can run on localhost (per `CLAUDE.md`).**

### Day 5 (Fri 2026-05-15) — meeting 2 / dry-run

- Demo script + slides.
- Final bug-bash slot. Time-box ruthlessly.

---

## Guy — Auth + Items

### Day 1 (Mon 2026-05-11) — work in your own files only

You can't run anything yet (skeleton not landed) — write schemas + route shells against `docs/api.md`.

1. `backend/app/auth/schemas.py` — module-level `CU_EMAIL_REGEX` compiled from `docs/api.md` §"CU email regex": `^[^@\s]+@(student\.)?chula\.ac\.th$`. No request body model — login is a redirect flow, not a JSON POST.
2. `backend/app/auth/routes.py` — empty handler stubs for `GET /api/auth/google`, `GET /api/auth/callback`, `POST /api/auth/logout`, `GET /api/auth/me`. Don't register the blueprint yet — P does that on Day 2 once your folder lands.
3. `backend/app/items/schemas.py` — pydantic `ItemCreate` discriminated by `type: "lost" | "found"`. Enforce the "exactly one of `last_seen_location_id` / `last_seen_location_text`" rule and the parallel rule on the found-side `_location` and `held_*` pairs (per `docs/api.md` §Item).
4. `backend/app/items/routes.py` — empty handler stubs for the five endpoints in `docs/api.md` §Items.

### Day 2 (Tue 2026-05-12) — auth done, guards published

After P's skeleton merges (~midday):

1. `backend/app/auth/guards.py` — **highest priority for the team, finish by EOD.**
   - `require_user()` → reads `session["user_id"]`, returns the user dict, raises `Unauthenticated` otherwise.
   - `require_web_admin()` → calls `require_user()`, then checks `role == "web_admin"`, raises `Forbidden` otherwise.
   - `require_any_admin()` → returns the user if role is `web_admin` or `location_admin`.
2. `backend/app/auth/routes.py` — implement the four endpoints. `GET /api/auth/google` = stash CSRF state in session, redirect to Google with `hd=chula.ac.th`. `GET /api/auth/callback` = verify state, exchange code for token, fetch userinfo, enforce CU regex on the returned email, upsert by email with `$setOnInsert` (preserves seeded admin roles), set `session["user_id"]`, redirect to `FRONTEND_ORIGIN`. On any failure redirect to `FRONTEND_ORIGIN/login?error=<code>`. `POST /api/auth/logout` = clear session, `204`. `GET /api/auth/me` = `require_user()` → return `User`.
3. Register `auth_bp` in `app/__init__.py` (small PR to P's file, coordinate).
4. Notify P and Kie on chat that guards are live so they can swap stubs.

### Day 3 (Wed 2026-05-13) — items list + create

`backend/app/items/routes.py`:

- `GET /api/items` — every query param in `docs/api.md` §Items must filter correctly. Default `status="open"`, default `limit=30` capped at 100. Return `{ "items": [...], "total": N }`. Build the Mongo filter dict explicitly — keep this readable, it's the function most likely to grow bugs.
- `GET /api/items/:id` — single item or `404 not_found`.
- `POST /api/items` — `require_user()`. Validate via `ItemCreate`. Insert with `status="open"`, `posted_by` from session user, `posted_at=utcnow()`. Return `201` + the created item.

### Day 4 (Thu 2026-05-14) — items admin actions

- `PATCH /api/items/:id/status` — full authz from `docs/api.md`: `web_admin` may touch any item; `location_admin` may only touch `found` items where `held_admin_location_id == user.admin_location_id`. Anything else → `403 forbidden`.
- `DELETE /api/items/:id` — same authz as PATCH. Hard delete is OK in v1 (per `docs/backend.md` "Database").
- Walk through every `frontend/src/api/items.ts` call to confirm shapes line up.

### Day 5 (Fri 2026-05-15) — bug bash

Pick up triaged items bugs from P. No new endpoints.

---

## Kie — Images, Seed, Validation, Tests

### Day 1 (Mon 2026-05-11) — work in your own files only

1. `backend/app/images/schemas.py` — constants: `MAX_BYTES = 5 * 1024 * 1024`, `ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}`. No pydantic body model — endpoint is multipart.
2. `backend/app/images/routes.py` — empty handler stubs for `POST /api/images`, `GET /api/images/:id`.
3. `backend/seed.py` — start the file. Import the location names + admin emails directly from the lists in `docs/api.md` §"Seed data". Idempotent: insert by `name` for locations, by `email` for admins. **Do not run yet** — needs P's `db.py`.

### Day 2 (Tue 2026-05-12) — images + seed

After P's skeleton merges:

1. `backend/seed.py` — finish + run against local Mongo. Verify the 20 locations + 3 admin users appear. Re-run; verify nothing duplicates.
2. `backend/app/images/routes.py`:
   - `POST /api/images` — `require_user()` (use stub gate until Guy's guards land EOD; swap on Day 3). Read `request.files["file"]`. Validate mime + size. Write to GridFS via the bucket handle in `app/db.py`. Return `{"id": "<oid hex>"}`, status `201`.
   - `GET /api/images/:id` — public, no auth. Stream bytes via `send_file` with the correct `Content-Type`. `404` if missing.
3. Register `images_bp` in `app/__init__.py` (coordinate the merge with P and Guy).

### Day 3 (Wed 2026-05-13) — validation tightening + tests

1. Swap the stub gate in `app/images/routes.py` for the real `require_user()` from Guy's guards.
2. Audit every blueprint for missing validation:
   - `app/locations/schemas.py` — name length bounds, strip whitespace.
   - `app/items/schemas.py` — title/description length bounds, category must be one of the documented constants.
   - `app/images/routes.py` — reject empty file, reject filename with no extension.
3. `backend/tests/` — start the test folder.
   - `tests/test_email_regex.py` — table-driven cases for the CU regex (positive: `a@chula.ac.th`, `a@student.chula.ac.th`; negative: `a@gmail.com`, `a@chula.ac.th.evil.com`, empty, no `@`).
   - `tests/test_items_query.py` — exercise the `GET /api/items` filter builder with each query param.

### Day 4 (Thu 2026-05-14)

1. `tests/test_auth_guards.py` — `require_user`, `require_web_admin`, `require_any_admin` happy path + each failure mode.
2. `tests/test_images.py` — mime rejection, size rejection, happy upload + read-back.
3. `backend/README.md` — how to run locally (env vars, `flask --app app run --debug`, where to put `.env`, how to run `seed.py`, how to run pytest). Mirror the snippet in `CLAUDE.md` "Running locally".
4. Spare cycles: pick up any bug from P's triage list.

### Day 5 (Fri 2026-05-15) — bug bash

Same as Guy — pick up triaged items, no new features.

---

## Daily sync points

- **EOD Mon 2026-05-11** — P's skeleton merged to `main`. Guy and Kie rebase.
- **EOD Tue 2026-05-12** — Guy's `auth/guards.py` live. P and Kie swap their stub gates Wed morning.
- **EOD Wed 2026-05-13** — every endpoint in `docs/api.md` exists and returns *something* sensible. P starts integration testing.
- **EOD Thu 2026-05-14** — bug list closed enough to stop merging features.
- **Fri 2026-05-15** — dry-run + slide review (Meeting 2 in `docs/sprint-plan.md`).

## Out of scope reminder

Everything in `CLAUDE.md` "Deferred to v2" is still deferred. If a v1 task tempts you toward auto-matching, claim workflows, notifications, or a campus map — drop a `TODO` and move on.

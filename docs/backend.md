# CUFinder — Backend Plan (v1)

Companion to `docs/api.md` (the wire contract) and `CLAUDE.md` (project-wide rules). This file captures backend-specific decisions agreed with the lead on 2026-04-26.

## Stack

| Concern | Choice | Notes |
|---|---|---|
| Language / framework | Python 3.11+, Flask | App factory + blueprints (locked in CLAUDE.md). |
| Request validation | **pydantic** | One declarative model per request body / query shape. |
| MongoDB driver | **pymongo** | Raw driver, no ODM. Work with dicts directly. |
| Auth | **Signed session cookie** | `flask.session` (itsdangerous-backed). `HttpOnly`, `SameSite=Lax`, `Secure` in prod. No JWT. |
| Image storage | MongoDB GridFS | Locked in CLAUDE.md. |
| CORS | `flask-cors` | Allow `http://localhost:5173` in dev; deploy origin in prod. |
| Env loading | `python-dotenv` | `.env` file in dev. |

No ORMs. No Docker. No background workers or queues.

## Folder layout

```
backend/
├── app/
│   ├── __init__.py     # create_app()
│   ├── config.py       # env-var loading + dev/prod config classes
│   ├── db.py           # MongoDB client + db handle
│   ├── errors.py       # central exception → JSON error handler
│   ├── auth/           # blueprint: login, logout, me
│   ├── items/          # blueprint: list, get, create, status, delete
│   ├── locations/      # blueprint: list, create, patch, delete
│   └── images/         # blueprint: upload, stream
├── seed.py             # idempotent seed script (locations + admin users)
├── requirements.txt
└── .env.example
```

## Build order

Each phase reuses foundations laid by the previous one. Do not skip ahead.

1. **Skeleton** — `create_app()`, config, Mongo connection, central error handler, CORS, `GET /api/health` returning `{"status":"ok"}`. Goal: prove the server starts and connects to Mongo.
2. **Locations CRUD** — `GET /api/locations` (public), `POST/PATCH/DELETE /api/locations(/:id)` (web admin only — gate with a stub since auth isn't built yet). This is where we set the patterns for routes, pydantic validation, and JSON error responses.
3. **Auth** — `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`. Mock CU email regex from `docs/api.md`. Seed the three admin users on first run. Replace the stub gate from phase 2 with real session checks.
4. **Items** — list with filters, get-one, create, `PATCH /:id/status`, `DELETE /:id`. Wire the role-based authz exactly as `docs/api.md` specifies: web admin can act on any item; location admin only on `found` items where `held_admin_location_id` matches their `admin_location_id`.
5. **Images** — `POST /api/images` (multipart, GridFS write), `GET /api/images/:id` (stream bytes). 5 MB cap, jpeg/png/webp only.
6. **Polish** — re-check CORS for the deploy origin, write a backend-local README, optional deploy to Render or Railway.

## Conventions

### Validation
Each blueprint defines pydantic models under `<blueprint>/schemas.py`. Route handlers parse the JSON body with `Model.model_validate(request.get_json())` and let `pydantic.ValidationError` surface to the central handler, which maps it to `400 validation_failed`.

### Error responses
All non-2xx responses follow the shape locked in `docs/api.md`:
```json
{ "error": { "code": "string", "message": "string" } }
```
A single `register_error_handlers(app)` in `errors.py` wires:
- `pydantic.ValidationError` → 400 `validation_failed`
- custom `Unauthenticated`, `Forbidden`, `NotFound`, `Conflict` exceptions → matching codes / status
- everything else → 500 `internal_error` (no stacktraces leaked to the client).

### Auth
- `flask.session` signed with `SESSION_SECRET` from env. Cookie attributes: `HttpOnly`, `SameSite=Lax`, `Secure` in prod.
- Helpers in `auth/guards.py`: `require_user()`, `require_web_admin()`, `require_any_admin()`. Each reads `session["user_id"]`, looks up the user, and raises `Unauthenticated` / `Forbidden` as needed.
- No password storage. Login = email matches the CU regex → look up or create the user → set `session["user_id"]`.

### Database
- One MongoDB database. Collections: `users`, `locations`, `items`. GridFS bucket: default `fs`.
- `_id` is a Mongo `ObjectId` server-side; serialize to a 24-char hex string in JSON.
- Soft delete on locations (`is_active=False`). Hard delete is acceptable for items in v1.

### Env vars
Required:
- `MONGODB_URI` — e.g. `mongodb://localhost:27017/cufinder`
- `SESSION_SECRET` — long random string for signing cookies
- `FRONTEND_ORIGIN` — `http://localhost:5173` in dev, deployed URL in prod

`.env.example` ships with placeholders; the real `.env` is gitignored.

### Seeding
`python seed.py` runs once on a fresh DB. Idempotent — insert locations only if missing by name; insert admin users only if missing by email. The location list and admin emails are in `docs/api.md` under "Seed data".

## Out of scope (v1)

Anything in the "Deferred to v2" list in CLAUDE.md, plus:
- Pagination beyond the existing `skip` / `limit` on `GET /api/items`.
- Rate limiting.
- Audit logs.
- Image deletion / orphan cleanup when an item is deleted (leave a TODO).
- Coverage targets for tests — write pytest cases only where they pay back (auth helpers, item-list query building).

## Cross-references

- **API contract** — `docs/api.md` (authoritative for endpoints, shapes, status codes).
- **Project rules** — `CLAUDE.md`.
- **Original proposal** — `docs/proposal.md`.

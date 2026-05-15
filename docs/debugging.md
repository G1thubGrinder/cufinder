# Finding a Bug — Setup, QA, Reporting, Debugging

A practical guide for the team. Covers the whole loop: **set up the app → find a bug → report it → debug it → fix it.**

If something here drifts from the code, fix the doc as well as the bug.

Cross-references:
- `CLAUDE.md` — project-wide rules and v1 scope.
- `docs/api.md` — wire contract. The single source of truth when a frontend ↔ backend mismatch is suspected.
- `docs/backend.md` — backend folder layout and conventions.
- `docs/backend-test.md` — what the existing pytest suite covers.

---

## 1. Set up locally from zero

Assume the teammate has just cloned the repo and has nothing else. Walk through every prerequisite.

### 1.1 Prerequisites

Install these globally before touching the repo:

| Tool | Version | Why |
|---|---|---|
| Git | any recent | clone, branch |
| Python | 3.11+ | backend runtime |
| Node.js + npm | Node 18+ | frontend runtime |
| MongoDB Community | 6.x or 7.x | local DB (or use an Atlas free cluster) |
| A browser | Chrome / Edge / Firefox | testing + DevTools |

Optional but recommended:
- **MongoDB Compass** — GUI for inspecting Mongo state when a bug is "the data looks wrong".
- **React Developer Tools** browser extension — inspect React tree and component props.
- **VS Code** — both apps debug well with built-in launch configs (see §4).

Verify the basics from a fresh terminal:

```powershell
git --version
python --version          # must print 3.11+
node --version            # must print v18+
npm --version
mongod --version          # skip if using Atlas
```

### 1.2 Clone

```powershell
git clone <repo-url> cufinder
cd cufinder
```

The repo is a monorepo with two independent app directories: `backend/` and `frontend/`. Each has its own dependencies and run command. Open two terminals — one per app.

### 1.3 Backend setup

From `backend/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1            # PowerShell
#   cmd:          .venv\Scripts\activate.bat
#   Git Bash/sh:  source .venv/Scripts/activate
#   macOS/Linux:  source .venv/bin/activate

pip install -r requirements.txt
Copy-Item .env.example .env
```

Now open `backend/.env` and fill in real values. At a minimum:

- `MONGODB_URI` — leave as `mongodb://localhost:27017/cufinder` if you have local Mongo running. Otherwise paste your Atlas SRV string.
- `SESSION_SECRET` — generate one:
  ```powershell
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI` — see §1.5.

Leave `FRONTEND_ORIGIN=http://localhost:5173` and `APP_ENV=dev` alone for local work.

### 1.4 Frontend setup

From `frontend/`:

```powershell
npm install
Copy-Item .env.example .env
```

Open `frontend/.env`. For most bug-hunting, you want **real** backend calls, so set:

```
VITE_USE_MOCK=false
```

Set `VITE_USE_MOCK=true` only when you want to exercise the UI in isolation against in-memory fake data (handy if the backend is down or you're triaging a UI-only bug — see §2.4).

Leave `VITE_API_BASE_URL` commented out for local dev — the Vite dev proxy in `vite.config.ts` forwards `/api/*` to `http://localhost:5001`.

### 1.5 Google OAuth credentials

Login is **Google OAuth restricted to CU emails** (`CLAUDE.md` → "Auth approach"). To log in locally:

1. Go to [Google Cloud Console](https://console.cloud.google.com) → **APIs & Services → Credentials**.
2. Create an **OAuth 2.0 Client ID**, type **Web application**.
3. Authorised redirect URI: `http://localhost:5001/api/auth/callback` (exactly this — port 5001 is required).
4. Copy the client ID and secret into `backend/.env`.

For team development, the lead can share a single dev OAuth client. The Google credentials are not committed to git.

### 1.6 MongoDB

Local Mongo:

```powershell
# Windows: start the MongoDB service if it isn't already.
# Quick check that it's reachable:
mongosh --eval "db.runCommand({ ping: 1 })"
```

Atlas: paste the SRV string into `MONGODB_URI`. Make sure your IP is allow-listed in the Atlas Network Access page.

### 1.7 Run both apps

Backend (from `backend/` with the venv activated):

```powershell
flask --app app run --debug --port 5001
```

Frontend (from `frontend/`, in a second terminal):

```powershell
npm run dev
```

Open <http://localhost:5173>. The Vite dev server proxies `/api/*` calls to the Flask backend on 5001.

### 1.8 Seed data

Run once on a fresh DB. Idempotent — safe to re-run.

```powershell
# from backend/ with the venv activated
python seed.py
```

This loads the 20 default locations and three admin accounts (see `backend/README.md`). **The seeded admin emails won't let you actually log in** unless they exist as real Google accounts. To exercise admin features, edit `seed.py` and swap one of the admin emails for a teammate's real `@chula.ac.th` account before re-running.

### 1.9 Sanity check

Backend healthcheck (in a third terminal):

```powershell
curl http://localhost:5001/api/health
# expect: {"status":"ok"}
```

If this returns `{"status":"ok"}`, Flask is up **and** can talk to Mongo. If it errors, the issue is one of those two — fix it before moving on.

In the browser, you should see the home page render with a list of items (empty until you post some).

---

## 2. Finding bugs (QA pass)

A "QA pass" means: deliberately exercise each feature in v1, both the happy path and the obvious failure modes, and write down anything that surprises you. The goal isn't exhaustive coverage — it's catching things that would embarrass us at the demo.

### 2.1 v1 features to exercise

For each feature, run through the **happy path** and at least the **bold edge cases**.

#### Auth (Google OAuth, CU domain only)

- Happy path: click **Login**, complete Google flow with a `@chula.ac.th` or `@student.chula.ac.th` account, land back on the app logged in.
- Edge cases:
  - Log in with a non-CU email (e.g. a personal Gmail). Expect a redirect to `/login?error=not_cu_email`. **Do not expect the app to crash.**
  - Cancel the Google consent screen. Expect a clean redirect with `?error=access_denied`.
  - Click **Logout**. Expect the session to clear; `GET /api/auth/me` should now return 401.
  - Open in an incognito window. Expect to be treated as unauthenticated.

#### Post a lost item

- Happy path: fill title, description, category, last-seen location (dropdown), last-seen date, contact info, image — submit.
- Edge cases:
  - Submit with required fields blank. Expect a `400 validation_failed` and a visible error, not a silent failure.
  - Pick a free-text last-seen location instead of the dropdown (only one of the two should be set).
  - Upload a non-image file (e.g. a PDF). Expect rejection by `POST /api/images`.
  - Upload an image > 5 MB. Expect rejection.

#### Post a found item

- Happy path: similar to lost, plus a "where currently held" field. Confirm both `found_location_*` and `held_*` fields behave.
- Edge cases: same as above, plus mixing the `held_admin_location_id` and `held_freetext` fields (exactly one allowed).

#### Browse / search / filter

- List loads with default filter `status=open`. Switch to `claimed` and `disposed` and confirm the list refreshes.
- Combine filters: category + location + date range + text search. Confirm results narrow correctly.
- Search with regex-special characters (e.g. `.*` or `\`). Should match literally, not as a regex. (See `test_items_query.py` for the backend rule.)
- Empty result set should render a clean empty state, not a blank page.

#### Admin dashboard

You need a logged-in admin account to test this (see §1.8). Two roles to cover:

- **`location_admin`** (e.g. seeded `eng.admin@chula.ac.th`): can mark/delete only `found` items whose `held_admin_location_id` matches their `admin_location_id`. Try to PATCH a `lost` item or a `found` item held elsewhere — expect `403 forbidden`.
- **`web_admin`** (e.g. seeded `web.admin@chula.ac.th`): can manage locations and moderate any item.
  - Create a new location, edit it, soft-delete it. Confirm soft-deleted locations don't appear in the public `GET /api/locations` list.
  - Try to create a duplicate location name — expect `409 conflict`.

### 2.2 Common failure modes specific to this app

These have caught us before; check them first when something is weird.

| Symptom | Likely cause | Where to look |
|---|---|---|
| OAuth redirect lands on `?error=invalid_state` | Session cookie was lost between `/google` and `/callback` (often a `SameSite` / cross-site issue). | `app/auth/routes.py`, `SESSION_COOKIE_SAMESITE` in `config.py`. |
| OAuth redirect lands on `?error=not_cu_email` even with a CU account | Email didn't match the CU regex. | `docs/api.md` "CU email regex"; `app/auth/schemas.py`. |
| Login appears to succeed but `GET /api/auth/me` returns 401 | Cookie not being sent. In a split-origin deploy this is a CORS + `SameSite=None; Secure` problem. | `app/__init__.py` CORS config, `config.py`. |
| Image upload returns 400 | File > 5 MB or wrong mime (`image/jpeg`, `image/png`, `image/webp` only). | `test_images.py` for the exact rules. |
| Items list ignores a filter | Filter param spelled differently on the wire than the frontend sends. | `docs/api.md` query params table; `app/items/routes.py` `_build_filter`. |
| `403 forbidden` on a location admin action | The item's `held_admin_location_id` doesn't match the admin's `admin_location_id`. | `app/auth/guards.py`. |
| Frontend shows real data even with `VITE_USE_MOCK=true` | The frontend was started before `.env` changed. Restart `npm run dev`. | `frontend/.env`. |
| `flask` command not found | Venv isn't activated, or it's activated in a different terminal. | Re-run the activation command from §1.3 in the current shell. |
| Port 5001 already in use | A previous `flask` process didn't exit, or another app is on 5001. **Don't change the port** — OAuth redirect is hardcoded. | Kill the stale process. |
| CORS error in browser console | `FRONTEND_ORIGIN` in `backend/.env` doesn't match what the browser is actually using. | `backend/.env`, `app/__init__.py`. |

### 2.3 Curl-ing the backend directly

To isolate "is this a frontend bug or a backend bug?", hit the API directly:

```powershell
# public
curl http://localhost:5001/api/health
curl http://localhost:5001/api/locations

# authenticated — needs the session cookie. Log in via the browser first,
# then copy the `session=...` cookie from DevTools and pass it:
curl -H "Cookie: session=<paste-here>" http://localhost:5001/api/auth/me
```

If the API returns what `docs/api.md` says it should, but the UI shows something else, the bug is in the frontend. And vice versa.

### 2.4 Mock-mode trick

`VITE_USE_MOCK=true` in `frontend/.env` makes the frontend use in-memory fake data from `frontend/src/api/mock/`. Two uses:

- **Triage a UI bug**: if it reproduces in mock mode, the bug is purely in the frontend — no backend changes needed.
- **Work while the backend is down**: keep building UI even when the backend can't run (e.g. someone is mid-refactor on `main`).

Restart `npm run dev` after changing the env file.

---

## 3. Reporting a bug

We use **GitHub Issues** on the repo. Keep reports short, but include enough that someone else can reproduce without asking.

### 3.1 Template

Paste this into the issue body and fill it in:

```markdown
**What happened**
One sentence. The observable symptom.

**Steps to reproduce**
1. ...
2. ...
3. ...

**Expected**
What should have happened.

**Actual**
What did happen. Include the exact error text or status code if any.

**Environment**
- Side: frontend / backend / both
- Browser + OS: e.g. Chrome 130 on Windows 11
- Branch / commit: `git rev-parse --short HEAD`
- Logged in as: regular user / location_admin / web_admin / not logged in
- VITE_USE_MOCK: true / false

**Evidence**
- Backend log (relevant lines from the Flask console)
- Browser console errors
- Network tab: request URL, method, status, response body
- Screenshot if it's a visual bug
```

### 3.2 Labels

Apply at least one **area** label and one **severity** label.

**Area** (which slice of the app):
- `area:auth` — login, session, role checks
- `area:items` — lost/found posting, list, filter
- `area:locations` — location CRUD, admin
- `area:images` — upload, GridFS, serving
- `area:admin` — admin dashboard UI / authz
- `area:infra` — setup, env, deploy, CORS

**Severity** (how urgent — we're 3 weeks from demo):
- `sev:P0` — blocks the demo. Login broken, app won't start, data loss. Fix today.
- `sev:P1` — a v1 feature is broken or wrong. Fix this sprint.
- `sev:P2` — minor, cosmetic, or easy workaround exists. Fix if time allows.

### 3.3 What to do before filing

Five-minute sanity check first. If any of these turns out to be the cause, fix it locally rather than filing:

1. Pull `main` — has someone already fixed it?
2. Restart both `flask` and `npm run dev` — picks up `.env` changes.
3. Run the backend suite: `pytest -q` from `backend/`. If a test fails, the bug is already covered — link the test in the issue.
4. Curl the backend directly (see §2.3) to confirm which side owns the bug.

---

## 4. Debugging a bug you've found

### 4.1 Decide where it lives

Before reaching for a debugger, classify the bug:

1. **Backend-only**: curl reproduces it without involving the frontend → §4.2.
2. **Frontend-only**: reproduces in `VITE_USE_MOCK=true` mode, or the API response looks correct in the Network tab but the UI is wrong → §4.3.
3. **Contract mismatch**: the API response is one shape but the frontend expects another → fix `docs/api.md` first, then bring both sides in line.
4. **DB / state**: the code is right but the data is unexpected → §4.4.

### 4.2 Backend debugging

**Flask debug mode** is on by default with `--debug` (see §1.7). That gives you:
- Auto-reload on file save.
- Werkzeug's in-browser interactive debugger when a request raises (only on `localhost`, never in prod). Click the >>> on any stack frame to drop into a REPL at that point.

**Print debugging** — fine for quick checks. `app/errors.py` swallows uncaught exceptions and returns `500 internal_error` to the client without the stack trace, so **always read the Flask console** for the real error.

**`breakpoint()`** — drop one in any handler:
```python
@items_bp.get("/api/items")
def list_items():
    filter_doc = _build_filter(request.args)
    breakpoint()       # pauses here; inspect filter_doc, request.args, etc.
    ...
```
Run Flask in a terminal (not via VS Code's "Run" button) so stdin is attached.

**VS Code launch config** — create `.vscode/launch.json` (gitignored, fine to keep local):
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Flask: backend",
      "type": "python",
      "request": "launch",
      "module": "flask",
      "args": ["--app", "app", "run", "--debug", "--port", "5001", "--no-reload"],
      "cwd": "${workspaceFolder}/backend",
      "env": { "FLASK_ENV": "development" },
      "jinja": true
    }
  ]
}
```
Set breakpoints in any `.py` file and hit F5.

**Run a single test** to bisect:
```powershell
# from backend/
pytest tests/test_items_query.py::test_specific_case -v
```
If the bug has a regression-worthy shape, add a failing test in `tests/` before fixing — it documents the bug and prevents reintroduction. See `docs/backend-test.md` for what the suite covers today.

### 4.3 Frontend debugging

**Browser DevTools** (F12) — your main tool. Three tabs matter:

- **Console** — JS errors and our own `ApiError` logs. `client-error.ts` defines the error type all API calls throw.
- **Network** — filter to `Fetch/XHR`. For any failed request, check:
  - Status code (compare to `docs/api.md`).
  - Request headers — is the session cookie being sent? (`Cookie: session=...`)
  - Response body — is it the error shape `{"error": {"code": ..., "message": ...}}`?
- **Application → Cookies** — is the `session` cookie present for `localhost:5001`? Is it `HttpOnly`?

**React DevTools** — inspect the component tree, props, and state. Especially useful for "this component re-renders too often" or "state isn't updating".

**Vite source maps** are on by default, so DevTools breakpoints land on the real `.ts`/`.tsx` lines.

**VS Code launch config** for the frontend (optional):
```json
{
  "name": "Chrome: frontend",
  "type": "chrome",
  "request": "launch",
  "url": "http://localhost:5173",
  "webRoot": "${workspaceFolder}/frontend"
}
```

**Toggle mock mode** to isolate (see §2.4).

### 4.4 Inspecting DB state

Two ways:

**`mongosh`**:
```powershell
mongosh "mongodb://localhost:27017/cufinder"
> db.items.find({ type: "found" }).limit(5).pretty()
> db.users.find({ role: { $ne: "user" } })
> db.locations.find({ is_active: false })
```

**MongoDB Compass** — point it at the same URI, browse `users`, `items`, `locations`, and the `fs.files` / `fs.chunks` GridFS collections.

When fixing a bug that came from bad seeded state, re-run `python seed.py` (idempotent) rather than hand-editing documents.

### 4.5 The "fix it" half

- For backend regressions, prefer adding a failing test in `backend/tests/` **before** fixing — `docs/backend-test.md` shows the existing patterns.
- For frontend regressions, add at least a manual repro note to the PR description so the reviewer can confirm the fix.
- Keep the fix scoped to the bug. Resist the urge to refactor while you're in there (`CLAUDE.md` → "Don't add features ... beyond what the task requires").
- Update `docs/api.md` if the bug exposed an ambiguity in the contract.

---

## 5. Quick reference — common commands

```powershell
# backend (from backend/ with venv active)
flask --app app run --debug --port 5001       # run dev server
pytest -q                                     # run all tests
pytest tests/test_items_query.py -v           # run one file
python seed.py                                # seed DB (idempotent)
python -c "import secrets; print(secrets.token_hex(32))"   # generate SESSION_SECRET

# frontend (from frontend/)
npm run dev                                   # run dev server
npm run build                                 # production build (catches type errors)

# git
git rev-parse --short HEAD                    # current commit for bug reports
git status                                    # before filing a bug, make sure you're on a clean main

# mongo
mongosh "mongodb://localhost:27017/cufinder"
curl http://localhost:5001/api/health         # backend up + Mongo reachable
```

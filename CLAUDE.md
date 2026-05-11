# CUFinder — Development Guide

A lost-and-found web app for Chulalongkorn University. See `docs/proposal.md` for the original course proposal.

## Project status

- **Stage:** v1 build. Started 2026-04-25, target demo around 2026-05-16 (~3 weeks).
- **Team:** 3 people — 1 lead (project owner), 1 frontend, 1 backend.
- **Work style:** independent-ish. Agree on the API contract early, then frontend and backend ship in parallel against it.

## v1 scope (build this)

These are the only features in v1. Do not start anything in the deferred list without explicit go-ahead from the lead.

1. **Auth** — login by CU email, with a regular-user vs admin role split. See "Auth approach" below.
2. **Post a lost item** — photo, description, category, last-seen location, date.
3. **Post a found item** — photo, description, where found, where currently held.
4. **Browse / search / filter** — by category, building/location, date range.
5. **Admin dashboard** — admins see items held at their location; can mark items claimed or disposed, and moderate listings.

## Deferred to v2 (do NOT build yet)

- Auto-matching between lost and found posts
- Claim workflow with identity verification
- Notifications (in-app or email)
- Campus map view

If a v1 task naturally invites a v2 feature ("while we're here we could just add matching"), don't. Drop a TODO and move on.

## Tech stack

- **Frontend:** React + TypeScript, built with Vite
- **Backend:** Python 3.11+, Flask (app factory pattern + blueprints)
- **Database:** MongoDB — local Mongo for dev, MongoDB Atlas free tier for deployment
- **Image storage:** MongoDB GridFS (everything in one DB to keep deploy simple)
- **API style:** REST, JSON

## Repo layout (monorepo)

```
cufinder/
├── frontend/          # Vite + React + TS
├── backend/           # Flask app
├── docs/              # proposal.md, api.md, design notes
├── README.md
└── CLAUDE.md          # this file
```

The two app directories are independent — each has its own package manager, lockfile, and run scripts. There is no shared build system; keep it simple.

## Key architectural decisions

### Auth approach: Google OAuth (CU domain only)

Login is **Google OAuth** restricted to the CU email domain. Decided 2026-05-11 after reviewing the original mock-login plan — graders all have `@chula.ac.th` accounts, so OAuth is realistic without gating the demo.

- Frontend redirects the user to `GET /api/auth/google`; backend bounces through Google's consent flow and lands on `GET /api/auth/callback`.
- Backend validates the email against the CU regex in `docs/api.md` **after** Google verifies it — the `hd=chula.ac.th` hint sent to Google is not trusted on its own.
- A small seed list of emails is flagged as `location_admin` / `web_admin` in the database; everyone else is a regular user (upserted on first login with `$setOnInsert` so seeded roles survive).
- Session is a signed cookie (`HttpOnly`, `SameSite=Lax`, `Secure` in prod). No password storage.
- Required env: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`. See `.env.example`.
- Do **not** add password flows or non-Google identity providers — still out of scope.

### Image storage: GridFS

- Upload endpoint stores the file in GridFS and saves the resulting `ObjectId` on the item document.
- Serve images via a Flask route that streams from GridFS (e.g. `GET /api/images/:id`).
- No S3, no Cloudinary, no local-disk storage. Keeping everything in MongoDB makes deployment painless.

### API contract first

Because frontend and backend ship in parallel, the API contract is the integration point. Before building a feature:

1. Define endpoint(s), request/response shapes, and status codes in `docs/api.md` (create if missing).
2. Frontend mocks against that contract; backend implements against it.
3. Changes to the contract require both sides to agree.

## Conventions

- **Branches:** `main` is the integration branch. Feature branches: `feat/<short-name>`, `fix/<short-name>`. Open PRs for review.
- **Commits:** short imperative subject (e.g. `add lost-item form`). No strict Conventional Commits unless the team opts in.
- **Python:** format with `black`, lint with `ruff`. Type hints encouraged but not required.
- **TypeScript:** strict mode on. ESLint + Prettier.
- **Tests:** not graded; write them where they pay back (form validation, auth helpers, search query building). Don't chase coverage.

## Running locally

Scaffolding doesn't exist yet — fill these in once it does:

- `frontend/`: `npm install && npm run dev`
- `backend/`: `python -m venv .venv && source .venv/Scripts/activate && pip install -r requirements.txt && flask --app app run --debug`
- Required env: `MONGODB_URI` pointing at local Mongo or an Atlas cluster, plus a `SESSION_SECRET` for signing cookies.

## Deployment (nice-to-have, not required)

If we want a live demo URL:

- **Frontend:** Vercel or Netlify (drop-in for Vite)
- **Backend:** Render or Railway free tier
- **Database:** MongoDB Atlas free tier
- Configure CORS on the Flask side to accept the deployed frontend origin.

Don't spend more than a day on this. The demo can run on localhost if needed.

## What Claude should and shouldn't do here

- **Do** read `docs/proposal.md` and `docs/api.md` (once it exists) before changing behavior.
- **Do** treat the v1 scope as a hard line. Suggest deferring v2 ideas, don't implement them.
- **Do** keep frontend and backend changes independent unless the lead asks for both.
- **Don't** add real OAuth, notification systems, or auto-matching without explicit go-ahead.
- **Don't** swap the image storage backend (GridFS) without discussion.
- **Don't** introduce new top-level tools (Docker, ORM layers, monorepo build systems) without asking. The team is small and the timeline is tight.

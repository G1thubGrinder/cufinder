# CUFinder — Sprint Plan

3-week v1 build, two sprints of ~10 days each. Demo target: **2026-05-16**.

Workflow per sprint: assign work → finish work → meeting.

Team:
- **Lead** — project owner, coordination, integration, deployment, demo prep
- **Frontend** — React + TypeScript (Vite)
- **Backend** — Python + Flask + MongoDB

---

## Sprint 1 — Foundations + Create paths
**2026-04-25 → 2026-05-05** (work) → **Meeting 1: ~2026-05-05**

**Goal at meeting 1:** A logged-in user can submit a lost or found item with a photo, and the data lands in MongoDB. End-to-end, no listing page yet.

### Lead
- Day 1: scaffold the monorepo (`frontend/`, `backend/` skeletons) so the others can `git pull` and start
- Draft `docs/api.md` — endpoints, request/response shapes, error codes — by Day 3 at the latest. **Highest-priority deliverable; it unblocks parallel work.**
- Define the MongoDB schema for `users`, `items` (lost + found unified, distinguished by a `type` field), and the admin seed list
- Decide the CU-email regex, lock it in `docs/api.md`
- Set up shared dev practices: branch naming, PR review, `.env.example` files
- Spare cycles: pair on whichever side is behind, or start deployment scaffolding (Render + Atlas) so Sprint 2 isn't crunched

### Frontend
- Vite + React + TS project, routing (React Router), base layout (header, nav)
- Pick a styling approach once and stick to it (Tailwind recommended for speed)
- **Login page** wired to mock-auth endpoint
- **Post Lost Item** form (photo, description, category, location, date)
- **Post Found Item** form (photo, description, found location, currently held at)
- Image upload UI (preview, single file, size limit)
- Auth state management (logged-in user in context/store)
- The Website style is #DE548E and #FFFFFF

### Backend
- Flask app factory + blueprints (`auth`, `items`, `images`)
- MongoDB connection + collection initializers
- **Mock auth endpoints**: `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me` — issue signed session cookie
- **GridFS image endpoints**: `POST /api/images`, `GET /api/images/:id`
- **Item create endpoints**: `POST /api/items/lost`, `POST /api/items/found` (or unified `POST /api/items` with `type` in body)
- Admin seed script

### Meeting 1 agenda (~30 min)
1. Live demo: log in → submit a lost item with photo → see it in DB
2. What broke / what was harder than expected
3. Confirm Sprint 2 scope (esp. cut deployment if behind)
4. Re-assign work for Sprint 2

---

## Sprint 2 — Discovery + Admin + Polish
**2026-05-06 → 2026-05-15** → **Meeting 2: 2026-05-15** (demo dry-run)

**Goal at meeting 2:** Full v1 demo-ready. Real users can browse, filter, and admins can manage items.

### Lead
- **Integration testing** — exercise every flow end-to-end as the FE+BE pieces merge
- **Deployment** to Vercel + Render + Atlas (drop if Sprint 1 ran late)
- Demo script, slides, talking points
- Bug triage during the bug-bash phase (last 2 days)

### Frontend
- **Listings page**: grid/list of items with search bar + filters (category, location, date range)
- Item detail page (full info + photo)
- **Admin dashboard** UI (table of items at admin's location, claim/dispose/moderate actions)
- Responsive polish (mobile browser)
- Empty states, loading states, basic error handling

### Backend
- **Item query endpoints**: `GET /api/items` with query params for filter/search
- **Item detail**: `GET /api/items/:id`
- **Admin endpoints**: update status (claimed/disposed), delete/moderate, list items at admin's location
- Server-side validation tightening
- CORS config for deployed frontend
- Help with deployment config

### Meeting 2 agenda (~45 min)
1. Full demo run-through (the script the lead will use on demo day)
2. Bug list — assign final fixes, time-box to demo day
3. Slides review

---

## Assumptions baked into this plan

- Lead role is mostly coordination + integration + deployment + demo prep, not owning a feature
- Frontend and backend devs have working familiarity with React/Flask (no learning curve baked in)
- Deployment is in scope as a stretch goal — first to be dropped if Sprint 1 runs late
- Sprint dates are calendar-day ranges, not workdays — adjust expectations if the team only works weekdays

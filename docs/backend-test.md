# Backend Test Run

Date: 2026-05-15. Run after the P1/P2 deploy-prep edits to confirm no regression.

## How

From `backend/` with the project venv:

```
.\.venv\Scripts\pytest.exe -q
```

Tests live under `backend/tests/` and use the in-memory GridFS / Mongo stubs in `conftest.py` — no real database is required.

## What's covered

| File | Tests | Scope |
|---|---|---|
| `test_email_regex.py` | 6 | CU email regex from `auth/schemas.py` (student + staff domains, rejects). |
| `test_auth_guards.py` | 9 | `require_user`, `require_web_admin`, `require_any_admin` — happy path + every 401/403 mode, including stale `user_id` session cleanup. |
| `test_items_query.py` | 11 | `_build_filter` for `GET /api/items`: status defaulting, invalid-value fallback, type/category/location/date/search filters, regex-escape on `q`. |
| `test_images.py` | 8 | `POST /api/images` (mime / size / empty / no-extension rejects) and `GET /api/images/:id` (success + invalid id + missing). |

Total: **34 tests**.

## Result

```
..................................                                       [100%]
34 passed in 1.80s
```

All green. The deploy-prep edits (`SESSION_COOKIE_SAMESITE` in `ProdConfig`, `gunicorn` in `requirements.txt`) aren't exercised by the suite — `ProdConfig` is only used when `APP_ENV=prod`, and `gunicorn` only matters in deployment — so a passing suite here is necessary but not sufficient. Live smoke-test on Render is still required (`docs/deployment.md` §"Smoke test on live URL").

# Campus Copies ERP — Project Changelog

All notable changes to the Campus Copies project will be documented in this file.

---

## [Phase 1 Foundation Setup] - 2026-07-22

### Version
`v0.1.0-alpha.1`

### Files Created
- `backend/requirements.txt`
- `backend/app/__init__.py`
- `backend/app/config.py`
- `backend/app/core/__init__.py`
- `backend/app/core/logging.py`
- `backend/app/core/errors.py`
- `backend/app/core/security.py`
- `backend/app/database.py`
- `backend/app/main.py`
- `backend/tests/test_foundation.py`
- `frontend/package.json`
- `frontend/tsconfig.json`
- `frontend/tsconfig.node.json`
- `frontend/vite.config.ts`
- `frontend/tailwind.config.js`
- `frontend/postcss.config.js`
- `frontend/index.html`
- `frontend/src/index.css`
- `frontend/src/types/api.ts`
- `frontend/src/api/client.ts`
- `frontend/src/App.tsx`
- `frontend/src/main.tsx`

### Features Added
- Created backend foundation with FastAPI app lifecycle, pydantic-settings configuration engine (`app/config.py`), structlog JSON structured logging with token redaction (`app/core/logging.py`), custom `AppException` hierarchy & standard JSON error envelopes (`app/core/errors.py`), `pwdlib` bcrypt password hashing & `PyJWT` token generators (`app/core/security.py`), SQLAlchemy 2.x engine with `NullPool` for Supabase PgBouncer (`app/database.py`), slowapi rate limiter, CORS middleware, and `/api/health` health check endpoint (`app/main.py`).
- Created frontend React 18 / Vite 5 / Tailwind CSS 3 foundation with TypeScript alias setup (`@/*`), standard API envelope types (`src/types/api.ts`), centralized fetch API client (`src/api/client.ts`) supporting JWT authorization header injection, timeout handling, and 401 unauthorized auto-logout event dispatch.
- Added backend unit test suite (`tests/test_foundation.py`).

### Bug Fixes
- None (Initial Phase 1 build).

### Known Issues
- Database tables and schema migrations will be created in Phase 2.

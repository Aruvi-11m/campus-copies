# Campus Copies ERP — Project Changelog

All notable changes to the Campus Copies project will be documented in this file.

---

## [Phase 3 Authentication & Authorization Engine] - 2026-07-23

### Version
`v0.3.0-alpha.1`

### Files Created
- `backend/app/models/enums.py`
- `backend/app/models/student.py`
- `backend/app/models/admin.py`
- `backend/app/models/session.py`
- `backend/app/models/__init__.py`
- `backend/app/schemas/auth.py`
- `backend/app/schemas/__init__.py`
- `backend/app/repositories/base.py`
- `backend/app/repositories/student_repository.py`
- `backend/app/repositories/admin_repository.py`
- `backend/app/repositories/session_repository.py`
- `backend/app/repositories/__init__.py`
- `backend/app/services/auth_service.py`
- `backend/app/services/__init__.py`
- `backend/app/dependencies.py`
- `backend/app/api/v1/auth.py`
- `backend/app/api/v1/students.py`
- `backend/app/api/v1/router.py`
- `backend/tests/conftest.py`
- `backend/tests/test_auth.py`

### Files Modified
- `backend/app/main.py`
- `backend/app/core/errors.py`
- `docs/Changelog.md`

### Features Added
- **Student Authentication**: Auto-registration / login flow (`POST /api/v1/auth/student/login`) validating 10-digit Indian mobile format (`^[6-9][0-9]{9}$`) and department. Generates 24-hour Student JWT tokens.
- **Admin Authentication**: Login endpoint (`POST /api/v1/auth/admin/login`) verifying bcrypt password hashes (12 rounds) via `pwdlib` and active status. Generates 8-hour Admin JWT tokens and records session entries in `sessions` table.
- **Admin Bootstrap**: One-time initial admin setup method (`bootstrap_initial_admin`) enforcing max 3 active administrators constraint.
- **Authorization Dependencies**: Implemented FastAPI security dependencies `extract_token_from_request`, `get_current_token_payload`, `get_current_user`, `require_student`, `require_admin`, and `verify_student_ownership`. Supports both Authorization Bearer header and `?token=<jwt>` query parameter authentication.
- **Student Profile API**: Profile retrieval endpoint (`GET /api/v1/students/me`) returning authenticated student data.
- **Automated Test Suite**: Added 21 automated unit, repository, service, security, and API contract tests (`backend/tests/test_auth.py` & `backend/tests/test_foundation.py`). All 21 tests passing.

### Bug Fixes
- Updated `validation_exception_handler` in `app/core/errors.py` to use `jsonable_encoder` to handle Pydantic ValueError exception serialization in JSON responses.

### Known Issues
- None.

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

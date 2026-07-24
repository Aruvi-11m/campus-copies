# Campus Copies ERP — Project Changelog

All notable changes to the Campus Copies project will be documented in this file.

---

---

## [Phase 10 Verification & Production Readiness] - 2026-07-23

### Version
`v1.0.0-rc.1`

### Files Created
- `backend/Dockerfile`
- `backend/.dockerignore`
- `docker-compose.yml`
- `nginx/default.conf`
- `prometheus.yml`
- `backend/app/core/scheduler.py`
- `backend/app/services/email_service.py`
- `.github/workflows/ci.yml`

### Files Modified
- `backend/requirements.txt`
- `backend/app/main.py`
- `backend/alembic/env.py`
- `docs/Changelog.md`

### Features Added
- **Production Dependencies**: Added `prometheus-fastapi-instrumentator`, `aiosmtplib`, `apscheduler`, `gunicorn`, and `alembic` to `requirements.txt`.
- **Alembic Migrations**: Initialized Alembic and generated the initial schema baseline migration (`81c3e3d55b90_initial_baseline.py`).
- **Background Jobs**: Integrated `APScheduler` in `app/core/scheduler.py` to run `cleanup_temporary_files` daily at midnight. Start and shutdown hooks added to FastAPI lifespan.
- **Monitoring & Metrics**: Integrated `prometheus-fastapi-instrumentator` in `app/main.py` to expose `/metrics` for Prometheus scraping.
- **Email Service**: Added `email_service.py` with `aiosmtplib` to send asynchronous HTML emails (configurable via environment variables).
- **Dockerization**: Created multi-service Docker configuration (`Dockerfile`, `.dockerignore`, `docker-compose.yml`, `nginx/default.conf`, `prometheus.yml`) for API, Nginx reverse proxy, and Prometheus.
- **CI/CD Pipeline**: Added GitHub Actions workflow (`.github/workflows/ci.yml`) to automatically run linting (`ruff`, `black`, `isort`, `bandit`, `mypy`), execute tests (`pytest --cov`), and build the Docker image on push/PR to main.
- **Code Formatting & Linting**: Ran `black`, `isort`, `ruff` across `backend/app` fixing formatting and import order.

### Bug Fixes
- None


## [Phase 9 System Administration, Settings, Audit Logs & Notifications] - 2026-07-23

### Version
`v0.9.0-alpha.1`

### Files Created
- `backend/app/models/setting.py`
- `backend/app/models/audit.py`
- `backend/app/models/notification.py`
- `backend/app/schemas/setting.py`
- `backend/app/schemas/audit.py`
- `backend/app/schemas/notification.py`
- `backend/app/schemas/system.py`
- `backend/app/repositories/setting_repository.py`
- `backend/app/repositories/audit_repository.py`
- `backend/app/repositories/notification_repository.py`
- `backend/app/services/settings_service.py`
- `backend/app/services/audit_service.py`
- `backend/app/services/notification_service.py`
- `backend/app/api/v1/admin_settings.py`
- `backend/app/api/v1/admin_audit.py`
- `backend/app/api/v1/admin_notifications.py`
- `backend/app/api/v1/admin_system.py`
- `backend/app/api/v1/student_notifications.py`
- `backend/tests/test_settings.py`
- `backend/tests/test_audit.py`
- `backend/tests/test_notifications.py`
- `backend/tests/test_system.py`

### Files Modified
- `backend/app/models/__init__.py`
- `backend/app/models/enums.py`
- `backend/app/schemas/__init__.py`
- `backend/app/repositories/__init__.py`
- `backend/app/services/__init__.py`
- `backend/app/api/v1/router.py`
- `backend/app/main.py`
- `backend/app/services/auth_service.py`
- `backend/app/services/finance_service.py`
- `backend/app/services/inventory_service.py`
- `backend/app/services/order_service.py`
- `backend/app/services/storage_service.py`
- `docs/Changelog.md`

### Features Added
- **Settings Engine**: Implemented `ApplicationSetting` model to store configurable values (e.g. print rates, bind rate, maintenance mode). Supports type-safe retrieval via `SettingsService`.
- **Audit Engine**: Created `AuditLog` model to track state changes. Hooked into Auth, Finance, Inventory, Orders, Storage to record all critical actions.
- **Notification Engine**: Developed `Notification` model and service to push alerts (e.g., Low Stock, Order Ready). Added APIs for Admins and Students to list and dismiss notifications.
- **System APIs**: Added endpoints for system health (`/api/v1/admin/system/health`) and SQLite DB backup logic.
- **Maintenance Mode Middleware**: Blocks non-admin requests when `maintenance_mode` setting is enabled.
- **Automated Test Suite**: Added tests for settings, audit logs, notifications, and system APIs, bringing the total to 106 backend tests passing.

### Bug Fixes
- Handled `AttributeError` on `InventoryItem.min_threshold` during low stock checks.
- Fixed `PaginatedResponse` schema implementation for notification and audit APIs to properly map `page`, `size`, `pages` variables.
- Replaced `JSONB` with `JSON` column types for generic SQLite compatibility.

---

## [Phase 8 Admin Dashboard, Analytics & Reporting Engine] - 2026-07-23

### Version
`v0.8.0-alpha.1`

### Files Created
- `backend/app/schemas/dashboard.py`
- `backend/app/schemas/analytics.py`
- `backend/app/schemas/reports.py`
- `backend/app/repositories/dashboard_repository.py`
- `backend/app/repositories/analytics_repository.py`
- `backend/app/repositories/report_repository.py`
- `backend/app/services/dashboard_service.py`
- `backend/app/services/analytics_service.py`
- `backend/app/services/reporting_service.py`
- `backend/app/api/v1/admin_dashboard.py`
- `backend/app/api/v1/admin_analytics.py`
- `backend/app/api/v1/admin_reports.py`
- `backend/app/api/v1/admin_export.py`
- `backend/tests/test_analytics.py`
- `backend/tests/test_reports.py`

### Files Modified
- `backend/app/api/v1/router.py`
- `backend/app/services/auth_service.py`
- `backend/app/services/order_service.py`
- `backend/app/services/finance_service.py`
- `backend/app/services/inventory_service.py`
- `backend/tests/conftest.py`

### Features Added
- **Admin Dashboard API**: Aggregated real-time metrics with 60-second TTL cache (`cachetools`). Returns pending orders, today's revenue, active students, etc.
- **Analytics API**: Historical and aggregated analytics for daily revenue, monthly revenue, order statuses, top departments, etc.
- **Reporting API**: CSV, Excel, and PDF exports for orders, payments, expenses, and inventory data using `openpyxl` and `fpdf2`.
- **Automated Test Suite**: Added 22 tests in `test_analytics.py` and `test_reports.py`. Total backend test count: 96 passed out of 96.
- **Bug Fixes**: Corrected field mappings in `ReportRepository` and `AnalyticsRepository` referencing `Student.full_name` and `InventoryItem.item_name`.

---

## [Phase 6 Payment Engine & Cash Management] - 2026-07-23

### Version
`v0.6.0-alpha.1`

### Files Created
- `backend/app/models/payment.py`
- `backend/app/models/expense.py`
- `backend/app/models/ledger_entry.py`
- `backend/app/schemas/payment.py`
- `backend/app/repositories/payment_repository.py`
- `backend/app/repositories/expense_repository.py`
- `backend/app/repositories/ledger_repository.py`
- `backend/app/services/finance_service.py`
- `backend/app/api/v1/payments.py`
- `backend/app/api/v1/expenses.py`
- `backend/tests/test_finance.py`

### Files Modified
- `backend/app/models/__init__.py`
- `backend/app/schemas/__init__.py`
- `backend/app/repositories/__init__.py`
- `backend/app/services/__init__.py`
- `backend/app/api/v1/router.py`
- `docs/Changelog.md`

### Features Added
- **Finance Models**: SQLAlchemy 2.x ORM models for `Payment`, `Expense`, and `LedgerEntry`. 
- **Finance Repositories**: Immutable append-only `LedgerRepository`, `PaymentRepository` enforcing unique order constraints, and `ExpenseRepository` for paginated expenses.
- **Finance Service**: `FinanceService` implementing robust transaction-protected payment verification with pessimistic locking (`FOR UPDATE`), duplicate prevention, automated transition of `Order` states to `PAID`, cash/UPI tracking, and real-time financial balance aggregation.
- **API Routes**:
  - `POST /api/v1/payments/verify` (Admin-only payment verification)
  - `GET /api/v1/payments/balance` (Admin-only current balance)
  - `GET /api/v1/payments/summary` (Admin-only financial summary)
  - `GET /api/v1/payments/ledger` (Admin-only paginated ledger)
  - `GET /api/v1/payments/{order_id}` (Admin-only payment details)
  - `POST /api/v1/expenses` (Admin-only expense creation with ledger integration)
  - `GET /api/v1/expenses` (Admin-only paginated expenses)
- **Automated Test Suite**: Added 25 tests covering Payment, Expense, Ledger models, repository logic, Finance Service validations, locking, duplicates, state checks, cash balance reduction on expenses, and API enforcement. Total backend test count: 68 passed out of 68.

### Bug Fixes
- Fixed test fixture issues with `PricingSetting` keyword arguments and JWT token payload dictionaries to match existing definitions.

---

## [Phase 5 Order Management Engine] - 2026-07-23

### Version
`v0.5.0-alpha.1`

### Files Created
- `backend/app/models/pickup_code.py`
- `backend/app/models/pricing_setting.py`
- `backend/app/models/order_status_history.py`
- `backend/app/repositories/order_repository.py`
- `backend/app/services/pricing_service.py`
- `backend/app/services/order_service.py`
- `backend/app/schemas/order.py`
- `backend/app/api/v1/orders.py`
- `backend/app/api/v1/admin_orders.py`
- `backend/tests/test_orders.py`

### Files Modified
- `backend/app/models/order.py`
- `backend/app/models/file.py`
- `backend/app/models/__init__.py`
- `backend/app/schemas/__init__.py`
- `backend/app/repositories/__init__.py`
- `backend/app/services/__init__.py`
- `backend/app/api/v1/router.py`
- `docs/Changelog.md`

### Features Added
- **Order Engine Models**: Implemented SQLAlchemy 2.x ORM models for `Order`, `PickupCode`, `PricingSetting`, and `OrderStatusHistory` matching `docs/Database.md`.
- **Order Repository Layer**: `OrderRepository` providing database methods for order creation, retrieval, student order history listing, admin search/filtering/pagination, and status transition logging.
- **Pricing Engine Service**: `PricingService` computing print job costs using per page rates (single side, double side, multi-page, color), binding rates (spiral, soft cover, hard cover, staple pins), color orientation constraint checks (`COLOR` mode requires `SINGLE_SIDE`), copy limits (1..100), bankers' rounding (`ROUND_HALF_EVEN`), and frozen price snapshotting upon submission.
- **Order Service & State Machine**: `OrderService` implementing student order submission (validating uploaded file ownership and 1..5 file limits), display ID generation (`CC-2026-XXXX`), 6-character uppercase alphanumeric pickup code generation (`PICKUP_CODE_CHARS`), and strict forward-only state machine validation (`PENDING_PAYMENT` -> `PAID` -> `PRINTING` -> `READY_FOR_PICKUP` -> `COMPLETED`).
- **State Machine Protection**: Rejects backward transitions, skipped states, and duplicate state updates by raising `ConflictError` (HTTP 409 Conflict).
- **Order API Routes**:
  - `POST /api/v1/orders` (Student order creation, rate-limited to 10/hour)
  - `GET /api/v1/orders` (Student order history with pagination)
  - `GET /api/v1/orders/{id}` (Order details with student ownership validation and admin override)
  - `PATCH /api/v1/orders/{id}/status` (Admin order status advancement enforcing state machine)
  - `GET /api/v1/admin/orders` (Admin order listing supporting search, status filter, department filter, date range filter, and pagination)
- **Automated Test Suite**: Added 12 order tests in `backend/tests/test_orders.py` covering pricing calculations, color rules, bankers' rounding, price snapshot immutability, state machine transitions, 409 conflict handling, student security, and admin search/filtering. Total backend test count: 43 passed out of 43.

### Bug Fixes
- Added `BigInteger().with_variant(Integer, "sqlite")` to autoincrement primary keys for SQLite in-memory test compatibility.

---

## [Phase 4 Storage & File Upload Engine] - 2026-07-23

### Version
`v0.4.0-alpha.1`

### Files Created
- `backend/app/models/file.py`
- `backend/app/models/order.py`
- `backend/app/schemas/file.py`
- `backend/app/repositories/file_repository.py`
- `backend/app/services/storage_service.py`
- `backend/app/api/v1/files.py`
- `backend/app/tasks/cleanup.py`
- `backend/app/tasks/__init__.py`
- `backend/tests/test_storage.py`

### Files Modified
- `backend/app/models/__init__.py`
- `backend/app/schemas/__init__.py`
- `backend/app/repositories/__init__.py`
- `backend/app/services/__init__.py`
- `backend/app/api/v1/router.py`
- `docs/Changelog.md`

### Features Added
- **OrderFile ORM Model & FileStatusEnum**: SQLAlchemy 2.x `OrderFile` model mapping to `order_files` table with `status` enum (`TEMPORARY`, `ATTACHED`, `ORPHANED`, `DELETED`), UUID keys, size validation, and timestamp fields.
- **File Repository Layer**: `FileRepository` providing database access methods for file creation, lookup by ID/path, student/order listing, status updates, and temporary file expiration queries.
- **Storage Service & Validation Engine**: `StorageService` enforcing extension whitelist (`.pdf`, `.doc`, `.docx`, `.ppt`, `.pptx`), max 200MB file size limit, python-magic binary header inspection (blocking renamed executables), UUID storage pathing (`temp/{student_id}/{uuid}.{ext}`), and chunked streaming uploads.
- **Supabase Private Storage Integration**: Integrated with Supabase Storage private bucket `order-files`.
- **Signed URL Generator**: Generates 1-hour time-limited signed URLs (`SIGNED_URL_EXPIRY = 3600`) with support for `inline` document viewer and `attachment` disposition headers.
- **File Management API Routes**:
  - `POST /api/v1/files/upload` (Multipart file upload, rate-limited to 20/hour)
  - `GET /api/v1/files/{id}` (File metadata retrieval with owner/admin security checks)
  - `GET /api/v1/files/{id}/download` (1-hour Signed URL generator with owner/admin security checks)
  - `DELETE /api/v1/files/{id}` (Atomic deletion of DB metadata and Supabase storage object)
- **Background Cleanup Task**: `run_temporary_file_cleanup` task purging temporary uploads older than 24 hours.
- **Automated Test Suite**: Added 10 storage tests in `backend/tests/test_storage.py` covering validation, magic-bytes checks, repository CRUD, signed URLs, owner security, API endpoints, and cleanup tasks. Total backend test count: 31 passed out of 31.

### Bug Fixes
- Added `libmagic` fallback detection in `StorageService` for systems lacking C libmagic libraries.

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

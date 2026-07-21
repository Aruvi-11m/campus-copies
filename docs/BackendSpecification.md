# Campus Copies — Backend Architecture Specification

| Field          | Value                                            |
| -------------- | ------------------------------------------------ |
| Document Title | Backend Architecture Specification               |
| Project Name   | Campus Copies                                    |
| Version        | 1.0.0-draft                                      |
| Status         | Awaiting Stakeholder Approval                    |
| Author         | Senior Backend Engineer & Principal Architect    |
| Created        | 2026-07-21                                       |
| Last Updated   | 2026-07-21                                       |
| References     | SRS.md v1.0.0, TechnologyStack.md v1.0.0 (Frozen), Architecture.md v2.0.0, DatabaseRelationships.md v1.0.0, Database.md v1.0.0, API.md v1.0.0, BusinessRules.md v1.0.0 |

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Application Startup & Lifecycle](#2-application-startup--lifecycle)
3. [Authentication & Authorization Module](#3-authentication--authorization-module)
4. [Service Layer Architecture](#4-service-layer-architecture)
5. [Repository & Data Access Layer](#5-repository--data-access-layer)
6. [Validation Layer](#6-validation-layer)
7. [Storage Layer Integration](#7-storage-layer-integration)
8. [Notification & Real-Time SSE Layer](#8-notification--real-time-sse-layer)
9. [Logging & Auditing Architecture](#9-logging--auditing-architecture)
10. [Background & Scheduled Tasks](#10-background--scheduled-tasks)
11. [Configuration & Environment Management](#11-configuration--environment-management)
12. [Global Error Handling Strategy](#12-global-error-handling-strategy)
13. [Testing Strategy](#13-testing-strategy)
14. [Future Expansion Architecture](#14-future-expansion-architecture)
15. [Backend Architectural Self-Review](#15-backend-architectural-self-review)

---

## 1. Project Structure

The backend application strictly adheres to a modular, layered clean-architecture design layout within Python 3.13+ and FastAPI:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app assembly & ASGI entrypoint
│   ├── config.py                   # Pydantic BaseSettings environment config
│   ├── database.py                 # SQLAlchemy 2.x engine & session management
│   ├── dependencies.py             # Global FastAPI dependency injection providers
│   │
│   ├── core/                       # Cross-cutting system modules
│   │   ├── __init__.py
│   │   ├── security.py             # PyJWT, pwdlib (bcrypt) password hashing
│   │   ├── middleware.py           # CORS, rate-limiting, structlog access logging
│   │   ├── errors.py               # Exception definitions & global handlers
│   │   └── logging.py              # structlog configuration & log processors
│   │
│   ├── db/                         # Database base definitions & migrations setup
│   │   ├── __init__.py
│   │   └── base_class.py           # SQLAlchemy DeclarativeBase class
│   │
│   ├── models/                     # SQLAlchemy 2.x ORM domain models
│   │   ├── __init__.py
│   │   ├── student.py              # Student ORM mapping
│   │   ├── admin.py                # Admin ORM mapping
│   │   ├── order.py                # Order ORM mapping
│   │   ├── file.py                 # OrderFile ORM mapping
│   │   ├── payment.py              # Payment ORM mapping
│   │   ├── pickup_code.py          # PickupCode ORM mapping
│   │   ├── inventory.py            # InventoryItem & Transaction mappings
│   │   ├── expense.py              # Expense ORM mapping
│   │   ├── profit_log.py           # ProfitLog ORM mapping
│   │   ├── audit_log.py            # AuditLog ORM mapping
│   │   ├── notification.py         # Notification ORM mapping
│   │   ├── setting.py              # Application & Pricing settings mappings
│   │   ├── status_history.py       # OrderStatusHistory ORM mapping
│   │   └── session.py              # Session ORM mapping
│   │
│   ├── schemas/                    # Pydantic v2 request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py                 # Login, Token & Credential schemas
│   │   ├── student.py              # Student request/response schemas
│   │   ├── order.py                # Order creation, status & detail schemas
│   │   ├── file.py                 # File upload & metadata schemas
│   │   ├── payment.py              # Payment verification schemas
│   │   ├── inventory.py            # Inventory item & transaction schemas
│   │   ├── expense.py              # Expense request schemas
│   │   ├── report.py               # Aggregated report envelope schemas
│   │   └── setting.py              # Pricing & App settings schemas
│   │
│   ├── repositories/               # Data access abstraction layer
│   │   ├── __init__.py
│   │   ├── base_repository.py      # Generic CRUD repository pattern
│   │   ├── student_repository.py   # Student DB queries
│   │   ├── admin_repository.py     # Admin DB queries
│   │   ├── order_repository.py     # Order & Status history DB queries
│   │   ├── file_repository.py      # OrderFile DB queries
│   │   ├── payment_repository.py   # Payment DB queries
│   │   ├── inventory_repository.py# Stock catalog & transaction DB queries
│   │   ├── expense_repository.py  # Expense DB queries
│   │   ├── report_repository.py   # Complex reporting aggregation SQL queries
│   │   └── audit_repository.py    # Audit log DB queries
│   │
│   ├── services/                   # Core business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py        # Registration, login & token validation
│   │   ├── order_service.py       # Order submission & lifecycle transitions
│   │   ├── pricing_service.py     # Price calculation & snapshotting
│   │   ├── payment_service.py     # Payment verification & cash balance updates
│   │   ├── inventory_service.py   # Stock allocation & threshold checking
│   │   ├── storage_service.py     # Supabase Storage client integration
│   │   ├── notification_service.py# SSE event queues & broadcast manager
│   │   ├── report_service.py      # Business report generation & ledger aggregation
│   │   ├── settings_service.py    # In-memory settings cache & persistence
│   │   └── audit_service.py       # Audit trail recording
│   │
│   ├── api/                        # API Route Handlers (v1)
│   │   ├── __init__.py
│   │   ├── router.py               # Master APIRouter registry
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py             # Auth endpoints
│   │       ├── students.py         # Student endpoints
│   │       ├── admins.py           # Admin management endpoints
│   │       ├── orders.py           # Order endpoints
│   │       ├── files.py            # File upload & signed URL endpoints
│   │       ├── payments.py         # Payment endpoints
│   │       ├── inventory.py        # Inventory endpoints
│   │       ├── expenses.py         # Expense endpoints
│   │       ├── reports.py          # Report endpoints
│   │       ├── settings.py         # Settings endpoints
│   │       └── notifications.py    # SSE stream & notification endpoints
│   │
│   └── tasks/                      # Background scheduled jobs
│       ├── __init__.py
│       ├── cleanup_tasks.py        # Garbage collection for temp files & stale sessions
│       └── scheduler.py            # Asyncio background task scheduler
│
├── alembic/                        # Database migration scripts
│   ├── env.py                      # Alembic env setup
│   └── versions/                   # Migration version files
├── pyproject.toml                  # Python 3.13 project specification & dependencies
├── requirements.txt                # Pinned production requirements
└── Dockerfile                      # Container definition for Render platform
```

### 1.1 Responsibilities of Key Directories
- **`app/main.py`**: Instantiates FastAPI app, registers lifespan events, CORS/rate-limit middleware, global exception handlers, and API routers.
- **`app/config.py`**: Loads and validates environment variables into typed `pydantic-settings` BaseSettings objects.
- **`app/database.py`**: Initializes SQLAlchemy 2.x engine (`DATABASE_URL` via PgBouncer or `DATABASE_URL_DIRECT`) using `NullPool` for transaction mode pooling.
- **`app/core/`**: Implements framework-agnostic cross-cutting concerns: security helpers (JWT signing, bcrypt verification), custom exceptions, and structured logging setup.
- **`app/models/`**: Maps PostgreSQL database tables to Python classes via SQLAlchemy 2.x `DeclarativeBase`.
- **`app/schemas/`**: Pydantic v2 schemas defining exact API request inputs and JSON response contracts.
- **`app/repositories/`**: Handles database query execution, filtering, joins, and transactions. Decouples DB operations from business logic.
- **`app/services/`**: Encapsulates all domain business rules defined in [BusinessRules.md](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/BusinessRules.md).
- **`app/api/v1/`**: FastAPI route controllers validating HTTP inputs, invoking services, and returning structured Pydantic responses.

---

## 2. Application Startup & Lifecycle

### 2.1 Configuration Loading
- Environment variables are loaded via `pydantic-settings` (`Settings` instance).
- Configuration validates required keys (`DATABASE_URL`, `JWT_SECRET`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`) on app startup; missing keys abort startup immediately (`SystemExit`).

### 2.2 Database Initialization
- SQLAlchemy `create_engine` connects to PostgreSQL.
- For application runtime via Supabase PgBouncer (Transaction Mode), the engine uses `poolclass=NullPool` and `pool_pre_ping=True`.
- For migrations (Alembic), `DATABASE_URL_DIRECT` connects directly to port 5432.

### 2.3 Supabase Storage Initialization
- `StorageService` initializes the `supabase-py` SDK client using `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`.
- Verifies connectivity to the private `order-files` bucket on startup.

### 2.4 Lifespan Events (`asynccontextmanager`)
- **Startup Phase**:
  1. Initialize structured logger (`structlog`).
  2. Test database connection (`SELECT 1`).
  3. Load initial settings into `SettingsService` in-memory cache.
  4. Launch background scheduler for temporary file cleanup and expired session purging.
- **Shutdown Phase**:
  1. Cancel background scheduled tasks gracefully.
  2. Close active SSE streams and notify connected clients.
  3. Dispose of SQLAlchemy database engine connections.

---

## 3. Authentication & Authorization Module

### 3.1 Authentication Pipeline
- **Student Authentication**:
  - Request: Name, 10-digit Indian Mobile (`^[6-9][0-9]{9}$`), Department.
  - Handler: `AuthService.authenticate_student()`.
  - Logic: Finds or creates student record; generates JWT token containing `{ sub: student_id, mobile, role: "student" }`.
- **Admin Authentication**:
  - Request: Username, Plaintext Password.
  - Handler: `AuthService.authenticate_admin()`.
  - Logic: Fetches admin by username (`is_active = TRUE`); verifies password using `pwdlib` (bcrypt); generates JWT token containing `{ sub: admin_id, username, role: "admin" }`.

### 3.2 Password Hashing
- Handled by `pwdlib` (`PasswordHash.recommended()`) using `bcrypt` (12 salt rounds).
- Plaintext passwords are never logged, cached, or saved in storage.

### 3.3 Authorization & Dependency Injection
- FastAPI route authorization enforced via reusable `Depends()`:
  - `get_current_user`: Extracts JWT from `Authorization: Bearer <token>` or `?token=<token>` (SSE stream).
  - `require_student`: Asserts JWT `role == "student"`.
  - `require_admin`: Asserts JWT `role == "admin"`.

---

## 4. Service Layer Architecture

Every business service encapsulates explicit domain rules defined in [BusinessRules.md](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/BusinessRules.md):

| Service Name | Primary Responsibilities |
|--------------|--------------------------|
| **`AuthService`** | Handles student auto-registration, admin login, bcrypt password checks, and JWT token issuance. |
| **`OrderService`**| Manages order submission, status state machine validation (`PENDING_PAYMENT` → `PAID` → `PRINTING` → `READY_FOR_PICKUP` → `COMPLETED`), and 6-digit pickup code verification. |
| **`PricingService`**| Calculates print prices ($\text{pages} \times \text{rate} \times \text{copies} + \text{binding}$), enforces Color Single-Side restriction, and snapshots pricing into order records. |
| **`PaymentService`**| Verifies payments, records monetary ledgers, updates `cash_in_hand` for cash transactions, and prevents duplicate payment marking. |
| **`InventoryService`**| Deducts consumable stock upon order completion, processes manual restocks/adjustments, and raises low-stock alerts (`current_stock < min_threshold`). |
| **`StorageService`**| Handles chunked upload streams to Supabase Storage, generates 1-hour signed URLs with proper inline/attachment disposition headers, and moves temp files to order paths. |
| **`NotificationService`**| Manages active in-memory SSE connections (`dict[str, asyncio.Queue]`), broadcasts `new_order` events, and records notification rows. |
| **`ReportService`**| Executes complex aggregate queries to produce Daily, Weekly, Monthly, and Yearly reports (Revenue, Expenses, Net Profit, Cash balance, Department breakdown). |
| **`SettingsService`**| Maintains in-memory key-value settings dictionary with 60-second max TTL fallback for eventual consistency. |
| **`AuditService`**| Inserts immutable entries into `audit_logs` capturing actor, action, resource ID, and JSON diffs. |

---

## 5. Repository & Data Access Layer

### 5.1 Repository Pattern
- All database queries are isolated inside repository classes (`OrderRepository`, `StudentRepository`, etc.).
- Repositories accept an active SQLAlchemy `Session` object passed via FastAPI dependency injection.

### 5.2 Transaction & Rollback Strategy
- Service methods manage transaction boundaries explicitly using `session.begin()` or atomic blocks.
- If any operation fails (e.g., file move failure or stock deduction error), `session.rollback()` is executed immediately, guaranteeing zero partial writes.

---

## 6. Validation Layer

### 6.1 Input Validation (Pydantic v2)
- All request parameters, headers, and request bodies are validated against Pydantic schemas before reaching route handlers.
- Schema failures instantly return standard `422 Unprocessable Entity` responses detailing field errors.

### 6.2 Business & File Validation
- `python-magic` inspects binary headers (magic bytes) to confirm file types match whitelist (`PDF`, `DOC`, `DOCX`, `PPT`, `PPTX`).
- File size is checked against 200 MB limit (209,715,200 bytes).
- Print config constraints (e.g., `color_mode = 'COLOR'` requiring `print_side = 'SINGLE_SIDE'`) are enforced by Pydantic model validators.

---

## 7. Storage Layer Integration

- **Provider**: Supabase Storage via `supabase-py` SDK.
- **Bucket**: `order-files` (Private bucket).
- **Upload Stream**: Files > 1 MB are uploaded in chunked memory buffers directly to Supabase to prevent container `/tmp` disk fill.
- **Signed URLs**: Generated with 1-hour expiration. PDF files set `responseDisposition = inline`; DOCX/PPTX files set `responseDisposition = attachment`.
- **Path Migration**: Order submission copies objects from `temp/{session_id}/` to `orders/{order_id}/` and deletes the temp object within a single service transaction.

---

## 8. Notification & Real-Time SSE Layer

- **Framework**: `sse-starlette` `EventSourceResponse`.
- **Endpoint**: `GET /api/v1/notifications/stream?token=<jwt>`.
- **Connection Registry**: In-memory dictionary `connections: dict[str, asyncio.Queue]` mapping `admin_id` to an asyncio queue.
- **Keepalive**: Pings sent every 30 seconds to prevent Render proxy timeouts.
- **Future Redis Roadmap**: Replace in-memory `dict` with Redis Pub/Sub channel (`orders:notifications`) when scaling to multiple backend workers.

---

## 9. Logging & Auditing Architecture

### 9.1 Application Logging (`structlog`)
- Structured JSON log format in production (`stdout`).
- Configured with contextual processors: `timestamp`, `log_level`, `request_id`, `user_id`.
- Access logs mask `token` query parameters to prevent JWT leakage.

### 9.2 Audit Log Recording (`AuditService`)
- Every domain mutation (status change, payment verification, stock update, setting edit) calls `AuditService.log()`.
- Records inserted into `audit_logs` containing `actor_id`, `actor_type`, `action`, `resource_type`, `resource_id`, `old_value`, `new_value`, `ip_address`, `metadata`.

---

## 10. Background & Scheduled Tasks

- Executed via `asyncio` background tasks initialized during app startup:
  1. **Temp File Cleanup Task**: Scans `order_files` every 6 hours for `status = 'TEMPORARY'` records older than 24 hours. Purges Supabase objects and updates DB status to `'DELETED'`.
  2. **Expired Session Cleanup Task**: Purges rows from `sessions` table where `expires_at < NOW() - INTERVAL '30 days'`.
  3. **Notification Cleanup Task**: Deletes read `notifications` older than 14 days.

---

## 11. Configuration & Environment Management

Managed via `pydantic-settings` with zero hardcoded values:

| Env Variable | Purpose | Security Level |
|--------------|---------|----------------|
| `DATABASE_URL` | Application DB connection string (PgBouncer port 6543) | **Secret** (Server-only) |
| `DATABASE_URL_DIRECT` | Alembic migration connection string (Direct port 5432) | **Secret** (Server-only) |
| `SUPABASE_URL` | Supabase API endpoint | Public/Server |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Service Role Key | **Secret** (Server-only, bypasses RLS) |
| `JWT_SECRET` | Secret key for signing JWTs | **Secret** (Server-only) |
| `ADMIN_SETUP_KEY` | One-time key for initial admin bootstrap | **Secret** (Server-only) |
| `CORS_ORIGINS` | Allowed frontend domains (Vercel) | Configuration |
| `ENVIRONMENT` | Runtime mode (`development` or `production`) | Configuration |

---

## 12. Global Error Handling Strategy

FastAPI custom exception handlers format all errors into a standard JSON response structure:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_STATUS_TRANSITION",
    "message": "Cannot transition order status from PENDING_PAYMENT to PRINTING. Must transition to PAID first.",
    "details": null
  }
}
```

### Custom Exception Mapping
- `AppException` (Base exception class)
  - `EntityNotFoundError` → `HTTP 404 Not Found`
  - `AuthenticationError` → `HTTP 401 Unauthorized`
  - `PermissionDeniedError` → `HTTP 403 Forbidden`
  - `InvalidStatusTransitionError` → `HTTP 409 Conflict`
  - `LimitExceededError` → `HTTP 409 Conflict`
  - `StorageServiceError` → `HTTP 503 Service Unavailable`
  - `DatabaseServiceError` → `HTTP 503 Service Unavailable`

---

## 13. Testing Strategy

- **Test Framework**: `pytest` + `pytest-asyncio` + `httpx`.
- **Unit Tests**: Test core domain logic (`PricingService`, `OrderService` state transitions, Pydantic schemas) in isolation with mock repositories.
- **Integration Tests**: Test repository query execution and Supabase Storage integration using isolated test databases.
- **API End-to-End Tests**: Test full FastAPI endpoint lifecycle from HTTP request payload to DB insertion and JSON response envelope.

---

## 14. Future Expansion Architecture

- **Printer Agent API**: Dedicated endpoint `GET /api/v1/agent/jobs` authenticated via API Key.
- **WhatsApp Webhook Integration**: Asynchronous status updates sent to student WhatsApp via background task queues.
- **Redis Integration**: Seamless upgrade path for SSE connections, shared settings cache, and distributed rate limiting across horizontal workers.

---

## 15. Backend Architectural Self-Review

| Criteria | Verification Status | Resolution Details |
|---|---|---|
| **Layer Isolation?** | Verified | Clean separation: Routes → Services → Repositories → Models. |
| **No Circular Imports?** | Verified | Dependency flow strictly downstream; interfaces passed via dependency injection. |
| **Security Controls?** | Verified | JWT verification, bcrypt hashing, secret protection, CORS, structlog URL parameter redacting. |
| **Data Consistency?** | Verified | Atomic transactions with automatic rollback on error. |
| **Memory & Storage Safety?** | Verified | Chunked file uploads avoid container `/tmp` disk fill; 60s settings cache TTL prevents worker stale state. |

---

*End of Backend Architecture Specification — Version 1.0.0-draft*

*This document is awaiting stakeholder review and approval before proceeding to implementation.*

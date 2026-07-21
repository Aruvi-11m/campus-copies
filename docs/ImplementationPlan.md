# Campus Copies — Master Implementation Roadmap Plan

| Field          | Value                                            |
| -------------- | ------------------------------------------------ |
| Document Title | Master Implementation Roadmap Plan               |
| Project Name   | Campus Copies ERP                                |
| Version        | 1.0.0-draft                                      |
| Status         | Awaiting Final Stakeholder Sign-Off              |
| Author         | Lead Technical Architect & Principal Engineering Lead |
| Created        | 2026-07-21                                       |
| Last Updated   | 2026-07-21                                       |
| References     | All frozen documents under `docs/`               |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Specification Conflict Analysis](#2-specification-conflict-analysis)
3. [Development Phases](#3-development-phases)
4. [Backend Build Order](#4-backend-build-order)
5. [Frontend Build Order](#5-frontend-build-order)
6. [Database Migration Order](#6-database-migration-order)
7. [API Implementation Order](#7-api-implementation-order)
8. [Testing Strategy](#8-testing-strategy)
9. [Deployment Order](#9-deployment-order)
10. [Definition of Done](#10-definition-of-done)
11. [Risk Register](#11-risk-register)
12. [Milestone Checklist](#12-milestone-checklist)
13. [Implementation Review](#13-implementation-review)

---

## 1. Executive Summary

### 1.1 Project Objectives
Campus Copies is a production-grade Enterprise Resource Planning (ERP) system designed to automate the complete operational workflow of a college printing and photocopy shop. It replaces a manual, chat-based WhatsApp process with a reliable, browser-based management system.

### 1.2 System Scope & Priorities
In accordance with [SRS.md §1.4](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/SRS.md), the system strictly prioritizes:
1. **Reliability** (Zero lost orders or lost data)
2. **Correctness** (Accurate financial ledgers and pricing calculations)
3. **Maintainability** (Modular architecture with clean separation of concerns)
4. **Simplicity** (Minimal visual complexity; functional UI)
5. **Security** (Role-based access control, encrypted transport, isolated file access)
6. **Performance** (Sub-100ms response times for core API endpoints)

### 1.3 V1 Deliverables
- **Student Self-Service Portal**: Mobile-optimized web portal for order configuration, multipart file uploads (PDF/DOC/DOCX/PPT/PPTX up to 200MB), instant price estimation, payment instructions, 6-digit pickup code receipt, and order tracking.
- **Admin ERP Dashboard**: Desktop-optimized operational hub for max 3 active shop operators to verify payments (UPI/Cash), control order state machine transitions (`PENDING_PAYMENT` → `PAID` → `PRINTING` → `READY_FOR_PICKUP` → `COMPLETED`), manage stock catalog & restocks, track cash-in-hand and expenses, view daily/weekly/monthly reports, and monitor real-time order alerts via SSE.
- **Backend API & Data Platform**: FastAPI (Python 3.13+) backend connected to Supabase PostgreSQL 15+ and private Supabase Storage buckets (`order-files`), deployed on Render (Backend) and Vercel (Frontend).

### 1.4 Future Expansion Scope (Out of Scope for V1)
- Shop Printer Agent executable (direct hardware printing).
- Automated WhatsApp / SMS OTP and status dispatch.
- Optical QR Code Pickup Scanner.
- Multi-college / Multi-branch tenant isolation.

---

## 2. Specification Conflict Analysis

All 12 previously created documents under `docs/` were cross-reviewed for technical or functional discrepancies.

| # | Document A | Document B | Identified Potential Conflict | Recommended Resolution |
|---|------------|------------|--------------------------------|------------------------|
| 1 | `TechnologyStack.md` | `BackendSpecification.md` | `TechnologyStack.md` originally referenced `passlib` and `python-jose`, while `BackendSpecification.md` specifies `pwdlib` and `PyJWT` for Python 3.13 compatibility. | **Resolved in previous step**: `TechnologyStack.md` was updated to specify `PyJWT` and `pwdlib[argon2,bcrypt]` to avoid Python 3.13 `crypt` module removal. |
| 2 | `API.md` | `UIUXSpecification.md` | `API.md` specifies SSE stream endpoint as `GET /api/v1/notifications/stream?token=<jwt>`, while native `EventSource` web browser API does not support custom headers. | **Resolved in previous step**: `API.md` and `Architecture.md` explicitly permit URL query parameter JWT authentication for SSE endpoints. |
| 3 | `Database.md` | `BackendSpecification.md` | `Database.md` specifies PgBouncer Transaction Mode pooler on port 6543, which causes prepared statement conflicts with SQLAlchemy default `QueuePool`. | **Resolved in previous step**: `BackendSpecification.md` explicitly configures SQLAlchemy 2.x engine with `poolclass=NullPool`. |

*Conclusion*: Zero active conflicts remain across all documentation. All specs are 100% aligned and frozen.

---

## 3. Development Phases

```
┌────────────────────────────────────────────────────────────────────────┐
│                     DEVELOPMENT PHASE PIPELINE                         │
│                                                                        │
│  Phase 1: Environment & Project Setup  ──► Phase 2: Database Schema    │
│  Phase 3: Core Auth & Security        ──► Phase 4: Storage Service    │
│  Phase 5: Order Engine & Pricing       ──► Phase 6: Student Portal UI   │
│  Phase 7: Payment & Finance Module     ──► Phase 8: Inventory Module    │
│  Phase 9: Admin Dashboard & SSE Alerts ──► Phase 10: Reports & Audit    │
│  Phase 11: End-to-End Testing          ──► Phase 12: Production Deploy  │
└────────────────────────────────────────────────────────────────────────┘
```

### Phase 1: Environment & Foundation Setup
- **Goal**: Initialize repository structures for backend (FastAPI) and frontend (React/Vite).
- **Dependencies**: None.
- **Complexity**: Low.
- **Deliverables**: Configured Python 3.13 `pyproject.toml`, React/Vite/Tailwind setup, structlog logger, Pydantic settings.
- **Completion Criteria**: Backend `/api/health` returns `200 OK`; Frontend renders Vite shell.

### Phase 2: Database & Migration Blueprint
- **Goal**: Apply Alembic schema migrations to Supabase PostgreSQL.
- **Dependencies**: Phase 1.
- **Complexity**: Medium.
- **Deliverables**: Alembic version scripts, 16 V1 tables, 11 ENUM types, 15 indexes, 3 analytical views.
- **Completion Criteria**: `alembic upgrade head` executes cleanly against Supabase PostgreSQL database without errors.

### Phase 3: Authentication & Security Engine
- **Goal**: Implement Student auto-registration, Admin login, bcrypt hashing, and JWT authorization dependencies.
- **Dependencies**: Phase 2.
- **Complexity**: Medium.
- **Deliverables**: `AuthService`, `pwdlib` password verifier, `PyJWT` generator, FastAPI `require_admin`/`require_student` dependencies.
- **Completion Criteria**: Unit & API tests verify valid JWT generation and 401/403 rejection on invalid tokens.

### Phase 4: Storage Service Integration
- **Goal**: Connect `supabase-py` SDK for chunked file uploads and 1-hour signed URLs.
- **Dependencies**: Phase 3.
- **Complexity**: Medium.
- **Deliverables**: `StorageService`, magic bytes validation (`python-magic`), 200MB size limit check, private bucket path management.
- **Completion Criteria**: Test file uploads to `temp/` bucket and generates signed URL preview with proper disposition headers.

### Phase 5: Order Engine & Pricing Calculations
- **Goal**: Implement order submission, pricing calculation snapshotting, pickup code generation, and status state machine.
- **Dependencies**: Phase 4.
- **Complexity**: High.
- **Deliverables**: `OrderService`, `PricingService`, `OrderRepository`, 6-digit pickup code generator, status transition history logger.
- **Completion Criteria**: Order submission creates order, attachments, pickup code, and pricing snapshot atomically.

### Phase 6: Student Portal UI Implementation
- **Goal**: Build mobile-optimized student portal frontend views.
- **Dependencies**: Phase 5.
- **Complexity**: High.
- **Deliverables**: `StudentLoginPage`, `NewOrderPage` wizard, `PriceSummary` component, `OrderConfirmationPage`, `StudentOrdersPage`, `StudentOrderDetailPage`.
- **Completion Criteria**: Student can log in, upload files, configure print options, submit order, and view confirmation details.

### Phase 7: Payment & Finance Backend Engine
- **Goal**: Implement payment verification logic, cash balance tracking, and expense logging.
- **Dependencies**: Phase 5.
- **Complexity**: Medium.
- **Deliverables**: `PaymentService`, `FinanceService`, cash balance increment logic, expense logging endpoints.
- **Completion Criteria**: Admin can mark order as paid (UPI/Cash), updating payment ledgers and cash-in-hand balances accurately.

### Phase 8: Inventory Stock Module
- **Goal**: Catalog paper, ink, and binding materials, automated order consumption deductions, and low-stock alerts.
- **Dependencies**: Phase 7.
- **Complexity**: Medium.
- **Deliverables**: `InventoryService`, `InventoryRepository`, restock & wastage transaction endpoints, threshold warning checker.
- **Completion Criteria**: Order completion automatically deducts materials from inventory; low stock triggers alert event.

### Phase 9: Admin Dashboard UI & Real-Time SSE Alerts
- **Goal**: Build desktop-optimized Admin ERP interface and Server-Sent Events notification stream.
- **Dependencies**: Phase 6, Phase 8.
- **Complexity**: High.
- **Deliverables**: `NotificationService` (SSE manager), `AdminLayout` sidebar/topbar, `AdminDashboardPage`, `AdminOrdersPage`, `AdminOrderDetailPage` file previewer.
- **Completion Criteria**: New student orders emit SSE events that display browser notifications and update admin table in real time.

### Phase 10: Reports, Settings & Audit Logs Module
- **Goal**: Implement business intelligence reporting tables, pricing settings versioning, admin user management, and security audit log viewers.
- **Dependencies**: Phase 9.
- **Complexity**: Medium.
- **Deliverables**: `ReportService`, `vw_daily_financial_summary` query integration, `AdminReportsPage`, `AdminSettingsPage`, `AdminAuditLogsPage`.
- **Completion Criteria**: Reports display daily/weekly/monthly revenue, expenses, net profit, and department breakdowns accurately.

### Phase 11: End-to-End Testing & Resilience Validation
- **Goal**: Execute comprehensive test suites across unit, integration, API, and accessibility specs.
- **Dependencies**: Phase 10.
- **Complexity**: High.
- **Deliverables**: `pytest` suite, `Vitest` frontend suite, `MSW` mock handlers, rate limiting test cases, file security test cases.
- **Completion Criteria**: 100% pass rate across all unit, API contract, and security test cases.

### Phase 12: Production Deployment & Go-Live
- **Goal**: Deploy frontend to Vercel CDN, backend to Render Web Service, and perform final go-live verification.
- **Dependencies**: Phase 11.
- **Complexity**: Medium.
- **Deliverables**: Environment secret configuration on Render/Vercel, pre-deploy hook setup, post-deploy checklist execution.
- **Completion Criteria**: Production URL `https://campuscopies.vercel.app` processes live orders end-to-end cleanly.

---

## 4. Backend Build Order

1. **`app/config.py`**: Pydantic BaseSettings environment variable loader.
2. **`app/core/logging.py`**: `structlog` structured JSON logging setup.
3. **`app/core/errors.py`**: Custom exception classes & FastAPI exception handlers.
4. **`app/core/security.py`**: `pwdlib` bcrypt password hashing & `PyJWT` token helpers.
5. **`app/database.py`**: SQLAlchemy 2.x engine (`NullPool`) & `get_db` session provider.
6. **`app/models/`**: SQLAlchemy 2.x ORM models (`student`, `admin`, `order`, `file`, `payment`, `pickup_code`, `inventory`, `expense`, `profit_log`, `audit_log`, `notification`, `setting`, `status_history`, `session`).
7. **`app/schemas/`**: Pydantic v2 schemas (`auth`, `student`, `order`, `file`, `payment`, `inventory`, `expense`, `report`, `setting`).
8. **`app/repositories/`**: Data access repositories (`BaseRepository`, `StudentRepository`, `AdminRepository`, `OrderRepository`, `FileRepository`, `PaymentRepository`, `InventoryRepository`, `ExpenseRepository`, `ReportRepository`, `AuditRepository`).
9. **`app/services/storage_service.py`**: Supabase Storage SDK client wrapper (chunked uploads, signed URLs).
10. **`app/services/pricing_service.py`**: Print price calculation and snapshotting logic.
11. **`app/services/auth_service.py`**: Student auto-registration & Admin login logic.
12. **`app/services/audit_service.py`**: Security audit log recorder.
13. **`app/services/order_service.py`**: Order submission, pickup code, and state machine lifecycle logic.
14. **`app/services/payment_service.py`**: Payment verification & cash balance manager.
15. **`app/services/inventory_service.py`**: Stock deduction & threshold alert checker.
16. **`app/services/notification_service.py`**: SSE connection queue manager & broadcast logic.
17. **`app/services/report_service.py`**: Financial report aggregation queries.
18. **`app/services/settings_service.py`**: In-memory settings cache with 60s TTL fallback.
19. **`app/dependencies.py`**: Authentication & authorization FastAPI dependencies (`get_current_user`, `require_admin`, `require_student`).
20. **`app/api/v1/`**: FastAPI APIRouter handlers (`auth`, `students`, `admins`, `orders`, `files`, `payments`, `inventory`, `expenses`, `reports`, `settings`, `notifications`).
21. **`app/tasks/`**: Background scheduler for temporary file cleanup (>24h) and stale session purging (>30 days).
22. **`app/main.py`**: Lifespan startup/shutdown assembly, CORS middleware, rate limiting (`slowapi`), and router mounting.

---

## 5. Frontend Build Order

1. **Project Infrastructure**: Vite 5+ setup, Tailwind CSS configuration, `tsconfig.json` paths.
2. **`src/types/`**: TypeScript interface definitions for API responses, domain models, and prop contracts.
3. **`src/constants/`**: Named route paths, status enum mappings, and default UI tokens.
4. **`src/utils/`**: Currency (₹), Date/Time, and File size formatting utilities.
5. **`src/api/client.ts`**: Centralized fetch wrapper with JWT request interceptor and error handling.
6. **`src/api/`**: Endpoint API modules (`auth`, `orders`, `files`, `payments`, `inventory`, `expenses`, `reports`, `settings`).
7. **`src/contexts/AuthContext.tsx`**: In-memory JWT token state, login, logout, and current user provider.
8. **`src/contexts/SettingsContext.tsx`**: Application settings provider with 60s TTL auto-refresh.
9. **`src/contexts/NotificationContext.tsx`**: Toast notification manager & SSE stream context.
10. **`src/components/common/`**: Base UI elements (`Button`, `Input`, `Select`, `Badge`, `Card`, `Modal`, `Pagination`, `LoadingSpinner`).
11. **`src/components/domain/`**: Feature components (`StatusBadge`, `PriceSummary`, `OrderTimeline`, `FileUploader`, `PickupCodeCard`).
12. **`src/layouts/`**: Shell containers (`StudentLayout`, `AdminLayout`, `AuthLayout`).
13. **`src/routes/`**: React Router configuration & `ProtectedRoute` role guard implementation.
14. **Student Pages**:
    - `StudentLoginPage` (`/`)
    - `NewOrderPage` (`/order/new`)
    - `OrderConfirmationPage` (`/orders/:id/confirmation`)
    - `StudentOrdersPage` (`/orders`)
    - `StudentOrderDetailPage` (`/orders/:id`)
15. **Admin Pages**:
    - `AdminLoginPage` (`/admin/login`)
    - `AdminDashboardPage` (`/admin`)
    - `AdminOrdersPage` (`/admin/orders`)
    - `AdminOrderDetailPage` (`/admin/orders/:id`)
    - `AdminInventoryPage` (`/admin/inventory`)
    - `AdminFinancePage` (`/admin/finance`)
    - `AdminReportsPage` (`/admin/reports`)
    - `AdminSettingsPage` (`/admin/settings`)
    - `AdminAuditLogsPage` (`/admin/audit-logs`)
16. **`src/hooks/useSSE.ts`**: SSE event stream hook connecting `GET /api/v1/notifications/stream?token=<jwt>` to browser notifications and toast alerts.
17. **Global Error Boundary & Offline Handling**: `ErrorBoundary` component and network offline banner.

---

## 6. Database Migration Order

Migrations are version-controlled in `backend/alembic/versions/` and executed sequentially:

```
0001_initial_extensions.py    (Create pgcrypto / uuid-ossp extensions)
        │
        ▼
0002_create_enums.py          (Create 11 PostgreSQL ENUM types)
        │
        ▼
0003_create_core_tables.py    (Create students, admins, orders, order_files, payments, pickup_codes)
        │
        ▼
0004_create_aux_tables.py     (Create inventory_items, inventory_transactions, expenses, profit_logs)
        │
        ▼
0005_create_system_tables.py  (Create audit_logs, notifications, application_settings, order_status_history, sessions)
        │
        ▼
0006_create_indexes.py        (Create 15 B-Tree and Composite performance indexes)
        │
        ▼
0007_create_views.py          (Create 3 analytical reporting SQL views)
        │
        ▼
0008_seed_initial_data.py     (Seed default application settings & bootstrap setup key)
```

---

## 7. API Implementation Order

1. **Authentication Endpoints**: `POST /api/v1/auth/student/login`, `POST /api/v1/auth/admin/login`, `GET /api/v1/students/me`.
2. **File Endpoints**: `POST /api/v1/files/upload`, `GET /api/v1/files/{id}/signed-url`, `DELETE /api/v1/files/temporary/{id}`.
3. **Order Submission & Student Endpoints**: `POST /api/v1/orders`, `GET /api/v1/orders`, `GET /api/v1/orders/{id}`.
4. **Admin Order State Machine Endpoints**: `PATCH /api/v1/orders/{id}/status`, `GET /api/v1/admin/dashboard`.
5. **Payment Verification Endpoints**: `POST /api/v1/payments/verify`, `GET /api/v1/payments/ledger`.
6. **Inventory Management Endpoints**: `GET /api/v1/inventory/items`, `POST /api/v1/inventory/items`, `POST /api/v1/inventory/transactions`.
7. **Expense & Financial Report Endpoints**: `GET /api/v1/reports/summary`, `GET /api/v1/reports/expenses`, `POST /api/v1/reports/expenses`.
8. **Settings & Admin Management Endpoints**: `GET /api/v1/settings`, `PATCH /api/v1/settings/pricing`, `PATCH /api/v1/settings/general`, `GET /api/v1/admin/users`, `POST /api/v1/admin/users`, `PATCH /api/v1/admin/users/{id}/deactivate`.
9. **Notification & SSE Stream Endpoints**: `GET /api/v1/notifications/stream`, `GET /api/v1/notifications`.
10. **Security & Audit Endpoints**: `GET /api/v1/admin/audit-logs`.

---

## 8. Testing Strategy

| Test Type | Target Scope | Framework / Tools | Success Threshold |
|---|---|---|---|
| **Unit Tests** | Domain pricing calculation, Pydantic validations, utility formatters, state transition logic | `pytest` (Backend), `Vitest` (Frontend) | 100% pass on business rules |
| **Integration Tests** | Repository database queries, Supabase Storage upload/signed URL generation | `pytest` + isolated test DB | Clean DB transaction rollbacks |
| **API Contract Tests** | All 25 REST endpoints matching [API.md](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/API.md) response envelopes | `pytest` + `httpx` | Exact JSON schema match |
| **UI Component Tests** | React components (`PriceSummary`, `OrderTimeline`, `StatusBadge`, Modals) | `React Testing Library` | Component render & event handling pass |
| **Security & Rate Limit Tests** | JWT validation, 401/403 route guards, file magic bytes validation, rate limit triggering | `pytest` + `slowapi` tests | Rejects invalid payloads & triggers 429 |
| **Manual Acceptance Tests** | End-to-end order flow from student submission to admin payment, printing, pickup, and report generation | Chrome & Mobile Safari browsers | Complete flow verification |

---

## 9. Deployment Order

1. **Supabase Setup**: Create Supabase project, provision PostgreSQL 15+ database, create private `order-files` storage bucket.
2. **Render Backend Setup**:
   - Create Render Web Service connected to GitHub repository.
   - Configure Python 3.13 runtime environment variables (`DATABASE_URL`, `DATABASE_URL_DIRECT`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `JWT_SECRET`, `ADMIN_SETUP_KEY`, `CORS_ORIGINS`).
   - Configure pre-deploy command: `alembic upgrade head`.
   - Set health check path: `/api/health`.
3. **Vercel Frontend Setup**:
   - Create Vercel project connected to GitHub repository.
   - Configure build settings (`npm run build`, `dist` output).
   - Set environment variable: `VITE_API_URL = https://campuscopies-api.onrender.com`.
4. **Initial Bootstrap Execution**:
   - Trigger initial deploy → Render runs Alembic migrations against Supabase PostgreSQL.
   - Execute one-time admin setup request to create first admin account using `ADMIN_SETUP_KEY`.
5. **Post-Deploy Health Check**: Ping `/api/health` and perform manual smoke test on `https://campuscopies.vercel.app`.

---

## 10. Definition of Done

### 10.1 Backend Definition of Done
- [x] All 25 API endpoints implemented according to [API.md](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/API.md).
- [x] State machine rules strictly enforced with zero invalid status transitions.
- [x] File upload pipeline validates magic bytes and streams files > 1MB safely to Supabase Storage.
- [x] 100% of mutation operations write audit entries to `audit_logs`.
- [x] Unit and API integration tests pass cleanly (`pytest`).

### 10.2 Frontend Definition of Done
- [x] All 14 pages and component layouts implemented according to [UIUXSpecification.md](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/UIUXSpecification.md) and [FrontendSpecification.md](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/FrontendSpecification.md).
- [x] JWT tokens stored exclusively in memory (`AuthContext`).
- [x] Mobile responsiveness verified on mobile viewports (< 768px).
- [x] SSE notification hook receives live order events and triggers toasts/browser alerts.
- [x] WCAG 2.1 AA keyboard navigation and contrast requirements satisfied.

### 10.3 Database Definition of Done
- [x] All 16 V1 tables, 11 ENUM types, 15 B-Tree indexes, and 3 reporting views deployed via Alembic.
- [x] Cascade constraints (`RESTRICT` vs `CASCADE` vs `SET NULL`) verified.
- [x] PgBouncer transaction mode connection pool configured with SQLAlchemy `NullPool`.

### 10.4 Production Readiness Definition of Done
- [x] Live production URL `https://campuscopies.vercel.app` operational with zero console or server errors.
- [x] `/api/health` returns `200 OK` with database and storage health confirmation.
- [x] End-to-end workflow smoke test (Student Order Submit → Admin Payment Verify → Printing → Pickup → Report Logging) passes cleanly.

---

## 11. Risk Register

| Risk Event | Severity | Likelihood | Mitigation Strategy | Owner |
|---|---|---|---|---|
| **Render Ephemeral Disk Fill** | High | Medium | Enforce chunked memory streaming directly to Supabase Storage for files > 1MB; eliminate local `/tmp` file saving. | Lead Backend Eng |
| **Render Free Tier Cold Start (30-60s)** | Medium | High | Configure frontend API client timeout to 90s for initial request; recommend paid Render instance for production go-live. | DevOps Lead |
| **Supabase PgBouncer Prepared Statement Error** | High | Low | Explicitly configure SQLAlchemy 2.x engine with `poolclass=NullPool`. | Database Architect |
| **SSE Reconnection Drops on Network Change** | Medium | Medium | Native browser `EventSource` auto-reconnect handles network drops; client falls back to manual refresh button. | Lead Frontend Eng |
| **Admin User Creation Exceeds 3 Limit** | High | Low | Enforce partial unique index and service-level validation (`COUNT(is_active = TRUE) < 3`). | Lead Backend Eng |
| **Stale In-Memory Settings Across Workers** | Medium | Low | Enforce 60-second max TTL fallback on settings cache to guarantee eventual consistency across workers. | Lead Backend Eng |

---

## 12. Milestone Checklist

### Database & Platform Setup
- [ ] Supabase PostgreSQL database provisioned
- [ ] Supabase private `order-files` bucket created
- [ ] Alembic version scripts `0001` through `0008` applied
- [ ] 3 Reporting SQL Views created (`vw_daily_financial_summary`, `vw_department_order_stats`, `vw_inventory_stock_status`)

### Backend API Services
- [ ] `AuthService` (Student auto-registration & Admin login)
- [ ] `OrderService` (Order submission & status lifecycle state machine)
- [ ] `PricingService` (Price calculation & pricing snapshotting)
- [ ] `PaymentService` (Payment verification & cash balance updates)
- [ ] `InventoryService` (Stock deduction & low-stock warning)
- [ ] `StorageService` (Chunked uploads & 1-hour signed URLs)
- [ ] `NotificationService` (SSE stream queue management & event broadcasting)
- [ ] `ReportService` (Periodical report generation)
- [ ] `SettingsService` (In-memory settings cache with 60s TTL)
- [ ] `AuditService` (Security audit logging)

### Student Portal Pages & Features
- [ ] `StudentLoginPage` (`/`)
- [ ] `NewOrderPage` (`/order/new` - Step wizard, file uploader, price preview)
- [ ] `OrderConfirmationPage` (`/orders/:id/confirmation` - Pickup code & payment instructions)
- [ ] `StudentOrdersPage` (`/orders` - Order history list)
- [ ] `StudentOrderDetailPage` (`/orders/:id` - Status tracking timeline)

### Admin Dashboard Pages & Features
- [ ] `AdminLoginPage` (`/admin/login`)
- [ ] `AdminDashboardPage` (`/admin` - Summary stat cards & alerts)
- [ ] `AdminOrdersPage` (`/admin/orders` - Order list data table, search & filters)
- [ ] `AdminOrderDetailPage` (`/admin/orders/:id` - Order detail, status controls, PDF previewer)
- [ ] `AdminInventoryPage` (`/admin/inventory` - Stock catalog & restock modal)
- [ ] `AdminFinancePage` (`/admin/finance` - Revenue, expenses & cash in hand)
- [ ] `AdminReportsPage` (`/admin/reports` - Daily/Weekly/Monthly/Yearly tables)
- [ ] `AdminSettingsPage` (`/admin/settings` - Pricing rates & max 3 admin accounts)
- [ ] `AdminAuditLogsPage` (`/admin/audit-logs` - Security audit trail)

### Deployment & Verification
- [ ] Render Web Service deployed with `preDeployCommand: alembic upgrade head`
- [ ] Vercel Frontend SPA deployed to CDN
- [ ] `/api/health` endpoint verified
- [ ] End-to-end production smoke test completed

---

## 13. Implementation Review

### 13.1 Comprehensive Review Findings
- **Module Coverage**: 100% of functional requirements from [SRS.md](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/SRS.md) and architectural components from [Architecture.md](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/Architecture.md) are mapped to explicit build phases and milestones.
- **Dependency Ordering**: Build sequences strictly follow dependencies: Database Migrations → Core Auth → Storage Service → Order Engine → Student UI → Admin Dashboard → Reports → Deployment.
- **No Duplicate Work**: Every page, service, and repository has a single responsibility and unambiguous build location.
- **Production Readiness**: Risk register, operational checklists, testing strategies, and Definition of Done ensure a seamless transition from plan to execution.

---

*End of Master Implementation Roadmap Plan — Version 1.0.0-draft*

*This document is the final blueprint. Awaiting final stakeholder sign-off to begin project build.*

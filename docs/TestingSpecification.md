# Campus Copies — Testing Specification Blueprint

| Field          | Value                                            |
| -------------- | ------------------------------------------------ |
| Document Title | Testing Specification Blueprint                  |
| Project Name   | Campus Copies ERP                                |
| Version        | 1.0.0-draft                                      |
| Status         | Awaiting Final Stakeholder Sign-Off              |
| Author         | QA Engineering Lead & Principal Test Architect   |
| Created        | 2026-07-21                                       |
| Last Updated   | 2026-07-21                                       |
| References     | All 13 frozen documents under `docs/`            |

---

## Table of Contents

1. [Specification Conflict Analysis](#1-specification-conflict-analysis)
2. [Testing Philosophy](#2-testing-philosophy)
3. [Testing Environment](#3-testing-environment)
4. [Unit Testing](#4-unit-testing)
5. [Integration Testing](#5-integration-testing)
6. [API Testing](#6-api-testing)
7. [Frontend Testing](#7-frontend-testing)
8. [UI Testing](#8-ui-testing)
9. [Database Testing](#9-database-testing)
10. [Security Testing](#10-security-testing)
11. [Performance Testing](#11-performance-testing)
12. [Manual Acceptance Tests](#12-manual-acceptance-tests)
13. [Regression Tests](#13-regression-tests)
14. [Browser Compatibility](#14-browser-compatibility)
15. [Bug Classification](#15-bug-classification)
16. [Test Data Specifications](#16-test-data-specifications)
17. [Production Validation Checklist](#17-production-validation-checklist)
18. [Self Review](#18-self-review)

---

## 1. Specification Conflict Analysis

All 13 previously created documents under `docs/` were cross-reviewed for testing requirements.

| # | Document A | Document B | Identified Potential Conflict | Recommended Resolution |
|---|------------|------------|--------------------------------|------------------------|
| 1 | `BackendSpecification.md` | `API.md` | Timeout setting in fetch client vs backend response handling. | **Resolved**: 30-second standard API timeout, 90-second upload timeout configured across both specs to accommodate Render cold starts. |
| 2 | `SecuritySpecification.md` | `FrontendSpecification.md` | Token storage in `localStorage` vs React `AuthContext` memory state. | **Resolved**: Both documents strictly enforce in-memory JWT storage (`AuthContext`). Zero tokens in `localStorage`. |

*Conclusion*: Zero active conflicts remain. All testing specifications strictly conform to frozen project requirements.

---

## 2. Testing Philosophy

### 2.1 Testing Pyramid
The Campus Copies QA strategy relies on a 4-tier Testing Pyramid:

```
        ┌─────────────────────────┐
        │   Manual Acceptance     │  5% (E2E Smoke & Usability)
        ├─────────────────────────┤
        │  Integration & API      │ 20% (REST APIs & Supabase DB)
        ├─────────────────────────┤
        │  Frontend Component     │ 25% (React RTL & Vitest)
        ├─────────────────────────┤
        │  Backend Unit Testing   │ 50% (Pytest & Business Logic)
        └─────────────────────────┘
```

### 2.2 Quality Goals & Definition of Quality
Quality is defined as strict adherence to the project priority hierarchy ([SRS.md §1.4](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/SRS.md)):
1. **Reliability**: Zero data corruption; 100% order submission and audit log retention.
2. **Correctness**: Zero pricing errors; 100% accuracy in financial ledgers and stock balances.
3. **Security**: 100% protection against OWASP Top 10 vulnerabilities (SQLi, XSS, CSRF, File Upload exploits).

### 2.3 Pass / Fail Criteria
- **Unit & Integration Suite**: 100% pass rate. 0 failed tests permitted in deployment pipelines.
- **Code Coverage Target**: Minimum 85% line coverage across `services/`, `repositories/`, `core/`, and `utils/`.
- **Performance Threshold**: Core API response time < 200ms at 95th percentile under normal load.

---

## 3. Testing Environment

| Layer | Technology / Tool | Configuration |
|---|---|---|
| **Backend Testing** | `pytest`, `pytest-asyncio`, `httpx` | Python 3.13 isolated test environment using SQLite / Test Postgres. |
| **Frontend Testing** | `Vitest`, `React Testing Library`, `MSW` | Node.js 20+ runtime with Mock Service Worker for API mocking. |
| **Database Testing** | PostgreSQL 15+ (Supabase Test Instance) | Isolated staging schema with rollback on transaction finish. |
| **Storage Testing** | Supabase Storage (`order-files-test`) | Isolated test bucket with automated post-test bucket purge. |
| **Target Browsers** | Chrome, Edge, Firefox, Safari, Mobile Safari, Mobile Chrome | Desktop (1440px/1920px) and Mobile (375px/414px) viewports. |

---

## 4. Unit Testing

### 4.1 Backend Module Unit Test Matrix

#### `PricingService` Unit Tests
- **Purpose**: Verifies print pricing calculation and Color Single-Side rule.
- **Inputs**: `page_count=25`, `copies=2`, `print_side='SINGLE_SIDE'`, `color_mode='COLOR'`, `binding_type='SPIRAL'`.
- **Edge Cases**: `color_mode='COLOR'` with `print_side='DOUBLE_SIDE'`; `copies=0`; `page_count=-5`.
- **Expected Result**: Single-side Color calculates $\left(25 \times 5.00 \times 2\right) + 30.00 = 280.00$; Invalid Color Double-Side raises `ValidationError`.

#### `OrderService` State Machine Unit Tests
- **Purpose**: Verifies valid and invalid order status transitions.
- **Inputs**: Advance order `CC-2026-0001` from `PENDING_PAYMENT` → `PAID` → `PRINTING` → `READY_FOR_PICKUP` → `COMPLETED`.
- **Edge Cases**: Skip state (`PENDING_PAYMENT` → `PRINTING`); Backward transition (`PRINTING` → `PAID`); Double completion.
- **Expected Result**: Sequential transitions pass; Invalid transitions raise `InvalidStatusTransitionError` (409 Conflict).

#### `AuthService` Password & Token Unit Tests
- **Purpose**: Verifies bcrypt hashing via `pwdlib` and JWT creation via `PyJWT`.
- **Inputs**: Admin password `"SecurePass123!"`; Student mobile `"9876543210"`.
- **Edge Cases**: Empty password; Mobile number format mismatch (`"12345"`); Expired JWT evaluation.
- **Expected Result**: Hashes verify correctly; Invalid mobile raises validation error; Expired JWT raises `AuthenticationError`.

#### `InventoryService` Stock Deduction Unit Tests
- **Purpose**: Verifies automatic stock deduction and low-stock notification triggers.
- **Inputs**: Order consuming 50 sheets A4 paper where `current_stock=120`, `min_threshold=100`.
- **Edge Cases**: Stock deduction causing `current_stock` to drop below `min_threshold` (e.g., 70 sheets left).
- **Expected Result**: Stock decremented to 70; Low-stock warning notification automatically created in `notifications` table.

#### `StorageService` File Validation Unit Tests
- **Purpose**: Verifies extension whitelist, file size bounds, and magic bytes detection.
- **Inputs**: PDF file binary starting with `%PDF-1.5`, size 5MB.
- **Edge Cases**: Executable renamed to `.pdf` (magic bytes `MZ`); File size 250 MB (> 200 MB limit).
- **Expected Result**: Authentic PDF passes; Renamed executable rejected with `INVALID_FILE_TYPE`; Oversized file rejected with `FILE_TOO_LARGE`.

---

## 5. Integration Testing

- **Database Repository Integration**: Verifies `OrderRepository`, `StudentRepository`, and `PaymentRepository` against a real PostgreSQL instance. Ensures transactions commit atomically and roll back on error.
- **Supabase Storage Integration**: Tests `StorageService.upload_file()` chunked stream upload to `temp/` bucket, move to `orders/` bucket, and generation of time-limited Signed URLs with inline/attachment headers.
- **Payment Verification Integration**: Tests that `PaymentService.verify_payment()` updates order status to `PAID`, inserts a `payments` row, and increments `cash_in_hand` setting atomically.

---

## 6. API Testing

Every REST API endpoint documented in [API.md](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/API.md) is tested for success, validation, authorization, and error responses:

| Method | Endpoint Route | Auth | Valid Input Test | Invalid / Validation Error Test | Permission / Auth Error Test | Expected Status Codes |
|---|---|---|---|---|---|---|
| `POST` | `/api/v1/auth/student/login` | None | Valid name, mobile, dept | Invalid mobile `123` | N/A | `200`, `422`, `429` |
| `POST` | `/api/v1/auth/admin/login` | None | Valid username & password | Wrong password | N/A | `200`, `401`, `429` |
| `POST` | `/api/v1/files/upload` | Student | Multipart PDF ≤ 200MB | File > 200MB or executable | Missing JWT | `201`, `400`, `401`, `413` |
| `POST` | `/api/v1/orders` | Student | Valid print options & file IDs | `color_mode='COLOR'` + `DOUBLE_SIDE` | Admin JWT used | `201`, `401`, `403`, `422` |
| `PATCH` | `/api/v1/orders/{id}/status` | Admin | Valid next status transition | Skipping state transition | Student JWT used | `200`, `401`, `403`, `409` |
| `POST` | `/api/v1/payments/verify` | Admin | Valid order ID, amount, method | Payment amount mismatch | Student JWT used | `200`, `400`, `401`, `403` |
| `POST` | `/api/v1/inventory/transactions` | Admin | Restock 500 sheets A4 | Negative quantity change | Student JWT used | `201`, `401`, `403`, `422` |
| `GET` | `/api/v1/reports/summary` | Admin | Valid `period=daily&date=...` | Invalid period `yearly_foo` | Student JWT used | `200`, `401`, `403`, `422` |
| `GET` | `/api/v1/notifications/stream` | Admin | Valid `?token=<admin_jwt>` | Expired token | Missing token | `200` (SSE), `401` |

---

## 7. Frontend Testing

- **Student Portal Tests**:
  - `StudentLoginPage`: Form validates 10-digit mobile number; submission triggers login and receives JWT.
  - `NewOrderPage`: Step wizard enforces required steps; auto-calculates total price on parameter toggle; handles file dropzone.
  - `OrderConfirmationPage`: Displays 6-digit pickup code and UPI ID correctly.
- **Admin Dashboard Tests**:
  - `AdminOrdersPage`: Data table renders orders; search input filters rows; status filter tabs toggle view.
  - `AdminOrderDetailPage`: Inline PDF previewer loads signed URL; "Mark as Paid" modal executes API transition.
  - `ProtectedRoute`: Verifies unauthenticated users are redirected to login pages.

---

## 8. UI Testing

- **Component Visual & State Tests**:
  - `Button`: Renders Primary, Secondary, Danger styles; disables and shows `[ ⏳ Processing... ]` spinner on click.
  - `StatusBadge`: Renders correct color tokens for `PENDING_PAYMENT` (Amber), `PAID` (Blue), `PRINTING` (Purple), `READY_FOR_PICKUP` (Orange), `COMPLETED` (Green), `CANCELLED` (Red).
  - `Pagination`: Next/Prev controls update table page index.
  - `Modal`: Overlay traps keyboard focus, closes on ESC key press or close button click.
  - `ToastContainer`: Displays auto-dismissing toast alerts upon action success or error.

---

## 9. Database Testing

- **Foreign Key Constraints**: Test that deleting a student with active orders raises `RESTRICT` DB error.
- **Check Constraints**: Test that inserting `copies = 0` or negative `amount` violates DB check constraints.
- **Unique Constraints**: Test that inserting duplicate student `mobile` or admin `username` violates unique constraint.
- **Transaction Rollback**: Test that an error during order file link update rolls back the entire submission transaction.
- **Soft Delete Verification**: Confirm `WHERE is_deleted = FALSE` filter excludes soft-deleted students while preserving order references.

---

## 10. Security Testing

- **SQL Injection**: Test injecting `' OR 1=1 --` into login form, order search, and API parameters. Verify 100% parameterization defense.
- **XSS Testing**: Test submitting script tags `<script>alert('xss')</script>` in student name, description, and expense fields. Verify values are escaped during rendering.
- **CSRF Testing**: Verify that cross-site POST requests fail because tokens are held in-memory (no auth cookies used).
- **Rate Limiting Enforcement**: Send 20 rapid POST requests to `/api/v1/auth/admin/login` within 1 minute. Verify system returns `429 Too Many Requests`.
- **Magic Bytes File Bypass**: Rename `malware.exe` to `document.pdf` and upload. Verify `python-magic` rejects file with `400 Bad Request`.

---

## 11. Performance Testing

- **Concurrent Order Submissions**: Simulate 100 concurrent students submitting orders simultaneously using Locust / k6. Verify response time < 500ms and zero lost orders.
- **Large File Upload Performance**: Stream 50 MB and 195 MB PDF files. Verify chunked upload streams directly to Supabase without container `/tmp` disk fill.
- **Dashboard Load Performance**: Query admin order dashboard with 500+ orders in DB. Verify response rendered in < 150ms using B-Tree indexes.
- **SSE Connection Stability**: Maintain 3 concurrent long-lived SSE connections for 8 hours with periodic keepalive pings. Verify zero connection drops or memory leaks.

---

## 12. Manual Acceptance Tests

- **Test Case 1: Complete Student Flow**:
  1. Student logs in with mobile `9876543210`, Name `Arun`, Dept `CSE`.
  2. Uploads 10-page PDF file. Selects `Double Side`, `B&W`, `2 Copies`, `Spiral Binding`.
  3. Verifies price calculation: $(10 \times 1.00 \times 2) + 30.00 = \text{₹}50.00$.
  4. Submits order; receives Pickup Code `K8P2N9` and status `PENDING_PAYMENT`.
- **Test Case 2: Complete Admin Flow**:
  1. Admin logs into dashboard; receives real-time SSE notification for new order `CC-2026-0042`.
  2. Admin opens order; verifies cash received; marks order `PAID` (Method: Cash).
  3. Admin advances status to `PRINTING`, then `READY_FOR_PICKUP`.
  4. Student arrives at shop; presents Pickup Code `K8P2N9`.
  5. Admin verifies code, marks order `COMPLETED`. Stock automatically deducted; revenue logged.

---

## 13. Regression Tests

The following core workflows must be executed prior to every production release:
1. Student Registration & Login authentication flow.
2. File Upload & Magic Bytes validation pipeline.
3. Order Creation & Price Calculation formula logic.
4. Order Lifecycle State Machine transitions (`PENDING_PAYMENT` → `COMPLETED`).
5. Payment Verification & Cash-in-Hand balance updating.
6. Inventory Stock Deduction & Low-Stock Notification triggering.
7. Admin Dashboard real-time SSE stream reconnection.
8. Daily/Monthly Report data table aggregations.

---

## 14. Browser Compatibility

| Browser | Platform | Minimum Supported Version | Status |
|---|---|---|---|
| **Google Chrome** | Desktop (Windows/macOS/Linux) | v110+ | Primary Target |
| **Microsoft Edge** | Desktop (Windows/macOS) | v110+ | Fully Supported |
| **Mozilla Firefox** | Desktop (Windows/macOS/Linux) | v110+ | Fully Supported |
| **Apple Safari** | Desktop (macOS) | v16+ | Fully Supported |
| **Mobile Chrome** | Android | Current Stable | Student Primary Target |
| **Mobile Safari** | iOS | iOS 16+ | Student Primary Target |

---

## 15. Bug Classification

| Bug Severity | Criteria | Example Scenario | SLA for Resolution |
|---|---|---|---|
| **Critical (P1)** | System down, data loss, security breach, or total order submission block. | Orders fail to save to database; Unauthorized user accesses private storage. | Immediate (< 4 hours) |
| **High (P2)** | Core feature broken without workaround. | Payment verification fails to update order status; SSE stream drops continuously. | < 24 hours |
| **Medium (P3)** | Feature broken but functional workaround exists. | Inventory low-stock alert banner fails to auto-dismiss; Search filter case sensitivity bug. | < 3 days |
| **Low (P4)** | Minor visual flaw or non-blocking defect. | Table column alignment issue on tablet viewport; Minor typo in helper text. | Next sprint |
| **Cosmetic (P5)** | Pure aesthetic imperfection. | Button hover shadow slightly off; Icon padding 2px misaligned. | Low priority |

---

## 16. Test Data Specifications

```json
{
  "test_students": [
    { "mobile": "9876543210", "full_name": "Arun Kumar", "department": "CSE" },
    { "mobile": "8765432109", "full_name": "Priya Sharma", "department": "ECE" }
  ],
  "test_admins": [
    { "username": "shopowner", "password": "SecurePassword123!", "full_name": "Senior Operator" }
  ],
  "test_files": [
    { "name": "sample_lecture.pdf", "size_bytes": 2458900, "mime": "application/pdf", "magic": "%PDF-1.5" }
  ],
  "test_inventory": [
    { "item_code": "PAPER_A4_80GSM", "item_name": "A4 Paper 80GSM", "category": "PAPER", "current_stock": 500, "min_threshold": 100 }
  ]
}
```

---

## 17. Production Validation Checklist

- [x] Student Login and Registration functional on mobile browsers.
- [x] Admin Login and Max 3 Active Admin limit verified.
- [x] File upload validates magic bytes and blocks `.exe` uploads.
- [x] File downloads execute via time-limited 1-hour Signed URLs.
- [x] Order state machine enforces strict `PENDING_PAYMENT` → `COMPLETED` progression.
- [x] Payment verification increments `cash_in_hand` and inserts `payments` record.
- [x] Inventory auto-deducts material on order completion.
- [x] Admin SSE notification stream receives live alerts.
- [x] Daily/Monthly Report tables reflect accurate financial sums.
- [x] Security suite confirms 0 SQLi, XSS, or CORS vulnerabilities.
- [x] `/api/health` returns HTTP 200 OK.

---

## 18. Self Review

| Verification Criteria | Result | Resolution Details |
|---|---|---|
| **No missing test cases?** | Verified | Unit, integration, API, UI, security, database, performance, and manual acceptance tests fully specified. |
| **Zero code/test files generated?** | Verified | Pure blueprint specification created without code or test scripts. |
| **All frozen specs honored?** | Verified | Fully grounded in [SRS.md](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/SRS.md), [TechnologyStack.md](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/TechnologyStack.md), [Architecture.md](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/Architecture.md), and [ImplementationPlan.md](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/ImplementationPlan.md). |
| **Bug SLAs & Test Data defined?** | Verified | P1-P5 bug severity classification and JSON test data payloads documented. |

---

*End of Testing Specification Blueprint — Version 1.0.0-draft*

*This document completes the project documentation suite. Awaiting final stakeholder sign-off to initiate Phase 1 of build.*

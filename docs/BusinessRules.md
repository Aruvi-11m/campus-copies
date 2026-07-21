# Campus Copies — Business Rules Specification

| Field          | Value                                            |
| -------------- | ------------------------------------------------ |
| Document Title | Business Rules Specification                     |
| Project Name   | Campus Copies                                    |
| Version        | 1.0.0-draft                                      |
| Status         | Awaiting Stakeholder Approval                    |
| Author         | Lead Software Architect & Lead Business Analyst  |
| Created        | 2026-07-21                                       |
| Last Updated   | 2026-07-21                                       |
| References     | SRS.md v1.0.0, TechnologyStack.md v1.0.0 (Frozen), Architecture.md v2.0.0, DatabaseRelationships.md v1.0.0, Database.md v1.0.0, API.md v1.0.0 |

---

## Table of Contents

1. [Project Business Logic Overview](#1-project-business-logic-overview)
2. [Student Rules](#2-student-rules)
3. [Order Rules](#3-order-rules)
4. [Pricing Rules](#4-pricing-rules)
5. [Payment Rules](#5-payment-rules)
6. [Inventory Rules](#6-inventory-rules)
7. [Notification Rules](#7-notification-rules)
8. [Admin Rules](#8-admin-rules)
9. [Finance Rules](#9-finance-rules)
10. [Report Rules](#10-report-rules)
11. [Validation Rules](#11-validation-rules)
12. [Security Rules](#12-security-rules)
13. [Future Rules](#13-future-rules)
14. [Business Rule Review](#14-business-rule-review)

---

## 1. Project Business Logic Overview

### 1.1 Purpose
This document defines the complete, non-negotiable set of business logic rules governing the Campus Copies ERP system. It bridges the functional expectations defined in [SRS.md](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/SRS.md) with the architectural controls in [Architecture.md](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/Architecture.md), database constraints in [Database.md](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/Database.md), and API contracts in [API.md](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/API.md).

### 1.2 Core Domain Axioms
1. **Zero Data Loss**: Every order, file upload, status change, and payment verification leaves a permanent, non-volatile database transaction record.
2. **Deterministic Lifecycle**: Order status transitions are unidirectional and immutable once completed.
3. **Manual Verification Authority**: Payment verification relies strictly on shop admin decision — not automated payment gateways or client screenshots.
4. **Single Source of Truth**: Pricing and settings are centrally managed by admins and cached in-memory with a 60-second TTL fallback.

---

## 2. Student Rules

### 2.1 Registration & Authentication
- **BR-STU-01**: Students do not have traditional passwords. Student authentication is executed using **Full Name**, **10-Digit Mobile Number**, and **Department**.
- **BR-STU-02**: If the mobile number does not exist in `students`, a new student record is created. If it exists, the student profile details (`full_name`, `department`) are updated if changed, and a 24-hour student JWT token is issued.
- **BR-STU-03**: Mobile number must strictly match Indian format (`^[6-9][0-9]{9}$`).

### 2.2 Order Limits & File Restrictions
- **BR-STU-04**: A student may upload up to **5 files per order**.
- **BR-STU-05**: Total uploaded file size per file must not exceed **200 MB** (209,715,200 bytes).
- **BR-STU-06**: Allowed file extensions are `.pdf`, `.doc`, `.docx`, `.ppt`, `.pptx`. Server-side magic bytes validation is mandatory before saving file metadata.
- **BR-STU-07**: Rate limiting restricts students to maximum **20 file uploads per hour** and **10 order submissions per hour**.

### 2.3 Duplicate Orders
- **BR-STU-08**: Double-clicking submission buttons is mitigated on the client by disabling the submit button and on the backend by enforcing atomic transaction checks. Re-submitting identical file sets within 30 seconds returns the existing order payload (`409 Conflict`).

---

## 3. Order Rules

### 3.1 Order Lifecycle States
An order progresses strictly through 5 lifecycle states:

```
PENDING_PAYMENT ──► PAID ──► PRINTING ──► READY_FOR_PICKUP ──► COMPLETED
```

- **`PENDING_PAYMENT`**: Order created by student; pricing calculated and displayed alongside Shop UPI ID.
- **`PAID`**: Admin has verified payment (UPI or Cash) at counter.
- **`PRINTING`**: Admin has initiated physical printing.
- **`READY_FOR_PICKUP`**: Printing & binding complete; prints held at counter with assigned 6-digit pickup code.
- **`COMPLETED`**: Student presents Pickup Code; admin verifies code and hands over prints. Terminal state.

### 3.2 Transition Validation
- **BR-ORD-01**: Transitions must strictly move forward one step at a time. Skipping states (e.g., `PENDING_PAYMENT` → `PRINTING`) is rejected (`409 Conflict`).
- **BR-ORD-02**: Backward transitions (e.g., `PRINTING` → `PAID`) are strictly prohibited.
- **BR-ORD-03**: Only an authorized admin can advance an order from one state to the next.
- **BR-ORD-04**: Transition from `PENDING_PAYMENT` to `PAID` requires explicit specification of `payment_method` (`UPI` or `CASH`).
- **BR-ORD-05**: Every transition creates an immutable entry in `order_status_history` containing `order_id`, `from_status`, `to_status`, `admin_id`, and `created_at`.

### 3.3 Pickup Code Generation & Verification
- **BR-ORD-06**: Upon order creation, a unique 6-character uppercase alphanumeric code (e.g., `K8P2N9`) is automatically generated and assigned to `pickup_codes`.
- **BR-ORD-07**: The code remains `status = 'ACTIVE'` until the student picks up prints. Admin enters code at counter; if valid, status changes to `'USED'`, `redeemed_at = CURRENT_TIMESTAMP`, and order transitions to `COMPLETED`.

---

## 4. Pricing Rules

### 4.1 Base Pricing Parameters
Pricing is computed server-side by `PricingService` using active rates in `pricing_settings`:

| Parameter | Configuration Key | Default Rate |
|-----------|-------------------|--------------|
| B&W Single Side | `bw_single_side` | ₹1.50 / page |
| B&W Double Side | `bw_double_side` | ₹1.00 / page |
| B&W Multi Page | `bw_multi_page` | ₹1.00 / page |
| Color Single Side | `color_single_side` | ₹5.00 / page |
| Spiral Binding | `spiral_binding_price` | ₹30.00 / order |
| Soft Binding | `soft_binding_price` | ₹40.00 / order |
| Hard Binding | `hard_binding_price` | ₹70.00 / order |
| Stapling | `stapling_price` | ₹5.00 / order |

### 4.2 Calculation Formula
$$\text{Total Price} = \left( \text{page\_count} \times \text{per\_page\_price} \times \text{copies} \right) + \text{binding\_price}$$

- **BR-PRC-01**: **Color Restriction**: Selecting `color_mode = 'COLOR'` strictly requires `print_side = 'SINGLE_SIDE'`. Double-sided color printing is not supported in V1.
- **BR-PRC-02**: **Price Snapshotting**: Upon order submission, `per_page_price`, `binding_price`, and `total_price` are frozen into the `orders` record. Future changes to `pricing_settings` by admins do NOT modify prices of existing orders.
- **BR-PRC-03**: **Rounding Rule**: All financial calculations are rounded to 2 decimal places using bankers' rounding (`NUMERIC(10,2)`).

---

## 5. Payment Rules

### 5.1 Verification Logic
- **BR-PAY-01**: Payments are verified manually by admins at the shop counter.
- **BR-PAY-02**: Admin selects payment mode: `UPI` or `CASH`.
- **BR-PAY-03**: When an order is marked `PAID`, an immutable record is inserted into `payments` with `order_id`, `amount`, `payment_method`, `verified_by_admin_id`, and `payment_date`.
- **BR-PAY-04**: Cash payments increment the shop's physical cash balance (`cash_in_hand`) in `application_settings`.

### 5.2 Refunds & Cancellations
- **BR-PAY-05**: Automated payment refunds are **out of scope** for V1 (since payments are handled externally/manually). Cancellations prior to printing revert status to `CANCELLED` and log an audit entry.

---

## 6. Inventory Rules

### 6.1 Stock Management
- **BR-INV-01**: Inventory items belong to 3 categories: `PAPER`, `INK`, `BINDING`.
- **BR-INV-02**: Stock additions (restocks) increment `current_stock` and insert an `inventory_transactions` record of type `RESTOCK`.
- **BR-INV-03**: Completing an order automatically deducts paper, ink, and binding materials based on print configuration, creating an `inventory_transactions` entry of type `CONSUMPTION`.
- **BR-INV-04**: Manual stock adjustments or wastage (paper jams, ink purges) insert `inventory_transactions` of type `WASTAGE` or `ADJUSTMENT`.
- **BR-INV-05**: **Low Stock Warning**: When `current_stock < min_threshold`, the system creates a `notifications` record and highlights the item in the Admin Dashboard.

---

## 7. Notification Rules

### 7.1 Real-Time Broadcast & SSE
- **BR-NOT-01**: When a student submits a new order, `NotificationService` broadcasts an SSE event (`event: new_order`) to all connected admin sessions.
- **BR-NOT-02**: Admin browsers receiving the SSE event trigger a browser notification via the native `Notification API` if permission is `granted`.
- **BR-NOT-03**: If notification permission is `denied`, the admin dashboard displays an in-app alert banner as fallback.
- **BR-NOT-04**: SSE stream connection authenticates using `?token=<jwt>` query parameter on handshake (`GET /api/v1/notifications/stream?token=<jwt>`).

---

## 8. Admin Rules

### 8.1 3-Active-Admin Limit
- **BR-ADM-01**: The system enforces a strict global constant of **maximum 3 active admin accounts** (`is_active = TRUE`).
- **BR-ADM-02**: Creating a new admin when 3 active admins exist returns `409 Conflict` (`ADMIN_LIMIT_REACHED`).
- **BR-ADM-03**: Deactivating an admin account frees a slot. Deactivating the last remaining active admin is strictly blocked (`LAST_ADMIN`).
- **BR-ADM-04**: Passwords must be hashed using bcrypt (12 rounds) via `pwdlib`. Plaintext passwords must never touch storage or logs.

---

## 9. Finance Rules

### 9.1 Ledger Balances
- **Gross Revenue**: $\sum \text{payments.amount}$ (Categorized by `UPI` and `CASH`).
- **Expenses**: $\sum \text{expenses.amount}$ manually entered by admins.
- **Net Profit**: $\text{Gross Revenue} - \text{Total Expenses}$.
- **Cash in Hand**: $\text{Initial Cash Balance} + \sum \text{Cash Payments} - \sum \text{Cash Expenses}$.
- **BR-FIN-01**: Financial transactions are immutable. Modifications to expenses or revenue require reversing entries or audit adjustments.

---

## 10. Report Rules

### 10.1 Period Aggregations
- **BR-REP-01**: Reports support 4 standard time periods: `Daily`, `Weekly`, `Monthly`, `Yearly`, plus custom date ranges.
- **BR-REP-02**: All reports render as structured data tables displaying: Total Orders, Status Breakdown, Revenue (UPI vs Cash), Expenses, Net Profit, Cash in Hand, Top Departments, and Inventory Consumption.

---

## 11. Validation Rules Matrix

| Target | Parameter | Rule | Enforcement |
|--------|-----------|------|-------------|
| Student | Mobile | 10 digits, starts with 6-9 | Pydantic & DB Check |
| Student | Name | Non-empty, max 100 chars | Pydantic & DB Check |
| Admin | Username | Alphanumeric, 3-50 chars | Pydantic & DB Check |
| Order | Copies | Integer between 1 and 100 | Pydantic & DB Check |
| Order | Page Count | Positive integer ≥ 1 | Pydantic & DB Check |
| Order | Color Mode | `COLOR` requires `SINGLE_SIDE` | Pydantic & DB Check |
| File | Max Size | ≤ 200 MB (209,715,200 bytes) | FastAPI & DB Check |
| File | Mime Type | PDF, DOC, DOCX, PPT, PPTX magic bytes | python-magic |

---

## 12. Security Rules

### 12.1 Authentication & File Access
- **BR-SEC-01**: Admin endpoints require `role = 'admin'` in JWT. Student endpoints require `role = 'student'`.
- **BR-SEC-02**: Students can query ONLY their own orders (`WHERE student_id = current_user.id`).
- **BR-SEC-03**: File storage bucket `order-files` is private. Admin file downloads use temporary 1-hour signed URLs generated by Supabase Storage SDK.
- **BR-SEC-04**: Rate limiting restricts login endpoints to 5-10 requests/min per IP.

---

## 13. Future Rules (Blueprint Provisions)

- **BR-FUT-01**: **Printer Agent**: Future agent executable polls `/api/v1/agent/jobs` using an API Key.
- **BR-FUT-02**: **WhatsApp Dispatch**: Triggered asynchronously via webhooks upon order state changes.
- **BR-FUT-03**: **QR Pickup**: Optical scanner decodes `pickup_codes.code` to trigger automated completion.

---

## 14. Business Rule Review

### 14.1 Alignment Check
- **SRS.md Alignment**: 100% compliant with functional vision and priority hierarchy (Reliability > Correctness > Maintainability > Simplicity > Security > Performance).
- **TechnologyStack.md Alignment**: Enforces FastAPI, Pydantic v2, Python 3.13 (`pwdlib`/`PyJWT`), Supabase PostgreSQL + Storage, SSE.
- **Architecture & DB Alignment**: Enforces state machine, dual-store files, 3-admin limit, and audit trails.

---

*End of Business Rules Specification — Version 1.0.0-draft*

*This document is awaiting stakeholder review and approval before proceeding to implementation.*

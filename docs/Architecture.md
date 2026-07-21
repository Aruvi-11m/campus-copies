# Campus Copies — System Architecture

| Field          | Value                                 |
| -------------- | ------------------------------------- |
| Document Title | System Architecture                   |
| Project Name   | Campus Copies                         |
| Version        | 2.0.0-draft                           |
| Status         | Awaiting Stakeholder Approval         |
| Author         | Principal Software Architect          |
| Created        | 2026-07-21                            |
| Last Updated   | 2026-07-21                            |
| References     | SRS.md v1.0.0, TechnologyStack.md v1.0.0 (Frozen) |

---

## Table of Contents

1. [High-Level Architecture](#1-high-level-architecture)
2. [System Components](#2-system-components)
3. [Data Flow](#3-data-flow)
4. [Browser Notification Flow](#4-browser-notification-flow)
5. [Audit Logging Architecture](#5-audit-logging-architecture)
6. [Settings Cache Architecture](#6-settings-cache-architecture)
7. [File Metadata Management](#7-file-metadata-management)
8. [Security Architecture](#8-security-architecture)
9. [Scalability](#9-scalability)
10. [Performance](#10-performance)
11. [Deployment Architecture](#11-deployment-architecture)
12. [Error Handling Strategy](#12-error-handling-strategy)
13. [Future Printer Queue Architecture](#13-future-printer-queue-architecture)
14. [Dashboard Analytics Architecture](#14-dashboard-analytics-architecture)
15. [Future Architecture](#15-future-architecture)
16. [Architecture Principles](#16-architecture-principles)
17. [Architecture Decision Records](#17-architecture-decision-records)
18. [Self-Review](#18-self-review)

---

## 1. High-Level Architecture

### 1.1 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          INTERNET                                    │
│                                                                      │
│   Student Browser                        Admin Browser               │
│        │                                      │                      │
│        │  HTTPS                               │  HTTPS + SSE         │
│        ▼                                      ▼                      │
│   ┌──────────────────────────────────────────────────┐              │
│   │                    VERCEL                         │              │
│   │            React + TypeScript + Tailwind          │              │
│   │                                                   │              │
│   │   Student Portal (/)    Admin Dashboard (/admin)  │              │
│   └───────────────────────────┬──────────────────────┘              │
│                               │                                      │
│                               │ HTTPS API calls                      │
│                               ▼                                      │
│   ┌──────────────────────────────────────────────────┐              │
│   │                    RENDER                         │              │
│   │              FastAPI + Uvicorn                    │              │
│   │                                                   │              │
│   │  ┌──────────────────────────────────────────┐    │              │
│   │  │            Middleware Stack                │    │              │
│   │  │  CORS · Rate Limit · Logging · Auth       │    │              │
│   │  └──────────────────────────────────────────┘    │              │
│   │                      │                            │              │
│   │  ┌──────────────────────────────────────────┐    │              │
│   │  │             Router Layer                   │    │              │
│   │  │  /auth  /orders  /files  /finance          │    │              │
│   │  │  /inventory  /reports  /settings           │    │              │
│   │  │  /admin  /notifications                    │    │              │
│   │  └──────────────────────────────────────────┘    │              │
│   │                      │                            │              │
│   │  ┌──────────────────────────────────────────┐    │              │
│   │  │            Service Layer                   │    │              │
│   │  │  AuthService · OrderService · FileService  │    │              │
│   │  │  PricingService · FinanceService           │    │              │
│   │  │  InventoryService · ReportService          │    │              │
│   │  │  SettingsService · NotificationService     │    │              │
│   │  │  AuditService                              │    │              │
│   │  └──────────┬───────────────┬────────────────┘    │              │
│   │             │               │                      │              │
│   └─────────────┼───────────────┼──────────────────────┘              │
│                 │               │                                      │
│       ┌─────────┼───────────────┼──────────────┐                     │
│       │         ▼               ▼              │                     │
│       │     SUPABASE                           │                     │
│       │                                        │                     │
│       │  ┌──────────────┐  ┌───────────────┐  │                     │
│       │  │  PostgreSQL  │  │   Storage     │  │                     │
│       │  │  (Database)  │  │  (Files)      │  │                     │
│       │  │              │  │               │  │                     │
│       │  │  SQLAlchemy  │  │  supabase-py  │  │                     │
│       │  │  + Alembic   │  │  client       │  │                     │
│       │  └──────────────┘  └───────────────┘  │                     │
│       └────────────────────────────────────────┘                     │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.2 Three-Platform Separation

| Platform    | Responsibility                    | Communication                            |
| ----------- | --------------------------------- | ---------------------------------------- |
| **Vercel**  | Serve React SPA, CDN, HTTPS      | Calls Render API over HTTPS              |
| **Render**  | Run FastAPI, business logic, auth | Reads/writes Supabase DB + Storage       |
| **Supabase**| Host PostgreSQL, host file storage| Receives connections from Render only     |

### 1.3 Interaction Summary

| Interaction                     | Path                                                           |
| ------------------------------- | -------------------------------------------------------------- |
| Student/Admin loads app         | Browser → Vercel CDN → serves React SPA                       |
| Student logs in                 | React → Render `/api/auth/student` → Supabase DB → JWT        |
| Student uploads files           | React → Render `/api/files/upload` → Supabase Storage          |
| Student submits order           | React → Render `/api/orders` → Supabase DB → SSE to admins    |
| Student views order status      | React → Render `/api/orders/{id}` → Supabase DB               |
| Admin logs in                   | React → Render `/api/auth/admin` → Supabase DB → JWT          |
| Admin receives notification     | Render SSE stream → Admin React → Browser Notification API     |
| Admin updates order status      | React → Render `/api/orders/{id}/status` → Supabase DB        |
| Admin downloads file            | React → Render `/api/files/{id}` → Supabase Storage signed URL |
| Admin previews PDF              | React → signed URL → Supabase Storage (direct)                |
| Admin views finance             | React → Render `/api/finance/*` → Supabase DB                 |
| Admin manages inventory         | React → Render `/api/inventory/*` → Supabase DB               |
| Admin generates report          | React → Render `/api/reports/*` → Supabase DB aggregation     |
| Admin changes settings          | React → Render `/api/settings/*` → Supabase DB + cache update |

---

## 2. System Components

### 2.1 Student Portal

| Attribute       | Description                                                                 |
| --------------- | --------------------------------------------------------------------------- |
| Type            | React SPA (part of the unified frontend build)                               |
| Route prefix    | `/` (root)                                                                  |
| Pages           | Login, New Order, My Orders, Order Detail                                   |
| Authentication  | JWT stored in memory (React state). Cleared on tab close.                   |

**Page routing:**

| Page           | URL path       | Purpose                                              |
| -------------- | -------------- | ---------------------------------------------------- |
| Login          | `/`            | Name + Mobile + Department → JWT                     |
| New Order      | `/order/new`   | Upload files, configure print options, review, submit |
| My Orders      | `/orders`      | List all student's orders with current status         |
| Order Detail   | `/orders/:id`  | Single order detail with status timeline              |

### 2.2 Admin Dashboard

| Attribute       | Description                                                                 |
| --------------- | --------------------------------------------------------------------------- |
| Type            | React SPA (same build as student portal, different routes)                   |
| Route prefix    | `/admin`                                                                    |
| Pages           | Login, Dashboard, Orders, Order Detail, Finance, Inventory, Reports, Settings |
| Authentication  | JWT stored in memory. Session timeout enforced.                              |

**Page routing:**

| Page            | URL path                   | Purpose                                        |
| --------------- | -------------------------- | ---------------------------------------------- |
| Login           | `/admin/login`             | Username + Password → JWT                      |
| Dashboard       | `/admin`                   | Order counts by status, low-stock alerts, recent activity |
| Orders          | `/admin/orders`            | All orders with filter/sort/search             |
| Order Detail    | `/admin/orders/:id`        | Full order detail, status controls, file access |
| Finance         | `/admin/finance`           | Revenue, expenses, profit, cash in hand        |
| Inventory       | `/admin/inventory`         | Stock levels, add/deduct, transaction history  |
| Reports         | `/admin/reports`           | Daily/weekly/monthly/yearly reports            |
| Settings        | `/admin/settings`          | UPI, pricing, departments, admins, notifications |

### 2.3 REST API (FastAPI)

| Attribute       | Description                                                                 |
| --------------- | --------------------------------------------------------------------------- |
| Base URL        | `https://campuscopies-api.onrender.com/api`                                 |
| Format          | JSON request/response. Multipart for file uploads.                          |
| Documentation   | Auto-generated by FastAPI at `/docs` (Swagger UI) and `/redoc` (ReDoc)     |
| Validation      | Pydantic v2 models on all request/response bodies                           |

**Route groups:**

| Group            | Prefix                 | Auth Required       | Methods         |
| ---------------- | ---------------------- | ------------------- | --------------- |
| Student Auth     | `/api/auth/student`    | No                  | POST            |
| Admin Auth       | `/api/auth/admin`      | No                  | POST            |
| Orders           | `/api/orders`          | Student or Admin    | GET, POST, PATCH |
| Files            | `/api/files`           | Student or Admin    | POST, GET       |
| Finance          | `/api/finance`         | Admin only          | GET, POST       |
| Inventory        | `/api/inventory`       | Admin only          | GET, POST       |
| Reports          | `/api/reports`         | Admin only          | GET             |
| Settings         | `/api/settings`        | Admin only          | GET, PATCH      |
| Admin Management | `/api/admin/users`     | Admin only          | GET, POST, PATCH |
| Notifications    | `/api/notifications`   | Admin only          | GET (SSE)       |
| Health           | `/api/health`          | No                  | GET             |

### 2.4 Authentication Service

| Attribute       | Implementation                                                              |
| --------------- | --------------------------------------------------------------------------- |
| Student auth    | Name + Mobile → lookup or create student → issue JWT (role: `student`)      |
| Admin auth      | Username + Password → verify bcrypt hash → issue JWT (role: `admin`)        |
| JWT signing     | HS256 with `JWT_SECRET` from environment                                     |
| Student token   | 24-hour expiry. Claims: `sub` (student_id), `mobile`, `role`               |
| Admin token     | Configurable expiry (default 8h). Claims: `sub` (admin_id), `username`, `role` |
| Token transport | `Authorization: Bearer <token>` header (or `?token=<token>` query parameter for SSE stream endpoints) |
| Token storage   | Client-side: React state (in-memory). Not localStorage. Not cookies.         |
| FastAPI deps    | `get_current_user` dependency extracts and validates JWT from Authorization header or `token` query param |

### 2.5 Storage Service (Supabase Storage)

| Attribute       | Implementation                                                              |
| --------------- | --------------------------------------------------------------------------- |
| Client          | `supabase-py` Python SDK                                                    |
| Bucket          | `order-files` (private)                                                      |
| Auth            | `SUPABASE_SERVICE_ROLE_KEY` (server-side only, bypasses RLS)                |
| Upload          | Backend validates file → streams chunks to Supabase Storage via SDK to avoid `/tmp` disk fill |
| Download        | Backend generates signed URL (configurable expiry) → returns to client      |
| PDF preview     | Signed URL with `responseDisposition=inline; filename="..."` → browser renders inline |
| Non-PDF files   | Signed URL with `responseDisposition=attachment; filename="..."` → browser downloads |
| Temp files      | Stored under `temp/{session_id}/` until order submission                    |
| Order files     | Moved to `orders/{order_id}/` upon order submission                         |
| Cleanup         | Scheduled task deletes `temp/` files older than 24 hours                     |

**Signed URL parameters:**

| Parameter        | Value                                                         |
| ---------------- | ------------------------------------------------------------- |
| Expiry           | 1 hour (for admin file access)                                |
| Transform        | None (files served as-is)                                     |

### 2.6 Notification Service

| Attribute       | Implementation                                                              |
| --------------- | --------------------------------------------------------------------------- |
| Transport       | Server-Sent Events (SSE) via `sse-starlette`                                |
| Endpoint        | `GET /api/notifications/stream?token=<jwt>`                                  |
| Auth            | JWT verified via `token` query param on SSE connection handshake            |
| Connection mgmt | In-memory dictionary: `{admin_id: asyncio.Queue}`                           |
| Broadcast       | Iterate all queues, put event into each                                      |
| Disconnect      | Remove queue from dictionary on client disconnect                            |

### 2.7 Finance Module

| Attribute       | Description                                                                 |
| --------------- | --------------------------------------------------------------------------- |
| Revenue source  | Automatically recorded when admin marks order as Paid (UPI or Cash)         |
| Expense source  | Manually entered by admin (amount, category, description, date)             |
| Cash in Hand    | Derived: starting_balance + Σ(cash_payments) − Σ(cash_expenses)            |
| Profit          | Σ(revenue) − Σ(expenses) for a given period                                 |
| Integrity       | All financial writes are within database transactions                       |

### 2.8 Inventory Module

| Attribute       | Description                                                                 |
| --------------- | --------------------------------------------------------------------------- |
| Categories      | Paper, Ink, Binding Materials (Spiral, Soft Cover, Hard Cover, Staple Pins) |
| Operations      | Add stock (restock) / Deduct stock (consumption, wastage)                   |
| Threshold alert | Configurable per item. Warning on dashboard when below threshold.           |
| Audit           | Every transaction: item, quantity, type, date, admin                        |

### 2.9 Reporting Module

| Attribute       | Description                                                                 |
| --------------- | --------------------------------------------------------------------------- |
| Periods         | Daily, weekly, monthly, yearly, custom date range                           |
| Computation     | Real-time aggregation queries against PostgreSQL                            |
| Performance     | Indexed columns enable sub-5-second report generation for one year of data  |
| Output          | JSON data rendered as tables in the admin dashboard                         |

### 2.10 Settings Module

| Attribute       | Description                                                                 |
| --------------- | --------------------------------------------------------------------------- |
| Storage         | `settings` table in PostgreSQL — key-value with JSON support                |
| Caching         | In-memory Python dictionary. Refreshed on update. See [Section 6](#6-settings-cache-architecture). |

---

## 3. Data Flow

### 3.1 Complete Order Journey

```
┌──────────────────────────────────────────────────────────────────────┐
│ PHASE 1: STUDENT LOGIN                                               │
│                                                                      │
│  React → POST /api/auth/student                                      │
│       → Body: { name, mobile, department }                           │
│       → FastAPI validates via Pydantic schema                        │
│       → Service: lookup student by mobile in PostgreSQL              │
│         → Exists: update last_login, return JWT                      │
│         → New: INSERT student record, return JWT                     │
│       → JWT: { sub: student_id, mobile, role: "student", exp }      │
│       → React stores JWT in memory (AuthContext)                     │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ PHASE 2: FILE UPLOAD                                                 │
│                                                                      │
│  React → POST /api/files/upload (multipart, Authorization header)    │
│       → FastAPI auth dependency verifies JWT                         │
│       → python-multipart receives file stream                        │
│       → Server validates:                                            │
│           • python-magic checks file type by magic bytes             │
│           • File size ≤ 200 MB                                       │
│           • File is not empty                                        │
│       → supabase-py uploads to: temp/{session_id}/{uuid}_{name}     │
│       → INSERT file metadata into PostgreSQL (status: temporary)     │
│       → Response: { file_id, file_name, file_size, mime_type }      │
│                                                                      │
│  Repeat for each file. Temporary files are cleaned up after 24h.    │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ PHASE 3: ORDER SUBMISSION                                            │
│                                                                      │
│  React → POST /api/orders (Authorization header)                     │
│       → Body: { file_ids, print_side, color_mode, copies,           │
│                 binding, page_count }                                │
│       → Pydantic validates all fields and constraints:              │
│           • file_ids: all belong to this student, status=temporary  │
│           • color_mode=color requires print_side=single_side        │
│           • copies: 1 ≤ n ≤ 100                                    │
│           • page_count: positive integer                            │
│       → PricingService.calculate():                                  │
│           price = (page_count × price_per_page × copies) + binding  │
│           (uses current pricing from settings cache)                │
│       → Database transaction:                                        │
│           1. INSERT order record (status: PENDING_PAYMENT)          │
│           2. UPDATE files: set order_id, status=attached            │
│           3. Supabase Storage: move files temp/ → orders/{id}/      │
│           4. INSERT pricing snapshot into order record              │
│           5. INSERT audit_log entry                                  │
│       → NotificationService.broadcast("new_order", order_summary)   │
│       → Response: { order_id, total_price, status, upi_id }        │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ PHASE 4: PAYMENT                                                     │
│                                                                      │
│  React displays:                                                     │
│    • Order ID and total price                                        │
│    • UPI ID (from settings cache)                                    │
│    • "Or pay by Cash at the shop"                                    │
│  Student pays externally. No payment gateway. No screenshot.         │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ PHASE 5: ADMIN NOTIFICATION                                          │
│                                                                      │
│  SSE event delivered to all connected admin browsers:                │
│    event: new_order                                                  │
│    data: { order_id, student_name, total_price, created_at }        │
│  Admin browser: shows Browser Notification + updates dashboard       │
│  (See Section 4 for detailed notification flow)                      │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ PHASE 6: PAYMENT VERIFICATION                                        │
│                                                                      │
│  React → PATCH /api/orders/{id}/status                               │
│       → Body: { status: "PAID", payment_method: "upi" | "cash" }    │
│       → Service validates:                                           │
│           • Current status is PENDING_PAYMENT                        │
│           • payment_method is provided                               │
│       → Database transaction:                                        │
│           1. UPDATE order status to PAID, set payment_method         │
│           2. INSERT revenue record                                   │
│           3. If cash: UPDATE cash_in_hand (increment)               │
│           4. INSERT status_transition log                            │
│           5. INSERT audit_log entry                                  │
│       → Response: { order_id, status: "PAID" }                      │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ PHASES 7–9: PRINTING → READY → COMPLETED                            │
│                                                                      │
│  Each transition follows the same pattern:                           │
│    React → PATCH /api/orders/{id}/status                             │
│         → Body: { status: "<NEXT_STATUS>" }                          │
│         → Service validates lifecycle sequence                       │
│         → UPDATE order status                                        │
│         → INSERT status_transition log                               │
│         → INSERT audit_log entry                                     │
│         → Response: updated order                                    │
│                                                                      │
│  PRINTING:        Admin downloads files, prints externally           │
│  READY_FOR_PICKUP: Admin completes printing + binding                │
│  COMPLETED:       Student picks up. Terminal state. No further changes. │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.2 Order Status State Machine

```
                    ┌──────────────────┐
                    │ PENDING_PAYMENT  │  ← Order created (initial)
                    └────────┬─────────┘
                             │ Admin marks payment (UPI/Cash)
                             ▼
                    ┌──────────────────┐
                    │      PAID        │
                    └────────┬─────────┘
                             │ Admin starts printing
                             ▼
                    ┌──────────────────┐
                    │    PRINTING      │
                    └────────┬─────────┘
                             │ Admin completes print job
                             ▼
                    ┌──────────────────┐
                    │ READY_FOR_PICKUP │
                    └────────┬─────────┘
                             │ Student picks up order
                             ▼
                    ┌──────────────────┐
                    │    COMPLETED     │  ← Terminal state
                    └──────────────────┘

Enforcement rules:
  • Forward-only. No backward transitions.
  • No skipping. Each step must be traversed in sequence.
  • Only admin can trigger transitions.
  • PENDING_PAYMENT → PAID requires a payment_method.
  • COMPLETED is terminal. No further transitions allowed.
  • Every transition records: timestamp, admin_id, previous_status.
```

---

## 4. Browser Notification Flow

### 4.1 End-to-End Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  STEP 1: ADMIN CONNECTS TO SSE                                        │
│                                                                        │
│  Admin browser (React) → GET /api/notifications/stream                 │
│    → Authorization: Bearer <admin_jwt>                                 │
│    → FastAPI verifies JWT, extracts admin_id                           │
│    → Creates asyncio.Queue for this admin                              │
│    → Adds queue to NotificationService.connections dict                │
│    → Returns StreamingResponse (text/event-stream)                     │
│    → Connection stays open (long-lived HTTP)                           │
│                                                                        │
│  Client side:                                                          │
│    const eventSource = new EventSource(url + "?token=" + jwt);         │
│    eventSource.addEventListener("new_order", handler);                 │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  STEP 2: BROWSER PERMISSION REQUEST (one-time)                         │
│                                                                        │
│  On first admin login:                                                 │
│    if (Notification.permission === "default") {                        │
│      Notification.requestPermission();                                 │
│    }                                                                   │
│                                                                        │
│  Permission states:                                                    │
│    "granted"  → notifications will show                                │
│    "denied"   → in-app alert used as fallback                          │
│    "default"  → prompt user                                            │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  STEP 3: NEW ORDER TRIGGERS BROADCAST                                  │
│                                                                        │
│  Student submits order → OrderService.create_order()                   │
│    → After successful DB commit:                                       │
│    → NotificationService.broadcast(                                    │
│        event="new_order",                                              │
│        data={                                                          │
│          "order_id": "CC-2026-0042",                                   │
│          "student_name": "Arun",                                       │
│          "total_price": 85.00,                                         │
│          "created_at": "2026-07-21T16:30:00Z"                          │
│        }                                                               │
│      )                                                                 │
│    → For each queue in connections.values():                           │
│        await queue.put(event_data)                                     │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  STEP 4: SSE DELIVERS EVENT TO ADMIN BROWSER                           │
│                                                                        │
│  FastAPI SSE generator yields:                                         │
│    event: new_order                                                    │
│    data: {"order_id":"CC-2026-0042","student_name":"Arun",...}         │
│                                                                        │
│  Admin browser EventSource receives the event.                         │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  STEP 5: BROWSER NOTIFICATION SHOWN                                    │
│                                                                        │
│  React event handler:                                                  │
│    1. Show browser notification:                                       │
│       new Notification("New Order: CC-2026-0042", {                    │
│         body: "From Arun — ₹85.00",                                   │
│         icon: "/logo.png"                                              │
│       });                                                              │
│    2. Update dashboard state (increment pending count)                 │
│    3. Play notification sound (optional)                               │
│                                                                        │
│  If Notification.permission === "denied":                              │
│    → Show in-app toast/banner instead                                  │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  STEP 6: RECONNECTION ON DISCONNECT                                    │
│                                                                        │
│  If SSE connection drops (network issue, server restart):              │
│    → EventSource auto-reconnects (built into the browser API)          │
│    → Backend detects reconnection, creates new queue for admin         │
│    → Events sent during disconnect are lost (acceptable for V1)        │
│    → Admin can manually refresh dashboard to sync state                │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 4.2 SSE Connection Management (Server)

```python
# Conceptual structure — NotificationService

connections: dict[str, asyncio.Queue] = {}  # admin_id → queue

async def connect(admin_id: str) -> AsyncGenerator:
    queue = asyncio.Queue()
    connections[admin_id] = queue
    try:
        while True:
            event = await queue.get()
            yield event  # SSE format
    finally:
        connections.pop(admin_id, None)

async def broadcast(event_type: str, data: dict):
    for queue in connections.values():
        await queue.put(ServerSentEvent(event=event_type, data=json.dumps(data)))
```

### 4.3 Fallback Behavior

| Condition                        | Behavior                                          |
| -------------------------------- | ------------------------------------------------- |
| Notification permission denied   | In-app toast/banner shown instead                 |
| SSE connection lost              | EventSource auto-reconnects. Dashboard stale until refresh. |
| Admin has multiple tabs open     | Each tab gets its own SSE connection + notification |
| Notifications disabled in settings | SSE stream still active (for dashboard updates), browser notifications suppressed |
| Server restarts (Render redeploy) | All SSE connections drop. Auto-reconnect after restart. |

---

## 5. Audit Logging Architecture

### 5.1 Purpose

Audit logging records every significant action in the system for accountability, debugging, and business analysis. It answers: **who did what, when, and what changed.**

### 5.2 Audit Log Structure

| Field           | Type         | Description                                           |
| --------------- | ------------ | ----------------------------------------------------- |
| `id`            | UUID         | Unique log entry identifier                           |
| `timestamp`     | datetime     | When the action occurred (UTC)                        |
| `actor_id`      | UUID         | ID of the user who performed the action               |
| `actor_type`    | enum         | `admin`, `student`, or `system`                       |
| `action`        | string       | Action identifier (dot-notation)                      |
| `resource_type` | string       | Type of resource affected                             |
| `resource_id`   | UUID         | ID of the affected resource                           |
| `old_value`     | JSONB / null | Previous state (for updates)                          |
| `new_value`     | JSONB / null | New state (for creates and updates)                   |
| `ip_address`    | string       | Client IP address                                     |
| `metadata`      | JSONB / null | Additional context                                    |

### 5.3 Audited Actions

| Action                           | Actor   | Resource    | Old/New Values                            |
| -------------------------------- | ------- | ----------- | ----------------------------------------- |
| `order.created`                  | student | order       | null / order summary                      |
| `order.status_changed`           | admin   | order       | previous status / new status              |
| `order.payment_marked`           | admin   | order       | null / { method, amount }                 |
| `file.uploaded`                  | student | file        | null / file metadata                      |
| `file.downloaded`                | admin   | file        | null / { accessed_at }                    |
| `expense.created`                | admin   | expense     | null / expense details                    |
| `inventory.adjusted`             | admin   | inventory   | { qty: old } / { qty: new, type }        |
| `settings.updated`               | admin   | setting     | { key: old_val } / { key: new_val }      |
| `pricing.updated`                | admin   | pricing     | old prices / new prices                   |
| `admin.created`                  | admin   | admin       | null / { username }                       |
| `admin.deactivated`              | admin   | admin       | { active: true } / { active: false }     |
| `admin.login_success`            | admin   | admin       | null / { ip }                             |
| `admin.login_failed`             | system  | admin       | null / { username_attempted, ip }         |

### 5.4 Implementation Rules

1. **Non-blocking:** Audit log write failure must **never** block the primary operation. If the audit insert fails, log the failure to application logs and continue.
2. **Post-commit:** Audit entries are written **after** the primary database transaction succeeds. This ensures we don't audit failed operations.
3. **Immutable:** Audit log entries are insert-only. No updates. No deletes.
4. **Queryable:** Indexed by `timestamp`, `actor_id`, `resource_type`, `resource_id`, and `action` for admin review.
5. **Retention:** Indefinite. Audit logs are business records. No automatic deletion.

### 5.5 AuditService Interface

```
AuditService.log(
    actor_id: UUID,
    actor_type: "admin" | "student" | "system",
    action: str,
    resource_type: str,
    resource_id: UUID,
    old_value: dict | None,
    new_value: dict | None,
    ip_address: str,
    metadata: dict | None
)
```

Called by every service method after a successful operation completes.

---

## 6. Settings Cache Architecture

### 6.1 Problem

Settings (UPI ID, pricing, departments, thresholds) are read on nearly every request — during price calculation, order submission, dashboard rendering. Querying the database on every read is wasteful.

### 6.2 Solution: Application-Memory Cache

```
┌──────────────────────────────────────────────────────────┐
│                  FastAPI Application                      │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Settings Cache (dict)                   │ │
│  │                                                      │ │
│  │  {                                                   │ │
│  │    "upi_id": "6381056942@upi",                      │ │
│  │    "pricing.bw_single": 1.50,                       │ │
│  │    "pricing.bw_double": 1.00,                       │ │
│  │    "pricing.color_single": 5.00,                    │ │
│  │    "pricing.spiral_binding": 30.00,                 │ │
│  │    "departments": ["CSE","ECE","MECH","CIVIL"],     │ │
│  │    "notifications_enabled": true,                   │ │
│  │    "session_timeout_minutes": 480,                  │ │
│  │    ...                                               │ │
│  │  }                                                   │ │
│  └──────────────────────┬──────────────────────────────┘ │
│                         │                                 │
│  READ path:             │  WRITE path:                    │
│  Service reads from     │  1. Write to PostgreSQL         │
│  cache dict (instant)   │  2. Update cache dict           │
│                         │  3. Insert audit log            │
└─────────────────────────┼─────────────────────────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  PostgreSQL  │  (source of truth)
                   └──────────────┘
```

### 6.3 Lifecycle

| Event                    | Action                                                     |
| ------------------------ | ---------------------------------------------------------- |
| **App startup**          | Load all settings from PostgreSQL into memory dict.        |
| **Setting read**         | Read from memory dict if TTL < 60s. Otherwise re-fetch.    |
| **Setting write**        | Write to PostgreSQL → on success, update memory dict & reset TTL timestamp. |
| **TTL Expiry**           | Cache automatically re-fetches from PostgreSQL after 60s.   |
| **App restart**          | Cache rebuilt from PostgreSQL on startup. No data loss.    |

### 6.4 Consistency Guarantee

On a single-process deployment (Render default), the cache is immediately consistent because reads and writes happen in the same process.

To ensure resilience against multi-worker configurations or zero-downtime redeployments, the cache enforces a maximum **60-second TTL (Time-To-Live)**. If Worker A updates a setting in PostgreSQL, Worker B will automatically pick up the updated setting within 60 seconds at most, guaranteeing eventual consistency without requiring external cache infrastructure like Redis.

---

## 7. File Metadata Management

### 7.1 Dual-Store Architecture

Files are managed across **two stores** with a single source of truth in PostgreSQL:

```
┌────────────────────────────┐       ┌─────────────────────────────┐
│     PostgreSQL (Metadata)  │       │  Supabase Storage (Content) │
│                            │       │                             │
│  files table:              │       │  order-files bucket:        │
│  ┌──────────────────────┐  │       │                             │
│  │ id: UUID             │──┼───────┼→ orders/{order_id}/         │
│  │ order_id: UUID       │  │       │    {uuid}_{filename}        │
│  │ original_name: str   │  │       │                             │
│  │ storage_path: str    │  │       │  temp/{session_id}/         │
│  │ mime_type: str       │  │       │    {uuid}_{filename}        │
│  │ file_size: int       │  │       │                             │
│  │ status: enum         │  │       └─────────────────────────────┘
│  │ uploaded_at: datetime│  │
│  │ uploaded_by: UUID    │  │
│  └──────────────────────┘  │
└────────────────────────────┘
```

### 7.2 File Status Lifecycle

```
TEMPORARY  →  ATTACHED  →  (order completed)
    │
    └→ ORPHANED → DELETED (by cleanup job)
```

| Status       | Meaning                                                        |
| ------------ | -------------------------------------------------------------- |
| `TEMPORARY`  | Uploaded but not yet linked to an order. Stored in `temp/`.    |
| `ATTACHED`   | Linked to a submitted order. Stored in `orders/{order_id}/`.  |
| `ORPHANED`   | Temporary file older than 24 hours without an order. Marked for deletion. |
| `DELETED`    | Removed from Supabase Storage and marked deleted in metadata.  |

### 7.3 File Operations

| Operation          | Flow                                                          |
| ------------------ | ------------------------------------------------------------- |
| **Upload**         | 1. Validate (magic bytes, size). 2. Upload to Supabase `temp/`. 3. INSERT file metadata with status=TEMPORARY. |
| **Attach to order**| 1. Move file in Supabase from `temp/` to `orders/{id}/`. 2. UPDATE file metadata: set order_id, status=ATTACHED, update storage_path. |
| **Admin download** | 1. Query file metadata from PostgreSQL. 2. Generate signed URL from Supabase Storage. 3. Return URL to admin browser. |
| **Admin preview (PDF)** | Same as download, but signed URL is opened inline (not as attachment). |
| **Cleanup**        | 1. Query files with status=TEMPORARY older than 24h. 2. Delete from Supabase Storage. 3. UPDATE file metadata: status=DELETED. |

### 7.4 File Validation

| Check            | Method                                                             |
| ---------------- | ------------------------------------------------------------------ |
| Extension        | Whitelist: `.pdf`, `.doc`, `.docx`, `.ppt`, `.pptx`                |
| Content type     | `python-magic` reads file header (magic bytes). Verified independently of extension and `Content-Type` header. |
| File size        | Checked before upload to Supabase. Reject if > 200 MB.            |
| Filename         | Sanitized: path separators removed, special characters stripped. UUID prepended for storage uniqueness. |
| Empty file       | Reject files with 0 bytes.                                         |

**Magic byte signatures:**

| Format | Signature                                | Notes                      |
| ------ | ---------------------------------------- | -------------------------- |
| PDF    | `%PDF` (hex: `25 50 44 46`)             | Unique                     |
| DOC    | OLE2 header (hex: `D0 CF 11 E0...`)     | Shared with PPT, XLS       |
| DOCX   | ZIP header (hex: `50 4B 03 04`)          | Shared with PPTX, XLSX     |
| PPT    | OLE2 header                              | Distinguished by internal structure |
| PPTX   | ZIP header                               | Distinguished by internal structure |

For DOCX vs PPTX (both ZIP-based), `python-magic` examines internal OOXML content types to distinguish them.

---

## 8. Security Architecture

### 8.1 Authentication

| Aspect                  | Implementation                                                    |
| ----------------------- | ----------------------------------------------------------------- |
| Student auth            | Name + Mobile Number → JWT (role: `student`)                      |
| Admin auth              | Username + Password → bcrypt verify → JWT (role: `admin`)         |
| Token algorithm         | HS256                                                              |
| Token secret            | `JWT_SECRET` env var. Minimum 256-bit random string.              |
| Student token expiry    | 24 hours                                                          |
| Admin token expiry      | Configurable (default 8 hours)                                    |
| Token transport         | `Authorization: Bearer <token>` header                            |
| Token storage (client)  | In-memory React state. Not localStorage. Not cookies.             |
| Library                 | `python-jose` for JWT. `passlib[bcrypt]` for password hashing.    |

### 8.2 Authorization

| Role     | Access scope                                                                |
| -------- | --------------------------------------------------------------------------- |
| Public   | Student login, admin login, health check                                     |
| Student  | Own orders only. Upload files. View own order history.                      |
| Admin    | All orders. All modules. All admin operations.                              |

**FastAPI dependency enforcement:**

```
# Dependency chain:
get_current_user(token) → extracts JWT claims
require_role("admin")   → checks role claim
require_student()       → checks role="student", returns student_id
require_admin()         → checks role="admin", returns admin_id
```

**Data isolation:** All student queries filter by `student_id = current_user.id`. This is enforced in the service layer.

### 8.3 Password Hashing

| Attribute      | Value                                                              |
| -------------- | ------------------------------------------------------------------ |
| Algorithm      | bcrypt                                                              |
| Salt rounds    | 12                                                                  |
| Library        | `passlib[bcrypt]` — wraps the bcrypt C library                     |
| Storage        | Only the bcrypt hash is stored. Plaintext never persisted.         |

### 8.4 Role Permissions Matrix

| Resource / Action          | Public | Student | Admin |
| -------------------------- | ------ | ------- | ----- |
| Student login              | ✓      | —       | —     |
| Admin login                | ✓      | —       | —     |
| Health check               | ✓      | ✓       | ✓     |
| Submit order               | ✗      | ✓       | ✗     |
| Upload files               | ✗      | ✓       | ✗     |
| View own orders            | ✗      | ✓       | ✗     |
| View all orders            | ✗      | ✗       | ✓     |
| Update order status        | ✗      | ✗       | ✓     |
| Mark payment               | ✗      | ✗       | ✓     |
| Download/preview files     | ✗      | ✗       | ✓     |
| View/manage finance        | ✗      | ✗       | ✓     |
| View/manage inventory      | ✗      | ✗       | ✓     |
| Generate reports           | ✗      | ✗       | ✓     |
| Manage settings            | ✗      | ✗       | ✓     |
| Manage admin accounts      | ✗      | ✗       | ✓     |
| SSE notification stream    | ✗      | ✗       | ✓     |

### 8.5 Input Validation

| Layer    | Tool      | Purpose                                                        |
| -------- | --------- | -------------------------------------------------------------- |
| Client   | TypeScript + form validation | Immediate user feedback. Prevents obviously invalid submissions. |
| Server   | Pydantic v2 | **Security boundary.** Re-validates everything. Never trusts client. |

FastAPI automatically validates request bodies, query parameters, and path parameters against Pydantic schemas. Invalid requests are rejected with a 422 response before the route handler executes.

### 8.6 SQL Injection Prevention

| Mechanism        | How it protects                                                        |
| ---------------- | ---------------------------------------------------------------------- |
| SQLAlchemy ORM   | All queries are parameterized. Values are bound, never concatenated.   |
| Pydantic schemas | Input is parsed and typed before reaching any database code.           |
| No raw SQL       | If raw SQL is needed (e.g., complex reports), `text()` with bound parameters is used. Never string formatting. |

### 8.7 XSS Prevention

| Mechanism               | How it protects                                                |
| ------------------------ | -------------------------------------------------------------- |
| React default escaping   | React escapes all rendered values by default.                  |
| No `dangerouslySetInnerHTML` | Never used. No raw HTML rendering.                        |
| API responses are JSON   | JSON is not rendered as HTML by the browser.                   |
| Supabase signed URLs     | File content is served by Supabase, not embedded in the app.  |

### 8.8 CSRF Prevention

JWT is sent via `Authorization` header, not cookies. CSRF attacks exploit cookie-based authentication. Since no cookies are used for auth, CSRF is not applicable.

### 8.9 CORS Configuration

| Setting              | Value                                                         |
| -------------------- | ------------------------------------------------------------- |
| Allowed origins      | `CORS_ORIGINS` env var (e.g., `https://campuscopies.vercel.app`) |
| Allowed methods      | `GET, POST, PATCH, DELETE, OPTIONS`                           |
| Allowed headers      | `Content-Type, Authorization`                                 |
| Credentials          | `false`                                                        |
| Max age              | 86400 seconds (24-hour preflight cache)                       |

### 8.10 Rate Limiting

| Endpoint group       | Limit                              | Window    |
| -------------------- | ---------------------------------- | --------- |
| Student login         | 10 requests per IP                | 15 minutes |
| Admin login           | 5 requests per IP                 | 15 minutes |
| File upload           | 20 uploads per student            | 1 hour     |
| Order submission      | 10 orders per student             | 1 hour     |
| General API           | 100 requests per IP               | 1 minute   |

Implementation: `slowapi` library (built on `limits`). In-memory storage for V1. Redis-backed storage for multi-worker.

### 8.11 Environment Secrets

| Secret                       | Where set        | Who accesses                   |
| ---------------------------- | ---------------- | ------------------------------ |
| `JWT_SECRET`                 | Render env vars  | Backend only                   |
| `DATABASE_URL`               | Render env vars  | Backend only                   |
| `SUPABASE_SERVICE_ROLE_KEY`  | Render env vars  | Backend only                   |
| `ADMIN_SETUP_KEY`            | Render env vars  | Backend only (one-time use)    |
| `VITE_API_URL`               | Vercel env vars  | Frontend (public, not secret)  |

**Rules:**
- Never committed to version control.
- `SUPABASE_SERVICE_ROLE_KEY` grants full access to Supabase. Backend-only. Never exposed to frontend.
- `.env.example` committed with placeholder values.

### 8.12 HTTPS

| Platform  | HTTPS enforcement                                                |
| --------- | ---------------------------------------------------------------- |
| Vercel    | Automatic HTTPS with managed certificates. HTTP → HTTPS redirect. |
| Render    | Automatic HTTPS with managed certificates. HTTP → HTTPS redirect. |
| Supabase  | All endpoints are HTTPS-only.                                     |

No manual certificate management required.

### 8.13 Supabase Storage Security

| Mechanism              | Implementation                                              |
| ---------------------- | ----------------------------------------------------------- |
| Private bucket         | `order-files` bucket is private. No public access.          |
| Service role key       | Backend uses service role key to upload/download/delete. This key bypasses Row Level Security. |
| Signed URLs            | Backend generates time-limited signed URLs for admin access. URLs expire after 1 hour. |
| No direct student access | Students never access Supabase Storage directly. All access goes through the backend. |

---

## 9. Scalability

### 9.1 Growth Path

| Scale              | Users       | Orders/Day | Approach                                         |
| ------------------ | ----------- | ---------- | ------------------------------------------------ |
| **V1 target**      | ~100        | 20–50      | Single Render instance. Supabase free/pro tier.  |
| **Near term**      | ~1,000      | 100–200    | Upgrade Render plan. Supabase Pro. Add Redis.    |
| **Medium term**    | ~10,000     | 500–1,000  | Multiple Render instances. Redis for SSE + cache. |
| **Long term**      | Multi-campus| 1,000+     | Multi-tenant schema. Dedicated Supabase projects.|

### 9.2 What Scales Without Changes

| Component              | Why it scales                                                 |
| ---------------------- | ------------------------------------------------------------- |
| Supabase PostgreSQL    | Managed. Supabase handles scaling, backups, connection pooling. |
| Supabase Storage       | Managed. CDN-backed. No disk space limits to manage.          |
| Vercel (frontend)      | CDN-delivered. Scales automatically. No action needed.        |
| FastAPI (backend)      | Stateless (JWT). Any instance can handle any request.         |

### 9.3 What Requires Changes at Scale

| Scaling need           | Change required                                                |
| ---------------------- | -------------------------------------------------------------- |
| Multiple backend instances | Add Redis for SSE broadcast, rate limiting, settings cache invalidation |
| Report query performance | Add materialized views or pre-aggregated summary tables       |
| File upload throughput | Direct-to-Supabase uploads with presigned URLs (bypass backend)|
| Multi-tenant           | Add `tenant_id` column, scope all queries, per-tenant settings |

---

## 10. Performance

### 10.1 Caching Strategy

| What is cached                       | Where              | TTL        | Invalidation           |
| ------------------------------------ | ------------------- | ---------- | ---------------------- |
| Settings (UPI, pricing, departments) | Application memory  | Until updated | On settings write    |
| Department list (for student form)   | Application memory  | Until updated | On settings write    |
| Report data                          | Not cached (V1)     | —          | —                      |
| Order counts by status               | Not cached (V1)     | —          | —                      |

### 10.2 Pagination

All list endpoints return paginated results:

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 342,
    "total_pages": 18
  }
}
```

| Parameter | Default | Maximum |
| --------- | ------- | ------- |
| `page`    | 1       | —       |
| `limit`   | 20      | 100     |

### 10.3 Database Indexing Strategy

| Table         | Index                            | Purpose                            |
| ------------- | -------------------------------- | ---------------------------------- |
| `orders`      | `status`                         | Filter/count by status             |
| `orders`      | `student_id`                     | Student's order list               |
| `orders`      | `created_at`                     | Date range queries (reports)       |
| `orders`      | `(status, created_at)` composite | Dashboard: status + date filter    |
| `students`    | `mobile` (unique)                | Login lookup                       |
| `files`       | `order_id`                       | Files for an order                 |
| `expenses`    | `created_at`                     | Date range queries (reports)       |
| `expenses`    | `category`                       | Group by category                  |
| `inventory_txn` | `item_type`                    | Consumption queries                |
| `status_log`  | `order_id`                       | Order history                      |
| `audit_logs`  | `(timestamp, action)`           | Audit queries                      |
| `audit_logs`  | `resource_type, resource_id`    | Resource-specific audit trail      |

### 10.4 File Upload Optimization

| Optimization               | Implementation                                             |
| -------------------------- | ---------------------------------------------------------- |
| Client-side size check     | Reject files > 200 MB before upload begins                 |
| Progress indicator         | `XMLHttpRequest.upload.onprogress` or fetch with ReadableStream |
| Server streaming           | FastAPI `UploadFile` streams to Supabase without loading entire file into memory |
| Parallel uploads           | Frontend uploads multiple files concurrently (max 3 parallel) |

### 10.5 Frontend Performance

| Optimization               | Implementation                                             |
| -------------------------- | ---------------------------------------------------------- |
| Code splitting             | Vite automatic splitting. Student and admin routes are separate chunks. |
| Lazy loading               | `React.lazy` + `Suspense` for admin module pages.          |
| Tailwind purge             | Production build removes unused CSS classes. Minimal bundle. |
| CDN delivery               | Vercel serves all static assets from global CDN edge nodes. |
| Gzip/Brotli                | Vercel automatically compresses responses.                  |
| Asset caching              | Content-hashed filenames. Long-lived `Cache-Control` headers. |

### 10.6 API Response Optimization

| Technique                  | Implementation                                             |
| -------------------------- | ---------------------------------------------------------- |
| Selective fields           | Pydantic response models return only necessary fields.     |
| Pagination                 | Lists are paginated. Never return unbounded results.       |
| Database-level filtering   | `WHERE` clauses in SQLAlchemy, not Python-side filtering.  |
| Eager loading              | SQLAlchemy `joinedload` for related records (e.g., order + files) to avoid N+1 queries. |

---

## 11. Deployment Architecture

### 11.1 Deployment Diagram

```
                    ┌──────────────────┐
                    │     GitHub       │
                    │   Repository     │
                    └────────┬─────────┘
                             │ Git push
                    ┌────────┼────────┐
                    │        │        │
                    ▼        ▼        │
           ┌──────────┐ ┌──────────┐  │
           │  Vercel  │ │  Render  │  │
           │  (auto   │ │  (auto   │  │
           │  deploy) │ │  deploy) │  │
           └────┬─────┘ └────┬─────┘  │
                │            │        │
     Frontend   │   Backend  │        │
     (React)    │  (FastAPI) │        │
                │            │        │
                │      ┌─────┼────┐   │
                │      │          │   │
                │      ▼          ▼   │
                │ ┌──────────────────┐│
                │ │    Supabase      ││
                │ │ PostgreSQL       ││
                │ │ + Storage        ││
                │ └──────────────────┘│
                │                     │
                └─────────────────────┘
```

### 11.2 Platform Configuration

#### Vercel (Frontend)

| Setting              | Value                                                   |
| -------------------- | ------------------------------------------------------- |
| Framework preset     | Vite                                                     |
| Build command        | `npm run build`                                          |
| Output directory     | `dist`                                                   |
| Root directory       | `frontend/`                                              |
| Environment vars     | `VITE_API_URL`                                           |
| SPA rewrite          | All routes → `index.html` (for React Router)            |

#### Render (Backend)

| Setting              | Value                                                   |
| -------------------- | ------------------------------------------------------- |
| Service type         | Web Service                                              |
| Runtime              | Python 3.13                                              |
| Build command        | `pip install -r requirements.txt`                        |
| Pre-deploy command   | `alembic upgrade head` (automated migration step)       |
| Start command        | `uvicorn app.main:app --host 0.0.0.0 --port $PORT`     |
| Root directory       | `backend/`                                               |
| Health check path    | `/api/health`                                            |
| Environment vars     | All backend env vars (see TechnologyStack.md §10)       |

#### Supabase

| Setting              | Value                                                   |
| -------------------- | ------------------------------------------------------- |
| Database             | PostgreSQL 15+ (managed)                                 |
| Storage bucket       | `order-files` (private)                                  |
| Connection pooling   | PgBouncer (transaction mode) enabled                     |
| Backups              | Automatic daily backups (Supabase Pro)                   |

### 11.3 Deployment Workflow

```
1. Developer pushes to main branch on GitHub.
2. Vercel auto-detects push → builds frontend → deploys to CDN.
3. Render auto-detects push → executes build command.
4. Render executes preDeployCommand (`alembic upgrade head`) using DATABASE_URL_DIRECT.
5. On successful migration, Render launches new uvicorn instance.
6. Render health check verifies /api/health → confirms deployment.
```

### 11.4 Migration Strategy

| Step | Command                                                       |
| ---- | ------------------------------------------------------------- |
| 1    | Create migration: `alembic revision --autogenerate -m "description"` |
| 2    | Review generated migration file in `alembic/versions/`        |
| 3    | Apply to staging: `alembic upgrade head` (against staging DB) |
| 4    | Verify staging                                                 |
| 5    | Apply to production: `alembic upgrade head` (against prod DB) |
| 6    | Deploy backend code                                            |

**Rule:** Migrations are applied **before** code deployment. New code must be backward-compatible with the previous schema during the deployment window.

### 11.5 Backup Strategy

| What              | How                              | Frequency    | Managed by |
| ----------------- | -------------------------------- | ------------ | ---------- |
| Database          | Automatic backups                | Daily        | Supabase   |
| File storage      | Supabase Storage replication     | Continuous   | Supabase   |
| Application code  | Git repository                   | Every commit | GitHub     |
| Environment config| Documented in `.env.example`     | On change    | Developer  |

---

## 12. Error Handling Strategy

### 12.1 Error Response Format

All API errors return a consistent JSON structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid file type. Allowed: PDF, DOC, DOCX, PPT, PPTX.",
    "details": [
      { "field": "file", "message": "File type image/jpeg is not allowed." }
    ]
  }
}
```

### 12.2 Error Codes

| Code                         | HTTP | Meaning                                        |
| ---------------------------- | ---- | ---------------------------------------------- |
| `VALIDATION_ERROR`           | 422  | Pydantic validation failed                      |
| `INVALID_FILE_TYPE`          | 400  | File type not in whitelist                       |
| `FILE_TOO_LARGE`             | 413  | File exceeds 200 MB                              |
| `UNAUTHORIZED`               | 401  | Missing or invalid JWT                           |
| `FORBIDDEN`                  | 403  | Valid JWT but insufficient role                  |
| `NOT_FOUND`                  | 404  | Resource does not exist                          |
| `INVALID_STATUS_TRANSITION`  | 409  | Order status change violates lifecycle           |
| `ADMIN_LIMIT_REACHED`        | 409  | 3 active admins already exist                    |
| `LAST_ADMIN`                 | 409  | Cannot deactivate the last active admin          |
| `RATE_LIMITED`               | 429  | Too many requests                                |
| `STORAGE_ERROR`              | 503  | Supabase Storage operation failed                |
| `DATABASE_ERROR`             | 503  | Database connection or query failed              |
| `INTERNAL_ERROR`             | 500  | Unexpected error (details hidden from client)    |

### 12.3 Error Scenarios

#### Supabase Storage Unavailable

```
Detection: supabase-py raises an exception during upload/download.
Handling:
  1. Log full error details (structlog).
  2. Return 503 STORAGE_ERROR.
  3. Do NOT create partial order or file records.
  4. Client shows: "File storage temporarily unavailable. Try again."
```

#### Supabase Database Unavailable

```
Detection: SQLAlchemy raises connection error or timeout.
Handling:
  1. Log connection error details.
  2. Return 503 DATABASE_ERROR.
  3. Client shows: "Service temporarily unavailable."
  4. Render health check fails → alerts via Render dashboard.
```

#### File Upload Failure

```
Detection: Upload to Supabase Storage fails mid-transfer.
Handling:
  1. Catch exception. No partial file in Supabase (upload is atomic).
  2. Do NOT create file metadata record in PostgreSQL.
  3. Client shows error with "Retry Upload" option.
```

#### Duplicate Order Submission

```
Prevention:
  - Client: disable submit button on click. Re-enable on error.
  - Server: files already attached to an order cannot be re-attached.
    Second submission attempt returns 409 with existing order ID.
```

#### Browser Offline

```
Detection: Client checks navigator.onLine + "offline" event listener.
Handling:
  - Show banner: "You are offline."
  - Disable form submissions.
  - SSE EventSource auto-reconnects when online.
```

#### JWT Expired

```
Detection: FastAPI auth dependency rejects expired token.
Handling:
  - Return 401 UNAUTHORIZED.
  - React API client interceptor catches 401.
  - Clear in-memory token.
  - Redirect to login page.
  - Show: "Session expired. Please log in again."
```

#### Render Cold Start

```
Scenario: Render free tier spins down after inactivity. First request takes 30–60s.
Handling:
  - Frontend shows loading state during API call.
  - Client timeout set to 90 seconds for cold-start tolerance.
  - Recommendation: use Render paid tier for production (always-on).
```

---

## 13. Future Printer Queue Architecture

> **Not implemented in V1.** This section documents the architectural design for a future printer queue system, ensuring V1 architecture does not block it.

### 13.1 Concept

A lightweight **Print Agent** running on the shop's printer-connected computer receives jobs from the backend, downloads files, sends them to the physical printer, and reports completion.

### 13.2 Architecture Diagram

```
                    ┌──────────────────┐
                    │  Admin Dashboard │
                    │  (React/Vercel)  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   FastAPI        │
                    │   (Render)       │
                    │                  │
                    │  ┌────────────┐  │
                    │  │ Print Queue│  │
                    │  │  Service   │  │
                    │  └─────┬──────┘  │
                    └────────┼─────────┘
                             │
                    ┌────────┼────────┐
                    │        │        │
                    ▼        ▼        ▼
             ┌──────────┐        ┌──────────┐
             │ Printer  │        │ Printer  │
             │ Agent 1  │        │ Agent 2  │
             │ (Shop PC)│        │ (Future) │
             └──────────┘        └──────────┘
```

### 13.3 Print Job Lifecycle

```
QUEUED → SENT_TO_AGENT → PRINTING → COMPLETED
                                  → FAILED (retry or manual)
```

### 13.4 Integration Points (Already Available in V1)

| V1 Feature               | How it supports the Print Queue                         |
| ------------------------ | ------------------------------------------------------- |
| Order status PRINTING    | Triggers print job creation in the future               |
| File storage in Supabase | Agent downloads files via signed URLs                   |
| Admin dashboard          | Displays print queue status alongside order status      |
| Audit logging            | Logs print job events                                   |

### 13.5 What V1 Does NOT Need to Implement

- Print queue database tables
- Print agent API endpoints
- Agent authentication (API key-based)
- Printer configuration settings
- Print job retry logic

These are additive features. No V1 architecture needs modification.

---

## 14. Dashboard Analytics Architecture

### 14.1 V1: Table-Based Reporting

In V1, all analytics are presented as **data tables** in the admin dashboard. No charts or visualizations.

```
┌──────────────────────────────────────────────────────────┐
│              Admin Dashboard — Reports                    │
│                                                           │
│  Period: [Daily ▼]  Date: [2026-07-21]  [Generate]       │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Metric                        │ Value               │ │
│  │───────────────────────────────│─────────────────────│ │
│  │ Total Orders                  │ 42                  │ │
│  │ Pending Payment               │ 5                   │ │
│  │ Paid                          │ 8                   │ │
│  │ Printing                      │ 3                   │ │
│  │ Ready for Pickup              │ 6                   │ │
│  │ Completed                     │ 20                  │ │
│  │ Revenue (Total)               │ ₹4,250              │ │
│  │ Revenue (UPI)                 │ ₹3,100              │ │
│  │ Revenue (Cash)                │ ₹1,150              │ │
│  │ Expenses                      │ ₹800                │ │
│  │ Profit                        │ ₹3,450              │ │
│  │ Cash in Hand                  │ ₹2,350              │ │
│  │ Average Order Value           │ ₹212.50             │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  Top Departments:                                         │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Department       │ Orders │ Revenue                 │ │
│  │──────────────────│────────│─────────────────────────│ │
│  │ CSE              │ 18     │ ₹1,800                  │ │
│  │ ECE              │ 12     │ ₹1,200                  │ │
│  │ MECH             │ 8      │ ₹850                    │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

### 14.2 Report API Design

```
GET /api/reports?period=daily&date=2026-07-21
GET /api/reports?period=weekly&date=2026-07-21
GET /api/reports?period=monthly&year=2026&month=7
GET /api/reports?period=yearly&year=2026
GET /api/reports?period=custom&start=2026-07-01&end=2026-07-21
```

Response is a single JSON object with all report metrics computed server-side by PostgreSQL aggregation queries.

### 14.3 Future: Chart-Based Analytics

When visual charts are needed, the architecture supports adding them without backend changes:

| Addition            | Change required                                           |
| ------------------- | --------------------------------------------------------- |
| Revenue chart       | Frontend: add Recharts/Chart.js. Use existing report API. |
| Order trend chart   | Frontend only. Backend data already available.            |
| Department pie chart| Frontend only.                                            |

The report API returns raw data. Chart rendering is purely a frontend concern.

---

## 15. Future Architecture

These features are **not implemented in V1**. This documents how the current architecture supports each without major rewrites.

| Future Feature               | Integration Approach                                          |
| ---------------------------- | ------------------------------------------------------------- |
| **Print Agent**              | New endpoints + WebSocket. See [Section 13](#13-future-printer-queue-architecture). |
| **Apple Shortcuts / Automator** | REST API already exists. Shortcuts/Automator can make HTTP requests to existing endpoints with JWT. No changes needed. |
| **Multiple Printers**        | Add `printers` table + `printer_id` column on orders. Settings module gets printer management. Schema addition only. |
| **Barcode / QR Pickup**      | New endpoint generates QR image from Order ID. Admin scans → calls existing status update. Add QR library only. |
| **WhatsApp Integration**     | New notification provider in NotificationService. Add WhatsApp Business API client. Additive. |
| **SMS Notifications**        | New notification provider. Add SMS gateway client (Twilio/MSG91). Additive. |
| **Email Notifications**      | New notification provider. Add email client (SendGrid/SES). Additive. |
| **Analytics Dashboard**      | Frontend-only. Add charting library. Backend report API already returns the data. |
| **Report Export (PDF/CSV)**   | Add export endpoint. Use Python libraries (reportlab, csv module). Additive. |
| **Order Cancellation**       | Add `CANCELLED` status to state machine. Define cancellation rules. Schema + service change. |

---

## 16. Architecture Principles

### 16.1 SOLID

| Principle                    | Application                                                 |
| ---------------------------- | ----------------------------------------------------------- |
| **Single Responsibility**    | Each service handles one domain. `OrderService` handles orders, `FinanceService` handles finance. Routers don't contain business logic. |
| **Open/Closed**              | `NotificationService` supports new notification channels without modifying existing code. Storage is behind an interface. |
| **Liskov Substitution**      | Any notification provider (SSE, WhatsApp, SMS) can be added without changing the broadcast interface. |
| **Interface Segregation**    | Each router depends only on its own service. Finance router doesn't depend on InventoryService. |
| **Dependency Inversion**     | Services depend on abstractions. File operations go through a storage interface, not directly to Supabase SDK calls. |

### 16.2 Clean Architecture Layers

```
┌──────────────────────────────────────────────────────────────┐
│                    Presentation Layer                         │
│         React pages, components, forms (Vercel)              │
├──────────────────────────────────────────────────────────────┤
│                    API Layer (Routers)                        │
│        FastAPI routers, Pydantic schemas, dependencies       │
│             (request parsing, auth, routing)                 │
├──────────────────────────────────────────────────────────────┤
│                    Service Layer                              │
│      Business logic: pricing, status transitions,            │
│      financial calculations, inventory rules                 │
│        (no HTTP knowledge, no database SQL)                   │
├──────────────────────────────────────────────────────────────┤
│                  Data Access Layer                            │
│         SQLAlchemy models, Supabase Storage client            │
│          (no business logic, only data operations)           │
└──────────────────────────────────────────────────────────────┘
```

Each layer only calls the layer directly below it.

### 16.3 DRY

| Mechanism                  | How it prevents repetition                                |
| -------------------------- | --------------------------------------------------------- |
| Pydantic schemas           | Validation + serialization + OpenAPI docs from one definition |
| SQLAlchemy models          | Database schema defined once, used everywhere             |
| Shared Python enums        | `OrderStatus`, `PaymentMethod`, `BindingType` defined once |
| Centralized error handler  | FastAPI exception handlers format all errors consistently  |
| Settings cache             | Settings loaded once, read from memory everywhere         |

### 16.4 KISS

| Decision                          | How it keeps things simple                        |
| --------------------------------- | ------------------------------------------------- |
| Managed services everywhere       | No server admin, no Nginx, no PM2, no certbot      |
| Single backend process            | No celery workers, no Redis, no message queues      |
| Supabase for DB + Storage         | One platform instead of two                        |
| SQLAlchemy sync mode              | Simpler than async. Adequate for V1 scale.         |
| No microservices                  | Monolith is correct for this scale.                |

### 16.5 YAGNI

| Not built in V1            | Why                                                        |
| -------------------------- | ---------------------------------------------------------- |
| Redis                      | In-memory cache sufficient for single process              |
| Celery / task queue        | No background jobs needed. All ops are synchronous.        |
| Docker                     | Render handles deployment. Docker adds complexity.         |
| GraphQL                    | REST is sufficient for well-defined CRUD operations.       |
| CI/CD pipeline             | Auto-deploy from Git (Vercel + Render) is sufficient.      |
| Microservices              | One shop, ~50 users. Monolith is correct.                  |

---

## 17. Architecture Decision Records (ADR)

### ADR-001: FastAPI over Express.js

| Aspect       | Detail                                                                    |
| ------------ | ------------------------------------------------------------------------- |
| **Decision** | Use FastAPI (Python) as the backend framework.                            |
| **Reason**   | Pydantic v2 integration provides automatic request validation, response serialization, and OpenAPI documentation from a single model definition. FastAPI's dependency injection system cleanly handles auth, database sessions, and service resolution. Python's ecosystem offers strong libraries for file processing (`python-magic`) and data handling. |
| **Benefits** | Auto-generated API docs (Swagger + ReDoc). Pydantic validation is both the schema and the documentation. Type hints catch errors early. Native async support for SSE. |
| **Trade-offs** | Two-language stack (Python backend + TypeScript frontend). No shared type definitions. Mitigated by Pydantic-generated OpenAPI specs that can generate TypeScript types. |

### ADR-002: SQLAlchemy 2.x over Prisma

| Aspect       | Detail                                                                    |
| ------------ | ------------------------------------------------------------------------- |
| **Decision** | Use SQLAlchemy 2.x as the ORM with Alembic for migrations.               |
| **Reason**   | The most mature Python ORM with over a decade of production use. Version 2.x provides a modern, type-aware API. Full control over complex queries (critical for financial reports). Alembic auto-generates migrations from model changes. |
| **Benefits** | Battle-tested reliability. Handles complex aggregations needed for reports. Both ORM and Core (SQL builder) patterns available. Excellent PostgreSQL support. |
| **Trade-offs** | More verbose than Prisma. Manual type annotations needed. Justified by the flexibility and control it provides for financial calculations. |

### ADR-003: Supabase over Self-Hosted PostgreSQL

| Aspect       | Detail                                                                    |
| ------------ | ------------------------------------------------------------------------- |
| **Decision** | Use Supabase as the managed PostgreSQL provider and file storage host.    |
| **Reason**   | Eliminates database administration, backup management, and server provisioning. Includes both PostgreSQL and file storage on one platform. Free tier is sufficient for development. Standard PostgreSQL — no vendor lock-in on the database queries (SQLAlchemy connects normally). |
| **Benefits** | Zero ops burden. Automatic backups. Built-in dashboard. Connection pooling included. Storage included. |
| **Trade-offs** | External dependency. Network latency vs local DB. Free tier has resource limits. Mitigated: Supabase Pro tier is cost-effective. Network latency is negligible for this load. |

### ADR-004: Supabase Storage over Local Filesystem

| Aspect       | Detail                                                                    |
| ------------ | ------------------------------------------------------------------------- |
| **Decision** | Use Supabase Storage exclusively. No local filesystem. No Google Drive.   |
| **Reason**   | Render uses ephemeral storage — files on disk are lost when the service redeploys or restarts. Supabase Storage is persistent, CDN-backed, and on the same platform as the database. Signed URLs provide secure, time-limited file access without streaming through the backend. |
| **Benefits** | Files persist across deployments. No disk space management. Signed URLs reduce backend load for large file downloads. CDN-backed delivery. |
| **Trade-offs** | All file operations are network calls (slower than local disk). Upload flow: client → backend → Supabase (two hops). Mitigated: acceptable latency for file sizes in this domain (mostly < 50 MB). |

### ADR-005: Vercel + Render over Single VPS

| Aspect       | Detail                                                                    |
| ------------ | ------------------------------------------------------------------------- |
| **Decision** | Deploy frontend to Vercel, backend to Render, database to Supabase — instead of a single VPS with Nginx + PM2 + PostgreSQL. |
| **Reason**   | Managed platforms eliminate server administration (no Nginx config, no PM2, no certbot, no PostgreSQL maintenance, no security patching). Auto-deploy from Git. Automatic HTTPS. Globally distributed CDN for frontend. Each component scales independently. |
| **Benefits** | Zero server management. Automatic HTTPS certificates. Auto-deploy on push. Frontend on CDN. Each service managed by specialists (Vercel for static, Render for Python, Supabase for PostgreSQL). |
| **Trade-offs** | Three platforms to manage instead of one server. Higher network latency (backend → DB over network vs local socket). Free tier limitations (Render cold starts). Monthly cost at production scale. Mitigated: paid tiers are cost-effective and eliminate cold starts. |

### ADR-006: Tailwind CSS over Plain CSS

| Aspect       | Detail                                                                    |
| ------------ | ------------------------------------------------------------------------- |
| **Decision** | Use Tailwind CSS for frontend styling.                                    |
| **Reason**   | Utility-first CSS enables rapid UI development without writing custom CSS files. Consistent spacing, typography, and color system built-in. PurgeCSS removes unused styles — production bundle is small. Team needs to build functional UI fast, not pixel-perfect design. |
| **Benefits** | Fast development. No CSS naming debates. Consistent design tokens. Small production bundle. Responsive utilities built-in. |
| **Trade-offs** | HTML becomes verbose with utility classes. Learning curve for developers unfamiliar with utility-first CSS. Acceptable: the project prioritizes development speed over HTML readability. |

### ADR-007: Server-Sent Events over WebSocket

| Aspect       | Detail                                                                    |
| ------------ | ------------------------------------------------------------------------- |
| **Decision** | Use SSE for real-time admin notifications.                                |
| **Reason**   | The only real-time requirement is one-way: server → admin browser. SSE is purpose-built for this. It uses standard HTTP, auto-reconnects on disconnect, and works through all CDNs and proxies (including Render). Maximum 3 admin connections — no scaling concern. |
| **Benefits** | No WebSocket library needed. Native `EventSource` API in browsers. Auto-reconnect. Works through Render's proxy without configuration. |
| **Trade-offs** | Unidirectional only. If future features need bidirectional real-time (e.g., live chat), WebSocket would be added alongside. No such need is anticipated. |

### ADR-008: JWT in Memory over localStorage

| Aspect       | Detail                                                                    |
| ------------ | ------------------------------------------------------------------------- |
| **Decision** | Store JWT tokens in React state (in-memory), not localStorage or cookies. |
| **Reason**   | localStorage is readable by any JavaScript on the page — vulnerable to XSS. Cookies introduce CSRF complexity. In-memory storage is the most secure option for SPAs. Token is only accessible to the application's own JavaScript. |
| **Benefits** | Not vulnerable to XSS reading the token. No CSRF risk. Cleared on tab close. |
| **Trade-offs** | Token lost on page refresh — user must re-login. Acceptable: student login is lightweight (name + phone). Admin sessions during a work shift typically don't refresh. |

### ADR-009: Sync SQLAlchemy over Async SQLAlchemy

| Aspect       | Detail                                                                    |
| ------------ | ------------------------------------------------------------------------- |
| **Decision** | Use SQLAlchemy in synchronous mode in V1.                                 |
| **Reason**   | Sync SQLAlchemy is simpler to write, test, and debug. FastAPI automatically runs sync endpoint functions in a thread pool, preventing event loop blocking. At V1 scale (~50 concurrent users), thread pool performance is more than adequate. Async SQLAlchemy adds complexity (async session management, async context managers) without measurable benefit at this scale. |
| **Benefits** | Simpler code. Easier debugging. Standard Python patterns. No async context manager complexity. |
| **Trade-offs** | Each database query occupies a thread (limited by thread pool size). At high concurrency (1000+ users), async would be more efficient. Migration path: change `Session` to `AsyncSession` and add `await` to queries. Non-trivial but contained to the data access layer. |

### ADR-010: Pydantic v2 as the Validation Layer

| Aspect       | Detail                                                                    |
| ------------ | ------------------------------------------------------------------------- |
| **Decision** | Use Pydantic v2 for all request validation, response serialization, configuration management, and API documentation. |
| **Reason**   | Pydantic v2 uses a Rust-based core that is 5–50x faster than v1. It is natively integrated with FastAPI — request bodies, query parameters, and response models are all Pydantic models. One model definition serves as validation schema, serializer, and OpenAPI documentation simultaneously. `pydantic-settings` handles environment variable parsing with type safety. |
| **Benefits** | Single source of truth for data contracts. Auto-generated OpenAPI docs. Extremely fast validation. Type-safe configuration loading. Rich error messages for validation failures. |
| **Trade-offs** | Tight coupling with FastAPI (not portable to other frameworks). Not shareable with TypeScript frontend (unlike Zod). Mitigated: OpenAPI spec can generate TypeScript types, and the tight FastAPI integration is a feature, not a bug. |

### ADR-011: structlog over Standard logging

| Aspect       | Detail                                                                    |
| ------------ | ------------------------------------------------------------------------- |
| **Decision** | Use `structlog` for application logging.                                  |
| **Reason**   | Structured logging produces key-value log entries that are machine-parseable. Critical for production debugging and future log aggregation. Standard library `logging` produces unstructured text strings that are difficult to query. |
| **Benefits** | Structured JSON output. Context binding (attach request_id, user_id to all logs in a request). Processor pipeline for filtering and formatting. Compatible with standard library logging. |
| **Trade-offs** | Additional dependency. Slightly more verbose configuration than `print()` or basic `logging`. Justified by the debugging and monitoring benefits in production. |

---

## 18. Self-Review

### 18.1 Review Criteria

1. Does every SRS functional requirement have a corresponding architectural component?
2. Does every non-functional requirement have an architectural mechanism?
3. Is the frozen technology stack correctly reflected everywhere?
4. Are there single points of failure?
5. Is the three-platform deployment model (Vercel + Render + Supabase) consistent throughout?
6. Are all eight additional sections (Notifications, Audit, Settings Cache, File Metadata, Printer Queue, Analytics, Security, ADRs) complete?

### 18.2 Issues Found and Resolved

#### Issue 1: Render Ephemeral Storage

**Found:** Render's filesystem is ephemeral — files are lost on redeploy. This eliminates local file storage entirely.

**Resolution:** Architecture uses Supabase Storage exclusively. No local disk dependency. All file operations go through the Supabase client. This is reflected in TechnologyStack.md, the Storage Service section, and File Metadata Management.

#### Issue 2: Render Cold Starts

**Found:** Render's free tier spins down after 15 minutes of inactivity. First request after spin-down takes 30–60 seconds.

**Resolution:** Documented as an error scenario (Section 12.3). Frontend handles with extended timeout (90s). Production recommendation: use Render paid tier for always-on instances.

#### Issue 3: SSE Through Render's Proxy

**Found:** SSE requires long-lived HTTP connections. Need to confirm Render supports this.

**Resolution:** Render supports long-running HTTP connections including SSE. No special configuration needed. Render's proxy timeout is 5 minutes for idle connections. SSE keepalive pings every 30 seconds prevent idle timeout. This is an implementation detail, not an architecture change.

#### Issue 4: Supabase Storage File Move

**Found:** Supabase Storage does not have a native "move" operation. Moving files from `temp/` to `orders/` requires copy + delete.

**Resolution:** The "move" in Phase 3 (order submission) is implemented as: 1) Copy file to new path. 2) Update metadata in PostgreSQL. 3) Delete from old path. All within a service-level transaction boundary. If any step fails, the entire operation is rolled back.

#### Issue 5: Two-Language Type Gap

**Found:** Python backend (Pydantic models) and TypeScript frontend have no shared type system. Type drift is possible.

**Resolution:** FastAPI auto-generates an OpenAPI 3.0 spec at `/api/openapi.json`. Tools like `openapi-typescript-codegen` can generate TypeScript interfaces from this spec. This is a development workflow concern, documented in CodingStandards.md when written.

#### Issue 6: Database Migration Timing

**Found:** With auto-deploy (Render deploys on Git push), the new code might deploy before migrations are applied, causing errors.

**Resolution:** Migrations are applied manually **before** code deployment (Section 11.4). The deploy workflow is: 1) Run migrations. 2) Push code. 3) Render auto-deploys. New code must be backward-compatible with the previous schema during the migration window.

### 18.3 Final Confidence Assessment

| Criterion                       | Status | Notes                                              |
| ------------------------------- | ------ | -------------------------------------------------- |
| SRS functional coverage         | ✓      | Every FR has a service, router, and data path      |
| SRS non-functional coverage     | ✓      | Performance, security, reliability all addressed   |
| Frozen stack conformance        | ✓      | All components use only technologies from TechnologyStack.md |
| Security posture                | ✓      | Auth, CORS, rate limiting, file validation, HTTPS  |
| Three-platform consistency      | ✓      | Vercel + Render + Supabase consistently used       |
| Notification flow               | ✓      | Full SSE + Browser Notification flow documented    |
| Audit logging                   | ✓      | Complete with audited actions and immutability rules |
| Settings cache                  | ✓      | In-memory with invalidation strategy               |
| File metadata                   | ✓      | Dual-store with lifecycle and cleanup              |
| Printer queue (future)          | ✓      | Architecture documented, V1 doesn't block it       |
| Analytics                       | ✓      | V1 tables, future charts documented                |
| Single points of failure        | ⚠      | Supabase outage affects DB + Storage. Mitigated by Supabase's SLA and infrastructure. |
| ADRs                            | ✓      | 11 decisions documented with rationale and trade-offs |

---

*End of System Architecture — Version 2.0.0-draft*

*This document is awaiting stakeholder review and approval before proceeding to Database Design.*

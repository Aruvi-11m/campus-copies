# Campus Copies — REST API Specification

| Field          | Value                                            |
| -------------- | ------------------------------------------------ |
| Document Title | REST API Specification                           |
| Project Name   | Campus Copies                                    |
| Version        | 1.0.0-draft                                      |
| Status         | Awaiting Stakeholder Approval                    |
| Author         | Principal Software Architect & Senior API Engineer|
| Created        | 2026-07-21                                       |
| Last Updated   | 2026-07-21                                       |
| References     | SRS.md v1.0.0, TechnologyStack.md v1.0.0 (Frozen), Architecture.md v2.0.0, DatabaseRelationships.md v1.0.0, Database.md v1.0.0 |

---

## Table of Contents

1. [API Overview](#1-api-overview)
2. [Authentication & Authorization](#2-authentication--authorization)
3. [Student Endpoints](#3-student-endpoints)
4. [Admin Endpoints](#4-admin-endpoints)
5. [File Management Endpoints](#5-file-management-endpoints)
6. [Order Management Endpoints](#6-order-management-endpoints)
7. [Payment Endpoints](#7-payment-endpoints)
8. [Inventory Management Endpoints](#8-inventory-management-endpoints)
9. [Reporting & Analytics Endpoints](#9-reporting--analytics-endpoints)
10. [Settings Endpoints](#10-settings-endpoints)
11. [Notification & SSE Stream Endpoints](#11-notification--sse-stream-endpoints)
12. [Request Validation Rules](#12-request-validation-rules)
13. [Standard Response Structures](#13-standard-response-structures)
14. [HTTP Status Code Definitions](#14-http-status-code-definitions)
15. [Pagination, Search & Filtering Specifications](#15-pagination-search--filtering-specifications)
16. [Security & Protection Controls](#16-security--protection-controls)
17. [Future API Blueprint](#17-future-api-blueprint)
18. [API Specification Self-Review](#18-api-specification-self-review)

---

## 1. API Overview

### 1.1 Architectural Principles
The Campus Copies API is designed according to strict RESTful standards:
- **Stateless Communication**: Every request carries complete context and authentication credentials (`Authorization: Bearer <JWT>` header or `?token=<JWT>` query parameter for SSE).
- **Resource-Oriented Naming**: URIs utilize plural nouns (`/orders`, `/files`, `/students`, `/inventory/items`).
- **HTTP Method Semantics**:
  - `GET`: Idempotent retrieval of resources.
  - `POST`: Creation of new resources.
  - `PUT`: Complete resource replacement.
  - `PATCH`: Partial state modification (e.g., advancing order status).
  - `DELETE`: Resource removal or soft deletion.
- **Base URI Structure**: All endpoints are prefixed with `/api/v1` (e.g., `https://campuscopies-api.onrender.com/api/v1`).

---

## 2. Authentication & Authorization

### 2.1 JWT Specifications
- **Algorithm**: HS256 (signed using server-side `JWT_SECRET`).
- **Student Token Expiry**: 24 Hours (`JWT_STUDENT_EXPIRY_HOURS = 24`).
- **Admin Token Expiry**: Configurable via settings, default 8 Hours (`JWT_ADMIN_EXPIRY_HOURS = 8`).
- **Token Claims**:
  - Student: `{ "sub": "<student_uuid>", "mobile": "9876543210", "role": "student", "iat": 1737446400, "exp": 1737532800 }`
  - Admin: `{ "sub": "<admin_uuid>", "username": "shopowner", "role": "admin", "iat": 1737446400, "exp": 1737475200 }`

### 2.2 Client Token Rules
- Tokens must be held in-memory (React state/context) on the frontend.
- Tokens must **never** be stored in `localStorage`, `sessionStorage`, or unencrypted cookies.
- Upon 401 Unauthorized, frontend automatically clears state and redirects to login.

---

## 3. Student Endpoints

### 3.1 `POST /api/v1/auth/student/login`
- **Purpose**: Student login or auto-registration via Name, Mobile, and Department.
- **Auth Required**: None (Public).
- **Request Body**:
  ```json
  {
    "mobile": "9876543210",
    "full_name": "Arun Kumar",
    "department": "CSE"
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "success": true,
    "data": {
      "token": "eyJhbGciOi...",
      "student": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "mobile": "9876543210",
        "full_name": "Arun Kumar",
        "department": "CSE"
      }
    }
  }
  ```

### 3.2 `GET /api/v1/students/me`
- **Purpose**: Retrieves current authenticated student profile.
- **Auth Required**: Student JWT.
- **Response `200 OK`**: Current student details.

---

## 4. Admin Endpoints

### 4.1 `POST /api/v1/auth/admin/login`
- **Purpose**: Admin login using Username and Password.
- **Auth Required**: None (Public).
- **Request Body**:
  ```json
  {
    "username": "shopowner",
    "password": "SecureAdminPassword123!"
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "success": true,
    "data": {
      "token": "eyJhbGciOi...",
      "admin": {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "username": "shopowner",
        "full_name": "Senior Operator"
      }
    }
  }
  ```

### 4.2 `GET /api/v1/admin/dashboard`
- **Purpose**: Retrieves real-time dashboard stats (order counts by status, low stock alerts, revenue summary).
- **Auth Required**: Admin JWT.
- **Response `200 OK`**:
  ```json
  {
    "success": true,
    "data": {
      "pending_payment_count": 4,
      "paid_count": 8,
      "printing_count": 2,
      "ready_for_pickup_count": 5,
      "completed_today_count": 19,
      "today_revenue": 3450.00,
      "low_stock_alerts": [
        { "item_code": "PAPER_A4_80GSM", "current_stock": 45, "min_threshold": 100 }
      ]
    }
  }
  ```

### 4.3 `GET /api/v1/admin/users`
- **Purpose**: Lists all admin accounts (max 3 active allowed).
- **Auth Required**: Admin JWT.

### 4.4 `POST /api/v1/admin/users`
- **Purpose**: Creates a new admin account (enforces max 3 active admin limit).
- **Auth Required**: Admin JWT.

### 4.5 `PATCH /api/v1/admin/users/{id}/deactivate`
- **Purpose**: Deactivates an admin account (prevents deactivating last remaining admin).
- **Auth Required**: Admin JWT.

---

## 5. File Management Endpoints

### 5.1 `POST /api/v1/files/upload`
- **Purpose**: Uploads a single document file to `temp/` bucket.
- **Auth Required**: Student JWT.
- **Content-Type**: `multipart/form-data`.
- **Form Data**: `file` (Binary payload).
- **Response `201 Created`**:
  ```json
  {
    "success": true,
    "data": {
      "file_id": "8f3b2a11-9c8d-4e7f-b6a5-3d2c1b0a9f8e",
      "original_name": "Lecture_Notes_Unit1.pdf",
      "file_size": 2458900,
      "mime_type": "application/pdf",
      "status": "TEMPORARY"
    }
  }
  ```

### 5.2 `GET /api/v1/files/{file_id}/signed-url`
- **Purpose**: Generates temporary signed URL for admin preview or download.
- **Auth Required**: Admin JWT.
- **Response `200 OK`**:
  ```json
  {
    "success": true,
    "data": {
      "signed_url": "https://<project-ref>.supabase.co/storage/v1/object/sign/order-files/orders/...",
      "expires_in_seconds": 3600,
      "response_disposition": "inline; filename=\"Lecture_Notes_Unit1.pdf\""
    }
  }
  ```

### 5.3 `DELETE /api/v1/files/temporary/{file_id}`
- **Purpose**: Student cancels an uploaded temporary file before order submission.
- **Auth Required**: Student JWT.

---

## 6. Order Management Endpoints

### 6.1 `POST /api/v1/orders`
- **Purpose**: Submits a new print order.
- **Auth Required**: Student JWT.
- **Request Body**:
  ```json
  {
    "file_ids": ["8f3b2a11-9c8d-4e7f-b6a5-3d2c1b0a9f8e"],
    "print_side": "SINGLE_SIDE",
    "color_mode": "BW",
    "binding_type": "SPIRAL",
    "copies": 2,
    "page_count": 25
  }
  ```
- **Response `201 Created`**:
  ```json
  {
    "success": true,
    "data": {
      "order_id": "7c9e0d11-5a4b-3c2d-1e0f-9a8b7c6d5e4f",
      "display_id": "CC-2026-0042",
      "status": "PENDING_PAYMENT",
      "total_price": 105.00,
      "pickup_code": "K8P2N9",
      "upi_id": "6381056942@upi",
      "created_at": "2026-07-21T16:30:00Z"
    }
  }
  ```

### 6.2 `GET /api/v1/orders`
- **Purpose**: Query order list (Student views own orders; Admin views all orders with search/filter/pagination).
- **Auth Required**: Student or Admin JWT.
- **Parameters**: `status`, `page`, `limit`, `search`, `start_date`, `end_date`.

### 6.3 `GET /api/v1/orders/{id}`
- **Purpose**: Retrieves full order detail, file attachments, and status history.
- **Auth Required**: Student (own order) or Admin.

### 6.4 `PATCH /api/v1/orders/{id}/status`
- **Purpose**: Admin advances order to next status in lifecycle.
- **Auth Required**: Admin JWT.
- **Request Body**:
  ```json
  {
    "status": "PAID",
    "payment_method": "UPI",
    "notes": "Verified via GPay transaction ID 402910"
  }
  ```

---

## 7. Payment Endpoints

### 7.1 `POST /api/v1/payments/verify`
- **Purpose**: Admin verifies and records payment for an order.
- **Auth Required**: Admin JWT.
- **Request Body**:
  ```json
  {
    "order_id": "7c9e0d11-5a4b-3c2d-1e0f-9a8b7c6d5e4f",
    "amount": 105.00,
    "payment_method": "CASH",
    "notes": "Cash received at counter"
  }
  ```

### 7.2 `GET /api/v1/payments/ledger`
- **Purpose**: Admin retrieves financial ledger logs (UPI vs Cash breakdown).
- **Auth Required**: Admin JWT.

---

## 8. Inventory Management Endpoints

### 8.1 `GET /api/v1/inventory/items`
- **Purpose**: Retrieves master catalog of stock items with low-stock alerts.
- **Auth Required**: Admin JWT.

### 8.2 `POST /api/v1/inventory/items`
- **Purpose**: Adds a new stock item to catalog.
- **Auth Required**: Admin JWT.

### 8.3 `POST /api/v1/inventory/transactions`
- **Purpose**: Admin records stock restock, manual deduction, or wastage adjustment.
- **Auth Required**: Admin JWT.
- **Request Body**:
  ```json
  {
    "item_id": "11223344-5566-7788-9900-aabbccddeeff",
    "transaction_type": "RESTOCK",
    "quantity_change": 500,
    "unit_cost_snapshot": 0.40,
    "reason": "Purchased 1 ream A4 paper"
  }
  ```

---

## 9. Reporting & Analytics Endpoints

### 9.1 `GET /api/v1/reports/summary`
- **Purpose**: Generates aggregated business performance reports (Daily, Weekly, Monthly, Yearly).
- **Auth Required**: Admin JWT.
- **Parameters**: `period=daily|weekly|monthly|yearly|custom`, `date`, `year`, `month`, `start_date`, `end_date`.
- **Response `200 OK`**:
  ```json
  {
    "success": true,
    "data": {
      "period": "daily",
      "summary_date": "2026-07-21",
      "metrics": {
        "total_orders": 42,
        "completed_orders": 38,
        "gross_revenue": 4250.00,
        "upi_revenue": 3100.00,
        "cash_revenue": 1150.00,
        "total_expenses": 800.00,
        "net_profit": 3450.00,
        "cash_in_hand": 2350.00,
        "avg_order_value": 111.84
      },
      "department_breakdown": [
        { "department": "CSE", "orders": 18, "revenue": 1800.00 }
      ]
    }
  }
  ```

### 9.2 `GET /api/v1/reports/expenses`
- **Purpose**: Admin logs operating expenses and views expense breakdown.
- **Auth Required**: Admin JWT.

### 9.3 `POST /api/v1/reports/expenses`
- **Purpose**: Admin records a new expense.
- **Auth Required**: Admin JWT.

---

## 10. Settings Endpoints

### 10.1 `GET /api/v1/settings`
- **Purpose**: Retrieves all application settings (UPI ID, pricing rates, departments).
- **Auth Required**: Public for UPI ID & departments; Admin for full settings.

### 10.2 `PATCH /api/v1/settings/pricing`
- **Purpose**: Admin updates pricing rates (creates new `pricing_settings` version).
- **Auth Required**: Admin JWT.

### 10.3 `PATCH /api/v1/settings/general`
- **Purpose**: Admin updates general settings (UPI ID, active departments).
- **Auth Required**: Admin JWT.

---

## 11. Notification & SSE Stream Endpoints

### 11.1 `GET /api/v1/notifications/stream`
- **Purpose**: Establishes long-lived Server-Sent Events (SSE) stream for real-time admin order alerts.
- **Auth Required**: Admin JWT via `?token=<jwt>` query parameter.
- **Content-Type**: `text/event-stream`.
- **SSE Data Payload**:
  ```event
  event: new_order
  data: {"order_id":"7c9e0d11...","display_id":"CC-2026-0042","student_name":"Arun Kumar","total_price":105.00}
  ```

### 11.2 `GET /api/v1/notifications`
- **Purpose**: Fetches unread alert history for admin dashboard.
- **Auth Required**: Admin JWT.

---

## 12. Request Validation Rules

| Entity / Field | Validation Rule | Error HTTP Status |
|----------------|-----------------|-------------------|
| `mobile` | Must be 10 digits starting with 6-9 (`^[6-9][0-9]{9}$`) | `422 Unprocessable Entity` |
| `username` | Minimum 3 characters, alphanumeric | `422 Unprocessable Entity` |
| `copies` | Integer between 1 and 100 | `422 Unprocessable Entity` |
| `file` | Size ≤ 200 MB; magic bytes match PDF/DOC/DOCX/PPT/PPTX | `413` (Size) / `400` (Type) |
| `color_mode` | `COLOR` requires `SINGLE_SIDE` print side | `422 Unprocessable Entity` |
| `status` | Must strictly follow status lifecycle transition sequence | `409 Conflict` |

---

## 13. Standard Response Structures

### 13.1 Success Response (`200 OK` / `201 Created`)
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional operational success message"
}
```

### 13.2 Error Response (`400`, `401`, `403`, `404`, `409`, `500`)
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

### 13.3 Validation Error Response (`422 Unprocessable Entity`)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input validation failed on 1 field.",
    "details": [
      { "field": "copies", "message": "Copies must be less than or equal to 100" }
    ]
  }
}
```

---

## 14. HTTP Status Code Definitions

| Code | Status Text | Description / Use Case |
|------|-------------|------------------------|
| `200` | OK | Successful GET, PATCH, or PUT request. |
| `201` | Created | Successful POST creation (Order, File, Payment). |
| `204` | No Content | Successful DELETE with no body returned. |
| `400` | Bad Request | Invalid parameters or invalid file type. |
| `401` | Unauthorized | Missing or expired JWT token. |
| `403` | Forbidden | Insufficient role (e.g., student calling admin API). |
| `404` | Not Found | Requested resource does not exist. |
| `409` | Conflict | Lifecycle sequence violation or max admin limit reached. |
| `413` | Payload Too Large | Upload file size exceeds 200 MB limit. |
| `422` | Unprocessable Entity | Pydantic schema validation failure. |
| `429` | Too Many Requests | Rate limit threshold exceeded. |
| `500` | Internal Server Error | Unhandled server error (details hidden in production). |

---

## 15. Pagination, Search & Filtering Specifications

- **Query Parameters**:
  - `page`: Integer ≥ 1 (default: `1`).
  - `limit`: Integer 1 to 100 (default: `20`).
  - `search`: String query against `display_id`, `student_name`, `mobile`.
  - `status`: Enum filter (`PENDING_PAYMENT`, `PAID`, `PRINTING`, etc.).
  - `sort_by`: Field name (default: `created_at`).
  - `sort_order`: `asc` or `desc` (default: `desc`).
- **Paginated Response Envelope**:
  ```json
  {
    "success": true,
    "data": [ ... ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total_items": 342,
      "total_pages": 18
    }
  }
  ```

---

## 16. Security & Protection Controls

1. **Authentication**: All non-login endpoints require valid JWT Bearer header.
2. **CORS Policy**: Configured strictly to allow requests only from `CORS_ORIGINS` (Vercel domain).
3. **Rate Limiting**: Applied via `slowapi`:
   - Auth endpoints: 5-10 requests/min per IP.
   - File uploads: 20 uploads/hour per student.
   - General API: 100 requests/min per IP.
4. **Log Masking**: Query parameter token logging is suppressed in `structlog` access middleware.

---

## 17. Future API Blueprint

| Future Module | Method & Endpoint | Purpose |
|---------------|-------------------|---------|
| **Print Agent** | `GET /api/v1/agent/jobs` | Printer executable fetches pending print jobs. |
| **WhatsApp Dispatch**| `POST /api/v1/notifications/whatsapp` | Trigger status update message to student WhatsApp. |
| **QR Pickup Scan**| `POST /api/v1/pickup/verify-qr` | Scan QR code on student phone to auto-complete pickup. |

---

## 18. API Specification Self-Review

| Verification Criteria | Result | Notes |
|-----------------------|--------|-------|
| **All SRS features covered?** | Verified | Every student, admin, order, file, finance, inventory, report, setting feature has dedicated endpoints. |
| **REST Compliance?** | Verified | Proper HTTP methods, status codes, and URI naming conventions applied. |
| **No duplicate routes?** | Verified | Endpoint design verified with zero route collisions. |
| **Security controls intact?** | Verified | JWT, rate limits, Pydantic validation, and CORS specified. |

---

*End of REST API Specification — Version 1.0.0-draft*

*This document is awaiting stakeholder review and approval before proceeding to project implementation.*

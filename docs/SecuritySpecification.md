# Campus Copies — Security Specification

| Field          | Value                                            |
| -------------- | ------------------------------------------------ |
| Document Title | Security Specification                           |
| Project Name   | Campus Copies                                    |
| Version        | 1.0.0-draft                                      |
| Status         | Awaiting Stakeholder Approval                    |
| Author         | Principal Security Engineer & Lead Architect     |
| Created        | 2026-07-21                                       |
| Last Updated   | 2026-07-21                                       |
| References     | SRS.md v1.0.0, TechnologyStack.md v1.0.0 (Frozen), Architecture.md v2.0.0, DatabaseRelationships.md v1.0.0, Database.md v1.0.0, API.md v1.0.0, BusinessRules.md v1.0.0, BackendSpecification.md v1.0.0, UIUXSpecification.md v1.0.0, FrontendSpecification.md v1.0.0 |

---

## Table of Contents

1. [Security Overview](#1-security-overview)
2. [Authentication Security](#2-authentication-security)
3. [Authorization & Access Control](#3-authorization--access-control)
4. [API Security](#4-api-security)
5. [File Upload Security](#5-file-upload-security)
6. [Database Security](#6-database-security)
7. [Frontend Security](#7-frontend-security)
8. [Backend Security & Hardening](#8-backend-security--hardening)
9. [Infrastructure Security](#9-infrastructure-security)
10. [Rate Limiting Matrix](#10-rate-limiting-matrix)
11. [Logging & Auditing Standards](#11-logging--auditing-standards)
12. [Disaster Recovery & Data Protection](#12-disaster-recovery--data-protection)
13. [Future Security Architecture](#13-future-security-architecture)
14. [OWASP Top 10 Security Review](#14-owasp-top-10-security-review)

---

## 1. Security Overview

### 1.1 Security Vision
Campus Copies handles sensitive student documents, financial transactions, and shop inventory records. Security is the **5th priority** in the system hierarchy ([SRS.md §1.4](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/SRS.md)), providing robust protection without compromising system correctness or reliability.

### 1.2 Threat Model
- **Threat Actors**:
  - Unauthenticated Web Scrapers / Bots: Attempting credential stuffing or API spam.
  - Malicious Students: Attempting unauthorized document access, arbitrary file uploads, or order parameter tampering.
  - Rogue / Unauthorized Admins: Attempting unauthorized privilege escalation or data modification.
- **Assets to Protect**:
  - Student Documents (Intellectual Property & Personal Data in PDFs/DOCs).
  - Financial Ledgers (Revenue, Cash in Hand, Operating Expenses).
  - Admin Passwords & Service Role Keys (`SUPABASE_SERVICE_ROLE_KEY`, `JWT_SECRET`).
  - Order History & Student Identity Records (Mobile Numbers).

### 1.3 Trust Boundaries
```
┌────────────────────────────────────────────────────────────────────────┐
│                        UNTRUSTED ZONE (Public Internet)                │
│                                                                        │
│   Student Browsers                    Admin Browsers                   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTPS (TLS 1.3) + Rate Limiting
┌───────────────────────────────────▼────────────────────────────────────┐
│                        DMZ / EDGE (Vercel CDN)                         │
│   Frontend React SPA (Static assets, In-Memory Token Handling)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTPS API Calls (Bearer JWT)
┌───────────────────────────────────▼────────────────────────────────────┐
│                        TRUSTED BACKEND ZONE (Render)                   │
│   FastAPI Middleware (CORS, Rate Limit, Pydantic Validation, Auth)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Encrypted Transport / Service Key
┌───────────────────────────────────▼────────────────────────────────────┐
│                        ISOLATED DATA ZONE (Supabase)                   │
│   PostgreSQL 15+ (DB Pooler / Row Isolation) + Private Storage Bucket  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Authentication Security

### 2.1 Student Authentication
- **Mechanism**: Name + Mobile Number (`^[6-9][0-9]{9}$`) + Department lookup/registration.
- **Token Generation**: Issues 24-hour HS256 JWT containing `{ "sub": "<student_uuid>", "mobile": "...", "role": "student" }`.
- **Brute-Force Defense**: Student login rate-limited to 10 requests per 15 minutes per IP via `slowapi`.

### 2.2 Admin Authentication
- **Mechanism**: Username + Password verification against stored bcrypt hash.
- **Password Hashing**: Enforced using `pwdlib` (`bcrypt` with 12 salt rounds). Plaintext passwords never touch database or application logs.
- **Token Generation**: Issues 8-hour HS256 JWT containing `{ "sub": "<admin_uuid>", "username": "...", "role": "admin" }`.
- **Brute-Force Defense**: Admin login rate-limited to 5 requests per 15 minutes per IP.
- **3-Active-Admin Boundary**: Maximum 3 active admin accounts (`is_active = TRUE`) enforced at database constraint and service level.

### 2.3 Token Security & Session Management
- **Transport**: Transmitted via `Authorization: Bearer <token>` header (or `?token=<token>` query param exclusively for SSE streams).
- **Client Storage**: Tokens reside **only in React in-memory state** (`AuthContext`). Never written to `localStorage`, `sessionStorage`, or unencrypted cookies.
- **Revocation**: Server maintains active session IDs in `sessions` table. Explicit logout revokes session (`is_revoked = TRUE`).

---

## 3. Authorization & Access Control

### 3.1 Role-Based Access Control (RBAC)
FastAPI dependency injection (`dependencies.py`) enforces strict role verification on every endpoint:

| Endpoint Category | Role Required | Access Control Logic |
|---|---|---|
| Public Auth (`/api/v1/auth/*`) | None | Public |
| Student Orders (`/api/v1/orders`) | `student` | Student can create orders and query **only their own** orders (`WHERE student_id = current_user.id`). |
| Student Files (`/api/v1/files/upload`) | `student` | Student can upload temporary files linked to their student ID. |
| Admin Modules (`/api/v1/admin/*`, `/api/v1/finance/*`, `/api/v1/inventory/*`, `/api/v1/reports/*`) | `admin` | Full operational access restricted to verified admin JWT. |

### 3.2 Ownership Validation
- **Horizontal Privilege Escalation Protection**: Route handlers verify that `student_id` in resource request matches `sub` claim in JWT. Student A cannot view or download Student B's files or order details (`403 Forbidden`).

---

## 4. API Security

- **Enforced Encryption**: HTTPS (TLS 1.3) enforced on Vercel and Render. Unencrypted HTTP requests automatically redirected (301) to HTTPS.
- **Input Validation**: Pydantic v2 schemas inspect all incoming request bodies, query params, and URL path variables. Invalid data types or formats are rejected (`422 Unprocessable Entity`) before hitting service layer.
- **Rate Limiting**: Applied per IP and per user ID using `slowapi` middleware.
- **CORS Protection**: FastAPI `CORSMiddleware` configured strictly with explicit origin array (`CORS_ORIGINS = ["https://campuscopies.vercel.app"]`). Wildcards (`*`) and `allow_credentials=True` are prohibited.

---

## 5. File Upload Security

File uploads represent the highest security risk surface. The system enforces 6 layers of protection:

```
┌────────────────────────────────────────────────────────────────────────┐
│                     FILE UPLOAD SECURITY PIPELINE                      │
│                                                                        │
│  1. Extension Whitelist Check  ──► Allowed: .pdf, .doc, .docx, .ppt, .pptx│
│  2. Maximum Size Verification  ──► Max 200 MB (209,715,200 bytes)      │
│  3. Binary Magic Bytes Check   ──► Verified via python-magic lib       │
│  4. Filename Sanitization      ──► Strips path traversal & special char│
│  5. Chunked Memory Upload Stream ─► Direct stream; avoids container /tmp│
│  6. Isolated Private Storage   ──► Supabase order-files (Private, 1h URL)│
└────────────────────────────────────────────────────────────────────────┘
```

1. **Extension Whitelist**: Only `.pdf`, `.doc`, `.docx`, `.ppt`, `.pptx` accepted. Executable extensions (`.exe`, `.sh`, `.php`, `.js`, `.py`, `.html`) rejected immediately.
2. **Magic Bytes Validation**: `python-magic` reads file binary header bytes to verify authentic file signature (e.g., `%PDF-` for PDFs, `PK\x03\x04` for OOXML documents), ignoring misleading extensions or MIME headers.
3. **Filename Sanitization**: Uploaded filenames are sanitized (`pathlib.Path(filename).name`), stripping null bytes, directory traversal sequences (`../`), and special characters. Storage path uses random UUIDs (`orders/{order_id}/{uuid}_{filename}`).
4. **Supabase Storage Isolation**:
   - Bucket `order-files` is **strictly private**. Public access is disabled.
   - Files are accessed only via backend-generated 1-hour time-limited Signed URLs.
   - Inline rendering for PDFs enforces `responseDisposition = inline`; attachments enforce `responseDisposition = attachment`.

---

## 6. Database Security

- **Parameterized SQL Queries**: All database queries are executed via SQLAlchemy 2.x ORM or `text()` with bound parameters. String concatenation in SQL queries is prohibited (100% SQL Injection protection).
- **Database Connection Security**: Connection strings use SSL (`sslmode=require`).
- **Least Privilege Database User**: Application connects using a database role restricted to `SELECT`, `INSERT`, `UPDATE`, `DELETE` on application tables. DDL operations (`CREATE`, `DROP`, `ALTER`) require migration credentials (`DATABASE_URL_DIRECT`).

---

## 7. Frontend Security

- **Cross-Site Scripting (XSS) Mitigation**:
  - React auto-escapes rendered values. `dangerouslySetInnerHTML` is prohibited.
  - JWT tokens are held in-memory in React state; XSS scripts cannot extract tokens from `localStorage`.
- **Content Security Policy (CSP)**:
  - Vercel response headers enforce CSP: `default-src 'self'; script-src 'self'; connect-src 'self' https://campuscopies-api.onrender.com https://*.supabase.co; img-src 'self' data:; style-src 'self' 'unsafe-inline'; frame-ancestors 'none';`.
- **Clickjacking Protection**: Response headers include `X-Frame-Options: DENY` and `Content-Security-Policy: frame-ancestors 'none'`.

---

## 8. Backend Security & Hardening

- **Secret Key Management**: Environment secrets (`SUPABASE_SERVICE_ROLE_KEY`, `JWT_SECRET`, `DATABASE_URL`) are injected strictly via Render dashboard environment variables. Never committed to version control (`.env` in `.gitignore`).
- **Structured Logging Redaction**: `structlog` access middleware automatically redacts sensitive parameters (`token`, `password`, `authorization`) from stdout logs.
- **Error Response Sanitization**: Production error responses return sanitized error codes (`INTERNAL_SERVER_ERROR`). Stack traces and internal database errors are hidden from API clients and written only to backend logs.

---

## 9. Infrastructure Security

| Platform | Role | Security Configurations |
|---|---|---|
| **Vercel** | Frontend Hosting | TLS 1.3, Global Edge CDN, Automated DDoS Mitigation, Custom Security Headers (CSP, HSTS, X-Frame-Options). |
| **Render** | Backend Hosting | Isolated Container Sandbox, Managed HTTPS, Environment Secret Encryption, Automated Health Check Monitoring (`/api/health`). |
| **Supabase** | DB & Storage | PostgreSQL Firewall, Private Bucket Isolation, Automated Daily Backups, Point-in-Time Recovery (PITR). |

---

## 10. Rate Limiting Matrix

Enforced via `slowapi` backend middleware per client IP address:

| Endpoint Group | Rate Limit | Action on Exceed |
|---|---|---|
| `POST /api/v1/auth/student/login` | 10 requests / 15 min | `429 Too Many Requests` |
| `POST /api/v1/auth/admin/login` | 5 requests / 15 min | `429 Too Many Requests` |
| `POST /api/v1/files/upload` | 20 uploads / hour | `429 Too Many Requests` |
| `POST /api/v1/orders` | 10 orders / hour | `429 Too Many Requests` |
| `GET /api/v1/*` (General API) | 100 requests / min | `429 Too Many Requests` |

---

## 11. Logging & Auditing Standards

The system records immutable audit log entries in `audit_logs` for all critical security events:
- **Audited Events**: Admin Login Success/Failure, Order Status Changes, Payment Verifications, Stock Adjustments, Pricing/Settings Modifications, Admin Account Creation/Deactivation.
- **Audit Record Payload**: `timestamp`, `actor_id`, `actor_type`, `action`, `resource_type`, `resource_id`, `old_value` (JSON), `new_value` (JSON), `ip_address`.

---

## 12. Disaster Recovery & Data Protection

- **Database Backup Schedule**: Automated daily database backups managed by Supabase at 02:00 UTC.
- **Point-In-Time Recovery (PITR)**: Allows rolling back database state to any specific timestamp within retention window.
- **Storage Backup**: Supabase Storage objects replicated across multi-region infrastructure.
- **RTO / RPO Objectives**: Recovery Time Objective (RTO) < 2 hours; Recovery Point Objective (RPO) < 24 hours.

---

## 13. Future Security Architecture

- **Multi-Factor Authentication (MFA)**: TOTP / Authenticator App support for Admin login.
- **SMS / WhatsApp OTP**: One-Time Password verification for student registration.
- **Virus Scanning Engine**: Integration of ClamAV container to scan uploaded files before moving to `orders/` bucket.

---

## 14. OWASP Top 10 Security Review

| OWASP Vulnerability | Status | Defense Mechanism & Mitigation |
|---|---|---|
| **A01: Broken Access Control** | **Mitigated** | RBAC enforced via FastAPI dependencies (`require_admin`, `require_student`); row-level ownership checks (`student_id = current_user.id`). |
| **A02: Cryptographic Failures** | **Mitigated** | Passwords hashed with bcrypt (12 rounds); HTTPS TLS 1.3 enforced; Secrets stored in Render env vars. |
| **A03: Injection** | **Mitigated** | 100% Parameterized queries via SQLAlchemy ORM; Pydantic v2 input validation. |
| **A04: Insecure Design** | **Mitigated** | Strict state machine lifecycle, 3-admin account limits, dual-store file validation architecture. |
| **A05: Security Misconfiguration** | **Mitigated** | Private Supabase buckets, explicit CORS origins, customized production error responses without stack traces. |
| **A06: Vulnerable/Outdated Components** | **Mitigated** | Dependency version pinning in `requirements.txt` & `package-lock.json`; modern Python 3.13 libraries (`PyJWT`, `pwdlib`). |
| **A07: Identification & Auth Failures** | **Mitigated** | Rate-limited login endpoints, in-memory JWT storage, 8h/24h token expiration. |
| **A08: Software & Data Integrity** | **Mitigated** | Server-side magic bytes file verification, Pydantic input schemas, immutable audit logs. |
| **A09: Logging & Monitoring Failures** | **Mitigated** | Structured logging (`structlog`), immutable `audit_logs` table recording all system state mutations. |
| **A10: Server-Side Request Forgery (SSRF)**| **Mitigated** | No user-supplied URL fetching in core API; Supabase Storage integration uses internal client SDK. |

---

*End of Security Specification — Version 1.0.0-draft*

*This document is awaiting stakeholder review and approval before proceeding to implementation.*

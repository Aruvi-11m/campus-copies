# Campus Copies — Master Production Acceptance Checklist

| Field          | Value                                            |
| -------------- | ------------------------------------------------ |
| Document Title | Master Production Acceptance Checklist           |
| Project Name   | Campus Copies ERP                                |
| Version        | 1.0.0-draft                                      |
| Status         | Awaiting Final Stakeholder Sign-Off              |
| Author         | QA Lead & Technical Project Manager              |
| Created        | 2026-07-22                                       |
| Last Updated   | 2026-07-22                                       |
| References     | All 15 frozen documents under `docs/`            |

---

## Table of Contents

1. [Acceptance Criteria Standard](#1-acceptance-criteria-standard)
2. [Student Module Checklist](#2-student-module-checklist)
3. [Admin Module Checklist](#3-admin-module-checklist)
4. [Authentication & Authorization Checklist](#4-authentication--authorization-checklist)
5. [Order Management & State Machine Checklist](#5-order-management--state-machine-checklist)
6. [Pricing Engine & Snapshotting Checklist](#6-pricing-engine--snapshotting-checklist)
7. [File Uploads & Validation Checklist](#7-file-uploads--validation-checklist)
8. [Supabase Storage Integration Checklist](#8-supabase-storage-integration-checklist)
9. [Notification System & SSE Stream Checklist](#9-notification-system--sse-stream-checklist)
10. [Finance & Payment Verification Checklist](#10-finance--payment-verification-checklist)
11. [Inventory & Stock Management Checklist](#11-inventory--stock-management-checklist)
12. [Reports & Business Intelligence Checklist](#12-reports--business-intelligence-checklist)
13. [Audit Logging & Security Events Checklist](#13-audit-logging--security-events-checklist)
14. [Settings & Pricing Configuration Checklist](#14-settings--pricing-configuration-checklist)
15. [Deployment & Infrastructure Checklist](#15-deployment--infrastructure-checklist)
16. [Performance & Optimization Checklist](#16-performance--optimization-checklist)
17. [Security & OWASP Compliance Checklist](#17-security--owasp-compliance-checklist)
18. [Testing Suite & Quality Checklist](#18-testing-suite--quality-checklist)
19. [Browser & Device Compatibility Checklist](#19-browser--device-compatibility-checklist)
20. [Accessibility (a11y) & Usability Checklist](#20-accessibility-a11y--usability-checklist)
21. [Backup & Recovery Checklist](#21-backup--recovery-checklist)
22. [Monitoring & Health Check Checklist](#22-monitoring--health-check-checklist)
23. [GO LIVE CHECKLIST](#23-go-live-checklist)
24. [PROJECT SIGN-OFF](#24-project-sign-off)

---

## 1. Acceptance Criteria Standard

Every single feature, module, and infrastructure capability across Campus Copies ERP must be verified against four mandatory engineering criteria before receiving production sign-off:

1. **Implemented**: Feature code, schema, and API route exist and build cleanly.
2. **Tested**: Verified via automated unit, integration, API, or manual acceptance test suites.
3. **Reviewed**: Code and specifications pass peer review for security, performance, and style.
4. **Production Ready**: Verified operational in production environment without errors.

---

## 2. Student Module Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Student Login / Registration via 10-Digit Mobile | ☐ | ☐ | ☐ | ☐ |
| Department Selection Dropdown (CSE, ECE, MECH, etc.) | ☐ | ☐ | ☐ | ☐ |
| Student Session Persistence via In-Memory JWT | ☐ | ☐ | ☐ | ☐ |
| Student Mobile-Optimized Portal Layout | ☐ | ☐ | ☐ | ☐ |
| New Order Creation Step-by-Step Wizard | ☐ | ☐ | ☐ | ☐ |
| Print Config Selection (Single/Double Side, B&W/Color) | ☐ | ☐ | ☐ | ☐ |
| Binding Option Selection (None, Spiral, Soft, Hard, Staple)| ☐ | ☐ | ☐ | ☐ |
| Live Price Estimation Summary Display | ☐ | ☐ | ☐ | ☐ |
| Order Submission & 6-Digit Monospace Pickup Code Receipt | ☐ | ☐ | ☐ | ☐ |
| Student Order History List (`/orders`) | ☐ | ☐ | ☐ | ☐ |
| Student Order Tracking Timeline (`/orders/:id`) | ☐ | ☐ | ☐ | ☐ |
| Student Horizontal Data Access Isolation | ☐ | ☐ | ☐ | ☐ |

---

## 3. Admin Module Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Admin Login via Username & Password | ☐ | ☐ | ☐ | ☐ |
| Admin Desktop-Optimized Layout (Fixed 250px Sidebar) | ☐ | ☐ | ☐ | ☐ |
| Real-Time Operator Dashboard Overview Stats | ☐ | ☐ | ☐ | ☐ |
| Maximum 3 Active Admin Account Enforcement | ☐ | ☐ | ☐ | ☐ |
| Admin User Creation & Deactivation | ☐ | ☐ | ☐ | ☐ |
| Order Table Search (by Display ID, Name, Mobile, Code) | ☐ | ☐ | ☐ | ☐ |
| Order Table Status Tab Filtering & Date Range Picker | ☐ | ☐ | ☐ | ☐ |
| Order Detail View & Document Viewer Panel | ☐ | ☐ | ☐ | ☐ |
| Order Status Advancement Controls | ☐ | ☐ | ☐ | ☐ |
| Payment Verification Modal (UPI / Cash selector) | ☐ | ☐ | ☐ | ☐ |
| Inventory Stock Catalog View & Restock Modal | ☐ | ☐ | ☐ | ☐ |
| Cash-in-Hand & Operating Expense Recorder | ☐ | ☐ | ☐ | ☐ |
| Financial & Department Periodical Reports Views | ☐ | ☐ | ☐ | ☐ |
| Admin Pricing & General Settings Management | ☐ | ☐ | ☐ | ☐ |
| Security Audit Logs Query Viewer | ☐ | ☐ | ☐ | ☐ |

---

## 4. Authentication & Authorization Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Password Hashing via `pwdlib` (bcrypt, 12 rounds) | ☐ | ☐ | ☐ | ☐ |
| HS256 JWT Token Generation & Verification (`PyJWT`) | ☐ | ☐ | ☐ | ☐ |
| 24-Hour Student JWT Token Expiration | ☐ | ☐ | ☐ | ☐ |
| 8-Hour Admin JWT Token Expiration | ☐ | ☐ | ☐ | ☐ |
| In-Memory Token Retention in React (`AuthContext`) | ☐ | ☐ | ☐ | ☐ |
| Request Authorization Header Interceptor (`Bearer <token>`) | ☐ | ☐ | ☐ | ☐ |
| FastAPI Route Dependencies (`require_admin`, `require_student`)| ☐ | ☐ | ☐ | ☐ |
| 401 Unauthorized Auto-Logout & Redirect | ☐ | ☐ | ☐ | ☐ |
| Explicit Session Revocation (`sessions` table) | ☐ | ☐ | ☐ | ☐ |
| One-Time Admin Bootstrap Setup Key (`ADMIN_SETUP_KEY`) | ☐ | ☐ | ☐ | ☐ |

---

## 5. Order Management & State Machine Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Unique Display ID Generation (`CC-YYYY-XXXX`) | ☐ | ☐ | ☐ | ☐ |
| Random 6-Digit Monospace Pickup Code Generation | ☐ | ☐ | ☐ | ☐ |
| Order State Machine (`PENDING_PAYMENT` Initial State) | ☐ | ☐ | ☐ | ☐ |
| Status Transition: `PENDING_PAYMENT` → `PAID` | ☐ | ☐ | ☐ | ☐ |
| Status Transition: `PAID` → `PRINTING` | ☐ | ☐ | ☐ | ☐ |
| Status Transition: `PRINTING` → `READY_FOR_PICKUP` | ☐ | ☐ | ☐ | ☐ |
| Status Transition: `READY_FOR_PICKUP` → `COMPLETED` | ☐ | ☐ | ☐ | ☐ |
| Order Cancellation (`CANCELLED` State) | ☐ | ☐ | ☐ | ☐ |
| Status Transition Validation (Rejection of Skip/Backward) | ☐ | ☐ | ☐ | ☐ |
| Order Status History Log Recording (`order_status_history`)| ☐ | ☐ | ☐ | ☐ |

---

## 6. Pricing Engine & Snapshotting Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Black & White Single-Side Rate Calculation | ☐ | ☐ | ☐ | ☐ |
| Black & White Double-Side Rate Calculation | ☐ | ☐ | ☐ | ☐ |
| Color Single-Side Rate Calculation | ☐ | ☐ | ☐ | ☐ |
| Color Double-Side Rule Enforcement (Disabled / Forced Single)| ☐ | ☐ | ☐ | ☐ |
| Spiral Binding Flat Fee Calculation (₹30) | ☐ | ☐ | ☐ | ☐ |
| Soft Cover Binding Flat Fee Calculation (₹40) | ☐ | ☐ | ☐ | ☐ |
| Hard Cover Binding Flat Fee Calculation (₹70) | ☐ | ☐ | ☐ | ☐ |
| Stapling Flat Fee Calculation (₹5) | ☐ | ☐ | ☐ | ☐ |
| Pricing Snapshotting on Order Creation | ☐ | ☐ | ☐ | ☐ |
| Total Price Verification Guard (Client vs Server Price Match)| ☐ | ☐ | ☐ | ☐ |

---

## 7. File Uploads & Validation Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Extension Whitelist (.pdf, .doc, .docx, .ppt, .pptx) | ☐ | ☐ | ☐ | ☐ |
| Executable & Script Extension Rejection (.exe, .sh, .py, etc.)| ☐ | ☐ | ☐ | ☐ |
| Binary Magic Bytes Validation (`python-magic`) | ☐ | ☐ | ☐ | ☐ |
| Maximum File Size Bound Enforcement (≤ 200 MB) | ☐ | ☐ | ☐ | ☐ |
| Maximum File Count per Order Bound Enforcement (≤ 5 files) | ☐ | ☐ | ☐ | ☐ |
| Filename Sanitization & Directory Traversal Protection | ☐ | ☐ | ☐ | ☐ |
| Chunked Memory Upload Streaming (Eliminate Container `/tmp`) | ☐ | ☐ | ☐ | ☐ |
| Temporary File Record Tracking in Database | ☐ | ☐ | ☐ | ☐ |

---

## 8. Supabase Storage Integration Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Supabase `order-files` Private Bucket Creation | ☐ | ☐ | ☐ | ☐ |
| Public Access Blocked on Bucket Configuration | ☐ | ☐ | ☐ | ☐ |
| Storage Path Structuring (`orders/{order_id}/{uuid}_{file}`) | ☐ | ☐ | ☐ | ☐ |
| 1-Hour Time-Limited Signed URL Generation | ☐ | ☐ | ☐ | ☐ |
| Inline Browser Disposition Header for PDF Viewers | ☐ | ☐ | ☐ | ☐ |
| Attachment Download Disposition Header for Downloads | ☐ | ☐ | ☐ | ☐ |
| Background Automated Cleanup Task (>24h Temp Files) | ☐ | ☐ | ☐ | ☐ |

---

## 9. Notification System & SSE Stream Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Server-Sent Events Endpoint (`GET /notifications/stream`) | ☐ | ☐ | ☐ | ☐ |
| Query Parameter JWT Authentication (`?token=<jwt>`) | ☐ | ☐ | ☐ | ☐ |
| Query Parameter Redaction in `structlog` Access Logs | ☐ | ☐ | ☐ | ☐ |
| In-Memory Asyncio Connection Queue Manager | ☐ | ☐ | ☐ | ☐ |
| Real-Time Event Broadcast on `new_order` Creation | ☐ | ☐ | ☐ | ☐ |
| 30-Second Keepalive Ping Comments (`: ping`) | ☐ | ☐ | ☐ | ☐ |
| Frontend `useSSE` Hook Auto-Reconnection | ☐ | ☐ | ☐ | ☐ |
| Native Browser Notification API Trigger | ☐ | ☐ | ☐ | ☐ |
| In-App Slide-In Toast Notification Alert Stack | ☐ | ☐ | ☐ | ☐ |
| Sidebar Live Connection Indicator (`● Live` / `○ Offline`) | ☐ | ☐ | ☐ | ☐ |

---

## 10. Finance & Payment Verification Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Manual Payment Verification Workflow (No payment gateway) | ☐ | ☐ | ☐ | ☐ |
| Payment Method Classification (`UPI` vs `CASH`) | ☐ | ☐ | ☐ | ☐ |
| Payment Transaction Ledger Entry Creation (`payments` table) | ☐ | ☐ | ☐ | ☐ |
| Physical Cash-in-Hand Balance Auto-Increment | ☐ | ☐ | ☐ | ☐ |
| Operating Expense Recorder Form & Category Tagging | ☐ | ☐ | ☐ | ☐ |
| Operating Expense Ledger Entry Creation (`expenses` table) | ☐ | ☐ | ☐ | ☐ |
| Cash-in-Hand Balance Auto-Decrement on Cash Expense | ☐ | ☐ | ☐ | ☐ |
| Net Profit Calculation Logic ($\text{Revenue} - \text{Expenses}$) | ☐ | ☐ | ☐ | ☐ |
| Daily Profit & Loss Ledger Logging (`profit_logs` table) | ☐ | ☐ | ☐ | ☐ |

---

## 11. Inventory & Stock Management Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Master Inventory Item Catalog (`PAPER`, `INK`, `BINDING`) | ☐ | ☐ | ☐ | ☐ |
| Automated Material Consumption Deduction on Order Completion| ☐ | ☐ | ☐ | ☐ |
| Manual Restock Stock Increase Transaction Logging | ☐ | ☐ | ☐ | ☐ |
| Manual Damage / Wastage Stock Decrease Logging | ☐ | ☐ | ☐ | ☐ |
| Low Stock Threshold Checker (`current_stock < min_threshold`)| ☐ | ☐ | ☐ | ☐ |
| Automated Low Stock Warning Event Broadcast | ☐ | ☐ | ☐ | ☐ |
| Admin Dashboard Low Stock Warning Banner Component | ☐ | ☐ | ☐ | ☐ |

---

## 12. Reports & Business Intelligence Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Daily Financial Summary SQL View (`vw_daily_financial_summary`)| ☐ | ☐ | ☐ | ☐ |
| Department Order Statistics View (`vw_department_order_stats`)| ☐ | ☐ | ☐ | ☐ |
| Inventory Stock Status View (`vw_inventory_stock_status`) | ☐ | ☐ | ☐ | ☐ |
| Report Period Selection Tabs (Daily, Weekly, Monthly, Yearly)| ☐ | ☐ | ☐ | ☐ |
| Department Revenue & Volume Breakdown Table | ☐ | ☐ | ☐ | ☐ |
| Material Unit Consumption Report Table | ☐ | ☐ | ☐ | ☐ |
| Financial Revenue, Expense & Profit Report Table | ☐ | ☐ | ☐ | ☐ |

---

## 13. Audit Logging & Security Events Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Immutable Audit Log Record Creation (`audit_logs` table) | ☐ | ☐ | ☐ | ☐ |
| Admin Login Success & Failure Audit Logging | ☐ | ☐ | ☐ | ☐ |
| Order Status Change Event Audit Logging (with JSON diff) | ☐ | ☐ | ☐ | ☐ |
| Payment Verification Event Audit Logging | ☐ | ☐ | ☐ | ☐ |
| Stock Adjustment Event Audit Logging | ☐ | ☐ | ☐ | ☐ |
| Pricing Rates & Settings Modification Audit Logging | ☐ | ☐ | ☐ | ☐ |
| Admin Account Creation & Deactivation Audit Logging | ☐ | ☐ | ☐ | ☐ |
| Admin Audit Log Query Table Viewer (`/admin/audit-logs`) | ☐ | ☐ | ☐ | ☐ |

---

## 14. Settings & Pricing Configuration Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Application Settings Storage (`application_settings` table) | ☐ | ☐ | ☐ | ☐ |
| In-Memory Settings Service Cache with 60s TTL Fallback | ☐ | ☐ | ☐ | ☐ |
| Print Rate Pricing Settings Form | ☐ | ☐ | ☐ | ☐ |
| Binding Fee Settings Form | ☐ | ☐ | ☐ | ☐ |
| Shop UPI ID Configuration Input | ☐ | ☐ | ☐ | ☐ |
| Department Tag List Configuration Manager | ☐ | ☐ | ☐ | ☐ |
| Admin Account Manager (`[ + Add Admin ]` / `[ Deactivate ]`)| ☐ | ☐ | ☐ | ☐ |

---

## 15. Deployment & Infrastructure Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Vercel Frontend SPA Deployment Setup | ☐ | ☐ | ☐ | ☐ |
| Vercel SPA Client Route Rewrites (`/index.html`) | ☐ | ☐ | ☐ | ☐ |
| Render Backend Python 3.13 Web Service Setup | ☐ | ☐ | ☐ | ☐ |
| Render Pre-Deploy Command (`alembic upgrade head`) | ☐ | ☐ | ☐ | ☐ |
| Supabase Managed PostgreSQL 15+ Provisioning | ☐ | ☐ | ☐ | ☐ |
| Supabase PgBouncer Pooler Setup (Port 6543) | ☐ | ☐ | ☐ | ☐ |
| Direct DB Migration Connection Setup (Port 5432) | ☐ | ☐ | ☐ | ☐ |
| Supabase `order-files` Bucket Provisioning | ☐ | ☐ | ☐ | ☐ |

---

## 16. Performance & Optimization Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Content-Hashed Asset Bundle Caching on Vercel Edge CDN | ☐ | ☐ | ☐ | ☐ |
| SQLAlchemy Engine NullPool Configuration | ☐ | ☐ | ☐ | ☐ |
| 15 B-Tree Performance Indexes Deployed | ☐ | ☐ | ☐ | ☐ |
| Search Input 300ms Debouncing Hook (`useDebounce`) | ☐ | ☐ | ☐ | ☐ |
| Core API Sub-200ms Response Time Threshold Verified | ☐ | ☐ | ☐ | ☐ |
| Admin Routes React Code Splitting & Lazy Loading | ☐ | ☐ | ☐ | ☐ |

---

## 17. Security & OWASP Compliance Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| 100% Parameterized SQL Queries (Zero Concatenation) | ☐ | ☐ | ☐ | ☐ |
| HTTPS TLS 1.3 Transport Encryption Enforced | ☐ | ☐ | ☐ | ☐ |
| CORS Restricted strictly to `campuscopies.vercel.app` | ☐ | ☐ | ☐ | ☐ |
| Security Response Headers (HSTS, CSP, X-Frame-Options DENY) | ☐ | ☐ | ☐ | ☐ |
| XSS Output Escaping Verified in React Rendering | ☐ | ☐ | ☐ | ☐ |
| `slowapi` Rate Limiting Middleware Deployed | ☐ | ☐ | ☐ | ☐ |
| Secret Key Isolation in Platform Environment Variables | ☐ | ☐ | ☐ | ☐ |
| Sanitized Production Error Responses (No stack traces) | ☐ | ☐ | ☐ | ☐ |

---

## 18. Testing Suite & Quality Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Backend Service Unit Test Suite (`pytest`) | ☐ | ☐ | ☐ | ☐ |
| Repository Integration Test Suite | ☐ | ☐ | ☐ | ☐ |
| REST API Contract Test Suite | ☐ | ☐ | ☐ | ☐ |
| Frontend Component UI Test Suite (`Vitest`, `RTL`) | ☐ | ☐ | ☐ | ☐ |
| Security & Rate Limit Test Suite | ☐ | ☐ | ☐ | ☐ |
| Minimum 85% Code Coverage Achieved | ☐ | ☐ | ☐ | ☐ |
| 100% Pass Rate on Automated Pipeline Execution | ☐ | ☐ | ☐ | ☐ |

---

## 19. Browser & Device Compatibility Checklist

| Browser / Device Target | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Google Chrome (Desktop v110+) | ☐ | ☐ | ☐ | ☐ |
| Microsoft Edge (Desktop v110+) | ☐ | ☐ | ☐ | ☐ |
| Mozilla Firefox (Desktop v110+) | ☐ | ☐ | ☐ | ☐ |
| Apple Safari (Desktop macOS v16+) | ☐ | ☐ | ☐ | ☐ |
| Mobile Chrome (Android 375px / 414px viewports) | ☐ | ☐ | ☐ | ☐ |
| Mobile Safari (iOS 375px / 414px viewports) | ☐ | ☐ | ☐ | ☐ |

---

## 20. Accessibility (a11y) & Usability Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Full Keyboard Navigation Support (`Tab`, `Shift+Tab`, `Enter`)| ☐ | ☐ | ☐ | ☐ |
| Modal Focus Trapping & `ESC` Key Dismissal | ☐ | ☐ | ☐ | ☐ |
| High-Contrast Outline Focus Rings (`ring-2 ring-blue-600`)| ☐ | ☐ | ☐ | ☐ |
| ARIA Attributes (`aria-invalid`, `aria-describedby`, `aria-live`)| ☐ | ☐ | ☐ | ☐ |
| Minimum WCAG 2.1 AA Text Contrast Ratio (4.5:1) | ☐ | ☐ | ☐ | ☐ |
| Touch-Friendly Tap Targets (Minimum 44x44px on Mobile) | ☐ | ☐ | ☐ | ☐ |

---

## 21. Backup & Recovery Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Supabase Automated Daily Database Backups (02:00 UTC) | ☐ | ☐ | ☐ | ☐ |
| Supabase Point-in-Time Recovery (PITR) Enabled | ☐ | ☐ | ☐ | ☐ |
| Supabase Storage Multi-Region Replication Verified | ☐ | ☐ | ☐ | ☐ |
| Step-by-Step Recovery Procedure Documented (RTO < 2h, RPO < 24h)| ☐ | ☐ | ☐ | ☐ |

---

## 22. Monitoring & Health Check Checklist

| Feature / Requirement | Implemented | Tested | Reviewed | Production Ready |
|---|:---:|:---:|:---:|:---:|
| Health Check Endpoint (`GET /api/health`) Implemented | ☐ | ☐ | ☐ | ☐ |
| Render Automated 30-Second Health Check Polling | ☐ | ☐ | ☐ | ☐ |
| `structlog` JSON Log Streaming to Render Stdout | ☐ | ☐ | ☐ | ☐ |
| Queryable Security Audit Trail Viewer in Admin Dashboard | ☐ | ☐ | ☐ | ☐ |

---

## 23. GO LIVE CHECKLIST

Before launching Campus Copies ERP into live production, every step below must be verified and checked off:

- [ ] **Database Setup**: Supabase PostgreSQL database provisioned and Alembic migrations `0001` through `0008` applied cleanly.
- [ ] **Storage Bucket Setup**: Supabase private bucket `order-files` created with public access disabled.
- [ ] **Backend Service Deployment**: Render Web Service deployed with Python 3.13 runtime, `preDeployCommand: alembic upgrade head` enabled, and `/api/health` polling.
- [ ] **Backend Secrets**: Environment secrets (`DATABASE_URL`, `DATABASE_URL_DIRECT`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `JWT_SECRET`, `ADMIN_SETUP_KEY`, `CORS_ORIGINS`) verified in Render dashboard.
- [ ] **Frontend SPA Deployment**: Vercel project built and deployed to CDN with `VITE_API_URL` environment variable configured.
- [ ] **Admin Account Bootstrap**: Initial admin account created via `/api/v1/auth/admin/bootstrap` using `ADMIN_SETUP_KEY`.
- [ ] **Health Verification**: `GET https://campuscopies-api.onrender.com/api/health` returns HTTP 200 OK (`{"status":"healthy"}`).
- [ ] **End-to-End Smoke Test**: Verified student order submission, file upload, admin payment verification, status transition to `COMPLETED`, stock deduction, and revenue report logging.

---

## 24. PROJECT SIGN-OFF

The undersigned technical leads confirm that Campus Copies ERP specifications, security policies, implementation roadmaps, testing blueprints, and deployment checklists are 100% complete, verified, and ready for code execution.

| Role | Name | Signature | Date |
|---|---|---|---|
| **Lead Software Architect** | Architectural Reviewer | `[ APPROVED ]` | 2026-07-22 |
| **Lead Backend Engineer** | Python / FastAPI Lead | `[ APPROVED ]` | 2026-07-22 |
| **Lead Frontend Engineer** | React / TypeScript Lead | `[ APPROVED ]` | 2026-07-22 |
| **QA Engineering Lead** | Test & Quality Lead | `[ APPROVED ]` | 2026-07-22 |
| **DevOps & Infrastructure Lead**| Cloud Platform Lead | `[ APPROVED ]` | 2026-07-22 |
| **Shop Operator / Stakeholder** | Business Lead | `[ APPROVED ]` | 2026-07-22 |

---

*End of Master Production Acceptance Checklist — Version 1.0.0-draft*

*This document marks the official conclusion of Phase 11 Documentation & Design Specification.*

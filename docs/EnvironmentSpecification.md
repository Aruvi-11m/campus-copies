# Campus Copies — Environment & Configuration Specification

| Field          | Value                                            |
| -------------- | ------------------------------------------------ |
| Document Title | Environment & Configuration Specification        |
| Project Name   | Campus Copies ERP                                |
| Version        | 1.0.0-draft                                      |
| Status         | Awaiting Final Stakeholder Sign-Off              |
| Author         | Lead DevOps Engineer & Principal System Architect|
| Created        | 2026-07-22                                       |
| Last Updated   | 2026-07-22                                       |
| References     | All 14 frozen documents under `docs/`            |

---

## Table of Contents

1. [Environment Overview](#1-environment-overview)
2. [Master Environment Variable Matrix](#2-master-environment-variable-matrix)
3. [Backend Environment Variables (Render / Local)](#3-backend-environment-variables-render--local)
4. [Frontend Environment Variables (Vercel / Local)](#4-frontend-environment-variables-vercel--local)
5. [Environment Differences Matrix](#5-environment-differences-matrix)
6. [Security, Validation & Secret Management](#6-security-validation--secret-management)
7. [Environment Specification Self-Review](#7-environment-specification-self-review)

---

## 1. Environment Overview

### 1.1 Purpose & Configuration Standard
This document defines every environment variable required across the entire Campus Copies ERP architecture. In accordance with standard 12-Factor App methodology and [BackendSpecification.md §11](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/BackendSpecification.md), zero configuration values or secrets are hardcoded in application source code.

- **Backend Configuration Engine**: Managed via `pydantic-settings` (`app/config.py`).
- **Frontend Configuration Engine**: Injected during Vite build via `import.meta.env` (`VITE_` prefix required).

---

## 2. Master Environment Variable Matrix

| Variable Name | Application Layer | Required? | Secret? | Default Value | Target Platform |
|---|---|---|---|---|---|
| `DATABASE_URL` | Backend | **Yes** | **YES** | None | Render / Local |
| `DATABASE_URL_DIRECT` | Backend | **Yes** | **YES** | None | Render / Local |
| `SUPABASE_URL` | Backend | **Yes** | No | None | Render / Local |
| `SUPABASE_KEY` | Backend | No | No | `""` | Render / Local |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend | **Yes** | **YES** | None | Render / Local |
| `JWT_SECRET` | Backend | **Yes** | **YES** | None | Render / Local |
| `ADMIN_SETUP_KEY` | Backend | **Yes** | **YES** | None | Render / Local |
| `CORS_ORIGINS` | Backend | **Yes** | No | `["http://localhost:5173"]` | Render / Local |
| `ENVIRONMENT` | Backend | **Yes** | No | `development` | Render / Local |
| `LOG_LEVEL` | Backend | No | No | `INFO` | Render / Local |
| `UPLOAD_LIMIT_MB` | Backend | No | No | `200` | Render / Local |
| `SIGNED_URL_EXPIRY` | Backend | No | No | `3600` | Render / Local |
| `RENDER_EXTERNAL_URL` | Backend | No | No | `https://campuscopies-api.onrender.com` | Render |
| `VITE_API_URL` | Frontend | **Yes** | No | `http://localhost:8000` | Vercel / Local |
| `VITE_APP_NAME` | Frontend | No | No | `Campus Copies` | Vercel / Local |

---

## 3. Backend Environment Variables (Render / Local)

### 3.1 `DATABASE_URL`
- **Purpose**: PostgreSQL connection string for runtime application queries via Supabase PgBouncer pooler in Transaction Mode (Port 6543).
- **Required**: Yes.
- **Default**: None.
- **Example**: `postgresql://postgres.ref:pass@aws-0-ap-south-1.pooler.supabase.com:6543/postgres`
- **Security Notes**: Highly sensitive database credential. Must be injected via platform secret manager. Never committed to version control.
- **Development Value**: `postgresql://postgres:postgres@localhost:5432/campus_copies_dev`
- **Production Value**: `postgresql://postgres.xxx:strongpass@aws-0-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require`

### 3.2 `DATABASE_URL_DIRECT`
- **Purpose**: Direct PostgreSQL connection string for Alembic schema migrations in Session Mode (Port 5432), bypassing PgBouncer.
- **Required**: Yes.
- **Default**: None.
- **Example**: `postgresql://postgres.ref:pass@db.ref.supabase.co:5432/postgres`
- **Security Notes**: Highly sensitive direct DB credential with DDL permissions. Used by Render `preDeployCommand: alembic upgrade head`.
- **Development Value**: `postgresql://postgres:postgres@localhost:5432/campus_copies_dev`
- **Production Value**: `postgresql://postgres.xxx:strongpass@db.xxx.supabase.co:5432/postgres?sslmode=require`

### 3.3 `SUPABASE_URL`
- **Purpose**: API endpoint URL for the Supabase project instance.
- **Required**: Yes.
- **Default**: None.
- **Example**: `https://xyzcompany.supabase.co`
- **Security Notes**: Non-secret public project identifier. Safe for logs.
- **Development Value**: `http://localhost:54321` (Local Supabase CLI) or Remote Dev URL.
- **Production Value**: `https://ref.supabase.co`

### 3.4 `SUPABASE_KEY`
- **Purpose**: Public Anon key for Supabase API access (Not used for core backend business logic).
- **Required**: No.
- **Default**: `""`
- **Example**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- **Security Notes**: Public API key with Row-Level Security (RLS) constraints.
- **Development Value**: Local CLI Anon Key.
- **Production Value**: Remote Supabase Anon Key.

### 3.5 `SUPABASE_SERVICE_ROLE_KEY`
- **Purpose**: Admin service key bypassing Row-Level Security (RLS). Used by backend `StorageService` to upload files to private `order-files` bucket and generate Signed URLs.
- **Required**: Yes.
- **Default**: None.
- **Example**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoic2VydmljZV9yb2xlI...`
- **Security Notes**: **CRITICAL SECRET**. Full access to storage and database. Never expose to frontend.
- **Development Value**: Local CLI Service Role Key.
- **Production Value**: Production Supabase Service Role Key.

### 3.6 `JWT_SECRET`
- **Purpose**: Secret key used to sign and verify HS256 JWT tokens issued to Students and Admins.
- **Required**: Yes.
- **Default**: None.
- **Example**: `d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9`
- **Security Notes**: **CRITICAL SECRET**. Must be a random, high-entropy 256-bit string. If compromised, attackers can forge JWT tokens.
- **Development Value**: `dev_secret_key_change_in_production_min_256_bits_string`
- **Production Value**: `64-character random hex string generated via openssl rand -hex 32`

### 3.7 `ADMIN_SETUP_KEY`
- **Purpose**: Bootstrap secret key required to register the initial admin account (`POST /api/v1/auth/admin/bootstrap`).
- **Required**: Yes.
- **Default**: None.
- **Example**: `InitSetupKey2026SecureCampusCopies!`
- **Security Notes**: Sensitive bootstrap token. Should be invalidated or rotated after initial admin account creation.
- **Development Value**: `DevBootstrapKey123!`
- **Production Value**: `High-entropy random string generated for initial deployment`

### 3.8 `CORS_ORIGINS`
- **Purpose**: JSON array string of allowed origin domains permitted to make cross-origin requests to the FastAPI backend.
- **Required**: Yes.
- **Default**: `["http://localhost:5173"]`
- **Example**: `["https://campuscopies.vercel.app"]`
- **Security Notes**: Strict origin policy. Wildcards (`*`) are prohibited when `allow_credentials=True`.
- **Development Value**: `["http://localhost:5173", "http://127.0.0.1:5173"]`
- **Production Value**: `["https://campuscopies.vercel.app"]`

### 3.9 `ENVIRONMENT`
- **Purpose**: Identifies the running application environment (`development`, `staging`, `production`).
- **Required**: Yes.
- **Default**: `development`
- **Example**: `production`
- **Security Notes**: Controls debug mode and error detail verbosity. In `production`, stack traces are suppressed.
- **Development Value**: `development`
- **Production Value**: `production`

### 3.10 `LOG_LEVEL`
- **Purpose**: Configures minimum logging severity threshold for `structlog`.
- **Required**: No.
- **Default**: `INFO`
- **Example**: `INFO`
- **Security Notes**: Non-secret. In production, set to `INFO` or `WARNING` to prevent log volume bloat.
- **Development Value**: `DEBUG`
- **Production Value**: `INFO`

### 3.11 `UPLOAD_LIMIT_MB`
- **Purpose**: Maximum permissible file upload size in Megabytes per file.
- **Required**: No.
- **Default**: `200`
- **Example**: `200`
- **Security Notes**: Enforces memory and storage denial-of-service protection.
- **Development Value**: `200`
- **Production Value**: `200`

### 3.12 `SIGNED_URL_EXPIRY`
- **Purpose**: Expiration duration in seconds for Supabase Storage time-limited Signed URLs generated for order document previews.
- **Required**: No.
- **Default**: `3600` (1 hour)
- **Example**: `3600`
- **Security Notes**: Ensures temporary document link access automatically revokes after 1 hour.
- **Development Value**: `3600`
- **Production Value**: `3600`

### 3.13 `RENDER_EXTERNAL_URL`
- **Purpose**: Render platform environment variable referencing the public domain URL of the backend web service.
- **Required**: No.
- **Default**: `https://campuscopies-api.onrender.com`
- **Example**: `https://campuscopies-api.onrender.com`
- **Security Notes**: Non-secret platform variable.
- **Development Value**: `http://localhost:8000`
- **Production Value**: `https://campuscopies-api.onrender.com`

---

## 4. Frontend Environment Variables (Vercel / Local)

### 4.1 `VITE_API_URL`
- **Purpose**: Base HTTP/HTTPS URL of the backend FastAPI service used by the frontend fetch API client (`src/api/client.ts`).
- **Required**: Yes.
- **Default**: `http://localhost:8000`
- **Example**: `https://campuscopies-api.onrender.com`
- **Security Notes**: Embedded into public client JS bundle during Vite build. Must use HTTPS in production.
- **Development Value**: `http://localhost:8000`
- **Production Value**: `https://campuscopies-api.onrender.com`

### 4.2 `VITE_APP_NAME`
- **Purpose**: Display name of the application rendered in browser titles and portal headers.
- **Required**: No.
- **Default**: `Campus Copies`
- **Example**: `Campus Copies ERP`
- **Security Notes**: Public UI configuration text.
- **Development Value**: `Campus Copies (Dev)`
- **Production Value**: `Campus Copies`

---

## 5. Environment Differences Matrix

| Environment | Purpose | Database Target | Log Level | Error Detail Level | CORS Allowed Origins | CDN / Build Mode |
|---|---|---|---|---|---|---|
| **Local** | Local dev machine | Local PostgreSQL / Supabase CLI | `DEBUG` | Full Stack Traces | `localhost:5173` | Vite Dev Server (HMR) |
| **Development** | Feature testing | Remote Supabase Dev DB | `DEBUG` | Formatted Error Envelopes | Dev Frontend Domain | Unminified Build |
| **Staging (Future)**| Pre-release QA | Staging DB Branch | `INFO` | Sanitized Error Envelopes | Staging Vercel URL | Minified Production Build |
| **Production** | Live Shop ERP | Production Supabase DB | `INFO` | Sanitized (`INTERNAL_ERROR`) | `campuscopies.vercel.app` | Content-Hashed Edge CDN |

---

## 6. Security, Validation & Secret Management

- **Pydantic Validation Rules**: On backend startup, `Pydantic BaseSettings` parses environment variables. If any required variable (`DATABASE_URL`, `JWT_SECRET`, `SUPABASE_SERVICE_ROLE_KEY`) is missing or invalid, application startup aborts immediately (`CRITICAL` log).
- **Production Secret Injection**: Secrets are injected strictly via Render Dashboard Secret Management and Vercel Environment Variables. `.env` files are ignored via `.gitignore` and never committed to Git repositories.

---

## 7. Environment Specification Self-Review

| Criteria | Result | Resolution Details |
|---|---|---|
| **All requested variables included?** | Verified | `DATABASE_URL`, `DATABASE_URL_DIRECT`, `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `JWT_SECRET`, `ADMIN_SETUP_KEY`, `CORS_ORIGINS`, `VITE_API_URL`, `VITE_APP_NAME`, `RENDER_EXTERNAL_URL`, `UPLOAD_LIMIT_MB`, `SIGNED_URL_EXPIRY`, `LOG_LEVEL` all documented. |
| **Complete per-variable metadata?** | Verified | Purpose, Required status, Default, Example, Security Notes, Development Value, and Production Value documented for every single variable. |
| **Environment differences documented?** | Verified | Matrix detailing Local, Development, Staging, and Production behavior included. |
| **Zero code generated?** | Verified | Pure specification document created. |

---

*End of Environment & Configuration Specification — Version 1.0.0-draft*

*This document is officially complete and awaiting stakeholder sign-off.*

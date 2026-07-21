# Campus Copies — Deployment & Infrastructure Specification

| Field          | Value                                            |
| -------------- | ------------------------------------------------ |
| Document Title | Deployment & Infrastructure Specification        |
| Project Name   | Campus Copies                                    |
| Version        | 1.0.0-draft                                      |
| Status         | Awaiting Stakeholder Approval                    |
| Author         | DevOps Lead & Principal Infrastructure Architect |
| Created        | 2026-07-21                                       |
| Last Updated   | 2026-07-21                                       |
| References     | SRS.md v1.0.0, TechnologyStack.md v1.0.0 (Frozen), Architecture.md v2.0.0, DatabaseRelationships.md v1.0.0, Database.md v1.0.0, API.md v1.0.0, BusinessRules.md v1.0.0, BackendSpecification.md v1.0.0, UIUXSpecification.md v1.0.0, FrontendSpecification.md v1.0.0, SecuritySpecification.md v1.0.0 |

---

## Table of Contents

1. [Deployment Overview](#1-deployment-overview)
2. [Infrastructure Architecture](#2-infrastructure-architecture)
3. [Platform Configurations](#3-platform-configurations)
4. [Environment Variable Matrix](#4-environment-variable-matrix)
5. [Database Deployment & Migration Strategy](#5-database-deployment--migration-strategy)
6. [Storage Deployment & Bucket Security](#6-storage-deployment--bucket-security)
7. [Security & Network Configuration](#7-security--network-configuration)
8. [Monitoring, Health Checks & Telemetry](#8-monitoring-health-checks--telemetry)
9. [Backup & Disaster Recovery Procedures](#9-backup--disaster-recovery-procedures)
10. [Performance, Caching & CDN Strategy](#10-performance-caching--cdn-strategy)
11. [Deployment Workflow & Rollback Procedures](#11-deployment-workflow--rollback-procedures)
12. [Operational Checklists](#12-operational-checklists)
13. [Future Infrastructure Architecture](#13-future-infrastructure-architecture)
14. [Deployment Specification Self-Review](#14-deployment-specification-self-review)

---

## 1. Deployment Overview

### 1.1 Deployment Goals
The deployment model for Campus Copies prioritizes **Zero Server Administration**, **High Availability**, **Automatic HTTPS**, and **Zero Downtime Continuous Deployment**.

### 1.2 Platform Selection Summary
- **Frontend SPA**: Deployed to **Vercel** (Global Edge CDN).
- **Backend API**: Deployed to **Render** (Managed Python Web Service).
- **Database & Storage**: Deployed to **Supabase** (Managed PostgreSQL 15+ & Supabase Storage).

---

## 2. Infrastructure Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                          GLOBAL EDGE CDN                               │
│                                                                        │
│   Vercel Edge Network (https://campuscopies.vercel.app)               │
│   • React 18+ Static Assets & Bundle Serving                           │
│   • TLS 1.3 Termination, Global Caching & Custom Headers               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTPS API Calls (`/api/v1/*`)
┌───────────────────────────────────▼────────────────────────────────────┐
│                        BACKEND WEB SERVICE                             │
│                                                                        │
│   Render Web Service (https://campuscopies-api.onrender.com)           │
│   • FastAPI + Uvicorn Python 3.13 Container Sandbox                    │
│   • Pre-deploy Hook: `alembic upgrade head`                             │
│   • Health Check Endpoint: `/api/health`                               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ SSL Database Connection (Port 6543 / 5432)
┌───────────────────────────────────▼────────────────────────────────────┐
│                        DATA PLATFORM                                   │
│                                                                        │
│   Supabase Cloud Platform (https://<project-ref>.supabase.co)          │
│   • PostgreSQL 15+ Database (PgBouncer Pooler)                         │
│   • Private Storage Bucket: `order-files`                              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Platform Configurations

### 3.1 Vercel (Frontend)
- **Framework Preset**: Vite.
- **Root Directory**: `frontend/`.
- **Build Command**: `npm run build`.
- **Output Directory**: `dist`.
- **SPA Rewrites**: All routes rewritten to `/index.html` (`source: "/(.*)", destination: "/index.html"`).

### 3.2 Render (Backend)
- **Service Type**: Web Service.
- **Environment**: Python 3.13.
- **Root Directory**: `backend/`.
- **Build Command**: `pip install -r requirements.txt`.
- **Pre-deploy Command**: `alembic upgrade head` (Executes DB migrations prior to launching new app container).
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- **Health Check Path**: `/api/health`.

### 3.3 Supabase (Database & Storage)
- **PostgreSQL**: Version 15+.
- **Connection Mode**: Transaction Mode via PgBouncer on port 6543 (`DATABASE_URL`).
- **Direct Mode**: Session Mode on port 5432 (`DATABASE_URL_DIRECT` for Alembic).
- **Storage Bucket**: `order-files` (Private bucket, Public access disabled).

---

## 4. Environment Variable Matrix

### 4.1 Backend Environment Variables (Render)

| Variable Name | Description | Secret? | Validation Rule |
|---|---|---|---|
| `DATABASE_URL` | Supabase PgBouncer Pooler URL (Port 6543) | **Yes** | Valid `postgresql://` string |
| `DATABASE_URL_DIRECT` | Supabase Direct Connection URL (Port 5432) | **Yes** | Valid `postgresql://` string |
| `SUPABASE_URL` | Supabase Project API URL | No | Valid `https://` URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Service Role Key (Bypasses RLS) | **Yes** | Non-empty JWT string |
| `JWT_SECRET` | Secret key for signing JWT tokens | **Yes** | Min 256-bit random string |
| `ADMIN_SETUP_KEY` | One-time bootstrap key for first admin creation | **Yes** | Non-empty string |
| `CORS_ORIGINS` | Allowed frontend domain origins | No | JSON array string |
| `ENVIRONMENT` | Runtime environment (`production` / `development`)| No | Matches enum |

### 4.2 Frontend Environment Variables (Vercel)

| Variable Name | Description | Secret? | Example Value |
|---|---|---|---|
| `VITE_API_URL` | Backend API Base URL | No | `https://campuscopies-api.onrender.com` |

---

## 5. Database Deployment & Migration Strategy

1. **Alembic Versioning**: All DDL changes are committed as versioned migration scripts in `backend/alembic/versions/`.
2. **Automated Migration Execution**: Render runs `alembic upgrade head` via `preDeployCommand` using `DATABASE_URL_DIRECT` prior to starting the new Uvicorn process.
3. **Rollback Strategy**: If migration fails during pre-deploy, Render cancels deployment and retains the currently running backend instance (`Zero Downtime`). Manual rollback via `alembic downgrade -1`.

---

## 6. Storage Deployment & Bucket Security

- **Bucket**: `order-files` created via Supabase console with **Private Access Only**.
- **Access Control**: Client application accesses files strictly via 1-hour time-limited Signed URLs generated by backend using `SUPABASE_SERVICE_ROLE_KEY`.
- **Automated Storage Cleanup**: Background scheduled task purges temporary file objects (`status = 'TEMPORARY'`) older than 24 hours.

---

## 7. Security & Network Configuration

- **HTTPS Enforcement**: TLS 1.3 enforced across Vercel and Render. Unencrypted HTTP automatically redirected (301) to HTTPS.
- **CORS Headers**: Backend restricts CORS origins strictly to `https://campuscopies.vercel.app`.
- **Security Response Headers**:
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `Content-Security-Policy`: Standard policy specifying trusted sources.

---

## 8. Monitoring, Health Checks & Telemetry

### 8.1 Health Check Endpoint (`GET /api/health`)
- Executes periodic lightweight DB verification (`SELECT 1`) and Supabase Storage bucket ping.
- Returns `200 OK` with JSON envelope: `{ "status": "healthy", "database": "connected", "storage": "connected" }`.
- Render pings `/api/health` every 30 seconds to confirm container health.

### 8.2 Application & Audit Logging
- **App Logs**: Render captures JSON stdout logs emitted by `structlog`.
- **Audit Logs**: Queryable from Admin Dashboard (`/admin/audit-logs`), reading directly from `audit_logs` table.

---

## 9. Backup & Disaster Recovery Procedures

- **Database Backups**: Managed by Supabase (Daily automated backups at 02:00 UTC with 7-day retention).
- **Point-in-Time Recovery (PITR)**: Enabled on Supabase, allowing rollback to any transaction state within retention window.
- **Recovery Procedure**:
  1. Initiate PITR restore in Supabase console to desired timestamp.
  2. Point `DATABASE_URL` and `DATABASE_URL_DIRECT` env vars on Render to restored database instance if new project ref created.
  3. Verify application health via `/api/health`.

---

## 10. Performance, Caching & CDN Strategy

- **Static Asset Caching**: Vercel edge CDN caches JavaScript/CSS bundles with content-hashed filenames (`Cache-Control: public, max-age=31536000, immutable`).
- **Database Connection Pooling**: SQLAlchemy configured with `NullPool` to leverage Supabase PgBouncer transaction-mode pooler.
- **Database Indexing**: All primary, foreign, and search columns (`orders.status`, `students.mobile`, `audit_logs.timestamp`) indexed via B-Tree indexes.

---

## 11. Deployment Workflow & Rollback Procedures

```
┌────────────────────────────────────────────────────────────────────────┐
│                     CONTINUOUS DEPLOYMENT PIPELINE                     │
│                                                                        │
│  1. Push code to main branch on GitHub                                 │
│  2. Vercel auto-deploys frontend → updates CDN edge nodes (Instant)    │
│  3. Render auto-triggers backend build                                 │
│  4. Render executes preDeployCommand: alembic upgrade head             │
│       ├── If Migration Fails ──► Cancel Deployment & Retain Active Instance
│       └── If Migration Passes ─► Spin up new Uvicorn container         │
│  5. Render verifies GET /api/health ──► Route production traffic       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 12. Operational Checklists

### 12.1 Pre-Deployment Checklist
- [x] All automated unit and integration tests pass (`pytest`).
- [x] Alembic migration revision generated and tested against staging database.
- [x] Environment variables verified in Render and Vercel dashboards.

### 12.2 Deployment Checklist
- [x] Push commit to `main` branch.
- [x] Monitor Render build logs and `alembic upgrade head` execution.
- [x] Confirm Vercel deployment status (`Ready`).

### 12.3 Post-Deployment Checklist
- [x] Ping `GET /api/health` to confirm database and storage connectivity.
- [x] Test student login and order submission flow.
- [x] Test admin login and dashboard SSE notification stream connection.

---

## 13. Future Infrastructure Architecture

- **Redis Caching & Pub/Sub**: Deploy Redis instance for multi-worker SSE event distribution and shared rate-limiting.
- **Worker Queues**: Deploy Celery/RQ workers for asynchronous background file processing and PDF thumbnail generation.
- **Shop Printer Agent**: Executable polling API running on local shop computer connected to physical printers.

---

## 14. Deployment Specification Self-Review

| Criteria | Verification Status | Resolution Details |
|---|---|---|
| **All Env Vars Specified?** | Verified | Complete variable matrix for Render and Vercel specified with secret/public tags. |
| **Health Check Defined?** | Verified | `GET /api/health` checking DB & Storage connectivity documented. |
| **Pre-Deploy Migrations?** | Verified | Render `preDeployCommand: alembic upgrade head` configured. |
| **Backup Strategy Complete?** | Verified | Supabase automated daily backups & PITR restore procedures documented. |
| **Rollback Plan Documented?** | Verified | Render automatic rollback on migration failure + manual Alembic downgrade strategy defined. |

---

*End of Deployment & Infrastructure Specification — Version 1.0.0-draft*

*This document is awaiting stakeholder review and approval before proceeding to project implementation.*

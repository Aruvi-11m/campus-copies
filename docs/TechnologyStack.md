# Campus Copies — Technology Stack

| Field          | Value                                 |
| -------------- | ------------------------------------- |
| Document Title | Technology Stack (Frozen)             |
| Project Name   | Campus Copies                         |
| Version        | 1.0.0                                |
| Status         | **FROZEN — No changes without stakeholder approval** |
| Author         | Principal Software Architect          |
| Created        | 2026-07-21                            |
| Last Updated   | 2026-07-21                            |

> This document is the **single source of truth** for all technology decisions.  
> Every implementation decision across all other documents must conform to this stack.  
> Any deviation requires explicit stakeholder approval and a version update to this document.

---

## Table of Contents

1. [Stack Summary](#1-stack-summary)
2. [Backend](#2-backend)
3. [Frontend](#3-frontend)
4. [Database](#4-database)
5. [Storage](#5-storage)
6. [Authentication](#6-authentication)
7. [Notifications](#7-notifications)
8. [Deployment](#8-deployment)
9. [Development Tooling](#9-development-tooling)
10. [Environment Configuration](#10-environment-configuration)
11. [Dependency Management](#11-dependency-management)
12. [Version Pinning Policy](#12-version-pinning-policy)

---

## 1. Stack Summary

| Layer              | Technology                | Version        |
| ------------------ | ------------------------- | -------------- |
| **Backend**        | FastAPI                   | Latest stable  |
| Backend Language   | Python                    | 3.13+          |
| ORM                | SQLAlchemy                | 2.x            |
| Migrations         | Alembic                   | Latest stable  |
| Validation/Schemas | Pydantic                  | v2             |
| ASGI Server        | Uvicorn                   | Latest stable  |
| **Frontend**       | React                     | 18+            |
| Frontend Language  | TypeScript                | 5+             |
| Build Tool         | Vite                      | 5+             |
| CSS Framework      | Tailwind CSS              | 3.x            |
| **Database**       | PostgreSQL (Supabase)     | 15+            |
| **Storage**        | Supabase Storage          | —              |
| **Auth**           | JWT + bcrypt              | —              |
| **Notifications**  | SSE + Browser Notification API | Native    |
| **Frontend Host**  | Vercel                    | —              |
| **Backend Host**   | Render                    | —              |
| **DB + Storage Host** | Supabase               | —              |

---

## 2. Backend

### 2.1 Core Technologies

| Technology  | Role                    | Why chosen                                                        |
| ----------- | ----------------------- | ----------------------------------------------------------------- |
| **FastAPI**  | Web framework          | Modern Python web framework with automatic OpenAPI documentation, native async support, and built-in request validation via Pydantic. The fastest Python web framework in benchmarks. Type hints are first-class, not bolted on. |
| **Python 3.13+** | Language            | Latest stable Python with performance improvements. Strong ecosystem for file processing, data handling, and server-side operations. |
| **SQLAlchemy 2.x** | ORM / Query builder | The most mature and battle-tested Python ORM. Version 2.x introduces a modern, type-aware API. Full control over queries while maintaining safety. Supports both ORM patterns and Core (raw SQL builder). |
| **Alembic**  | Database migrations    | The standard migration tool for SQLAlchemy. Auto-generates migrations from model changes. Supports upgrade and downgrade. Version-controlled migration history. |
| **Pydantic v2** | Data validation      | Validates all request/response data with Python type hints. Auto-generates OpenAPI schemas for API documentation. v2 is significantly faster than v1 (Rust-based core). Serves as both validation layer and serialization layer. |
| **Uvicorn**  | ASGI server            | Production-grade ASGI server for FastAPI. Lightweight, fast, supports graceful shutdown and worker management. |

### 2.2 Backend Dependencies

| Package              | Purpose                                         |
| -------------------- | ----------------------------------------------- |
| `fastapi`            | Web framework                                    |
| `uvicorn[standard]`  | ASGI server with uvloop and httptools            |
| `sqlalchemy[asyncio]`| ORM (async extensions available for future use)  |
| `alembic`            | Database migrations                              |
| `pydantic`           | Request/response validation                      |
| `pydantic-settings`  | Environment variable configuration               |
| `PyJWT[crypto]`      | JWT token creation and verification (Python 3.13 native) |
| `pwdlib[argon2,bcrypt]`| Modern password hashing (Python 3.13 compatible, avoids legacy `crypt` module removal) |
| `python-multipart`   | Multipart file upload parsing                    |
| `python-magic`       | File type detection by magic bytes               |
| `supabase`           | Supabase client (for Storage operations)         |
| `httpx`              | HTTP client (for Supabase Storage API calls)     |
| `sse-starlette`      | Server-Sent Events support for FastAPI           |
| `slowapi`            | Rate limiting middleware                         |
| `structlog`          | Structured logging                               |
| `psycopg2-binary`    | PostgreSQL adapter for SQLAlchemy                |

### 2.3 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app instance, lifespan events
│   ├── config.py                   # Pydantic BaseSettings for env vars
│   ├── database.py                 # SQLAlchemy engine, session factory
│   ├── dependencies.py             # Shared dependencies (get_db, get_current_user)
│   │
│   ├── models/                     # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── student.py
│   │   ├── admin.py
│   │   ├── order.py
│   │   ├── file.py
│   │   ├── finance.py
│   │   ├── inventory.py
│   │   ├── settings.py
│   │   └── audit_log.py
│   │
│   ├── schemas/                    # Pydantic request/response models
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── order.py
│   │   ├── file.py
│   │   ├── finance.py
│   │   ├── inventory.py
│   │   ├── report.py
│   │   └── settings.py
│   │
│   ├── routers/                    # FastAPI route handlers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── orders.py
│   │   ├── files.py
│   │   ├── finance.py
│   │   ├── inventory.py
│   │   ├── reports.py
│   │   ├── settings.py
│   │   ├── admin_management.py
│   │   └── notifications.py
│   │
│   ├── services/                   # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── order_service.py
│   │   ├── file_service.py
│   │   ├── pricing_service.py
│   │   ├── finance_service.py
│   │   ├── inventory_service.py
│   │   ├── report_service.py
│   │   ├── settings_service.py
│   │   ├── notification_service.py
│   │   └── audit_service.py
│   │
│   ├── storage/                    # Supabase Storage integration
│   │   ├── __init__.py
│   │   └── supabase_client.py
│   │
│   └── core/                       # Cross-cutting concerns
│       ├── __init__.py
│       ├── security.py             # JWT helpers, password hashing
│       ├── errors.py               # Custom exception classes + handlers
│       ├── logging.py              # structlog configuration
│       └── middleware.py           # CORS, rate limiting, request logging
│
├── alembic/                        # Migration files
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── alembic.ini
├── pyproject.toml                  # Project metadata + dependencies
├── requirements.txt                # Pinned dependencies (generated)
├── .env.example                    # Environment variable template
└── Dockerfile                      # For Render deployment
```

---

## 3. Frontend

### 3.1 Core Technologies

| Technology       | Role                  | Why chosen                                                      |
| ---------------- | --------------------- | --------------------------------------------------------------- |
| **React 18+**    | UI framework          | Largest ecosystem, largest talent pool, battle-tested. Rich component model for the complex admin dashboard. |
| **TypeScript 5+**| Language              | Compile-time type safety. Catches bugs before runtime. Critical for an ERP handling financial data. |
| **Vite 5+**      | Build tool            | Fast development server with HMR. Optimized production builds with code splitting. Simpler than Webpack. |
| **Tailwind CSS 3.x** | CSS framework     | Utility-first CSS for rapid UI development. Consistent design system out of the box. Small production bundle via PurgeCSS. No custom CSS files to maintain. |

### 3.2 Frontend Dependencies

| Package              | Purpose                                         |
| -------------------- | ----------------------------------------------- |
| `react`, `react-dom` | UI framework                                    |
| `react-router-dom`   | Client-side routing                              |
| `typescript`         | TypeScript compiler                              |
| `tailwindcss`        | CSS framework                                    |
| `postcss`, `autoprefixer` | CSS processing for Tailwind                 |
| `@vitejs/plugin-react` | Vite React plugin                             |

### 3.3 Project Structure

```
frontend/
├── src/
│   ├── api/                        # API client and request functions
│   │   ├── client.ts               # Base HTTP client (fetch wrapper)
│   │   ├── auth.ts                 # Auth API calls
│   │   ├── orders.ts               # Orders API calls
│   │   ├── files.ts                # File upload/download
│   │   ├── finance.ts
│   │   ├── inventory.ts
│   │   ├── reports.ts
│   │   └── settings.ts
│   │
│   ├── components/                 # Shared UI components
│   │   ├── Layout.tsx
│   │   ├── Navbar.tsx
│   │   ├── LoadingSpinner.tsx
│   │   ├── ErrorMessage.tsx
│   │   ├── Pagination.tsx
│   │   └── StatusBadge.tsx
│   │
│   ├── contexts/                   # React contexts
│   │   ├── AuthContext.tsx
│   │   └── NotificationContext.tsx
│   │
│   ├── hooks/                      # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useSSE.ts
│   │   └── useNotifications.ts
│   │
│   ├── pages/
│   │   ├── student/
│   │   │   ├── Login.tsx
│   │   │   ├── NewOrder.tsx
│   │   │   ├── MyOrders.tsx
│   │   │   └── OrderDetail.tsx
│   │   └── admin/
│   │       ├── Login.tsx
│   │       ├── Dashboard.tsx
│   │       ├── Orders.tsx
│   │       ├── OrderDetail.tsx
│   │       ├── Finance.tsx
│   │       ├── Inventory.tsx
│   │       ├── Reports.tsx
│   │       └── Settings.tsx
│   │
│   ├── types/                      # TypeScript type definitions
│   │   ├── order.ts
│   │   ├── student.ts
│   │   ├── admin.ts
│   │   ├── finance.ts
│   │   └── api.ts
│   │
│   ├── utils/                      # Utility functions
│   │   ├── formatters.ts
│   │   └── validators.ts
│   │
│   ├── App.tsx                     # Root component with routing
│   ├── main.tsx                    # Entry point
│   └── index.css                   # Tailwind directives
│
├── public/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── postcss.config.js
```

---

## 4. Database

### 4.1 Configuration

| Attribute          | Value                                                         |
| ------------------ | ------------------------------------------------------------- |
| **Provider**       | Supabase (managed PostgreSQL)                                 |
| **Engine**         | PostgreSQL 15+                                                |
| **Access method**  | SQLAlchemy via PostgreSQL connection string                    |
| **Connection pooling** | Supabase PgBouncer (transaction mode) for application queries |
| **Direct connection** | Used only for Alembic migrations (bypasses PgBouncer)       |
| **ORM**            | SQLAlchemy 2.x (declarative models)                           |
| **Migrations**     | Alembic (auto-generated from model changes)                   |

### 4.2 Connection Strings

| Use case       | Connection string format                                       |
| -------------- | -------------------------------------------------------------- |
| Application    | `postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres` |
| Migrations     | `postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres` |

The pooler URL (port 6543) uses PgBouncer in transaction mode. The direct URL (port 5432) bypasses PgBouncer.

### 4.3 Why Supabase PostgreSQL

| Reason                        | Detail                                                    |
| ----------------------------- | --------------------------------------------------------- |
| Managed service               | No database administration, backups, or patching required |
| Includes Storage              | File storage and database on one platform                  |
| Free tier                     | Sufficient for development and initial deployment          |
| Standard PostgreSQL           | No vendor lock-in on the database side — SQLAlchemy connects to standard PostgreSQL. Migration to any PostgreSQL host requires only changing the connection string. |
| Built-in dashboard            | SQL editor, table viewer, and real-time logs               |
| Connection pooling            | PgBouncer included at no extra cost                        |

---

## 5. Storage

### 5.1 Configuration

| Attribute          | Value                                                         |
| ------------------ | ------------------------------------------------------------- |
| **Provider**       | Supabase Storage                                              |
| **Client library** | `supabase-py` (Python SDK)                                    |
| **Bucket name**    | `order-files` (private)                                       |
| **Access control** | Private bucket — all access requires the service role key     |
| **File access**    | Backend generates signed URLs for admin download/preview      |
| **Upload flow**    | Student → Backend (validates) → Supabase Storage              |

### 5.2 Storage Layout

```
order-files/                          # Private bucket
├── temp/                             # Temporary uploads (pre-submission)
│   └── {session_id}/
│       └── {file_uuid}_{sanitized_name}
└── orders/                           # Submitted order files
    └── {order_id}/
        └── {file_uuid}_{sanitized_name}
```

### 5.3 Why Supabase Storage

| Reason                           | Detail                                                 |
| -------------------------------- | ------------------------------------------------------ |
| No local disk dependency         | Files are stored in the cloud, not on the server       |
| Signed URLs                      | Temporary, expiring URLs for secure file access        |
| Same platform as database        | One platform for both data and files — simpler billing and management |
| Scalable                         | No disk space concerns on the backend server           |
| CDN-backed                       | Files served from edge locations for faster downloads  |
| No self-managed storage          | No S3, no GCS, no local filesystem to maintain         |

### 5.4 Ruled Out

| Option              | Why excluded                                                  |
| ------------------- | ------------------------------------------------------------- |
| Local filesystem    | Render has ephemeral storage — files are lost on redeploy     |
| Google Drive        | Not designed for programmatic file storage at scale           |
| AWS S3              | Additional vendor — Supabase Storage is already available     |
| Google Cloud Storage| Additional vendor — unnecessary complexity                    |

---

## 6. Authentication

| Attribute            | Value                                                       |
| -------------------- | ----------------------------------------------------------- |
| **Token type**       | JSON Web Token (JWT)                                         |
| **Signing algorithm**| HS256                                                        |
| **Library**          | `python-jose` (JWT), `passlib` (bcrypt)                      |
| **Password hashing** | bcrypt (12 rounds)                                           |
| **Student auth**     | Name + Mobile Number → JWT (role: student)                   |
| **Admin auth**       | Username + Password → verify bcrypt hash → JWT (role: admin) |
| **Token storage**    | Client-side: in-memory React state                           |
| **Token transport**  | HTTP `Authorization: Bearer <token>` header                  |

> **Note:** We use our own JWT implementation, not Supabase Auth.  
> Supabase is used only for PostgreSQL and Storage.  
> This keeps authentication fully under our control.

---

## 7. Notifications

| Attribute               | Value                                                    |
| ----------------------- | -------------------------------------------------------- |
| **Server → Client**     | Server-Sent Events (SSE) via `sse-starlette`             |
| **Client notification** | Browser Notification API                                  |
| **Transport**           | Standard HTTP (GET with `text/event-stream` content type) |
| **Connection scope**    | Admin only (max 3 concurrent connections)                 |
| **Event types**         | `new_order`, `order_status_changed`                       |

---

## 8. Deployment

### 8.1 Deployment Map

```
┌────────────────────────────────────────────────────────────────────┐
│                         INTERNET                                    │
│                                                                     │
│   Student Browser              Admin Browser                       │
│        │                            │                               │
│        ▼                            ▼                               │
│   ┌──────────┐              ┌──────────┐                           │
│   │  Vercel  │              │  Vercel  │                           │
│   │ (React)  │              │ (React)  │                           │
│   └────┬─────┘              └────┬─────┘                           │
│        │     API calls           │                                  │
│        └───────────┬─────────────┘                                  │
│                    ▼                                                │
│           ┌──────────────┐                                          │
│           │    Render    │                                          │
│           │  (FastAPI)   │                                          │
│           └──────┬───────┘                                          │
│                  │                                                  │
│        ┌─────────┼─────────┐                                       │
│        ▼                   ▼                                       │
│  ┌───────────┐      ┌───────────────┐                              │
│  │ Supabase  │      │   Supabase    │                              │
│  │ PostgreSQL│      │   Storage     │                              │
│  └───────────┘      └───────────────┘                              │
└────────────────────────────────────────────────────────────────────┘
```

### 8.2 Platform Details

| Platform     | Hosts                | URL pattern                                  |
| ------------ | -------------------- | -------------------------------------------- |
| **Vercel**   | React frontend       | `https://campuscopies.vercel.app`            |
| **Render**   | FastAPI backend      | `https://campuscopies-api.onrender.com`      |
| **Supabase** | PostgreSQL + Storage | `https://<project-ref>.supabase.co`          |

### 8.3 Platform Justifications

| Platform     | Why chosen                                                          |
| ------------ | ------------------------------------------------------------------- |
| **Vercel**   | Zero-config deployment for React+Vite. Global CDN. Automatic HTTPS. Preview deployments per branch. Generous free tier. |
| **Render**   | Managed hosting for Python web apps. Automatic builds from Git. Managed HTTPS. Environment variable management. Free tier available for prototyping, paid tier for production reliability. |
| **Supabase** | Combined PostgreSQL + Storage on one platform. Managed backups. Dashboard for database administration. Free tier for development. Straightforward upgrade path for production. |

---

## 9. Development Tooling

| Tool             | Purpose                                                     |
| ---------------- | ----------------------------------------------------------- |
| `ruff`           | Python linter and formatter (replaces flake8, black, isort) |
| `mypy`           | Python static type checker                                   |
| `pytest`         | Python testing framework                                     |
| `eslint`         | TypeScript/React linter                                      |
| `prettier`       | TypeScript/CSS formatter                                     |
| `vitest`         | Frontend unit testing                                        |
| Git              | Version control                                              |
| GitHub           | Repository hosting (assumed)                                 |

---

## 10. Environment Configuration

### 10.1 Backend Environment Variables

| Variable                  | Description                              | Example                                    |
| ------------------------- | ---------------------------------------- | ------------------------------------------ |
| `DATABASE_URL`            | Supabase PostgreSQL pooler URL           | `postgresql://postgres.xxx:pwd@host:6543/postgres` |
| `DATABASE_URL_DIRECT`     | Supabase PostgreSQL direct URL           | `postgresql://postgres.xxx:pwd@host:5432/postgres` |
| `SUPABASE_URL`            | Supabase project URL                     | `https://xxx.supabase.co`                  |
| `SUPABASE_SERVICE_ROLE_KEY`| Supabase service role key (server-only) | `eyJhbGciOi...`                            |
| `JWT_SECRET`              | Secret for signing JWT tokens            | (256-bit random string)                    |
| `JWT_ALGORITHM`           | JWT signing algorithm                    | `HS256`                                    |
| `JWT_STUDENT_EXPIRY_HOURS`| Student token lifetime                   | `24`                                       |
| `JWT_ADMIN_EXPIRY_HOURS`  | Admin token lifetime                     | `8`                                        |
| `ADMIN_SETUP_KEY`         | One-time key for first admin creation    | (random string, deleted after first use)   |
| `CORS_ORIGINS`            | Allowed frontend origins                 | `https://campuscopies.vercel.app`          |
| `LOG_LEVEL`               | Logging level                            | `info`                                     |
| `ENVIRONMENT`             | Runtime environment                      | `production`                               |

### 10.2 Frontend Environment Variables

| Variable                  | Description                              | Example                                    |
| ------------------------- | ---------------------------------------- | ------------------------------------------ |
| `VITE_API_URL`            | Backend API base URL                     | `https://campuscopies-api.onrender.com`    |

### 10.3 Rules

- `.env` files are **never** committed to version control.
- `.env.example` is committed with placeholder values and descriptions.
- Production variables are set via Render dashboard and Vercel dashboard.
- `SUPABASE_SERVICE_ROLE_KEY` is **backend-only**. Never exposed to the frontend.

---

## 11. Dependency Management

| Stack    | Tool                    | Lock file              |
| -------- | ----------------------- | ---------------------- |
| Backend  | `pip` + `pyproject.toml`| `requirements.txt`     |
| Frontend | `npm`                   | `package-lock.json`    |

### 11.1 Backend Dependency Workflow

```bash
# Add dependency to pyproject.toml
# Generate pinned requirements:
pip-compile pyproject.toml -o requirements.txt

# Install in development:
pip install -r requirements.txt

# Install on Render (production):
pip install -r requirements.txt
```

### 11.2 Frontend Dependency Workflow

```bash
# Add dependency:
npm install <package>

# Install from lock file (CI/production):
npm ci
```

---

## 12. Version Pinning Policy

| Dependency type | Policy                                                          |
| --------------- | --------------------------------------------------------------- |
| Runtime deps    | Pin to exact version in lock file. Update deliberately.         |
| Dev deps        | Pin to exact version in lock file.                               |
| Python          | Minimum 3.13. Use latest patch release.                         |
| Node.js         | LTS version (20.x or later). Use latest LTS patch.             |
| PostgreSQL      | 15+. Managed by Supabase — version is determined by Supabase.  |

---

*End of Technology Stack — Version 1.0.0 (Frozen)*

*All implementation must conform to this document.*

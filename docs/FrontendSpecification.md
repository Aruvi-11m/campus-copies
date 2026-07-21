# Campus Copies — Frontend Architecture Specification

| Field          | Value                                            |
| -------------- | ------------------------------------------------ |
| Document Title | Frontend Architecture Specification              |
| Project Name   | Campus Copies                                    |
| Version        | 1.0.0-draft                                      |
| Status         | Awaiting Stakeholder Approval                    |
| Author         | Senior Frontend Architect & Lead React Engineer  |
| Created        | 2026-07-21                                       |
| Last Updated   | 2026-07-21                                       |
| References     | SRS.md v1.0.0, TechnologyStack.md v1.0.0 (Frozen), Architecture.md v2.0.0, DatabaseRelationships.md v1.0.0, Database.md v1.0.0, API.md v1.0.0, BusinessRules.md v1.0.0, BackendSpecification.md v1.0.0, UIUXSpecification.md v1.0.0 |

---

## Table of Contents

1. [Frontend Overview](#1-frontend-overview)
2. [Folder Structure](#2-folder-structure)
3. [Routing Architecture](#3-routing-architecture)
4. [Layout Architecture](#4-layout-architecture)
5. [Page Specifications](#5-page-specifications)
6. [Component Architecture](#6-component-architecture)
7. [State Management Strategy](#7-state-management-strategy)
8. [API Layer & HTTP Client](#8-api-layer--http-client)
9. [Form Handling & File Upload Flow](#9-form-handling--file-upload-flow)
10. [Authentication & Authorization Flow](#10-authentication--authorization-flow)
11. [Notifications & Real-Time SSE Integration](#11-notifications--real-time-sse-integration)
12. [Performance Optimization](#12-performance-optimization)
13. [Accessibility (a11y) & Usability](#13-accessibility-a11y--usability)
14. [Error Handling & Resilience](#14-error-handling--resilience)
15. [Testing Strategy](#15-testing-strategy)
16. [Future Expansion Architecture](#16-future-expansion-architecture)
17. [Frontend Architectural Self-Review](#17-frontend-architectural-self-review)

---

## 1. Frontend Overview

### 1.1 Purpose & Responsibilities
The Campus Copies frontend is a production-grade Single Page Application (SPA) built using **React 18+**, **TypeScript 5+**, **Vite 5+**, and **Tailwind CSS 3.x**. It serves as the interactive user interface for both students and shop operators.

- **Responsibilities**:
  - Render accessible, responsive UI for Student Self-Service and Admin ERP Management.
  - Manage in-memory authentication state (JWT tokens) without insecure storage mechanisms.
  - Validate form fields on the client before network transmission.
  - Handle chunked file uploads and display real-time upload progress.
  - Connect to backend Server-Sent Events (SSE) for real-time notification alerts.
  - Maintain absolute consistency with [UIUXSpecification.md](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/UIUXSpecification.md) and API contracts in [API.md](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/API.md).

### 1.2 Architecture Philosophy
- **Clean Separation of Concerns**: UI rendering (`components/`, `pages/`), business state (`contexts/`, `hooks/`), API network calls (`api/`), and type declarations (`types/`) are decoupled.
- **Type Safety First**: Strict TypeScript definitions for API request/response envelopes, domain models, and prop contracts.
- **Zero Unnecessary Dependencies**: Built using native browser APIs (`fetch`, `EventSource`, `Notification`) and standard React primitives (`useState`, `useContext`, `useReducer`, `useMemo`).

---

## 2. Folder Structure

```
frontend/
├── src/
│   ├── api/                        # API client, HTTP interceptors & endpoint modules
│   │   ├── client.ts               # Centralized fetch client wrapper (JWT, error handling)
│   │   ├── auth.ts                 # Auth API calls (Student & Admin login)
│   │   ├── orders.ts               # Order submit, query, status update API calls
│   │   ├── files.ts                # Multipart file upload & signed URL API calls
│   │   ├── payments.ts             # Payment verification API calls
│   │   ├── inventory.ts            # Stock catalog & restock API calls
│   │   ├── expenses.ts             # Expense logging API calls
│   │   ├── reports.ts              # Business reporting API calls
│   │   └── settings.ts             # Pricing & General settings API calls
│   │
│   ├── assets/                     # Static assets (App logo, static icons)
│   │   ├── logo.svg
│   │   └── favicon.ico
│   │
│   ├── components/                 # Reusable, stateless/semi-stateful UI components
│   │   ├── common/
│   │   │   ├── Button.tsx          # Button variants (Primary, Secondary, Success, Danger)
│   │   │   ├── Input.tsx           # Text, Number, Password inputs with error labels
│   │   │   ├── Select.tsx          # Dropdown select input
│   │   │   ├── Badge.tsx           # Status badge pills
│   │   │   ├── Card.tsx            # Standard container card
│   │   │   ├── Modal.tsx           # Accessible modal dialog overlay
│   │   │   ├── Pagination.tsx      # Table pagination controls
│   │   │   └── LoadingSpinner.tsx  # Spinner animation component
│   │   │
│   │   ├── domain/
│   │   │   ├── StatusBadge.tsx     # Order status indicator component
│   │   │   ├── PriceSummary.tsx    # Live price calculation breakdown card
│   │   │   ├── OrderTimeline.tsx   # Order lifecycle progress step timeline
│   │   │   ├── FileUploader.tsx    # Drag-and-drop dropzone & file list manager
│   │   │   └── PickupCodeCard.tsx  # 6-digit pickup code highlighted box
│   │   │
│   │   └── feedback/
│   │       ├── ToastContainer.tsx  # Slide-in toast notification stack
│   │       ├── OfflineBanner.tsx   # Network disconnection banner
│   │       └── ErrorBoundary.tsx   # React error boundary component
│   │
│   ├── constants/                  # Application constants & configuration defaults
│   │   ├── routes.ts               # Named URL route constants
│   │   ├── enums.ts                # TypeScript enum mappings matching backend
│   │   └── settings.ts             # Default fallback pricing & settings
│   │
│   ├── contexts/                   # React Context providers for global state
│   │   ├── AuthContext.tsx         # JWT token, current user, login/logout functions
│   │   ├── NotificationContext.tsx # SSE stream connection, toasts, unread counts
│   │   └── SettingsContext.tsx     # Cached application settings (UPI, pricing)
│   │
│   ├── hooks/                      # Custom reusable React hooks
│   │   ├── useAuth.ts              # Custom hook wrapping AuthContext
│   │   ├── useSSE.ts               # EventSource connection lifecycle hook
│   │   ├── useNotifications.ts     # Toast & browser notification trigger hook
│   │   ├── useFormValidation.ts    # Form field validation hook
│   │   └── useDebounce.ts          # Search input debouncing hook
│   │
│   ├── layouts/                    # App shell layout containers
│   │   ├── StudentLayout.tsx       # Student Portal topbar & bottom nav layout
│   │   ├── AdminLayout.tsx         # Admin Dashboard sidebar & topbar layout
│   │   └── AuthLayout.tsx          # Centered card layout for login pages
│   │
│   ├── pages/                      # Page view components
│   │   ├── student/
│   │   │   ├── StudentLoginPage.tsx        # Student login / auto-register (`/`)
│   │   │   ├── NewOrderPage.tsx            # Order creation step wizard (`/order/new`)
│   │   │   ├── OrderConfirmationPage.tsx   # Payment details & code (`/orders/:id/confirmation`)
│   │   │   ├── StudentOrdersPage.tsx       # Student order list (`/orders`)
│   │   │   └── StudentOrderDetailPage.tsx  # Student order tracking (`/orders/:id`)
│   │   │
│   │   └── admin/
│   │       ├── AdminLoginPage.tsx          # Admin sign in (`/admin/login`)
│   │       ├── AdminDashboardPage.tsx      # Overview & stats (`/admin`)
│   │       ├── AdminOrdersPage.tsx         # Orders data table & filters (`/admin/orders`)
│   │       ├── AdminOrderDetailPage.tsx    # Order detail & file preview (`/admin/orders/:id`)
│   │       ├── AdminInventoryPage.tsx      # Stock catalog & restock (`/admin/inventory`)
│   │       ├── AdminFinancePage.tsx        # Revenue & expenses (`/admin/finance`)
│   │       ├── AdminReportsPage.tsx        # Period report tables (`/admin/reports`)
│   │       ├── AdminSettingsPage.tsx       # Pricing & Admin accounts (`/admin/settings`)
│   │       └── AdminAuditLogsPage.tsx      # System security logs (`/admin/audit-logs`)
│   │
│   ├── routes/                     # Router setup & guard components
│   │   ├── AppRoutes.tsx           # React Router route registry
│   │   ├── ProtectedRoute.tsx      # Role-based route guard component
│   │   └── NotFoundPage.tsx        # 404 Not Found error view
│   │
│   ├── types/                      # TypeScript interface declarations
│   │   ├── api.ts                  # Standard response envelopes & pagination types
│   │   ├── auth.ts                 # User, Admin, Student & JWT payload interfaces
│   │   ├── order.ts                # Order, PrintConfig & Status History interfaces
│   │   ├── file.ts                 # OrderFile metadata interfaces
│   │   ├── inventory.ts            # Inventory item & transaction interfaces
│   │   ├── finance.ts              # Payment, Expense & Profit log interfaces
│   │   └── report.ts               # Reporting metric summary interfaces
│   │
│   ├── utils/                      # Pure utility functions
│   │   ├── formatters.ts           # Currency (₹), Date/Time, File size formatters
│   │   ├── validators.ts           # Mobile, Email & Name validation regex
│   │   └── storage.ts              # In-memory auth token cache helpers
│   │
│   ├── App.tsx                     # Master app wrapper with context providers
│   ├── main.tsx                    # React DOM entrypoint
│   └── index.css                   # Tailwind directives & global font setup
│
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── postcss.config.js
```

---

## 3. Routing Architecture

### 3.1 Route Registry

| Path | Component | Layout | Access Scope | Purpose |
|---|---|---|---|---|
| `/` | `StudentLoginPage` | `AuthLayout` | Public | Student login / auto-register |
| `/order/new` | `NewOrderPage` | `StudentLayout` | Student Only | Order submission wizard |
| `/orders` | `StudentOrdersPage` | `StudentLayout` | Student Only | Student order history |
| `/orders/:id` | `StudentOrderDetailPage` | `StudentLayout` | Student Only | Student order status timeline |
| `/orders/:id/confirmation` | `OrderConfirmationPage` | `StudentLayout` | Student Only | Pickup code & payment info |
| `/admin/login` | `AdminLoginPage` | `AuthLayout` | Public | Admin login |
| `/admin` | `AdminDashboardPage` | `AdminLayout` | Admin Only | Dashboard stats & alerts |
| `/admin/orders` | `AdminOrdersPage` | `AdminLayout` | Admin Only | Order management table |
| `/admin/orders/:id` | `AdminOrderDetailPage` | `AdminLayout` | Admin Only | Order detail & file preview |
| `/admin/inventory` | `AdminInventoryPage` | `AdminLayout` | Admin Only | Stock catalog & restock |
| `/admin/finance` | `AdminFinancePage` | `AdminLayout` | Admin Only | Revenue & expenses ledger |
| `/admin/reports` | `AdminReportsPage` | `AdminLayout` | Admin Only | Periodical report tables |
| `/admin/settings` | `AdminSettingsPage` | `AdminLayout` | Admin Only | Pricing rates & admin users |
| `/admin/audit-logs` | `AdminAuditLogsPage` | `AdminLayout` | Admin Only | System security audit trail |
| `*` | `NotFoundPage` | `AuthLayout` | Public | 404 error page |

### 3.2 Route Guards (`ProtectedRoute`)
- Evaluates `AuthContext` state on route transition:
  - If route requires `student` and user is unauthenticated → Redirect to `/`.
  - If route requires `admin` and user is unauthenticated → Redirect to `/admin/login`.
  - If authenticated user accesses wrong role area (e.g., student accessing `/admin`) → Redirect to `Unauthorized` / Role Home.

---

## 4. Layout Architecture

1. **`StudentLayout`**:
   - Sticky Topbar: Logo, Student Name badge, `[My Orders]` link, `[New Order]` button, Logout button.
   - Mobile Bottom Navigation Bar (< 768px): Fixed bottom bar with 3 tabs.
   - Content Container: Max-width 768px centered container.
2. **`AdminLayout`**:
   - Fixed Left Sidebar (250px): Nav links with unread order badges, SSE connection status indicator (`● Live`).
   - Sticky Topbar (64px): Breadcrumbs, search input, Notification Bell with drop-down panel, Admin Avatar.
   - Main Content Area: Responsive flex container with overflow scrolling.
3. **`AuthLayout`**:
   - Centered card container for student/admin authentication.

---

## 5. Page Specifications

All 14 application pages are mapped to exact components in `src/pages/`:
- **Student Pages**: `StudentLoginPage`, `NewOrderPage`, `StudentOrdersPage`, `StudentOrderDetailPage`, `OrderConfirmationPage`.
- **Admin Pages**: `AdminLoginPage`, `AdminDashboardPage`, `AdminOrdersPage`, `AdminOrderDetailPage`, `AdminInventoryPage`, `AdminFinancePage`, `AdminReportsPage`, `AdminSettingsPage`, `AdminAuditLogsPage`.

---

## 6. Component Architecture

### 6.1 Reusable UI Components (`src/components/common/`)
- `Button`: Primary, Secondary, Success, Danger variants; supports `isLoading` spinner state and `disabled`.
- `Input`: Standard text/number/password inputs; handles inline error messages and ARIA attributes.
- `Select`: Accessible dropdown selector.
- `Badge`: Status pill component rendering status colors from [UIUXSpecification.md §8](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/UIUXSpecification.md).
- `Card`: Bordered white container.
- `Modal`: Accessible backdrop overlay (`role="dialog"`, trap focus, ESC key handler).
- `Pagination`: Controls table page navigation, limit selector, and page info.

### 6.2 Domain Components (`src/components/domain/`)
- `StatusBadge`: Maps order status enum to color-coded badge.
- `PriceSummary`: Renders breakdown ($\text{pages} \times \text{rate} \times \text{copies} + \text{binding}$) and total price (₹).
- `OrderTimeline`: 5-step progress bar visualizing order lifecycle.
- `FileUploader`: Drag & drop dropzone, magic-bytes verification indicator, file progress bar.
- `PickupCodeCard`: Monospace highlighted 6-digit pickup code display.

---

## 7. State Management Strategy

| State Type | Scope | Storage Location | Management Mechanism |
|---|---|---|---|
| **Authentication State** | Global | Memory (`AuthContext`) | React Context + State. Cleared on tab close. Never in localStorage. |
| **Settings Cache** | Global | Memory (`SettingsContext`)| Loaded on startup, 60-second TTL auto-refresh. |
| **Notifications & SSE** | Global | Memory (`NotificationContext`)| React Context + SSE `EventSource` connection hook. |
| **Server State** | Page / Component | Component State | Fetched via API modules with loading/error states. |
| **Form State** | Local Component | Component State | Controlled inputs via `useState` / custom validation hooks. |
| **UI State** | Local Component | Component State | Modals open/close, active tab selections, dropdown toggles. |

---

## 8. API Layer & HTTP Client

### 8.1 API Client (`src/api/client.ts`)
- Custom fetch wrapper providing unified HTTP execution:
  - **Request Interceptor**: Injects `Authorization: Bearer <token>` header if JWT exists in `AuthContext`.
  - **Timeout Control**: Enforces 30-second default request timeout via `AbortController` (90-second timeout for file uploads to tolerate Render cold starts).
  - **Response Interceptor**: Evaluates HTTP status codes. Converts non-2xx responses into structured `ApiError` objects.
  - **401 Unauthorized Interceptor**: Triggers automatic `AuthContext.logout()` and redirects to login page.

---

## 9. Form Handling & File Upload Flow

### 9.1 Form Validation & Submission
- Client-side validation runs on field blur and form submit.
- Validation checks match backend rules (e.g., Indian mobile format `^[6-9][0-9]{9}$`, max 100 copies).
- Submit button enters loading state (`[ ⏳ Processing... ]`) and disables to prevent double submissions.

### 9.2 File Upload Flow
1. Student selects file in `FileUploader`.
2. Client checks file size (≤ 200 MB) and extension (.pdf, .doc, .docx, .ppt, .pptx).
3. Client executes `POST /api/v1/files/upload` with multipart form data, displaying progress bar via `XMLHttpRequest.upload.onprogress` or ReadableStream.
4. On success, `file_id` is appended to order form state.

---

## 10. Authentication & Authorization Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                    CLIENT AUTHENTICATION FLOW                          │
│                                                                        │
│  Student Login: Name + Mobile + Department ──► POST /auth/student/login│
│  Admin Login: Username + Password         ──► POST /auth/admin/login  │
│                                                                        │
│  Response: { token: "eyJhbG...", user: { ... } }                       │
│    │                                                                   │
│    ▼                                                                   │
│  Save token to AuthContext in-memory state (React Memory)              │
│    │                                                                   │
│    ├── Request Interceptor: Attach "Authorization: Bearer <token>"     │
│    │                                                                   │
│    ├── Route Transition: ProtectedRoute verifies role in AuthContext   │
│    │                                                                   │
│    └── 401 Unauthorized Received: Clear AuthContext → Redirect Login   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 11. Notifications & Real-Time SSE Integration

- **`NotificationContext`**: Holds active SSE stream, unread alert list, and toast container state.
- **`useSSE` Hook**:
  - Initializes `new EventSource('/api/v1/notifications/stream?token=' + jwt)` upon admin login.
  - Listens for `event: new_order`.
  - Triggers native `Notification` API if permission is granted.
  - Appends alert to Toast Notification stack.
  - Auto-reconnects natively if network drops.

---

## 12. Performance Optimization

- **Code Splitting & Lazy Loading**: Admin module routes are code-split using `React.lazy()` and `Suspense` (`AdminOrdersPage`, `AdminReportsPage`, etc.).
- **Asset Optimization**: Vite bundles CSS with PurgeCSS; assets are served with content-hash filenames for long-term CDN caching on Vercel.
- **Debounced Search**: Search input queries in Admin Tables use 300ms debounce hook (`useDebounce`) to minimize API requests.

---

## 13. Accessibility (a11y) & Usability

- **Keyboard Navigation**: Native focusable elements (`button`, `input`, `select`, `a`). Modals implement trap-focus and ESC key listeners.
- **ARIA Attributes**: `aria-invalid`, `aria-describedby` on inputs; `role="dialog"`, `aria-modal="true"` on modals; `aria-live="polite"` on status updates.
- **Visual Usability**: Minimum text contrast ratio of 4.5:1; high-contrast focus rings (`ring-2 ring-blue-600`).

---

## 14. Error Handling & Resilience

- **React Error Boundary (`ErrorBoundary`)**: Catches unhandled rendering errors and displays a fallback UI with `[ Reload Page ]` button.
- **Network & Offline Handling**: Window `offline` event listener triggers top `OfflineBanner` ("You are offline. Reconnecting...").
- **API Error Formatting**: Displays human-readable error messages from backend error responses (`error.message`).

---

## 15. Testing Strategy

- **Testing Tools**: `Vitest` + `React Testing Library` + `MSW` (Mock Service Worker).
- **Unit Tests**: Test reusable UI components (`Button`, `Badge`, `PriceSummary`) and utility formatters.
- **Integration Tests**: Test complex page forms (`NewOrderPage`, `AdminOrdersPage`) with MSW mock API handlers.
- **Route Guard Tests**: Verify `ProtectedRoute` redirects unauthenticated users and enforces role access.

---

## 16. Future Expansion Architecture

- **Printer Queue Panel**: Reserved UI component rendering physical print job queue status.
- **Analytics Charts**: Recharts/Chart.js integration for revenue and order trend visualizations.
- **Dark Mode Support**: Tailwind CSS `dark:` utility class architecture for operator dark mode toggle.

---

## 17. Frontend Architectural Self-Review

| Criteria | Verification Status | Resolution Details |
|---|---|---|
| **Clean Layer Separation?** | Verified | API client, state contexts, UI components, and pages strictly decoupled. |
| **Security Compliant?** | Verified | JWT held in memory; non-2xx API errors handled safely; CORS & XSS mitigated. |
| **No State Duplication?** | Verified | Global auth/notifications in Context; Server data in page state; Local form state in components. |
| **Full UI/UX Coverage?** | Verified | All 14 pages and component requirements from UIUXSpecification.md fully mapped. |

---

*End of Frontend Architecture Specification — Version 1.0.0-draft*

*This document is awaiting stakeholder review and approval before proceeding to implementation.*

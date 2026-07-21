# Campus Copies — Database Relationships Design

| Field          | Value                                            |
| -------------- | ------------------------------------------------ |
| Document Title | Database Relationships Design                    |
| Project Name   | Campus Copies                                    |
| Version        | 1.0.0-draft                                      |
| Status         | Awaiting Stakeholder Approval                    |
| Author         | Database Architect & Principal Software Architect|
| Created        | 2026-07-21                                       |
| Last Updated   | 2026-07-21                                       |
| References     | SRS.md v1.0.0, TechnologyStack.md v1.0.0 (Frozen), Architecture.md v2.0.0 |

---

## Table of Contents

1. [Database Overview](#1-database-overview)
2. [Database Entities](#2-database-entities)
3. [Entity Relationships](#3-entity-relationships)
4. [Primary Keys](#4-primary-keys)
5. [Foreign Keys](#5-foreign-keys)
6. [Unique Constraints](#6-unique-constraints)
7. [Index Strategy](#7-index-strategy)
8. [Soft Delete Policy](#8-soft-delete-policy)
9. [Audit Fields](#9-audit-fields)
10. [Cascade Rules](#10-cascade-rules)
11. [Order Life Cycle](#11-order-life-cycle)
12. [File Life Cycle](#12-file-life-cycle)
13. [Payment Flow](#13-payment-flow)
14. [Reporting Relationships](#14-reporting-relationships)
15. [Future Relationships](#15-future-relationships)
16. [ER Diagram](#16-er-diagram)
17. [Naming Conventions](#17-naming-conventions)
18. [Database Design Review](#18-database-design-review)

---

## 1. Database Overview

### 1.1 Why PostgreSQL Was Chosen

PostgreSQL 15+ was chosen as the relational database engine (hosted on Supabase) for the following reasons:

1. **ACID Compliance & Data Integrity**: Financial operations (Revenue, Expenses, Profit, Cash in Hand) and inventory adjustments require absolute strictness. Multi-statement transactions must either succeed entirely or fail without partial writes. PostgreSQL provides full ACID guarantees with serializable/read-committed isolation.
2. **Row-Level Locking**: Concurrent admin operations (marking orders as paid, updating inventory, generating reports) require non-blocking reads and fine-grained row-level write locks (`SELECT FOR UPDATE`), preventing race conditions.
3. **Rich Data Types & JSONB Support**: PostgreSQL native support for UUIDs, Timestamptz, Decimals, Enums, and JSONB allows storing semi-structured metadata (such as audit diffs and dynamic application settings) alongside structured relational tables with high query performance.
4. **Managed Infrastructure & PgBouncer**: Supabase provides managed PostgreSQL 15+ with built-in connection pooling via PgBouncer, automated daily backups, point-in-time recovery, and zero operational overhead.
5. **No Vendor Lock-In**: Standard PostgreSQL protocol guarantees that application code (SQLAlchemy 2.x ORM) connects via standard `postgresql://` drivers (`psycopg2` / `asyncpg`), allowing future migration to any PostgreSQL host (AWS RDS, GCP Cloud SQL, self-hosted) by changing only the connection string.

### 1.2 Why Relational Database

A relational database model is mandatory for Campus Copies due to the domain structure:

- **Strict Schema Enforcement**: Print pricing formulas, financial ledgers, order lifecycles, and inventory balances require explicit foreign key constraints, check constraints, and type enforcement.
- **Relational Integrity**: An Order must strictly belong to a Student, contain one or more Files, belong to a single Payment entry, maintain a chronological Audit/Status history, and map to specific Inventory consumption logs.
- **Aggregation & Reporting**: Business intelligence requires complex SQL queries joining orders, payments, expenses, and inventory across customizable date ranges. Relational engines excel at multi-table JOINs and GROUP BY aggregations.

### 1.3 Multi-Table Design Philosophy

The database schema follows strict normalization principles (Third Normal Form - 3NF):

- **Zero Data Redundancy**: Student details are stored once in `students`; Order configuration is stored once in `orders`; Pricing history is snapshotted into order records to prevent historical revenue skew when pricing settings change.
- **Single Responsibility per Table**: Financial records (`payments`, `expenses`, `profit_logs`) are separated from status progression (`order_status_history`) and inventory transactions (`inventory_transactions`).
- **Audit Traceability**: State mutations leave immutable historical trails across dedicated audit tables (`audit_logs`, `order_status_history`, `inventory_transactions`) rather than mutating records in place without trace.

### 1.4 Future Scalability

- **Multi-Tenant Readiness**: Every entity design includes isolated foreign key boundaries. Extending to multiple college branches in future releases requires adding a `tenant_id` column to root tables without structural redesign.
- **Partitioning Strategy**: High-volume tables (`audit_logs`, `order_status_history`, `inventory_transactions`) are designed so they can be range-partitioned by `created_at` (e.g., monthly/yearly partitions) as historical volume grows into millions of rows.

---

## 2. Database Entities

The system defines 18 core entities categorized into active V1 domain tables and future expansion entities:

### 2.1 Active V1 Entities

| # | Entity Name | Table Name | Purpose |
|---|-------------|------------|---------|
| 1 | **Students** | `students` | Identifies college students submitting print jobs (Name, Mobile Number, Department). |
| 2 | **Admins** | `admins` | Identifies authorized shop operators (max 3 active accounts). Stores bcrypt password hashes. |
| 3 | **Orders** | `orders` | Core transaction entity tracking print configuration, pricing, student link, and current state. |
| 4 | **OrderFiles** | `order_files` | Tracks metadata for uploaded files linked to temporary uploads or finalized orders. |
| 5 | **Payments** | `payments` | Records payment confirmation details (Amount, Method: UPI/Cash, Admin Verifier, Timestamp). |
| 6 | **PickupCodes** | `pickup_codes` | Tracks unique 6-digit alphanumeric codes generated per order for secure shop pickup verification. |
| 7 | **PricingSettings** | `pricing_settings` | Stores per-page and binding price rates (B&W single/double, Color, Spiral, Soft, Hard, Stapling). |
| 8 | **InventoryItems** | `inventory_items` | Master catalog of consumable physical stock (Paper types, Ink cartridges, Binding materials). |
| 9 | **InventoryTransactions** | `inventory_transactions` | Audit log of all stock movements (Restock additions, Order consumption, Wastage deductions). |
| 10 | **Expenses** | `expenses` | Tracks shop operating expenses manually entered by admins (Category, Amount, Description, Date). |
| 11 | **ProfitLogs** | `profit_logs` | Daily/period aggregated financial snapshot (Revenue, Expenses, Net Profit, Cash in Hand). |
| 12 | **AuditLogs** | `audit_logs` | Immutable audit trail capturing all system mutations (Actor, Action, Resource, Old/New JSON state). |
| 13 | **Notifications** | `notifications` | Internal event queue for real-time admin alert broadcasts (Order submitted, Low stock). |
| 14 | **ApplicationSettings** | `application_settings` | Centralized system key-value configuration (UPI ID, Admin limit, Notifications flag, Departments). |
| 15 | **OrderStatusHistory** | `order_status_history` | Chronological transition log tracking every status advancement per order (From, To, Admin, Timestamp). |
| 16 | **Sessions** | `sessions` | Tracks active admin login sessions, token issuance, activity timestamps, and invalidation status. |

### 2.2 Future Entities (Reserved Blueprint)

| # | Entity Name | Table Name | Future Purpose |
|---|-------------|------------|----------------|
| 17 | **PrinterQueue** | `printer_queue` | Holds print jobs dispatched to local Shop Printer Agent executable. |
| 18 | **Reports & Analytics** | `analytics_snapshots` | Pre-aggregated metric caches for multi-year trend analysis and charts. |

---

## 3. Entity Relationships

```
┌─────────────────┐       1:N       ┌─────────────────┐       1:N       ┌─────────────────┐
│    students     ├─────────────────┤     orders      ├─────────────────┤   order_files   │
└────────┬────────┘                 └────────┬────────┘                 └─────────────────┘
         │                                   │
         │ 1:N                               │ 1:1
         ▼                                   ▼
┌─────────────────┐                 ┌─────────────────┐
│  notifications  │                 │    payments     │
└─────────────────┘                 └─────────────────┘
                                             │
                                             │ 1:1
                                             ▼
┌─────────────────┐       1:N       ┌─────────────────┐
│     admins      ├─────────────────┤  pickup_codes   │
└────────┬────────┘                 └─────────────────┘
         │
         │ 1:N                      ┌─────────────────┐       1:N       ┌─────────────────┐
         ├─────────────────────────►│order_status_hist│◄────────────────┤     orders      │
         │                          └─────────────────┘                 └─────────────────┘
         │ 1:N                      ┌─────────────────┐
         ├─────────────────────────►│   audit_logs    │
         │                          └─────────────────┘
         │ 1:N                      ┌─────────────────┐       1:N       ┌─────────────────┐
         ├─────────────────────────►│inventory_transac│◄────────────────┤ inventory_items │
         │                          └─────────────────┘                 └─────────────────┘
         │ 1:N                      ┌─────────────────┐
         └─────────────────────────►│    expenses     │
                                    └─────────────────┘
```

### 3.1 Detailed Cardinality Specifications

1. **Student → Orders** (`1 : N` - One-to-Many):
   - A single `Student` can place multiple `Orders` over time.
   - An `Order` belongs to exactly one `Student`.
   - Mandatory foreign key `orders.student_id` → `students.id`.

2. **Order → OrderFiles** (`1 : N` - One-to-Many):
   - An `Order` contains one or more uploaded `OrderFiles` (minimum 1 file).
   - An `OrderFile` belongs to zero or one `Order` (null when temporarily uploaded before submission; linked upon submission).
   - Foreign key `order_files.order_id` → `orders.id` (nullable for temp files).

3. **Order → Payment** (`1 : 1` - One-to-One):
   - An `Order` has at most one associated `Payment` record.
   - A `Payment` record belongs to exactly one `Order`.
   - Unique foreign key `payments.order_id` → `orders.id`.

4. **Order → PickupCode** (`1 : 1` - One-to-One):
   - An `Order` has exactly one `PickupCode` generated upon creation.
   - A `PickupCode` identifies exactly one `Order`.
   - Unique foreign key `pickup_codes.order_id` → `orders.id`.

5. **Order → OrderStatusHistory** (`1 : N` - One-to-Many):
   - An `Order` records multiple entries in `order_status_history` as it progresses through lifecycle states (`PENDING_PAYMENT` → `PAID` → `PRINTING` → `READY_FOR_PICKUP` → `COMPLETED`).
   - Each history record belongs to exactly one `Order`.
   - Foreign key `order_status_history.order_id` → `orders.id`.

6. **Admin → OrderStatusHistory** (`0..1 : N` - Optional One-to-Many):
   - An `Admin` triggers status transitions. `order_status_history.admin_id` references the `Admin` who authorized the state change. Initial creation transition (`PENDING_PAYMENT`) has `admin_id = NULL`.

7. **Admin → Payments** (`1 : N` - One-to-Many):
   - An `Admin` verifies and records payment. Foreign key `payments.verified_by_admin_id` → `admins.id`.

8. **Admin → AuditLogs** (`0..1 : N` - Optional One-to-Many):
   - An `Admin` action generates audit logs. `audit_logs.actor_id` references `admins.id` (or `students.id` when action is performed by a student).

9. **Admin → Expenses** (`1 : N` - One-to-Many):
   - An `Admin` records an expense entry. Foreign key `expenses.created_by_admin_id` → `admins.id`.

10. **InventoryItem → InventoryTransactions** (`1 : N` - One-to-Many):
    - An `InventoryItem` has multiple `InventoryTransactions` recording restocks, deductions, or order consumptions.
    - Mandatory foreign key `inventory_transactions.item_id` → `inventory_items.id`.

11. **Admin → InventoryTransactions** (`1 : N` - One-to-Many):
    - Foreign key `inventory_transactions.admin_id` → `admins.id` records which admin authorized the stock adjustment.

12. **Admin → Sessions** (`1 : N` - One-to-Many):
    - An `Admin` can have multiple historical or active browser `Sessions`. Foreign key `sessions.admin_id` → `admins.id`.

---

## 4. Primary Keys

### 4.1 Primary Key Strategy Selection

The database employs **UUIDv4 (Universally Unique Identifiers)** for all public, user-facing, and core domain entities, and **BigInt Auto-Incrementing Integers** for internal append-only audit/log tables.

| Strategy | Applied Entities | Rationale |
|----------|------------------|-----------|
| **UUIDv4** (`UUID`) | `students`, `admins`, `orders`, `order_files`, `payments`, `pickup_codes`, `inventory_items`, `expenses`, `sessions` | • Prevents sequential ID enumeration security attacks (e.g., guessing order IDs or file IDs in URLs).<br>• Allows offline/client-side ID generation if needed.<br>• Simplifies multi-tenant and multi-database merging in future expansion.<br>• Native 128-bit support in PostgreSQL (`gen_random_uuid()`). |
| **BigInt Auto-Increment** (`BIGINT GENERATED ALWAYS AS IDENTITY`) | `order_status_history`, `inventory_transactions`, `audit_logs`, `notifications`, `profit_logs`, `pricing_settings` | • Maximum insert performance for append-only logs.<br>• Natural chronological ordering.<br>• Smaller index tree footprint (8 bytes vs 16 bytes). |

### 4.2 Primary Key Matrix

| Entity Table | PK Column | Data Type | Generation Strategy | Trade-offs & Mitigation |
|--------------|-----------|-----------|---------------------|--------------------------|
| `students` | `id` | `UUID` | `gen_random_uuid()` | Slightly larger index size vs Integer. Mitigated by UUIDv4 index optimizations in PostgreSQL 15+. |
| `admins` | `id` | `UUID` | `gen_random_uuid()` | Max 3 rows active. Size impact is zero. |
| `orders` | `id` | `UUID` | `gen_random_uuid()` | Primary identifier. Safe from URL scraping (`/orders/550e8400-e29b-41d4-a716-446655440000`). |
| `order_files` | `id` | `UUID` | `gen_random_uuid()` | Ensures storage path uniqueness (`orders/{id}/{file_id}_filename`). |
| `payments` | `id` | `UUID` | `gen_random_uuid()` | Financial isolation. |
| `pickup_codes` | `id` | `UUID` | `gen_random_uuid()` | Internal PK. (Business pickup code is stored in `code` column). |
| `inventory_items` | `id` | `UUID` | `gen_random_uuid()` | Entity isolation for stock catalog items. |
| `expenses` | `id` | `UUID` | `gen_random_uuid()` | Financial isolation. |
| `sessions` | `id` | `UUID` | `gen_random_uuid()` | Session token handle. |
| `order_status_history` | `id` | `BIGINT` | `IDENTITY` | High insert volume. High index efficiency. |
| `inventory_transactions`| `id` | `BIGINT` | `IDENTITY` | High insert volume. |
| `audit_logs` | `id` | `BIGINT` | `IDENTITY` | Highest insert volume in application. |
| `notifications` | `id` | `BIGINT` | `IDENTITY` | Append-only event queue. |
| `profit_logs` | `id` | `BIGINT` | `IDENTITY` | Periodic financial summary. |
| `pricing_settings` | `id` | `BIGINT` | `IDENTITY` | Internal sequential versioning. |

---

## 5. Foreign Keys

### 5.1 Complete Foreign Key Reference Table

| Constraint Name | Source Table | Source Column | Referenced Table | Referenced Column | On Delete | On Update | Reason for Existence |
|-----------------|--------------|---------------|------------------|-------------------|-----------|-----------|----------------------|
| `fk_orders_student` | `orders` | `student_id` | `students` | `id` | `RESTRICT` | `CASCADE` | Guarantees every order is linked to a valid student. Prevents deletion of students with active orders. |
| `fk_order_files_order` | `order_files` | `order_id` | `orders` | `id` | `CASCADE` | `CASCADE` | Links files to order. Deleting an order cascades deletion of file metadata records. |
| `fk_order_files_student` | `order_files` | `student_id` | `students` | `id` | `RESTRICT` | `CASCADE` | Links temporary uploads to student before order submission. |
| `fk_payments_order` | `payments` | `order_id` | `orders` | `id` | `RESTRICT` | `CASCADE` | Links payment record to exactly one order. Restricts order deletion if payment exists. |
| `fk_payments_admin` | `payments` | `verified_by_admin_id`| `admins` | `id` | `RESTRICT` | `CASCADE` | Identifies which admin verified the payment. |
| `fk_pickup_codes_order` | `pickup_codes` | `order_id` | `orders` | `id` | `CASCADE` | `CASCADE` | Links pickup code to order. Cascades deletion if order is deleted. |
| `fk_status_hist_order` | `order_status_history` | `order_id` | `orders` | `id` | `CASCADE` | `CASCADE` | Maintains lifecycle history for order. |
| `fk_status_hist_admin` | `order_status_history` | `admin_id` | `admins` | `id` | `SET NULL` | `CASCADE` | Identifies admin who advanced order status. Nullable for student initial submission. |
| `fk_inv_txn_item` | `inventory_transactions`| `item_id` | `inventory_items` | `id` | `RESTRICT` | `CASCADE` | Connects stock transaction to stock item. Restricts item deletion if transactions exist. |
| `fk_inv_txn_admin` | `inventory_transactions`| `admin_id` | `admins` | `id` | `RESTRICT` | `CASCADE` | Identifies admin authorizing manual stock change or restock. |
| `fk_inv_txn_order` | `inventory_transactions`| `order_id` | `orders` | `id` | `SET NULL` | `CASCADE` | Connects automated stock consumption transaction to specific order (nullable for manual restock). |
| `fk_expenses_admin` | `expenses` | `created_by_admin_id`| `admins` | `id` | `RESTRICT` | `CASCADE` | Identifies admin recording operating expense. |
| `fk_sessions_admin` | `sessions` | `admin_id` | `admins` | `id` | `CASCADE` | `CASCADE` | Links active session to admin. Cascades deletion if admin account is purged. |
| `fk_notifications_order`| `notifications` | `order_id` | `orders` | `id` | `SET NULL` | `CASCADE` | Connects real-time notification alert to order context. |

---

## 6. Unique Constraints

Unique constraints enforce business rules at the database engine level:

| Constraint Name | Table Name | Columns | Business Rule Enforced |
|-----------------|------------|---------|------------------------|
| `uq_students_mobile` | `students` | `mobile` | Student mobile numbers must be unique. One account per mobile number. |
| `uq_admins_username` | `admins` | `username` | Admin login usernames must be unique. |
| `uq_orders_display_id` | `orders` | `display_id` | Human-readable Order ID (e.g., `CC-2026-0001`) must be strictly unique. |
| `uq_payments_order_id` | `payments` | `order_id` | An order can have at most one payment entry. |
| `uq_pickup_codes_order_id` | `pickup_codes` | `order_id` | An order can have at most one pickup code record. |
| `uq_pickup_codes_active_code` | `pickup_codes` | `code` WHERE `status = 'ACTIVE'` | Partial unique index: Active pickup codes must be unique among currently active orders to avoid pickup ambiguity. |
| `uq_inventory_items_code` | `inventory_items` | `item_code` | Inventory SKU/Item code must be unique (e.g., `PAPER_A4_80GSM`). |
| `uq_app_settings_key` | `application_settings`| `setting_key` | System setting keys must be unique. |
| `uq_profit_logs_date` | `profit_logs` | `log_date` | Exactly one aggregated profit summary log entry per calendar date. |

---

## 7. Index Strategy

Indexes are applied strategically to optimize critical read queries, search filters, and join operations while minimizing write overhead.

### 7.1 Index Specification Table

| Index Name | Target Table | Columns Indexed | Index Type | Target Query Optimization |
|------------|--------------|-----------------|------------|---------------------------|
| `idx_orders_status` | `orders` | `status` | B-Tree | Admin Dashboard filtering: `SELECT * FROM orders WHERE status = 'PRINTING'` |
| `idx_orders_student_id` | `orders` | `student_id` | B-Tree | Student portal order list: `SELECT * FROM orders WHERE student_id = ?` |
| `idx_orders_created_at` | `orders` | `created_at DESC` | B-Tree | Date range filtering & chronological sorting for reports and dashboards. |
| `idx_orders_status_created`| `orders` | `status, created_at DESC` | Composite B-Tree | Admin dashboard: status-filtered order list sorted by newest first. |
| `idx_students_mobile` | `students` | `mobile` | Hash / B-Tree | Student login lookup: `SELECT * FROM students WHERE mobile = ?` |
| `idx_admins_username` | `admins` | `username` | B-Tree | Admin login lookup: `SELECT * FROM admins WHERE username = ?` |
| `idx_order_files_order_id`| `order_files` | `order_id` | B-Tree | Order details view: `SELECT * FROM order_files WHERE order_id = ?` |
| `idx_order_files_status` | `order_files` | `status` | B-Tree | Cleanup scheduled job: `SELECT * FROM order_files WHERE status = 'TEMPORARY' AND uploaded_at < ?` |
| `idx_payments_method` | `payments` | `payment_method` | B-Tree | Financial reports: breakdown by UPI vs Cash. |
| `idx_expenses_date` | `expenses` | `expense_date` | B-Tree | Financial reports: `WHERE expense_date BETWEEN ? AND ?` |
| `idx_expenses_category` | `expenses` | `category` | B-Tree | Expense summary grouping by category. |
| `idx_inv_txn_item_date` | `inventory_transactions`| `item_id, created_at DESC` | Composite B-Tree | Stock audit history for specific item. |
| `idx_audit_logs_timestamp`| `audit_logs` | `timestamp DESC` | B-Tree | System audit log view sorted by time. |
| `idx_audit_logs_resource` | `audit_logs` | `resource_type, resource_id`| Composite B-Tree | Audit trail lookup for specific entity (e.g., all edits to Order X). |
| `idx_audit_logs_actor` | `audit_logs` | `actor_id, actor_type` | Composite B-Tree | Audit trail lookup for specific admin or student. |

---

## 8. Soft Delete Policy

Data retention rules are categorized strictly to maintain financial/legal integrity while allowing system hygiene.

### 8.1 Retention Policy Classification

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DATA RETENTION POLICY                           │
│                                                                        │
│  NEVER DELETE (Immutable Audit / Financial Records)                    │
│    • orders                     • payments                             │
│    • expenses                   • profit_logs                          │
│    • audit_logs                 • order_status_history                 │
│    • inventory_transactions                                            │
│                                                                        │
│  SOFT DELETE (Isolate entity from UI without breaking FKs)             │
│    • students                   • admins                               │
│    • inventory_items                                                   │
│                                                                        │
│  SCHEDULED HARD DELETE (Physical Storage & Temp Cleanup)              │
│    • order_files (Temporary unsubmitted files older than 24 hours)     │
│    • sessions (Expired admin login sessions older than 30 days)        │
│    • notifications (Read alerts older than 14 days)                    │
└────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Entity-by-Entity Policy Specification

| Table | Policy | Mechanism | Business & Financial Rationale |
|-------|--------|-----------|--------------------------------|
| `orders` | **Never Delete** | Status set to `CANCELLED` if abandoned before payment. Record stays forever. | Orders represent historical business activity, revenue history, and tax records. Must never be hard deleted. |
| `payments` | **Never Delete** | None. | Financial ledger. Immutable proof of income. |
| `expenses` | **Never Delete** | None. | Financial ledger. Immutable proof of expenditure. |
| `profit_logs` | **Never Delete** | None. | Aggregated historical revenue/profit data. |
| `audit_logs` | **Never Delete** | None. | System security log. Permanent accountability record. |
| `order_status_history`| **Never Delete**| None. | Immutable order lifecycle audit log. |
| `inventory_transactions`| **Never Delete**| None.| Stock audit ledger. |
| `students` | **Soft Delete** | `is_deleted` (boolean) + `deleted_at` (timestamptz). | Preserves student reference on past completed orders while hiding deactivated accounts from student lookup. |
| `admins` | **Soft Delete** | `is_active` (boolean) + `deactivated_at` (timestamptz). | Deactivated admins cannot log in, but historical audit/payment verification records authored by them remain intact. Max 3 active limit check evaluates `WHERE is_active = TRUE`. |
| `inventory_items`| **Soft Delete**| `is_archived` (boolean). | Discontinued paper/ink types are archived from dropdowns without breaking historical order/inventory logs. |
| `order_files` | **Hard Delete (Conditional)**| `status = 'DELETED'` in DB; file object deleted from Supabase Storage. | Unsubmitted temporary files (`status = 'TEMPORARY'`) older than 24h are hard-deleted from storage and DB by cron job. Files attached to completed orders (`status = 'ATTACHED'`) are retained as long as storage policy dictates. |
| `sessions` | **Hard Delete** | `DELETE FROM sessions WHERE expires_at < NOW() - INTERVAL '30 days'` | Cleans up stale JWT session tracking records periodically. |
| `notifications` | **Hard Delete** | `DELETE FROM notifications WHERE is_read = TRUE AND created_at < NOW() - INTERVAL '14 days'` | Keeps event queue lightweight. |

---

## 9. Audit Fields

Standardized timestamp and tracking fields are enforced across all primary domain tables to maintain audit compliance.

### 9.1 Standardized Field Specifications

| Audit Field Name | Data Type | Default Value | Nullable | Purpose |
|------------------|-----------|---------------|----------|---------|
| `created_at` | `TIMESTAMPTZ` | `CURRENT_TIMESTAMP` | No | Exact UTC timestamp when row was inserted. |
| `updated_at` | `TIMESTAMPTZ` | `CURRENT_TIMESTAMP` | No | Exact UTC timestamp when row was last modified (updated via DB trigger or ORM hook). |
| `created_by` | `UUID` | Optional / Nullable | Yes | FK referencing `admins.id` or `students.id` who created the row. |
| `updated_by` | `UUID` | Optional / Nullable | Yes | FK referencing `admins.id` or `students.id` who last updated the row. |
| `deleted_at` | `TIMESTAMPTZ` | `NULL` | Yes | UTC timestamp set when entity is soft-deleted. `NULL` means active. |

### 9.2 Application Matrix

| Table Name | `created_at` | `updated_at` | `created_by` | `updated_by` | `deleted_at` | Notes |
|------------|--------------|--------------|--------------|--------------|--------------|-------|
| `students` | ✓ | ✓ | — | — | ✓ (`deleted_at`) | Self-registered via student portal. |
| `admins` | ✓ | ✓ | ✓ (`created_by_admin_id`) | ✓ | ✓ (`deactivated_at`) | Created by existing admin. |
| `orders` | ✓ | ✓ | ✓ (`student_id`) | ✓ (`updated_by_admin_id`) | — | Never deleted. |
| `order_files` | ✓ | ✓ | ✓ (`student_id`) | — | ✓ (`deleted_at`) | Soft/Hard deletion flag. |
| `payments` | ✓ | — | ✓ (`verified_by_admin_id`)| — | — | Immutable once inserted. |
| `expenses` | ✓ | ✓ | ✓ (`created_by_admin_id`) | ✓ | — | Financial entry. |
| `inventory_items`| ✓ | ✓ | ✓ | ✓ | ✓ (`archived_at`) | Stock catalog item. |
| `inventory_transactions`| ✓ | — | ✓ (`admin_id`) | — | — | Immutable log entry. |
| `order_status_history`| ✓ | — | ✓ (`admin_id`) | — | — | Immutable log entry. |
| `audit_logs` | ✓ | — | ✓ (`actor_id`) | — | — | Immutable log entry. |
| `pricing_settings`| ✓ | — | ✓ (`admin_id`) | — | — | Immutable pricing snapshot. |
| `application_settings`| ✓ | ✓ | — | ✓ | — | Key-value settings. |

---

## 10. Cascade Rules

Cascade behavior is explicitly configured to ensure data integrity without accidental loss of historical records.

```
Student Deletion Attempt
  │
  ├── Has Orders? ───► RESTRICT (Error: Cannot delete student with active/past orders)
  └── No Orders?  ───► Soft Delete (Set is_deleted = true, retain record)

Order Deletion Attempt (Only via Admin Override in dev/testing)
  │
  ├── order_files ──────────► CASCADE (Metadata deleted; Storage file purged)
  ├── pickup_codes ─────────► CASCADE (Pickup code deleted)
  ├── order_status_history ─► CASCADE (History purged)
  ├── payments ─────────────► RESTRICT (Error: Cannot delete order with payment record!)
  └── inventory_transactions► SET NULL (Stock transaction retains quantity but nulls order link)

Admin Account Deactivation
  │
  ├── Active Session ───────► CASCADE (Immediate token revocation)
  ├── Past Verified Payments ► RESTRICT / RETAIN (Keep verified_by_admin_id FK intact)
  └── Audit Log Entries ────► RETAIN (Keep actor_id FK intact)
```

### 10.1 Detailed Cascade Policy Table

| Parent Entity | Child Entity | FK Constraint Name | On Delete Action | Technical & Integrity Justification |
|---------------|--------------|--------------------|------------------|-------------------------------------|
| `students` | `orders` | `fk_orders_student` | `RESTRICT` | **Critical**: A student record cannot be deleted if historical orders exist. Prevents orphaned orders and revenue distortion. |
| `orders` | `order_files` | `fk_order_files_order` | `CASCADE` | If an unsubmitted or test order is purged, associated file metadata is automatically cascaded. |
| `orders` | `payments` | `fk_payments_order` | `RESTRICT` | An order with a payment record **cannot** be deleted. Protects financial audit trail. |
| `orders` | `pickup_codes` | `fk_pickup_codes_order` | `CASCADE` | Pickup code is tied to order lifecycle; deleted if order is purged. |
| `orders` | `order_status_history`| `fk_status_hist_order` | `CASCADE` | Lifecycle history is tied to order. |
| `orders` | `inventory_transactions`| `fk_inv_txn_order` | `SET NULL` | If an order is cancelled/removed, stock consumption entries retain their material cost numbers but clear the `order_id` reference. |
| `admins` | `sessions` | `fk_sessions_admin` | `CASCADE` | Deactivating/removing an admin instantly purges all active session rows, forcing logout. |
| `admins` | `payments` | `fk_payments_admin` | `RESTRICT` | Deactivating an admin retains their ID on historical payments they verified. |
| `admins` | `order_status_history`| `fk_status_hist_admin` | `SET NULL` | If an admin row is removed, status history retains timestamp and status but nulls admin reference. |
| `inventory_items`| `inventory_transactions`| `fk_inv_txn_item` | `RESTRICT` | Inventory catalog item cannot be deleted if historical stock transactions exist. Item must be archived (`is_archived = TRUE`) instead. |

---

## 11. Order Life Cycle

The order lifecycle relationship flow enforces a strict sequence of DB state updates and automated audit triggers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ORDER LIFECYCLE FLOW                            │
│                                                                        │
│  1. SUBMISSION                                                         │
│     Student → INSERT students (if new)                                 │
│             → INSERT orders (status: PENDING_PAYMENT)                  │
│             → UPDATE order_files (set order_id, status: ATTACHED)      │
│             → INSERT pickup_codes (code: random 6-char, status: ACTIVE)│
│             → INSERT order_status_history (status: PENDING_PAYMENT)    │
│             → INSERT audit_logs (action: 'order.created')              │
│             → INSERT notifications (event: 'new_order')                │
│                                                                        │
│  2. PAYMENT VERIFICATION                                               │
│     Admin   → INSERT payments (amount, method: UPI/CASH, admin_id)    │
│             → UPDATE orders (status: PAID, payment_method)             │
│             → If CASH: UPDATE application_settings (increment cash)    │
│             → INSERT order_status_history (status: PAID)               │
│             → INSERT audit_logs (action: 'order.payment_marked')       │
│                                                                        │
│  3. PRINTING                                                           │
│     Admin   → UPDATE orders (status: PRINTING)                         │
│             → INSERT order_status_history (status: PRINTING)           │
│             → INSERT audit_logs (action: 'order.printing_started')     │
│                                                                        │
│  4. READY FOR PICKUP                                                   │
│     Admin   → UPDATE orders (status: READY_FOR_PICKUP)                 │
│             → INSERT order_status_history (status: READY_FOR_PICKUP)   │
│             → INSERT audit_logs (action: 'order.ready_for_pickup')    │
│                                                                        │
│  5. COMPLETION & PICKUP                                                │
│     Student shows Pickup Code → Admin verifies code                    │
│     Admin   → UPDATE orders (status: COMPLETED)                        │
│             → UPDATE pickup_codes (status: USED, redeemed_at: NOW)     │
│             → INSERT order_status_history (status: COMPLETED)          │
│             → INSERT inventory_transactions (deduct paper/ink/binding) │
│             → INSERT profit_logs (update daily summary)                │
│             → INSERT audit_logs (action: 'order.completed')            │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 12. File Life Cycle

The storage and metadata lifecycle enforces file security, isolation, and automated garbage collection:

```
┌────────────────────────────────────────────────────────────────────────┐
│                         FILE LIFECYCLE FLOW                            │
│                                                                        │
│  1. UPLOAD (Pre-Submission)                                            │
│     Student uploads file → Backend validates magic bytes & size (≤200MB)│
│                         → Uploads to Supabase: temp/{session_id}/{id}  │
│                         → INSERT order_files (status: TEMPORARY,      │
│                                   order_id: NULL, student_id)          │
│                                                                        │
│  2. SUBMISSION (Order Linked)                                          │
│     Student submits order → Move file in Supabase:                     │
│                             temp/{session_id}/... → orders/{order_id}/│
│                         → UPDATE order_files                           │
│                           set order_id = order_id, status = ATTACHED   │
│                                                                        │
│  3. ACCESS & PREVIEW                                                   │
│     Admin requests file  → Backend verifies admin JWT                  │
│                          → Generates Supabase Signed URL (expiry 1h)   │
│                          → PDF: responseDisposition = inline           │
│                          → DOCX/PPTX: responseDisposition = attachment │
│                          → INSERT audit_logs (action: 'file.accessed') │
│                                                                        │
│  4. CLEANUP (Garbage Collection Cron)                                  │
│     Scheduled Task runs  → SELECT order_files                          │
│                            WHERE status = 'TEMPORARY'                  │
│                              AND uploaded_at < NOW() - INTERVAL '24h'  │
│                          → Delete objects from Supabase Storage        │
│                          → UPDATE order_files set status = 'DELETED',  │
│                                   deleted_at = NOW()                   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 13. Payment Flow

The payment verification flow ensures ledger accuracy between UPI transactions and physical cash in hand:

```
┌────────────────────────────────────────────────────────────────────────┐
│                         PAYMENT LEDGER FLOW                            │
│                                                                        │
│  Student submits order (Total: ₹85.00)                                 │
│    │                                                                   │
│    ├── Payment Method Selection (Student pays externally)              │
│    │     ├── Option A: UPI Payment to Shop UPI ID                      │
│    │     └── Option B: Cash Payment at Shop Counter                    │
│    │                                                                   │
│    └── Admin Verification at Shop                                      │
│          │                                                             │
│          ├── Admin opens Order CC-2026-0042                             │
│          ├── Admin verifies payment received                           │
│          └── Admin selects "Mark as Paid" (Method: UPI or CASH)        │
│                │                                                       │
│                ▼ DB Transaction                                        │
│          ┌──────────────────────────────────────────────────────────┐  │
│          │ 1. INSERT INTO payments (order_id, amount, method,      │  │
│          │                         verified_by_admin_id)            │  │
│          │ 2. UPDATE orders SET status = 'PAID',                    │  │
│          │                     payment_method = method              │  │
│          │ 3. IF method == 'CASH':                                   │  │
│          │      UPDATE application_settings                         │  │
│          │      SET value = value + 85.00                           │  │
│          │      WHERE setting_key = 'cash_in_hand'                  │  │
│          │ 4. INSERT INTO order_status_history (status: PAID)       │  │
│          │ 5. INSERT INTO audit_logs (action: 'order.payment_marked')│  │
│          └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 14. Reporting Relationships

Reports are computed on-the-fly from granular transaction records across five primary data streams:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        REPORTING DATA AGGREGATION                      │
│                                                                        │
│   orders ──────────► Count of Total Orders                             │
│                      Orders Breakdown by Status                        │
│                      Top Departments by Order Volume                   │
│                                                                        │
│   payments ────────► Total Gross Revenue                               │
│                      Revenue Split: UPI Revenue vs Cash Revenue        │
│                                                                        │
│   expenses ────────► Total Operating Expenses                          │
│                      Expense Breakdown by Category                     │
│                                                                        │
│   profit_logs ─────► Calculated Net Profit (Gross Revenue - Expenses)  │
│                      Calculated Cash in Hand Balance                   │
│                      Average Order Value (AOV)                         │
│                                                                        │
│   inventory_txns ──► Material Consumption Units (Paper, Ink, Binding)  │
│                      Total Inventory Cost Consumed                     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 15. Future Relationships

The schema incorporates explicit foreign key extensions and structural designs for future releases:

| Future Module | Entity Relationship Integration | Design Provision in Schema |
|---------------|----------------------------------|----------------------------|
| **Printer Queue** | `orders` (`1`) ──► `printer_queue` (`N`) | `printer_queue` table holds `order_id`, `printer_id`, `status` (`QUEUED`, `PRINTING`, `FAILED`). |
| **WhatsApp Notifications** | `students` (`1`) ──► `whatsapp_logs` (`N`) | `whatsapp_logs` links `student_id` and `order_id` to track message delivery status. |
| **SMS Notifications** | `students` (`1`) ──► `sms_logs` (`N`) | `sms_logs` tracks SMS gateway dispatch for status changes. |
| **Email Notifications**| `students` (`1`) ──► `email_logs` (`N`) | `email_logs` tracks transactional email receipts. |
| **QR Pickup / Barcode** | `orders` (`1`) ──► `pickup_codes` (`1`) | `pickup_codes` table contains `qr_hash` string for optical scanner validation. |
| **Analytics Snapshots**| `profit_logs` (`N`) ──► `analytics_snapshots` (`1`) | Pre-aggregated monthly summary tables for fast multi-year chart rendering. |
| **Multi-College / Multi-Branch** | `tenants` (`1`) ──► All Tables (`N`) | `tenant_id` column added to root entities for multi-tenant isolation. |

---

## 16. ER Diagram

```
+-----------------------------------------------------------------------------------+
|                                  CAMPUS COPIES ERD                                |
+-----------------------------------------------------------------------------------+

  +-----------------------+              +----------------------------------+
  |       STUDENTS        |              |              ORDERS              |
  +-----------------------+              +----------------------------------+
  | PK  id (UUID)         |1            N| PK  id (UUID)                    |
  | UQ  mobile (VARCHAR)  +--------------+ FK  student_id (UUID)            |
  |     full_name (VARCHAR|              | UQ  display_id (VARCHAR)         |
  |     department(VARCHAR|              |     status (ENUM)                |
  |     created_at (TZ)   |              |     print_side (ENUM)            |
  |     updated_at (TZ)   |              |     color_mode (ENUM)            |
  |     deleted_at (TZ)   |              |     binding_type (ENUM)          |
  +-----------+-----------+              |     copies (INT)                 |
              |                          |     page_count (INT)             |
              | 1                        |     total_price (DECIMAL)        |
              |                          |     created_at (TZ)              |
              | N                        |     updated_at (TZ)              |
  +-----------v-----------+              +--+--------+---------+---------+--+
  |      ORDER_FILES      |                 |        |         |         |
  +-----------------------+                 |1       |1        |1        |1
  | PK  id (UUID)         |                 |        |         |         |
  | FK  order_id (UUID)   |<----------------+        |         |         |
  | FK  student_id (UUID) |                          |         |         |
  |     original_name (STR|                          |         |         |
  |     storage_path (STR)|                          |         |         |
  |     file_size (BIGINT)|                          |         |         |
  |     mime_type (STR)   |                          v         |         |
  |     status (ENUM)     |              +-------------------+ |         |
  |     uploaded_at (TZ)  |              |     PAYMENTS      | |         |
  +-----------------------+              +-------------------+ |         |
                                         | PK  id (UUID)     | |         |
                                         | FK  order_id(UUID)|<+         |
                                         |     amount(DEC)   |           |
                                         |     method (ENUM) |           |
                                         | FK  verified_by   |           |
                                         |     payment_date  |           |
                                         +---------+---------+           |
                                                   |                     |
                                                   | N                   |
  +-----------------------+                        |                     |
  |        ADMINS         |                        |                     |
  +-----------------------+                        |                     |
  | PK  id (UUID)         |1                       |                     |
  | UQ  username (VARCHAR)|                        |                     |
  |     password_hash(STR)|                        v                     v
  |     full_name (VARCHAR|              +-------------------+ +--------------------+
  |     is_active (BOOL)  +------------->|    SESSIONS       | |    PICKUP_CODES    |
  |     created_at (TZ)   |1            N+-------------------+ +--------------------+
  +----+-----+-----+------+              | PK  id (UUID)     | | PK  id (UUID)      |
       |     |     |                     | FK  admin_id(UUID)| | FK  order_id (UUID) |
      1|    1|    1|                     |     token (STR)   | | UQ  code (VARCHAR) |
       |     |     |                     |     expires_at(TZ)| |     status (ENUM)  |
       vN    vN    vN                    +-------------------+ +--------------------+
  +----+--+ +--+---+ +----+--+
  |EXPENSE| |AUDIT | |STATUS |
  | LOGS  | | LOGS | |HISTORY|
  +-------+ +------+ +-------+

  +-----------------------+              +----------------------------------+
  |    INVENTORY_ITEMS    |              |      INVENTORY_TRANSACTIONS      |
  +-----------------------+              +----------------------------------+
  | PK  id (UUID)         |1            N| PK  id (BIGINT)                  |
  | UQ  item_code (STR)   +--------------+ FK  item_id (UUID)               |
  |     item_name (STR)   |              | FK  admin_id (UUID)              |
  |     category (ENUM)   |              | FK  order_id (UUID, NULL)      |
  |     current_stock(INT)|              |     transaction_type (ENUM)      |
  |     min_threshold(INT)|              |     quantity_change (INT)        |
  |     unit_cost (DEC)   |              |     reason (TEXT)                |
  |     is_archived (BOOL)|              |     created_at (TZ)              |
  +-----------------------+              +----------------------------------+
```

---

## 17. Naming Conventions

Strict database naming standards are enforced across all SQL definitions:

### 17.1 Table Naming Rules
- **Plural Form**: Snake_case plural nouns (`students`, `orders`, `order_files`, `inventory_items`).
- **Lowercase Only**: No camelCase or PascalCase.
- **Prefixes**: No arbitrary prefixes (avoid `tb_` or `tbl_`).

### 17.2 Column Naming Rules
- **Lowercase Snake_Case**: `student_id`, `created_at`, `total_price`.
- **Primary Keys**: `id` for all tables.
- **Foreign Keys**: `{singular_referenced_table}_id` (e.g., `student_id`, `order_id`, `item_id`).
- **Booleans**: Prefixed with `is_` or `has_` (`is_active`, `is_deleted`, `is_archived`).
- **Timestamps**: Suffixed with `_at` (`created_at`, `updated_at`, `deleted_at`, `uploaded_at`).
- **Dates**: Suffixed with `_date` (`expense_date`, `log_date`).

### 17.3 Constraint & Index Naming Rules

| Object Type | Naming Pattern | Example |
|-------------|----------------|---------|
| Primary Key | `pk_{table_name}` | `pk_orders` |
| Foreign Key | `fk_{source_table}_{referenced_table}` | `fk_orders_students` |
| Unique Constraint | `uq_{table_name}_{column_name}` | `uq_students_mobile` |
| Check Constraint | `ck_{table_name}_{rule}` | `ck_orders_copies_positive` |
| B-Tree Index | `idx_{table_name}_{column_name}` | `idx_orders_status` |
| Composite Index | `idx_{table_name}_{col1}_{col2}` | `idx_orders_status_created_at` |

---

## 18. Database Design Review

A comprehensive architectural self-review was conducted against the relationship design:

### 18.1 Self-Review Checklist & Resolutions

| Review Criteria | Evaluation & Resolution |
|-----------------|-------------------------|
| **Missing Tables?** | All 18 required entities (`students`, `admins`, `orders`, `order_files`, `payments`, `pickup_codes`, `pricing_settings`, `inventory_items`, `inventory_transactions`, `expenses`, `profit_logs`, `audit_logs`, `notifications`, `application_settings`, `order_status_history`, `sessions`, `printer_queue`, `analytics_snapshots`) are fully defined. |
| **Circular Dependencies?** | Checked dependency tree. Dependencies flow strictly downward: `Student` → `Order` → `File` / `Payment` / `PickupCode` / `StatusHistory`. No circular foreign keys exist. |
| **Duplicate Entities?** | Verified clear separation: `payments` handles monetary receipts; `expenses` handles operational outflows; `profit_logs` aggregates totals; `pricing_settings` snapshots rates. No duplication. |
| **Missing Indexes?** | All high-cardinality search columns (`orders.status`, `orders.created_at`, `students.mobile`, `admins.username`, `order_files.status`, `audit_logs.timestamp`) have dedicated indexes specified. |
| **Missing Foreign Keys?** | All 14 entity relationships enforce explicit FK constraints with defined `ON DELETE` / `ON UPDATE` actions. |
| **Performance Bottlenecks?** | High-volume append-only log tables (`audit_logs`, `order_status_history`, `inventory_transactions`) use 64-bit `BIGINT IDENTITY` primary keys for maximum write throughput. |
| **Future Scalability?** | UUID primary keys for domain entities prevent key collision during future multi-branch or cloud sync expansion. |
| **Security Concerns?** | Passwords stored strictly as bcrypt hashes in `admins.password_hash`. UUIDs prevent sequential URL guessing. Financial ledgers are protected by `RESTRICT` delete constraints. |

---

*End of Database Relationships Design — Version 1.0.0-draft*

*This document is awaiting stakeholder review and approval before proceeding to Database SQL Schema creation.*

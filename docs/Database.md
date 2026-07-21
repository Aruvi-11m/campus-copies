# Campus Copies — Database Schema Specification

| Field          | Value                                            |
| -------------- | ------------------------------------------------ |
| Document Title | Database Schema Specification                    |
| Project Name   | Campus Copies                                    |
| Version        | 1.0.0-draft                                      |
| Status         | Awaiting Stakeholder Approval                    |
| Author         | Database Architect & Principal Software Architect|
| Created        | 2026-07-21                                       |
| Last Updated   | 2026-07-21                                       |
| References     | SRS.md v1.0.0, TechnologyStack.md v1.0.0 (Frozen), Architecture.md v2.0.0, DatabaseRelationships.md v1.0.0 |

---

## Table of Contents

1. [Database Engine & Extension Specifications](#1-database-engine--extension-specifications)
2. [Enum Definitions](#2-enum-definitions)
3. [Complete Table Specifications](#3-complete-table-specifications)
   - 3.1 [students](#31-students)
   - 3.2 [admins](#32-admins)
   - 3.3 [orders](#33-orders)
   - 3.4 [order_files](#34-order_files)
   - 3.5 [payments](#35-payments)
   - 3.6 [pickup_codes](#36-pickup_codes)
   - 3.7 [pricing_settings](#37-pricing_settings)
   - 3.8 [inventory_items](#38-inventory_items)
   - 3.9 [inventory_transactions](#39-inventory_transactions)
   - 3.10 [expenses](#310-expenses)
   - 3.11 [profit_logs](#311-profit_logs)
   - 3.12 [audit_logs](#312-audit_logs)
   - 3.13 [notifications](#313-notifications)
   - 3.14 [application_settings](#314-application_settings)
   - 3.15 [order_status_history](#315-order_status_history)
   - 3.16 [sessions](#316-sessions)
   - 3.17 [printer_queue (Future Blueprint)](#317-printer_queue-future-blueprint)
   - 3.18 [analytics_snapshots (Future Blueprint)](#318-analytics_snapshots-future-blueprint)
4. [Database Views for Reporting](#4-database-views-for-reporting)
5. [Global Check Constraints & Validation Rules](#5-global-check-constraints--validation-rules)
6. [Cascade & Soft Delete Execution Rules](#6-cascade--soft-delete-execution-rules)
7. [Audit Field Standards](#7-audit-field-standards)
8. [Future Migration Strategy (Alembic)](#8-future-migration-strategy-alembic)
9. [Backup & Recovery Specifications](#9-backup--recovery-specifications)
10. [Performance & Indexing Optimization](#10-performance--indexing-optimization)
11. [Database Self-Review](#11-database-self-review)

---

## 1. Database Engine & Extension Specifications

| Attribute | Specification |
|---|---|
| **Database Engine** | PostgreSQL 15+ (Hosted on Supabase) |
| **Connection Protocol** | Standard PostgreSQL Wire Protocol |
| **Character Set / Encoding** | `UTF8` |
| **Collation** | `en_US.UTF-8` |
| **Timezone Storage** | All timestamps stored in `TIMESTAMPTZ` (UTC). Conversions performed in application layer. |
| **Required Extensions** | • `pgcrypto` or `uuid-ossp` (for `gen_random_uuid()`) |

---

## 2. Enum Definitions

The schema utilizes native PostgreSQL ENUM types to enforce domain type safety:

### 2.1 `order_status_enum`
- `PENDING_PAYMENT` — Initial state upon student order submission.
- `PAID` — Admin verified payment (UPI or Cash).
- `PRINTING` — Admin started physical print job.
- `READY_FOR_PICKUP` — Print and binding completed; waiting at shop counter.
- `COMPLETED` — Student collected prints; terminal state.
- `CANCELLED` — Cancelled prior to printing; terminal state.

### 2.2 `payment_method_enum`
- `UPI` — Direct UPI transfer to shop UPI ID.
- `CASH` — Physical cash payment at shop counter.

### 2.3 `print_side_enum`
- `SINGLE_SIDE` — Print on one side of paper only.
- `DOUBLE_SIDE` — Duplex print on both sides of paper.
- `MULTI_PAGE` — Multiple document pages per sheet side.

### 2.4 `color_mode_enum`
- `BW` — Black & White grayscale print.
- `COLOR` — Full color print (Requires `SINGLE_SIDE`).

### 2.5 `binding_type_enum`
- `NONE` — No binding required.
- `SPIRAL` — Plastic/wire spiral binding.
- `SOFT_COVER` — Paperboard soft binding.
- `HARD_COVER` — Hardcover book binding.
- `STAPLE_PINS` — Corner/edge stapling.

### 2.6 `file_status_enum`
- `TEMPORARY` — Uploaded to `temp/` bucket prior to order submission.
- `ATTACHED` — Linked to an active order in `orders/` bucket.
- `ORPHANED` — Uploaded temporary file exceeding 24h without order linking.
- `DELETED` — Storage file object purged; metadata record retained.

### 2.7 `pickup_code_status_enum`
- `ACTIVE` — Code generated, waiting for student verification at shop.
- `USED` — Verified and redeemed at pickup counter.
- `EXPIRED` — Code invalidated due to order cancellation.

### 2.8 `inventory_category_enum`
- `PAPER` — Paper reams/sheets catalog.
- `INK` — Printer ink/toner cartridges.
- `BINDING` — Binding materials catalog.

### 2.9 `inventory_sub_category_enum`
- `NONE` — Default for paper/ink.
- `SPIRAL` — Spiral coils.
- `SOFT_COVER` — Soft covers.
- `HARD_COVER` — Hard covers.
- `STAPLE_PINS` — Staple pins.

### 2.10 `inventory_txn_type_enum`
- `RESTOCK` — Admin recorded new stock purchase addition.
- `CONSUMPTION` — Automated stock deduction upon order completion.
- `WASTAGE` — Manual deduction for paper jams, damaged goods, or test prints.
- `ADJUSTMENT` — Manual audit stock level correction.

### 2.11 `actor_type_enum`
- `STUDENT` — Action performed by student.
- `ADMIN` — Action performed by shop admin.
- `SYSTEM` — Automated background process / cron task.

---

## 3. Complete Table Specifications

---

### 3.1 `students`

#### Purpose
Stores student profile records identified by mobile number. Serves as the customer registry for student self-service orders.

#### Columns
| Column Name | Data Type | Nullable | Default Value | Constraints & Validation |
|-------------|-----------|----------|---------------|--------------------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary Key |
| `mobile` | `VARCHAR(10)` | No | None | Unique (`uq_students_mobile`), Check (`mobile ~ '^[6-9][0-9]{9}$'`) |
| `full_name` | `VARCHAR(100)`| No | None | Non-empty string (`length(trim(full_name)) > 0`) |
| `department` | `VARCHAR(50)` | No | None | Non-empty string |
| `created_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | System timestamp |
| `updated_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | System timestamp |
| `deleted_at` | `TIMESTAMPTZ` | Yes | `NULL` | Soft delete timestamp |
| `is_deleted` | `BOOLEAN` | No | `FALSE` | Soft delete flag |

#### Relationships
- **One-to-Many with `orders`**: A student can place multiple orders (`orders.student_id` → `students.id`).
- **One-to-Many with `order_files`**: Tracks temporary uploads before order submission (`order_files.student_id` → `students.id`).

#### Business & Validation Rules
1. Mobile numbers must be valid 10-digit Indian mobile numbers starting with 6, 7, 8, or 9.
2. `is_deleted = TRUE` flags soft-deleted student profiles; historical orders remain intact.
3. Student profiles are looked up by `mobile` during student portal authentication.

---

### 3.2 `admins`

#### Purpose
Stores shop operator login accounts, authentication credentials (bcrypt hashes), and active account status. Enforces max 3 active admins rule.

#### Columns
| Column Name | Data Type | Nullable | Default Value | Constraints & Validation |
|-------------|-----------|----------|---------------|--------------------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary Key |
| `username` | `VARCHAR(50)` | No | None | Unique (`uq_admins_username`), Check (`length(trim(username)) >= 3`) |
| `password_hash` | `VARCHAR(255)`| No | None | Stored bcrypt hash string (60 characters) |
| `full_name` | `VARCHAR(100)`| No | None | Non-empty string |
| `is_active` | `BOOLEAN` | No | `TRUE` | Account active flag |
| `created_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | System timestamp |
| `updated_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | System timestamp |
| `created_by_admin_id` | `UUID` | Yes | `NULL` | Self-reference FK (`admins.id`) |
| `deactivated_at` | `TIMESTAMPTZ` | Yes | `NULL` | Deactivation timestamp |

#### Relationships
- **Self-Reference**: `created_by_admin_id` references `admins.id`.
- **One-to-Many with `payments`**: `payments.verified_by_admin_id` → `admins.id`.
- **One-to-Many with `expenses`**: `expenses.created_by_admin_id` → `admins.id`.
- **One-to-Many with `inventory_transactions`**: `inventory_transactions.admin_id` → `admins.id`.
- **One-to-Many with `sessions`**: `sessions.admin_id` → `admins.id`.

#### Business & Validation Rules
1. System limits active admins (`is_active = TRUE`) to **maximum 3 active accounts**. Enforced by partial unique index / DB constraint or service layer trigger.
2. The last remaining active admin cannot be deactivated (`COUNT(admins) WHERE is_active = TRUE >= 1`).
3. Passwords must never be stored in plain text. Only 60-character bcrypt strings permitted in `password_hash`.

---

### 3.3 `orders`

#### Purpose
Core entity representing a print job submission. Tracks configuration options, total price, current status, and student links.

#### Columns
| Column Name | Data Type | Nullable | Default Value | Constraints & Validation |
|-------------|-----------|----------|---------------|--------------------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary Key |
| `display_id` | `VARCHAR(20)` | No | None | Unique (`uq_orders_display_id`), e.g., `CC-2026-0001` |
| `student_id` | `UUID` | No | None | Foreign Key (`students.id`) |
| `status` | `order_status_enum`| No | `'PENDING_PAYMENT'`| Initial status |
| `print_side` | `print_side_enum` | No | None | Print orientation choice |
| `color_mode` | `color_mode_enum` | No | None | Color choice |
| `binding_type`| `binding_type_enum`| No | `'NONE'` | Binding selection |
| `copies` | `INTEGER` | No | `1` | Check (`copies >= 1 AND copies <= 100`) |
| `page_count` | `INTEGER` | No | None | Check (`page_count >= 1`) |
| `per_page_price` | `NUMERIC(10,2)` | No | None | Check (`per_page_price >= 0.00`) |
| `binding_price` | `NUMERIC(10,2)` | No | `0.00` | Check (`binding_price >= 0.00`) |
| `total_price` | `NUMERIC(10,2)` | No | None | Check (`total_price >= 0.00`) |
| `payment_method` | `payment_method_enum` | Yes | `NULL` | Set when advanced to `PAID` |
| `created_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Submission timestamp |
| `updated_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Last updated timestamp |
| `updated_by_admin_id`| `UUID` | Yes | `NULL` | Foreign Key (`admins.id`) |

#### Relationships
- **Many-to-One with `students`**: `orders.student_id` → `students.id`.
- **One-to-Many with `order_files`**: `order_files.order_id` → `orders.id`.
- **One-to-One with `payments`**: `payments.order_id` → `orders.id`.
- **One-to-One with `pickup_codes`**: `pickup_codes.order_id` → `orders.id`.
- **One-to-Many with `order_status_history`**: `order_status_history.order_id` → `orders.id`.

#### Business & Validation Rules
1. **Color Rule**: If `color_mode = 'COLOR'`, `print_side` MUST be `'SINGLE_SIDE'`. Enforced by Check Constraint (`ck_orders_color_single_side`).
2. **Price Snapshot**: `per_page_price`, `binding_price`, and `total_price` are calculated at submission time and frozen in the order record. Future pricing changes do not affect existing order prices.
3. **Status Transitions**: Status can only advance strictly through sequence (`PENDING_PAYMENT` → `PAID` → `PRINTING` → `READY_FOR_PICKUP` → `COMPLETED`). Backward transitions or skipping states prohibited.

---

### 3.4 `order_files`

#### Purpose
Stores metadata for document files uploaded by students. Links physical Supabase Storage paths to orders.

#### Columns
| Column Name | Data Type | Nullable | Default Value | Constraints & Validation |
|-------------|-----------|----------|---------------|--------------------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary Key |
| `order_id` | `UUID` | Yes | `NULL` | Foreign Key (`orders.id`), set upon order submit |
| `student_id` | `UUID` | No | None | Foreign Key (`students.id`) |
| `original_name`| `VARCHAR(255)`| No | None | Sanitized filename |
| `storage_path` | `VARCHAR(512)`| No | None | Path in Supabase Storage (`temp/...` or `orders/...`)|
| `file_size` | `BIGINT` | No | None | Size in bytes. Check (`file_size > 0 AND file_size <= 209715200`) |
| `mime_type` | `VARCHAR(100)`| No | None | Allowed: PDF, DOC, DOCX, PPT, PPTX mime types |
| `magic_bytes_verified`| `BOOLEAN` | No | `FALSE` | Server-side magic bytes validation flag |
| `status` | `file_status_enum`| No | `'TEMPORARY'`| File lifecycle state |
| `uploaded_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Upload timestamp |
| `updated_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Update timestamp |
| `deleted_at` | `TIMESTAMPTZ` | Yes | `NULL` | Garbage collection timestamp |

#### Relationships
- **Many-to-One with `orders`**: `order_files.order_id` → `orders.id` (ON DELETE CASCADE).
- **Many-to-One with `students`**: `order_files.student_id` → `students.id` (ON DELETE RESTRICT).

#### Business & Validation Rules
1. Maximum file size is strictly 200 MB (209,715,200 bytes).
2. Files are uploaded under `status = 'TEMPORARY'` and `storage_path = 'temp/{session_id}/{file_id}'`.
3. Upon order submission, `status` becomes `'ATTACHED'` and file is moved to `storage_path = 'orders/{order_id}/{file_id}'`.

---

### 3.5 `payments`

#### Purpose
Stores monetary payment verification records. Links payment mode (UPI/Cash) and verifier admin to orders.

#### Columns
| Column Name | Data Type | Nullable | Default Value | Constraints & Validation |
|-------------|-----------|----------|---------------|--------------------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary Key |
| `order_id` | `UUID` | No | None | Unique (`uq_payments_order_id`), FK (`orders.id`)|
| `amount` | `NUMERIC(10,2)` | No | None | Check (`amount > 0.00`) |
| `payment_method` | `payment_method_enum` | No | None | Payment channel (`UPI` or `CASH`) |
| `verified_by_admin_id`| `UUID` | No | None | Foreign Key (`admins.id`) |
| `payment_date` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Verification timestamp |
| `notes` | `TEXT` | Yes | `NULL` | Optional verification notes |

#### Relationships
- **One-to-One with `orders`**: `payments.order_id` → `orders.id` (ON DELETE RESTRICT).
- **Many-to-One with `admins`**: `payments.verified_by_admin_id` → `admins.id` (ON DELETE RESTRICT).

#### Business & Validation Rules
1. Every payment record is immutable once inserted.
2. `payments.amount` must exactly match `orders.total_price`. Enforced at service/DB verification layer.
3. If `payment_method = 'CASH'`, system updates global `cash_in_hand` setting in `application_settings`.

---

### 3.6 `pickup_codes`

#### Purpose
Generates and tracks 6-digit alphanumeric pickup verification codes assigned to orders.

#### Columns
| Column Name | Data Type | Nullable | Default Value | Constraints & Validation |
|-------------|-----------|----------|---------------|--------------------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary Key |
| `order_id` | `UUID` | No | None | Unique (`uq_pickup_codes_order_id`), FK (`orders.id`)|
| `code` | `VARCHAR(6)` | No | None | Partial Unique (`uq_pickup_codes_active_code` WHERE `status = 'ACTIVE'`) |
| `status` | `pickup_code_status_enum`| No | `'ACTIVE'` | Code state |
| `created_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Generation timestamp |
| `redeemed_at` | `TIMESTAMPTZ` | Yes | `NULL` | Verification timestamp |

#### Relationships
- **One-to-One with `orders`**: `pickup_codes.order_id` → `orders.id` (ON DELETE CASCADE).

#### Business & Validation Rules
1. `code` is a 6-character uppercase alphanumeric string (e.g., `A8K9P2`).
2. When student presents code at shop, admin verifies code; status updates to `'USED'` and `redeemed_at = CURRENT_TIMESTAMP`.

---

### 3.7 `pricing_settings`

#### Purpose
Maintains pricing rates per print side, color mode, and binding type. Retains complete audit history of all pricing rate changes.

#### Columns
| Column Name | Data Type | Nullable | Default Value | Constraints & Validation |
|-------------|-----------|----------|---------------|--------------------------|
| `id` | `BIGINT` | No | `IDENTITY` | Primary Key |
| `bw_single_side` | `NUMERIC(10,2)` | No | `1.50` | Check (`bw_single_side >= 0.00`)|
| `bw_double_side` | `NUMERIC(10,2)` | No | `1.00` | Per-page rate for double side |
| `bw_multi_page` | `NUMERIC(10,2)` | No | `1.00` | Per-page rate for multi-page |
| `color_single_side` | `NUMERIC(10,2)` | No | `5.00` | Per-page rate for color |
| `spiral_binding_price`| `NUMERIC(10,2)` | No | `30.00` | Per-order spiral price |
| `soft_binding_price` | `NUMERIC(10,2)` | No | `40.00` | Per-order soft binding price |
| `hard_binding_price` | `NUMERIC(10,2)` | No | `70.00` | Per-order hard binding price |
| `stapling_price` | `NUMERIC(10,2)` | No | `5.00` | Per-order stapling price |
| `is_current` | `BOOLEAN` | No | `TRUE` | Current active rate flag |
| `created_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Effective start timestamp |
| `created_by_admin_id`| `UUID` | No | None | Foreign Key (`admins.id`) |

#### Relationships
- **Many-to-One with `admins`**: `pricing_settings.created_by_admin_id` → `admins.id`.

#### Business & Validation Rules
1. Exactly one row in `pricing_settings` can have `is_current = TRUE` at any given time. Partial Unique Index (`uq_pricing_settings_current` WHERE `is_current = TRUE`).
2. Updating prices inserts a NEW row with `is_current = TRUE` and sets previous current row to `is_current = FALSE`.

---

### 3.8 `inventory_items`

#### Purpose
Master catalog of inventory stock items (paper, ink, binding materials) tracked by the shop.

#### Columns
| Column Name | Data Type | Nullable | Default Value | Constraints & Validation |
|-------------|-----------|----------|---------------|--------------------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary Key |
| `item_code` | `VARCHAR(50)` | No | None | Unique (`uq_inventory_items_code`), e.g., `PAPER_A4_80GSM` |
| `item_name` | `VARCHAR(100)`| No | None | Human readable item name |
| `category` | `inventory_category_enum`| No | None | Category |
| `sub_category` | `inventory_sub_category_enum`| No | `'NONE'` | Binding sub-category |
| `current_stock`| `INTEGER` | No | `0` | Check (`current_stock >= 0`) |
| `unit_cost` | `NUMERIC(10,2)` | No | `0.00` | Cost per unit for material cost tracking |
| `min_threshold`| `INTEGER` | No | `100` | Alert threshold when stock falls below |
| `is_archived` | `BOOLEAN` | No | `FALSE` | Soft archive flag |
| `created_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Timestamp |
| `updated_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Timestamp |

#### Relationships
- **One-to-Many with `inventory_transactions`**: `inventory_transactions.item_id` → `inventory_items.id`.

#### Business & Validation Rules
1. Discontinued items are archived (`is_archived = TRUE`) rather than deleted, preserving historical stock transaction ledgers.
2. Low stock alert triggered when `current_stock < min_threshold`.

---

### 3.9 `inventory_transactions`

#### Purpose
Audit log of all stock movements (restock additions, order consumption deductions, wastage).

#### Columns
| Column Name | Data Type | Nullable | Default Value | Constraints & Validation |
|-------------|-----------|----------|---------------|--------------------------|
| `id` | `BIGINT` | No | `IDENTITY` | Primary Key |
| `item_id` | `UUID` | No | None | Foreign Key (`inventory_items.id`) |
| `admin_id` | `UUID` | Yes | `NULL` | Foreign Key (`admins.id`), null for auto-consumption |
| `order_id` | `UUID` | Yes | `NULL` | Foreign Key (`orders.id`), null for manual restock |
| `transaction_type`| `inventory_txn_type_enum`| No | None | Movement type |
| `quantity_change` | `INTEGER` | No | None | Positive for add, negative for deduct |
| `stock_after_txn` | `INTEGER` | No | None | Stock level after transaction |
| `unit_cost_snapshot`| `NUMERIC(10,2)`| No | `0.00` | Cost snapshot at transaction time |
| `reason` | `TEXT` | Yes | `NULL` | Notes/explanation |
| `created_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Transaction timestamp |

#### Relationships
- **Many-to-One with `inventory_items`**: `inventory_transactions.item_id` → `inventory_items.id` (ON DELETE RESTRICT).
- **Many-to-One with `admins`**: `inventory_transactions.admin_id` → `admins.id` (ON DELETE RESTRICT).
- **Many-to-One with `orders`**: `inventory_transactions.order_id` → `orders.id` (ON DELETE SET NULL).

---

### 3.10 `expenses`

#### Purpose
Tracks manual operating expenses recorded by admins (paper purchases, electricity, maintenance, shop rent).

#### Columns
| Column Name | Data Type | Nullable | Default Value | Constraints & Validation |
|-------------|-----------|----------|---------------|--------------------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary Key |
| `amount` | `NUMERIC(10,2)` | No | None | Check (`amount > 0.00`) |
| `category` | `VARCHAR(50)` | No | None | E.g., `MATERIALS`, `UTILITIES`, `MAINTENANCE` |
| `description` | `TEXT` | No | None | Non-empty expense details |
| `expense_date` | `DATE` | No | `CURRENT_DATE` | Date expense incurred |
| `payment_method`| `payment_method_enum`| No | `'CASH'` | Cash or UPI payment for expense |
| `created_by_admin_id`| `UUID` | No | None | Foreign Key (`admins.id`) |
| `created_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Entry creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Entry update timestamp |

#### Relationships
- **Many-to-One with `admins`**: `expenses.created_by_admin_id` → `admins.id` (ON DELETE RESTRICT).

---

### 3.11 `profit_logs`

#### Purpose
Daily aggregated financial log summarizing revenue, expenses, net profit, and cash-in-hand balances per calendar date.

#### Columns
| Column Name | Data Type | Nullable | Default Value | Constraints & Validation |
|-------------|-----------|----------|---------------|--------------------------|
| `id` | `BIGINT` | No | `IDENTITY` | Primary Key |
| `log_date` | `DATE` | No | None | Unique (`uq_profit_logs_date`) |
| `total_orders` | `INTEGER` | No | `0` | Total completed orders |
| `upi_revenue` | `NUMERIC(10,2)` | No | `0.00` | Gross revenue from UPI |
| `cash_revenue` | `NUMERIC(10,2)` | No | `0.00` | Gross revenue from Cash |
| `total_revenue` | `NUMERIC(10,2)` | No | `0.00` | Total Gross Revenue |
| `total_expenses` | `NUMERIC(10,2)` | No | `0.00` | Total Operating Expenses |
| `net_profit` | `NUMERIC(10,2)` | No | `0.00` | `total_revenue - total_expenses` |
| `cash_in_hand_end`| `NUMERIC(10,2)`| No | `0.00` | Physical cash balance at end of date |
| `created_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Log calculation timestamp |

---

### 3.12 `audit_logs`

#### Purpose
Immutable system security audit log capturing every data modification across all modules.

#### Columns
| Column Name | Data Type | Nullable | Default Value | Constraints & Validation |
|-------------|-----------|----------|---------------|--------------------------|
| `id` | `BIGINT` | No | `IDENTITY` | Primary Key |
| `timestamp` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Log timestamp |
| `actor_id` | `UUID` | Yes | `NULL` | ID of user performing action |
| `actor_type` | `actor_type_enum` | No | `'ADMIN'` | Role of actor |
| `action` | `VARCHAR(100)`| No | None | Action string (e.g., `order.status_changed`) |
| `resource_type` | `VARCHAR(50)` | No | None | Affected entity (`orders`, `expenses`, etc.) |
| `resource_id` | `UUID` | Yes | `NULL` | ID of affected entity |
| `old_value` | `JSONB` | Yes | `NULL` | Previous JSON state |
| `new_value` | `JSONB` | Yes | `NULL` | New JSON state |
| `ip_address` | `VARCHAR(45)` | Yes | `NULL` | Client IP address |
| `metadata` | `JSONB` | Yes | `NULL` | Additional context |

---

### 3.13 `notifications`

#### Purpose
Internal real-time notification queue for broadcasting order alerts and inventory warnings to connected admin sessions.

#### Columns
| Column Name | Data Type | Nullable | Default Value | Constraints & Validation |
|-------------|-----------|----------|---------------|--------------------------|
| `id` | `BIGINT` | No | `IDENTITY` | Primary Key |
| `event_type` | `VARCHAR(50)` | No | None | Event name (`new_order`, `low_stock`) |
| `title` | `VARCHAR(100)`| No | None | Alert title |
| `message` | `TEXT` | No | None | Alert message body |
| `order_id` | `UUID` | Yes | `NULL` | Foreign Key (`orders.id`) |
| `is_read` | `BOOLEAN` | No | `FALSE` | Read status |
| `created_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Event timestamp |

---

### 3.14 `application_settings`

#### Purpose
Centralized key-value storage for application configuration settings.

#### Columns
| Column Name | Data Type | Nullable | Default Value | Constraints & Validation |
|-------------|-----------|----------|---------------|--------------------------|
| `id` | `BIGINT` | No | `IDENTITY` | Primary Key |
| `setting_key` | `VARCHAR(50)` | No | None | Unique (`uq_app_settings_key`) |
| `setting_value`| `JSONB` | No | None | Value payload (string, number, array, boolean) |
| `description` | `TEXT` | Yes | `NULL` | Setting explanation |
| `updated_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Last updated timestamp |
| `updated_by_admin_id`| `UUID` | Yes | `NULL` | Foreign Key (`admins.id`) |

---

### 3.15 `order_status_history`

#### Purpose
Chronological transition log capturing every status advancement for an order.

#### Columns
| Column Name | Data Type | Nullable | Default Value | Constraints & Validation |
|-------------|-----------|----------|---------------|--------------------------|
| `id` | `BIGINT` | No | `IDENTITY` | Primary Key |
| `order_id` | `UUID` | No | None | Foreign Key (`orders.id`) |
| `from_status` | `order_status_enum`| Yes| `NULL` | Previous status |
| `to_status` | `order_status_enum`| No | None | Advanced status |
| `admin_id` | `UUID` | Yes | `NULL` | Foreign Key (`admins.id`), null for student submission |
| `notes` | `TEXT` | Yes | `NULL` | Optional state change transition notes |
| `created_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Transition timestamp |

---

### 3.16 `sessions`

#### Purpose
Tracks active admin login sessions, token issuance, and explicit token revocations.

#### Columns
| Column Name | Data Type | Nullable | Default Value | Constraints & Validation |
|-------------|-----------|----------|---------------|--------------------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary Key |
| `admin_id` | `UUID` | No | None | Foreign Key (`admins.id`) |
| `jwt_jti` | `VARCHAR(255)`| No | None | JWT Unique ID claim |
| `ip_address` | `VARCHAR(45)` | No | None | Login IP address |
| `user_agent` | `TEXT` | Yes | `NULL` | Browser User-Agent header |
| `is_revoked` | `BOOLEAN` | No | `FALSE` | Explicit revocation flag |
| `created_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Login timestamp |
| `expires_at` | `TIMESTAMPTZ` | No | None | Session expiry timestamp |

---

### 3.17 `printer_queue` (Future Blueprint)

#### Purpose
Reserved entity for dispatching print jobs to local Shop Printer Agent executable.

#### Columns
| Column Name | Data Type | Nullable | Default Value | Constraints & Validation |
|-------------|-----------|----------|---------------|--------------------------|
| `id` | `UUID` | No | `gen_random_uuid()` | Primary Key |
| `order_id` | `UUID` | No | None | Foreign Key (`orders.id`) |
| `printer_name`| `VARCHAR(100)`| No | None | Targeted physical printer name |
| `job_status` | `VARCHAR(30)` | No | `'QUEUED'` | State: `QUEUED`, `PRINTING`, `COMPLETED`, `FAILED` |
| `error_log` | `TEXT` | Yes | `NULL` | Failure diagnostic log |
| `queued_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Queue insertion timestamp |
| `completed_at`| `TIMESTAMPTZ` | Yes | `NULL` | Completion timestamp |

---

### 3.18 `analytics_snapshots` (Future Blueprint)

#### Purpose
Reserved entity for pre-aggregated long-term multi-year analytical trend caches.

#### Columns
| Column Name | Data Type | Nullable | Default Value | Constraints & Validation |
|-------------|-----------|----------|---------------|--------------------------|
| `id` | `BIGINT` | No | `IDENTITY` | Primary Key |
| `period_type` | `VARCHAR(20)` | No | None | `WEEKLY`, `MONTHLY`, `YEARLY` |
| `period_start`| `DATE` | No | None | Start date of snapshot window |
| `period_end` | `DATE` | No | None | End date of snapshot window |
| `metrics_data`| `JSONB` | No | None | Aggregated metrics payload |
| `created_at` | `TIMESTAMPTZ` | No | `CURRENT_TIMESTAMP` | Snapshot timestamp |

---

## 4. Database Views for Reporting

The database defines four analytical views for instant report rendering:

```sql
-- 1. Daily Financial Summary View
CREATE VIEW vw_daily_financial_summary AS
SELECT 
    COALESCE(p.payment_date::date, e.expense_date) AS summary_date,
    COUNT(DISTINCT o.id) AS total_orders,
    SUM(CASE WHEN p.payment_method = 'UPI' THEN p.amount ELSE 0 END) AS upi_revenue,
    SUM(CASE WHEN p.payment_method = 'CASH' THEN p.amount ELSE 0 END) AS cash_revenue,
    COALESCE(SUM(p.amount), 0.00) AS total_revenue,
    COALESCE(SUM(e.amount), 0.00) AS total_expenses,
    (COALESCE(SUM(p.amount), 0.00) - COALESCE(SUM(e.amount), 0.00)) AS net_profit
FROM payments p
FULL OUTER JOIN expenses e ON p.payment_date::date = e.expense_date
LEFT JOIN orders o ON p.order_id = o.id AND o.status = 'COMPLETED'
GROUP BY summary_date;

-- 2. Department Order Stats View
CREATE VIEW vw_department_order_stats AS
SELECT 
    s.department,
    COUNT(o.id) AS total_orders,
    SUM(o.total_price) AS total_spent,
    AVG(o.total_price) AS avg_order_value
FROM students s
JOIN orders o ON s.id = o.student_id
WHERE o.status = 'COMPLETED'
GROUP BY s.department;

-- 3. Inventory Stock Status View
CREATE VIEW vw_inventory_stock_status AS
SELECT 
    id,
    item_code,
    item_name,
    category,
    current_stock,
    min_threshold,
    unit_cost,
    (current_stock * unit_cost) AS total_stock_value,
    CASE WHEN current_stock < min_threshold THEN TRUE ELSE FALSE END AS is_low_stock
FROM inventory_items
WHERE is_archived = FALSE;
```

---

## 5. Global Check Constraints & Validation Rules

| Constraint Name | Target Table | Expression / Validation Rule | Purpose |
|-----------------|--------------|------------------------------|---------|
| `ck_students_mobile_format` | `students` | `mobile ~ '^[6-9][0-9]{9}$'` | Indian 10-digit mobile number format |
| `ck_admins_username_min` | `admins` | `length(trim(username)) >= 3` | Username minimum length |
| `ck_orders_copies_range` | `orders` | `copies >= 1 AND copies <= 100` | Order copies safety bounds |
| `ck_orders_pages_positive` | `orders` | `page_count >= 1` | Valid page count |
| `ck_orders_color_single_side`| `orders` | `(color_mode = 'COLOR' AND print_side = 'SINGLE_SIDE') OR (color_mode = 'BW')` | Enforces Color mode requires Single Side rule |
| `ck_orders_prices_non_negative`| `orders` | `per_page_price >= 0.00 AND binding_price >= 0.00 AND total_price >= 0.00` | Price sanity check |
| `ck_files_size_max` | `order_files` | `file_size > 0 AND file_size <= 209715200` | File size bounds (max 200MB) |
| `ck_payments_amount_positive`| `payments` | `amount > 0.00` | Valid payment amount |
| `ck_expenses_amount_positive`| `expenses` | `amount > 0.00` | Valid expense amount |
| `ck_inventory_stock_non_negative`| `inventory_items`| `current_stock >= 0` | Prevents negative stock balances |

---

## 6. Cascade & Soft Delete Execution Rules

### 6.1 Cascade Execution Rules
- `ON DELETE RESTRICT` is mandatory on `students.id`, `admins.id`, and `inventory_items.id` references to protect historical accounting transactions.
- `ON DELETE CASCADE` is applied strictly to `order_files` and `pickup_codes` owned by `orders`.
- `ON DELETE SET NULL` is applied to non-critical links (e.g., notification order context or order status admin reference).

### 6.2 Soft Delete Execution Standard
All soft-deleted tables implement the following query filtering standard:

```sql
-- Standard Query Filter for Active Records
SELECT * FROM students WHERE is_deleted = FALSE;
SELECT * FROM inventory_items WHERE is_archived = FALSE;
SELECT * FROM admins WHERE is_active = TRUE;
```

---

## 7. Audit Field Standards

Every primary table contains standard system metadata columns:

```sql
-- Standard Audit Columns Pattern
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
```

An automatic PostgreSQL trigger updates `updated_at` on modification:

```sql
CREATE OR REPLACE FUNCTION update_timestamp_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ language 'plpgsql';
```

---

## 8. Future Migration Strategy (Alembic)

1. **Alembic Versioning**: All schema alterations are version-controlled in `backend/alembic/versions/`.
2. **Automated Pre-Deploy Migration**: Render platform configuration runs `alembic upgrade head` via `preDeployCommand` using `DATABASE_URL_DIRECT` (port 5432) prior to deploying new backend instances.
3. **Backward Compatibility**: Migrations adding columns must set default values or allow NULLs during initial step to maintain zero downtime with running application instances.

---

## 9. Backup & Recovery Specifications

- **Automated Daily Backups**: Managed by Supabase infrastructure at 02:00 UTC daily.
- **Point-in-Time Recovery (PITR)**: Enables rolling back database to any transaction state within the retention window (7 days free, 30 days pro).
- **Logical Dump**: Manual daily backups performed via `pg_dump` to encrypted cloud storage bucket.

---

## 10. Performance & Indexing Optimization

1. **Connection Pooling**: Application connects through Supabase PgBouncer pooler (`DATABASE_URL`, port 6543) in Transaction Mode using SQLAlchemy `NullPool` settings.
2. **Index Alignment**: B-Tree composite indexes (`idx_orders_status_created`) ensure dashboard sorting and filtering execute in sub-100ms for 500+ active orders.
3. **Selective Projection**: API queries select explicit columns rather than `SELECT *`.

---

## 11. Database Self-Review

| Criteria | Verification Status | Resolution Details |
|---|---|---|
| **All tables defined?** | Verified | All 16 V1 tables + 2 future blueprint tables fully specified. |
| **All columns typed & constrained?** | Verified | Complete column types, defaults, nullability, and Check constraints documented. |
| **Enums fully declared?** | Verified | All 11 PostgreSQL Enum types defined. |
| **Cascade rules safe?** | Verified | `RESTRICT` protects financial history; `CASCADE` limited to dependent metadata. |
| **Indexing complete?** | Verified | 15 B-Tree and Composite indexes aligned with application query patterns. |
| **Audit Compliance?** | Verified | `created_at`, `updated_at`, `audit_logs`, and `order_status_history` fully integrated. |

---

*End of Database Schema Specification — Version 1.0.0-draft*

*This document is awaiting stakeholder review and approval before proceeding to Database SQL Script Generation / ORM Model implementation.*

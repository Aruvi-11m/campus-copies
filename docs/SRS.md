# Campus Copies — Software Requirements Specification (SRS)

| Field              | Value                                      |
| ------------------ | ------------------------------------------ |
| Document Title     | Software Requirements Specification        |
| Project Name       | Campus Copies                              |
| Version            | 1.0.0-draft                                |
| Status             | Awaiting Stakeholder Approval              |
| Author             | Lead Software Architect                    |
| Created            | 2026-07-21                                 |
| Last Updated       | 2026-07-21                                 |

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Business Objectives](#2-business-objectives)
3. [Scope](#3-scope)
4. [Actors](#4-actors)
5. [Functional Requirements](#5-functional-requirements)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [User Workflows](#7-user-workflows)
8. [Constraints](#8-constraints)
9. [Future Expansion](#9-future-expansion)
10. [Success Criteria](#10-success-criteria)
11. [Assumptions](#11-assumptions)
12. [Risks](#12-risks)
13. [Dependencies](#13-dependencies)
14. [Out of Scope Features](#14-out-of-scope-features)
15. [Glossary](#15-glossary)
16. [Questions Before Development](#16-questions-before-development)

---

## 1. Project Overview

### 1.1 Purpose

Campus Copies is a production-grade Enterprise Resource Planning (ERP) system designed for a college printing and photocopying shop. It replaces an existing manual, WhatsApp-based workflow with a browser-based management system.

### 1.2 Problem Statement

The current workflow operates through WhatsApp messages. Students send files, specifications, and payment confirmations through chat. The shop owner manually tracks orders, payments, and inventory through memory and informal record-keeping.

This approach creates the following problems:

- Orders are lost or forgotten in chat history.
- No centralized record of payments, revenues, or expenses.
- No inventory tracking — stock shortages are discovered only at the point of use.
- No structured order queue — priority and status are managed mentally.
- Payment verification relies on screenshots that can be fabricated.
- No reporting capability for business performance analysis.
- The process does not scale beyond a single operator.

### 1.3 Solution

Campus Copies provides a structured, browser-based system where:

- Students submit print orders through a web form instead of WhatsApp.
- Admins manage, track, and fulfill orders through a dedicated dashboard.
- Payments are tracked and verified by admin decision — not by screenshot.
- Inventory, finances, and reports are maintained automatically.
- The system enforces a defined order lifecycle with clear status transitions.

### 1.4 Project Priorities

Listed in strict order of importance:

| Priority | Attribute       | Rationale                                                                     |
| -------- | --------------- | ----------------------------------------------------------------------------- |
| 1        | Reliability     | The system must not lose orders or data. A lost order is a lost customer.     |
| 2        | Correctness     | Pricing, status, and inventory calculations must be accurate.                 |
| 3        | Maintainability | The codebase must be understandable and modifiable by future developers.      |
| 4        | Simplicity      | Minimal UI complexity. Functionality over aesthetics.                         |
| 5        | Security        | Admin data, student data, and financial records must be protected.            |
| 6        | Performance     | The system must respond quickly on low-bandwidth college campus networks.     |

Beautiful UI is explicitly **not** a priority. Functional, clear, and usable interfaces are sufficient.

---

## 2. Business Objectives

| ID     | Objective                                                                                   |
| ------ | ------------------------------------------------------------------------------------------- |
| BO-01  | Eliminate dependency on WhatsApp for receiving and managing print orders.                    |
| BO-02  | Provide a single system to manage orders from submission to pickup.                         |
| BO-03  | Enable accurate financial tracking — revenue, expenses, profit, and cash in hand.           |
| BO-04  | Enable inventory tracking for paper, ink, and binding materials.                            |
| BO-05  | Provide daily, weekly, monthly, and yearly business performance reports.                    |
| BO-06  | Support up to 3 concurrent admin operators for the shop.                                    |
| BO-07  | Reduce order processing errors caused by miscommunication in chat.                          |
| BO-08  | Provide students with a fast, self-service order submission experience.                     |

---

## 3. Scope

### 3.1 In Scope (Version 1)

- Student-facing order submission portal (browser-based).
- Admin-facing dashboard for order management, finance, inventory, reports, and settings.
- File upload and storage for print orders.
- Manual payment verification by admin.
- Order lifecycle management with defined status transitions.
- Dynamic pricing configurable by admin.
- Financial tracking: revenue, expenses, profit, cash in hand.
- Inventory tracking: paper, ink, binding materials.
- Reporting: daily, weekly, monthly, yearly.
- Admin settings management.
- Browser notifications for new orders (admin only).

### 3.2 Out of Scope (Version 1)

See [Section 14](#14-out-of-scope-features) for the full list.

---

## 4. Actors

### 4.1 Student

| Attribute       | Description                                                                     |
| --------------- | ------------------------------------------------------------------------------- |
| Identity        | A college student who needs documents printed or photocopied.                   |
| Authentication  | Name + Mobile Number. No password.                                              |
| Capabilities    | Submit orders, upload files, select print options, view order status.            |
| Access Level    | Can only view and interact with their own orders.                               |
| Technical Skill | Assumed to have basic smartphone/computer literacy.                              |

### 4.2 Admin

| Attribute       | Description                                                                     |
| --------------- | ------------------------------------------------------------------------------- |
| Identity        | Shop owner or authorized staff member.                                          |
| Authentication  | Username + Password. Secure login.                                              |
| Capabilities    | Manage all orders, manage payments, manage inventory, manage finance, generate reports, configure settings, manage other admins. |
| Access Level    | Full system access.                                                             |
| Limit           | Maximum 3 active admin accounts at any time.                                    |

---

## 5. Functional Requirements

### 5.1 Student Authentication

| ID      | Requirement                                                                                  |
| ------- | -------------------------------------------------------------------------------------------- |
| FR-1.1  | The system shall allow a student to log in by providing their **Name** and **Mobile Number**. |
| FR-1.2  | The system shall require the student to select their **Department** from a predefined list.   |
| FR-1.3  | The department list shall be managed by the admin through the Settings module.                |
| FR-1.4  | If a mobile number already exists in the system, the system shall associate the new session with the existing student record. |
| FR-1.5  | Student login does not require a password.                                                   |
| FR-1.6  | The mobile number shall be validated as a 10-digit Indian mobile number.                     |
| FR-1.7  | The student name shall be required and non-empty.                                            |

### 5.2 File Upload

| ID      | Requirement                                                                                  |
| ------- | -------------------------------------------------------------------------------------------- |
| FR-2.1  | The system shall allow a student to upload **multiple files** in a single order.              |
| FR-2.2  | Supported file formats: **PDF, DOC, DOCX, PPT, PPTX**.                                      |
| FR-2.3  | The system shall reject any file not matching the supported formats.                         |
| FR-2.4  | The maximum upload size shall be **200 MB per file**.                                        |
| FR-2.5  | The system shall store the original uploaded file without any modification or conversion.    |
| FR-2.6  | The system shall validate file integrity after upload (file is not corrupted or empty).      |
| FR-2.7  | The system shall display upload progress to the student.                                     |
| FR-2.8  | If an upload fails, the system shall notify the student and allow retry.                     |

### 5.3 Print Configuration

| ID      | Requirement                                                                                  |
| ------- | -------------------------------------------------------------------------------------------- |
| FR-3.1  | The paper size shall be fixed to **A4**. No other paper size is supported in Version 1.      |
| FR-3.2  | The student shall select one **print side** option per order: **Single Side**, **Double Side**, or **Multi-page**. |
| FR-3.3  | The student shall select one **color mode**: **Black & White** or **Color**.                  |
| FR-3.4  | **Color printing is restricted to Single Side only.** If the student selects Color, the print side must be Single Side. The system shall enforce this constraint. |
| FR-3.5  | Black & White printing is available for all print side options (Single Side, Double Side, Multi-page). |
| FR-3.6  | The student shall specify the **number of copies**, with a minimum of **1** and a maximum of **100**. |
| FR-3.7  | The student shall select one **binding option**: **None**, **Spiral**, **Soft**, **Hard**, or **Stapling**. |
| FR-3.8  | The system shall apply the selected print configuration to **all files** within the order.   |
| FR-3.9  | The default values shall be: Single Side, Black & White, 1 copy, No binding.                 |

### 5.4 Order Price Calculation

| ID      | Requirement                                                                                  |
| ------- | -------------------------------------------------------------------------------------------- |
| FR-4.1  | The system shall calculate the total order price based on the admin-configured pricing rules. |
| FR-4.2  | Pricing factors: print side type, color mode, number of pages, number of copies, binding type. |
| FR-4.3  | The calculated price shall be displayed to the student **before** order confirmation.        |
| FR-4.4  | The price shall be computed using the pricing rules active at the time of order creation.    |
| FR-4.5  | If admin updates pricing after an order is created, the existing order price shall **not** change. |

### 5.5 Order Submission

| ID      | Requirement                                                                                  |
| ------- | -------------------------------------------------------------------------------------------- |
| FR-5.1  | The system shall allow the student to review all order details (files, configuration, price) before submission. |
| FR-5.2  | Upon submission, the order shall be assigned the status **Pending Payment**.                  |
| FR-5.3  | Each order shall be assigned a unique, human-readable **Order ID**.                          |
| FR-5.4  | The system shall record the order creation timestamp.                                        |
| FR-5.5  | Upon order submission, the system shall trigger a **browser notification** to all active admin sessions. |

### 5.6 Payment

| ID      | Requirement                                                                                  |
| ------- | -------------------------------------------------------------------------------------------- |
| FR-6.1  | After order submission, the system shall display the **UPI ID** to the student for payment.  |
| FR-6.2  | The default UPI ID is **6381056942@upi**. This is configurable by admin through Settings.    |
| FR-6.3  | The system shall provide a **Cash Payment** option for students who wish to pay in person.   |
| FR-6.4  | The system shall **not** require or accept a payment screenshot from the student.            |
| FR-6.5  | Payment verification is entirely manual — the admin marks the payment status.                |
| FR-6.6  | The admin shall set the payment status to one of: **Pending**, **Paid via UPI**, **Paid via Cash**. |
| FR-6.7  | When admin marks payment as **Paid via Cash**, the system shall add the order amount to **Cash in Hand**. |
| FR-6.8  | When admin marks payment as **Paid via UPI**, the system shall record it as UPI revenue.     |

### 5.7 Order Status Lifecycle

| ID      | Requirement                                                                                  |
| ------- | -------------------------------------------------------------------------------------------- |
| FR-7.1  | Every order shall follow this status lifecycle in strict sequence:                           |

```
Pending Payment → Paid → Printing → Ready for Pickup → Completed
```

| ID      | Requirement                                                                                  |
| ------- | -------------------------------------------------------------------------------------------- |
| FR-7.2  | The system shall **not** allow skipping any status in the lifecycle.                         |
| FR-7.3  | The system shall **not** allow backward status transitions (e.g., Printing → Paid).         |
| FR-7.4  | Only an admin can transition an order from one status to the next.                           |
| FR-7.5  | The transition from **Pending Payment** to **Paid** requires the admin to set the payment method (UPI or Cash). |
| FR-7.6  | The system shall record the timestamp of every status transition.                            |
| FR-7.7  | The system shall record which admin performed each status transition.                        |

### 5.8 Order Tracking (Student)

| ID      | Requirement                                                                                  |
| ------- | -------------------------------------------------------------------------------------------- |
| FR-8.1  | The student shall be able to view the current status of their submitted orders.              |
| FR-8.2  | The student shall be able to view their order history (all past orders).                     |
| FR-8.3  | The student shall see: Order ID, file names, print configuration, price, current status, timestamps. |

### 5.9 Order Management (Admin)

| ID      | Requirement                                                                                  |
| ------- | -------------------------------------------------------------------------------------------- |
| FR-9.1  | The admin dashboard shall display all orders, sortable and filterable by status.             |
| FR-9.2  | The admin shall be able to view full order details: student name, mobile number, department, files, configuration, price, status history. |
| FR-9.3  | The admin shall be able to advance an order to the next status in the lifecycle.             |
| FR-9.4  | The admin shall be able to download any uploaded file from an order.                         |
| FR-9.5  | The admin shall be able to preview PDF files directly in the browser.                        |
| FR-9.6  | For non-PDF files (DOC, DOCX, PPT, PPTX), the admin shall download the file.               |
| FR-9.7  | The admin shall receive **browser notifications** when a new order is submitted.             |
| FR-9.8  | The admin dashboard shall display a count of orders in each status category.                 |

### 5.10 Admin Authentication and Management

| ID       | Requirement                                                                                 |
| -------- | ------------------------------------------------------------------------------------------- |
| FR-10.1  | Admin login shall require a **username** and **password**.                                  |
| FR-10.2  | Passwords shall be stored securely using a one-way hashing algorithm.                       |
| FR-10.3  | The system shall support a maximum of **3 active admin accounts** at any time.              |
| FR-10.4  | An existing admin shall be able to create new admin accounts (up to the limit of 3).        |
| FR-10.5  | An admin shall be able to deactivate another admin account.                                 |
| FR-10.6  | A deactivated admin account shall not count toward the 3-admin limit.                       |
| FR-10.7  | The system shall prevent deletion of the last remaining active admin account.               |
| FR-10.8  | Admin sessions shall expire after a configurable period of inactivity.                      |

### 5.11 Finance Module

| ID       | Requirement                                                                                 |
| -------- | ------------------------------------------------------------------------------------------- |
| FR-11.1  | The system shall track **Revenue**: total income from all completed paid orders.            |
| FR-11.2  | Revenue shall be categorized by payment method: **UPI** and **Cash**.                       |
| FR-11.3  | The system shall track **Expenses**: costs incurred for materials and operations.           |
| FR-11.4  | The admin shall be able to manually add expense entries with: amount, category, description, date. |
| FR-11.5  | The system shall calculate **Profit**: Revenue minus Expenses.                              |
| FR-11.6  | The system shall track **Cash in Hand**: the current physical cash available.               |
| FR-11.7  | Cash in Hand shall increase when a cash payment is received.                                |
| FR-11.8  | Cash in Hand shall decrease when a cash expense is recorded.                                |
| FR-11.9  | The system shall track **Material Cost**: cost of paper, ink, and binding materials consumed. |
| FR-11.10 | The admin shall be able to configure the unit cost of each inventory item through Settings.  |

#### 5.11.1 Dynamic Pricing

| ID       | Requirement                                                                                 |
| -------- | ------------------------------------------------------------------------------------------- |
| FR-11.11 | The admin shall be able to configure pricing for each combination of print options.         |
| FR-11.12 | Pricing shall be configurable for at minimum the following parameters:                      |

| Price Parameter                    | Description                                |
| ---------------------------------- | ------------------------------------------ |
| Black & White — Single Side        | Per-page price                             |
| Black & White — Double Side        | Per-page price                             |
| Black & White — Multi-page         | Per-page price                             |
| Color — Single Side                | Per-page price                             |
| Spiral Binding                     | Per-order price                            |
| Soft Binding                       | Per-order price                            |
| Hard Binding                       | Per-order price                            |
| Stapling                           | Per-order price                            |

| ID       | Requirement                                                                                 |
| -------- | ------------------------------------------------------------------------------------------- |
| FR-11.13 | Price changes shall take effect only for **new orders** created after the change.           |
| FR-11.14 | The system shall retain a history of pricing changes for audit purposes.                    |

### 5.12 Inventory Module

| ID       | Requirement                                                                                 |
| -------- | ------------------------------------------------------------------------------------------- |
| FR-12.1  | The system shall track inventory for three categories: **Paper**, **Binding Materials**, **Ink**. |
| FR-12.2  | The admin shall be able to view current stock levels for each inventory item.               |
| FR-12.3  | The admin shall be able to add stock (record a purchase/restock).                           |
| FR-12.4  | The admin shall be able to manually deduct stock (record consumption or wastage).           |
| FR-12.5  | Each inventory transaction shall record: item, quantity, type (add/deduct), date, admin who made the change. |
| FR-12.6  | The system shall display a warning when any inventory item falls below a configurable threshold. |
| FR-12.7  | Inventory items under **Binding Materials** shall be sub-categorized: Spiral, Soft Cover, Hard Cover, Staple Pins. |

### 5.13 Reports Module

| ID       | Requirement                                                                                 |
| -------- | ------------------------------------------------------------------------------------------- |
| FR-13.1  | The system shall generate reports for four time periods: **Daily**, **Weekly**, **Monthly**, **Yearly**. |
| FR-13.2  | Each report shall include:                                                                  |

| Report Data Point               | Description                                          |
| ------------------------------- | ---------------------------------------------------- |
| Total Orders                    | Count of orders in the period.                       |
| Orders by Status                | Breakdown by each status in the lifecycle.           |
| Revenue                         | Total income in the period.                          |
| Revenue by Payment Method       | Breakdown by UPI and Cash.                           |
| Expenses                        | Total expenses in the period.                        |
| Profit                          | Revenue minus Expenses.                              |
| Cash in Hand                    | Current cash balance at the end of the period.       |
| Top Departments                 | Departments with the most orders.                    |
| Inventory Consumption           | Units consumed per inventory item.                   |
| Average Order Value             | Revenue divided by total completed orders.           |

| ID       | Requirement                                                                                 |
| -------- | ------------------------------------------------------------------------------------------- |
| FR-13.3  | The admin shall be able to select a specific date or date range for reports.                |
| FR-13.4  | Reports shall be viewable within the admin dashboard.                                       |

### 5.14 Settings Module

| ID       | Requirement                                                                                 |
| -------- | ------------------------------------------------------------------------------------------- |
| FR-14.1  | **UPI ID**: The admin shall be able to view and update the UPI ID displayed to students.   |
| FR-14.2  | **Pricing**: The admin shall be able to view and update all pricing parameters (see FR-11.12). |
| FR-14.3  | **Inventory Costs**: The admin shall be able to view and update unit costs for each inventory item. |
| FR-14.4  | **Admin Limit**: The system shall enforce a maximum of 3 active admins. This limit is a system constant and is not configurable. |
| FR-14.5  | **Notifications**: The admin shall be able to enable or disable browser notifications.      |
| FR-14.6  | **Departments**: The admin shall be able to add, edit, and remove department names. Removing a department shall not affect existing orders associated with that department. |

### 5.15 Notification System

| ID       | Requirement                                                                                 |
| -------- | ------------------------------------------------------------------------------------------- |
| FR-15.1  | The system shall send a **browser notification** to all active admin sessions when a new order is submitted. |
| FR-15.2  | Notifications shall work using the browser's built-in Notification API (Web Push not required in V1). |
| FR-15.3  | The notification shall include: Order ID and student name.                                  |
| FR-15.4  | The admin must grant browser notification permission. The system shall prompt for this on first login. |
| FR-15.5  | If notifications are disabled in settings, no notifications shall be sent.                  |

---

## 6. Non-Functional Requirements

### 6.1 Performance

| ID      | Requirement                                                                                  |
| ------- | -------------------------------------------------------------------------------------------- |
| NFR-1.1 | Pages shall load within **2 seconds** on a standard broadband connection.                   |
| NFR-1.2 | File uploads shall support resumable/chunked uploads for files over **10 MB**.               |
| NFR-1.3 | The admin dashboard shall render the order list within **1 second** for up to **500 active orders**. |
| NFR-1.4 | Report generation shall complete within **5 seconds** for up to **1 year** of data.         |
| NFR-1.5 | The system shall handle at least **50 concurrent users** without performance degradation.   |

### 6.2 Security

| ID      | Requirement                                                                                  |
| ------- | -------------------------------------------------------------------------------------------- |
| NFR-2.1 | All communication between client and server shall use **HTTPS**.                             |
| NFR-2.2 | Admin passwords shall be hashed using a strong, industry-standard one-way hashing algorithm (e.g., bcrypt, argon2). |
| NFR-2.3 | Student sessions shall be tied to the device/browser session. Session tokens shall expire.   |
| NFR-2.4 | Admin sessions shall expire after a configurable inactivity timeout.                        |
| NFR-2.5 | All admin-only endpoints shall be protected by authentication and authorization checks.     |
| NFR-2.6 | Uploaded files shall be stored in a location that is not directly accessible via URL without authentication. |
| NFR-2.7 | Input validation shall be performed on both client and server sides.                        |
| NFR-2.8 | The system shall protect against common web vulnerabilities: XSS, CSRF, SQL injection, path traversal. |
| NFR-2.9 | File uploads shall be validated for file type (by content, not just extension) and size on the server. |
| NFR-2.10 | Rate limiting shall be applied to login endpoints and file upload endpoints.                |

### 6.3 Reliability

| ID      | Requirement                                                                                  |
| ------- | -------------------------------------------------------------------------------------------- |
| NFR-3.1 | The system shall not lose any submitted order or uploaded file under normal operation.       |
| NFR-3.2 | Database operations that affect orders or payments shall be transactional.                   |
| NFR-3.3 | The system shall handle unexpected errors gracefully, displaying user-friendly error messages without exposing internal details. |
| NFR-3.4 | File upload failures shall not leave partial or orphaned files in storage.                   |
| NFR-3.5 | The system shall target **99.5% uptime** during operating hours (8 AM to 8 PM, Monday to Saturday). |

### 6.4 Scalability

| ID      | Requirement                                                                                  |
| ------- | -------------------------------------------------------------------------------------------- |
| NFR-4.1 | The system shall be designed as a single-tenant deployment (one college shop).               |
| NFR-4.2 | The architecture shall support migration to a multi-tenant model in future versions if needed. |
| NFR-4.3 | File storage shall be abstracted so the storage backend (local disk, cloud storage) can be swapped without code changes. |

### 6.5 Maintainability

| ID      | Requirement                                                                                  |
| ------- | -------------------------------------------------------------------------------------------- |
| NFR-5.1 | The codebase shall follow consistent coding standards documented in CodingStandards.md.     |
| NFR-5.2 | All business logic shall be separated from presentation logic.                               |
| NFR-5.3 | The system shall include structured logging for debugging and auditing.                      |
| NFR-5.4 | Configuration (database credentials, file paths, ports) shall be managed through environment variables, not hardcoded. |
| NFR-5.5 | All public API endpoints shall be documented.                                                |

### 6.6 Accessibility

| ID      | Requirement                                                                                  |
| ------- | -------------------------------------------------------------------------------------------- |
| NFR-6.1 | The interface shall be usable with keyboard navigation.                                      |
| NFR-6.2 | Form elements shall have proper labels.                                                      |
| NFR-6.3 | Error messages shall be clearly associated with the relevant form fields.                    |
| NFR-6.4 | The interface shall be functional (not necessarily optimized) on mobile browsers.            |

### 6.7 Browser Compatibility

| ID      | Requirement                                                                                  |
| ------- | -------------------------------------------------------------------------------------------- |
| NFR-7.1 | The system shall be fully functional on the latest two major versions of: **Chrome**, **Firefox**, **Safari**, **Edge**. |
| NFR-7.2 | The student portal shall be functional on **mobile browsers** (Chrome for Android, Safari for iOS). |
| NFR-7.3 | Internet Explorer is not supported.                                                          |

---

## 7. User Workflows

### 7.1 Student Workflow

```
1.  Student opens the Campus Copies web application.
2.  Student enters Name and Mobile Number.
3.  Student selects Department from the dropdown.
4.  Student is taken to the Order Submission page.
5.  Student uploads one or more files (PDF, DOC, DOCX, PPT, PPTX).
6.  Student selects print configuration:
      a. Print Side: Single Side / Double Side / Multi-page
      b. Color Mode: Black & White / Color (Color forces Single Side)
      c. Number of Copies: 1–100
      d. Binding: None / Spiral / Soft / Hard / Stapling
7.  System calculates and displays the total price.
8.  Student reviews order summary (files, configuration, price).
9.  Student confirms and submits the order.
10. System assigns Order ID and sets status to "Pending Payment".
11. System displays UPI ID for payment.
12. Student makes payment via UPI or plans to pay via Cash.
13. Student can view order status on the "My Orders" page.
14. Student picks up the printed order from the shop.
```

### 7.2 Admin Workflow

```
1.  Admin logs in with Username and Password.
2.  Admin lands on the Dashboard showing order counts by status.
3.  Admin receives a browser notification when a new order arrives.
4.  Admin opens the order queue, filtered by "Pending Payment" status.
5.  Admin views order details: student info, files, configuration, price.
6.  Admin verifies payment (checks UPI app or receives cash).
7.  Admin marks payment as "Paid via UPI" or "Paid via Cash".
      → Order status moves to "Paid".
8.  Admin downloads/previews the files.
9.  Admin begins printing and marks status as "Printing".
10. Admin completes printing, applies binding if requested.
11. Admin marks status as "Ready for Pickup".
12. Student arrives and collects the order.
13. Admin marks status as "Completed".
```

### 7.3 Payment Workflow

```
1.  Order is submitted → Status: "Pending Payment".
2.  System displays UPI ID (6381056942@upi) to the student.
3.  Student pays via UPI or indicates Cash Payment.
4.  Student does NOT upload a payment screenshot.
5.  Admin checks UPI app for payment receipt, OR student pays cash in person.
6.  Admin opens the order in the admin dashboard.
7.  Admin selects payment method:
      a. "Paid via UPI" → Revenue recorded as UPI income.
      b. "Paid via Cash" → Revenue recorded as Cash income.
         Cash in Hand is incremented by the order amount.
8.  Order status transitions from "Pending Payment" to "Paid".
9.  If payment is not received, the order remains in "Pending Payment".
```

### 7.4 Pickup Workflow

```
1.  Admin completes printing → marks order as "Ready for Pickup".
2.  Student visits the shop.
3.  Student references their Order ID (visible on their "My Orders" page).
4.  Admin locates the order in the dashboard.
5.  Admin hands over the printed material.
6.  Admin marks order as "Completed".
7.  The order is finalized. No further status changes are possible.
```

### 7.5 Inventory Workflow

```
1.  Admin navigates to the Inventory module.
2.  Admin views current stock levels for: Paper, Ink, Binding Materials.
3.  When new stock is purchased:
      a. Admin adds stock with quantity and date.
      b. Admin records the purchase cost as an expense (in the Finance module).
4.  When stock is consumed or wasted:
      a. Admin manually deducts stock with quantity and date.
5.  When stock falls below the configured threshold:
      a. System displays a low-stock warning on the dashboard.
6.  Admin reviews inventory history for consumption trends.
```

---

## 8. Constraints

| ID   | Constraint                                                                                     |
| ---- | ---------------------------------------------------------------------------------------------- |
| C-01 | **Paper size**: Only A4. No A3, Letter, Legal, or custom sizes.                                |
| C-02 | **Color printing**: Restricted to Single Side only. No Color + Double Side or Color + Multi-page. |
| C-03 | **File formats**: Only PDF, DOC, DOCX, PPT, PPTX. No images, spreadsheets, or other formats. |
| C-04 | **File conversion**: No automatic conversion of DOC/DOCX/PPT/PPTX to PDF in Version 1. Admin downloads and converts manually. |
| C-05 | **Admin limit**: Maximum 3 active admin accounts.                                             |
| C-06 | **Copy limit**: 1 to 100 copies per order.                                                    |
| C-07 | **File size**: Maximum 200 MB per file.                                                       |
| C-08 | **Payment verification**: Manual only. No payment gateway integration. No UPI auto-verify.    |
| C-09 | **Notification type**: Browser Notification API only. No SMS, no email, no mobile push.       |
| C-10 | **Single tenant**: The system serves one shop. No multi-shop or franchise support.            |
| C-11 | **Deployment**: Single-server deployment. No microservices, no container orchestration required in V1. |
| C-12 | **Language**: English only. No localization or multi-language support in V1.                   |

---

## 9. Future Expansion

These features are **not** part of Version 1 but are anticipated for future versions. The architecture should not actively block these expansions.

| ID   | Feature                          | Description                                                    |
| ---- | -------------------------------- | -------------------------------------------------------------- |
| FE-01 | Automatic File Conversion       | Server-side conversion of DOC/DOCX/PPT/PPTX to PDF for preview and printing. |
| FE-02 | Payment Gateway Integration     | Razorpay, Stripe, or UPI auto-verification for automated payment confirmation. |
| FE-03 | SMS/Email Notifications         | Notify students via SMS or email when order status changes.    |
| FE-04 | Page Count Detection            | Automatically detect the number of pages in uploaded documents. |
| FE-05 | Student Accounts with Password  | Secure student authentication with OTP or password.            |
| FE-06 | Multi-Paper Size Support        | Support for A3, Legal, and custom paper sizes.                 |
| FE-07 | Image File Support              | Support for JPG, PNG, TIFF uploads for printing.               |
| FE-08 | Multi-Tenant / Multi-Shop       | Support multiple shops under one deployment.                   |
| FE-09 | Analytics Dashboard             | Visual charts and trends for business performance.             |
| FE-10 | Report Export                   | Export reports as PDF or CSV.                                   |
| FE-11 | Order Cancellation              | Allow students or admins to cancel orders with defined rules.  |
| FE-12 | Refund Tracking                 | Track refunds for cancelled or failed orders.                  |
| FE-13 | Automatic Inventory Deduction   | Deduct inventory automatically based on order specifications.  |
| FE-14 | Mobile App                      | Native or PWA mobile application for students and admins.      |

---

## 10. Success Criteria

The project shall be considered successful when:

| ID    | Criterion                                                                                    |
| ----- | -------------------------------------------------------------------------------------------- |
| SC-01 | A student can submit a print order through the browser without using WhatsApp.               |
| SC-02 | An admin can view, manage, and fulfill orders entirely through the admin dashboard.          |
| SC-03 | Payment is tracked per order with payment method (UPI/Cash) recorded by admin.               |
| SC-04 | The complete order lifecycle (Pending Payment → Completed) is enforced by the system.        |
| SC-05 | Financial summary (revenue, expenses, profit, cash in hand) is accurate.                     |
| SC-06 | Inventory levels are trackable and low-stock warnings function correctly.                    |
| SC-07 | Reports can be generated for daily, weekly, monthly, and yearly periods.                     |
| SC-08 | No order is lost during normal system operation.                                             |
| SC-09 | The system handles at least 50 concurrent users without degradation.                         |
| SC-10 | Admin accounts are secured with hashed passwords and session management.                     |

---

## 11. Assumptions

| ID   | Assumption                                                                                    |
| ---- | --------------------------------------------------------------------------------------------- |
| A-01 | The shop operates from a **single physical location** on a college campus.                    |
| A-02 | Students and admins have access to a **modern web browser** (Chrome, Firefox, Safari, Edge).  |
| A-03 | The shop has a **stable internet connection** for the server and admin devices.               |
| A-04 | Students have intermittent internet access sufficient to submit orders and upload files.      |
| A-05 | Student login by Name + Mobile Number is considered acceptable for V1 (no strong identity verification). |
| A-06 | The admin manually verifies payments by checking their UPI app or receiving cash in person.   |
| A-07 | The admin manually converts non-PDF files to printable format outside the system in V1.      |
| A-08 | The system will be deployed on a single server (VPS, college server, or cloud VM).           |
| A-09 | The 200 MB upload limit refers to a **per-file** limit, not a per-order total.               |
| A-10 | Print configuration (side, color, copies, binding) applies to the **entire order**, not individual files within an order. |
| A-11 | The admin is responsible for entering the number of pages per order for accurate pricing. Automatic page count detection is a future feature. |
| A-12 | There is no order cancellation flow in V1. Orders in "Pending Payment" that are never paid are manually handled by admin. |
| A-13 | Inventory deduction is a manual process in V1. The admin manually updates inventory levels.  |
| A-14 | The system does not need to function offline.                                                 |

---

## 12. Risks

| ID   | Risk                                                  | Likelihood | Impact | Mitigation                                                                 |
| ---- | ----------------------------------------------------- | ---------- | ------ | -------------------------------------------------------------------------- |
| R-01 | Student submits false identity (fake name/number).    | High       | Low    | V1 accepts this risk. Name+phone is for identification, not security. OTP verification is a future feature. |
| R-02 | Large file uploads fail on poor network connections.  | High       | Medium | Implement chunked/resumable uploads. Show upload progress. Allow retry.    |
| R-03 | Admin forgets to update order status.                 | Medium     | Medium | Dashboard prominently shows stale orders. Consider auto-reminders in future. |
| R-04 | Payment is received but admin forgets to mark as paid.| Medium     | Medium | "Pending Payment" orders are prominently displayed. Admin reviews them regularly. |
| R-05 | Stale orders accumulate (never paid, never cancelled).| Medium     | Low    | No auto-cancellation in V1. Admin manually reviews and handles stale orders. |
| R-06 | File storage fills up the server disk.               | Medium     | High   | Monitor disk usage. Implement file retention policy in future version. Low-disk warning in logs. |
| R-07 | Concurrent admin edits to the same order.            | Low        | Medium | Status transition is an atomic operation. Last writer wins at the field level. |
| R-08 | Server downtime during peak hours.                   | Low        | High   | Single-server deployment is a known limitation. Regular backups. Cloud hosting with SLA recommended. |
| R-09 | Browser notification permission denied by admin.     | Medium     | Low    | Prompt admin to enable. Display in-app alert as a fallback.                |
| R-10 | Pricing misconfigured by admin.                      | Low        | High   | Display preview of calculated price. Pricing history for audit.            |

---

## 13. Dependencies

| ID   | Dependency                                                                                   |
| ---- | -------------------------------------------------------------------------------------------- |
| D-01 | A **modern web browser** on the student's device (laptop or smartphone).                     |
| D-02 | A **modern web browser** on the admin's device (laptop or desktop preferred).                |
| D-03 | A **stable internet connection** at the shop for the server and admin devices.               |
| D-04 | A **UPI-enabled bank account** for receiving online payments.                                |
| D-05 | A **server or hosting environment** (VPS, cloud VM, or on-premises machine) for deployment.  |
| D-06 | A **database system** (to be determined in the Architecture phase).                          |
| D-07 | A **file storage system** (local disk or cloud storage, to be determined in Architecture).   |
| D-08 | **HTTPS certificate** for secure communication (e.g., Let's Encrypt).                       |

---

## 14. Out of Scope Features

The following features are explicitly **not** included in Version 1:

| ID    | Feature                                 | Reason                                                              |
| ----- | --------------------------------------- | ------------------------------------------------------------------- |
| OOS-01 | Automatic file conversion (to PDF)     | Complexity. Requires LibreOffice/Pandoc server-side. Deferred.      |
| OOS-02 | Payment gateway integration            | Cost and complexity. Manual verification is sufficient for V1.      |
| OOS-03 | Payment screenshot upload              | Explicitly excluded by stakeholder. Unreliable verification method. |
| OOS-04 | SMS or email notifications             | Cost (SMS gateway fees). Complexity. Browser notifications suffice. |
| OOS-05 | Automatic page count detection         | Requires server-side document parsing. Complex for non-PDF formats. |
| OOS-06 | Student password/OTP authentication    | Complexity. Name + Phone is sufficient for V1 shop context.         |
| OOS-07 | Order cancellation by student          | Business process not yet defined. Requires refund workflow.         |
| OOS-08 | Refund tracking                        | No cancellation in V1, so no refunds needed.                        |
| OOS-09 | Automatic inventory deduction          | Requires page count detection. Manual tracking in V1.               |
| OOS-10 | Multi-paper-size support               | Only A4 in V1. Simplifies pricing and inventory.                    |
| OOS-11 | Image format uploads (JPG, PNG, etc.)  | Only document formats in V1.                                        |
| OOS-12 | Report export (PDF/CSV)               | Dashboard-only viewing in V1.                                        |
| OOS-13 | Student mobile app                     | Web-only in V1. Mobile browser is sufficient.                        |
| OOS-14 | Chat or messaging between student/admin| Not required. Status tracking replaces the need for chat.            |
| OOS-15 | Order editing after submission          | Once submitted, an order is immutable. Student creates a new order.  |
| OOS-16 | Bulk order management                  | Admin processes orders individually in V1.                           |
| OOS-17 | Offline operation                      | Internet connection is required.                                     |
| OOS-18 | Multi-language support                 | English only in V1.                                                  |

---

## 15. Glossary

| Term              | Definition                                                                                  |
| ----------------- | ------------------------------------------------------------------------------------------- |
| Order             | A request submitted by a student to print one or more files with specified configurations.  |
| Order ID          | A unique, human-readable identifier assigned to each order upon submission.                 |
| Order Status      | The current stage of an order in its lifecycle: Pending Payment, Paid, Printing, Ready for Pickup, Completed. |
| Admin             | An authorized shop operator who manages orders, payments, inventory, finance, and settings. |
| Student           | A college student who submits print orders through the web application.                     |
| UPI               | Unified Payments Interface — a real-time payment system used in India.                      |
| Cash in Hand      | The total physical cash currently available at the shop, tracked by the system.             |
| Dynamic Pricing   | Admin-configurable pricing that can be changed at any time and applies to future orders.   |
| Single Side       | Printing on one side of the paper.                                                          |
| Double Side       | Printing on both sides of the paper (also called duplex printing).                         |
| Multi-page        | Printing multiple document pages on a single sheet of paper (e.g., 2-up, 4-up).           |
| Binding           | The method of fastening printed pages together: Spiral, Soft (cover), Hard (cover), Stapling, or None. |
| Material Cost     | The cost of raw materials (paper, ink, binding materials) consumed to fulfill orders.       |
| Revenue           | Total income from paid orders.                                                              |
| Expense           | Any cost incurred in running the shop, including material costs and operational costs.      |
| Profit            | Revenue minus Expenses over a given period.                                                 |
| Browser Notification | A system notification displayed by the web browser, using the Web Notification API.       |
| Session           | A time-limited authenticated connection between a user and the system.                      |
| Inventory Threshold | A configured minimum stock level below which the system displays a low-stock warning.     |
| Department        | The academic department of the student (e.g., Computer Science, Mechanical Engineering).   |

---

## 16. Requirement Validation Checklist

Every question below must be answered before Architecture Design begins. They are grouped by domain and ordered from most critical to least critical.

---

### Pricing & Page Count

> These questions block the core price calculation engine. The system cannot compute an order total without answers here.

☐ **1.** The system prices orders "per page." Since automatic page count detection is out of scope for V1, who enters the page count — the student when placing the order, or the admin after reviewing the files?

☐ **2.** For PDF files specifically, should the system automatically read the page count from the file, or is manual entry still required?

☐ **3.** For Multi-page printing (multiple document pages on one physical sheet), is the price calculated per **document page** or per **physical sheet**? Example: 4 document pages on 1 sheet — is that charged as 4 pages or 1 page?

---

### Print Configuration

> These questions define the order submission form and the constraints the system enforces.

☐ **4.** Does "Multi-page" mean printing multiple document pages on a single physical sheet (e.g., 2 pages per sheet, 4 pages per sheet)?

☐ **5.** If yes, does the student choose the layout (2-up, 4-up, etc.), or is it always a fixed layout decided by the shop?

☐ **6.** Color is restricted to "Single Side only." Confirm: if a student selects Multi-page, should Color be unavailable — same as Double Side?

☐ **7.** Do all files in a single order share the same print settings (side, color, copies, binding)? Or can the student set different settings for each file? If per-file, can different files also have different binding options?

---

### Order Management

> These questions affect the order lifecycle, storage, and operational limits.

☐ **8.** Can an admin permanently delete an order (e.g., a spam or accidental duplicate submission)?

☐ **9.** Should orders stuck in "Pending Payment" automatically expire after a certain number of hours or days? Or does the admin handle stale orders manually?

☐ **10.** After an order is marked "Completed," how long should the uploaded files be kept on the server? Permanently? Or deleted after a set number of days?

☐ **11.** Is there a maximum number of files a student can upload in one order? (e.g., 5 files, 10 files, unlimited?)

☐ **12.** Can the student add a text note or special instruction to the order? (e.g., "Print only pages 3–10" or "Landscape orientation for slides")

---

### Finance

> These questions affect the Cash in Hand and Expense tracking modules.

☐ **13.** When the system is first set up, can the admin enter a starting Cash in Hand balance (the cash already in the register)?

☐ **14.** Should the admin be able to record a **cash withdrawal** (money taken out of the register for bank deposit or personal use)? This would reduce Cash in Hand but is not a business expense.

☐ **15.** Are trackable expenses limited to material costs (paper, ink, binding), or should the admin also be able to log operational costs (electricity, rent, equipment repair)?

---

### Admin Management

> These questions affect the initial system setup and admin permissions.

☐ **16.** How is the very first admin account created? Options: (a) automatically created during deployment with a default username/password, or (b) a one-time setup screen in the browser on first visit.

☐ **17.** Are all admin accounts equal in authority? Or is there one "Super Admin" who has exclusive control over settings and other admin accounts?

☐ **18.** Can an admin change their own password from the dashboard?

---

### Inventory

> These questions affect how inventory quantities are recorded and displayed.

☐ **19.** What unit of measurement should be used for each inventory item? For example: Paper = individual sheets or reams? Ink = cartridges or some other unit? Binding materials = individual units per type?

☐ **20.** Is the inventory list fixed to Paper, Ink, and Binding Materials? Or should the admin be able to add custom inventory categories?

---

### Student Identity

> These questions affect how returning students are identified.

☐ **21.** If a student logs in with the same phone number but a slightly different name (e.g., "Arun" one day and "Arun K" the next), should the system update the stored name to the new one, or keep the original name unchanged?

☐ **22.** Can the same phone number be used to log in from two devices at the same time? Or should the system allow only one active session per phone number?

---

### Notifications

> This question affects whether students receive any system alerts.

☐ **23.** Should students see any notification or alert (within the web app) when their order moves to "Ready for Pickup"? Or are all notifications admin-only in V1?

---

### File Upload Limits

> This confirms a stated assumption about upload size.

☐ **24.** The SRS assumes the 200 MB upload limit is **per file**, not per order total. A student uploading 3 files of 150 MB each (450 MB total) would be allowed. Is this correct?

---

### Summary

| Group                | Questions | Criticality |
| -------------------- | --------- | ----------- |
| Pricing & Page Count | 1–3       | Blocks core feature |
| Print Configuration  | 4–7       | Blocks order form |
| Order Management     | 8–12      | Affects lifecycle |
| Finance              | 13–15     | Affects finance module |
| Admin Management     | 16–18     | Affects setup |
| Inventory            | 19–20     | Affects inventory module |
| Student Identity     | 21–22     | Affects student records |
| Notifications        | 23        | Affects student experience |
| File Upload Limits   | 24        | Confirms assumption |
| **Total**            | **24**    | |

---

*All 24 questions must be resolved before proceeding to Architecture Design.*

*No architecture, database, or API decisions will be made until this checklist is fully answered.*

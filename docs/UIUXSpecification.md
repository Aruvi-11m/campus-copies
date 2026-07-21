# Campus Copies — UI/UX Specification

| Field          | Value                                            |
| -------------- | ------------------------------------------------ |
| Document Title | UI/UX Specification                              |
| Project Name   | Campus Copies                                    |
| Version        | 1.0.0-draft                                      |
| Status         | Awaiting Stakeholder Approval                    |
| Author         | Senior Frontend Architect & Lead UI/UX Designer  |
| Created        | 2026-07-21                                       |
| Last Updated   | 2026-07-21                                       |
| References     | SRS.md v1.0.0, TechnologyStack.md v1.0.0 (Frozen), Architecture.md v2.0.0, DatabaseRelationships.md v1.0.0, Database.md v1.0.0, API.md v1.0.0, BusinessRules.md v1.0.0, BackendSpecification.md v1.0.0 |

---

## Table of Contents

1. [Design Philosophy](#1-design-philosophy)
2. [Navigation & Layout Architecture](#2-navigation--layout-architecture)
3. [Student Portal Screens](#3-student-portal-screens)
4. [Admin Dashboard Screens](#4-admin-dashboard-screens)
5. [Table Design & Data Controls](#5-table-design--data-controls)
6. [Form Design & Interactive Feedback](#6-form-design--interactive-feedback)
7. [Dialogs & Modal Specifications](#7-dialogs--modal-specifications)
8. [Status Colors & Indicator Standards](#8-status-colors--indicator-standards)
9. [Component System: Icons, Buttons, Badges & Cards](#9-component-system-icons-buttons-badges--cards)
10. [Responsive Layout & Viewport Behavior](#10-responsive-layout--viewport-behavior)
11. [Accessibility (a11y) Standards](#11-accessibility-a11y-standards)
12. [Notification & SSE User Experience](#12-notification--sse-user-experience)
13. [Future UI Blueprint](#13-future-ui-blueprint)
14. [UI/UX Specification Self-Review](#14-uiux-specification-self-review)

---

## 1. Design Philosophy

The UI/UX design of Campus Copies adheres strictly to the core priority hierarchy established in [SRS.md §1.4](file:///Users/thamizaruvi/.gemini/antigravity-ide/scratch/campus-copies-erp/docs/SRS.md): **Reliability > Correctness > Maintainability > Simplicity > Security > Performance**.

- **Functional & Task-Focused**: Beautiful UI is explicitly *not* a priority. Functionality, readability, and speed are paramount. Interfaces contain zero decorative clutter or unnecessary animations.
- **Minimalist Aesthetic**: Clean, high-contrast visual hierarchy utilizing Tailwind CSS utility classes. Clean typography, high-contrast text ratios, and distinct status indicators.
- **Fast & Responsive**: Immediate user feedback for every action (button loading states, instant validation errors, optimistic UI updates where appropriate).
- **Desktop First for Admin, Mobile First for Students**:
  - The **Student Portal** is optimized for mobile browsers (Chrome on Android, Safari on iOS) where students submit orders.
  - The **Admin Dashboard** is optimized for desktop viewports (1440px / 1920px) at the shop counter where admins manage high-density order tables.
- **Accessibility Compliance**: Built to meet WCAG 2.1 AA standards for keyboard navigation, screen reader compatibility, and color contrast ratios.

---

## 2. Navigation & Layout Architecture

### 2.1 Student Portal Navigation Layout
- **Header Topbar**: Minimal sticky top bar containing Campus Copies brand logo, student name/mobile badge, "My Orders" link, "New Order" button, and Logout button.
- **Mobile Drawer / Bottom Navigation**: On mobile viewports (< 768px), navigation collapses to a fixed bottom navigation bar with 3 tabs: `[ + New Order ]`, `[ My Orders ]`, `[ Profile ]`.

### 2.2 Admin Dashboard Navigation Layout
- **Sidebar (Left Fixed 250px)**:
  - Header: Campus Copies Admin Logo + Active Operator Name.
  - Navigation Links (with icon + badge count):
    - `[ Dashboard ]` (Summary & low-stock alerts)
    - `[ Orders ]` (Badge: Pending order count)
    - `[ Inventory ]` (Badge: Low stock warning count)
    - `[ Finance ]` (Revenue, expenses, profit)
    - `[ Reports ]` (Daily, weekly, monthly, yearly data tables)
    - `[ Settings ]` (Pricing rates, UPI ID, admin accounts)
    - `[ Audit Logs ]` (Security logs)
  - Footer: Current Server Time (UTC/IST), SSE Connection Status Indicator (`● Live` / `○ Offline`), Logout Button.
- **Topbar (Top Fixed 64px)**:
  - Breadcrumb navigation (`Admin / Orders / CC-2026-0042`).
  - Search bar (Instant order search by Display ID or Mobile).
  - Notification Bell Icon (with unread badge count & drop-down toast panel).
  - Operator Profile Avatar & Role Badge (`Admin`).

---

## 3. Student Portal Screens

### 3.1 Student Login Screen (`/`)
- **Layout**: Centered card container on clean background.
- **Elements**:
  - App Logo & Headline: "Campus Copies — Student Print Portal".
  - Form Fields:
    - `Full Name`: Required text input.
    - `Mobile Number`: Required 10-digit Indian mobile number (`^[6-9][0-9]{9}$`), prefixed with `+91`.
    - `Department`: Select dropdown (`CSE`, `ECE`, `MECH`, `CIVIL`, `EEE`, `IT`, `OTHERS`).
  - Action Button: `[ Continue to Order → ]` (Full width, primary color).
  - Helper Text: "No password required. Login or register instantly with your phone number."

### 3.2 Student Home / New Order Screen (`/order/new`)
- **Layout**: Single-page step-by-step form wizard (Mobile optimized).
- **Step 1: File Upload Section**:
  - Drag & Drop Dropzone + `[ Browse Files ]` button.
  - Accepted Types label: `PDF, DOC, DOCX, PPT, PPTX (Max 200 MB per file, up to 5 files)`.
  - File List Card: Displays uploaded filename, size (MB), progress bar, magic-bytes verification checkmark, and `[ Delete ]` button.
- **Step 2: Print Configuration Section**:
  - `Print Side`: Segmented toggle `[ Single Side ]` | `[ Double Side ]` | `[ Multi-Page ]`.
  - `Color Mode`: Segmented toggle `[ Black & White ]` | `[ Color ]`.
    - *UI Rule*: Selecting `Color` automatically disables `Double Side` and forces `Single Side` (with hint: "Color printing is available in Single Side only").
  - `Copies`: Number stepper input `[-] [ 1 ] [+]` (Range: 1 to 100).
  - `Page Count`: Number input (auto-detected for PDFs, manually confirmed for DOC/PPT).
  - `Binding Option`: Cards radio selection `[ None ]` | `[ Spiral (₹30) ]` | `[ Soft Cover (₹40) ]` | `[ Hard Cover (₹70) ]` | `[ Stapling (₹5) ]`.
- **Step 3: Price Calculation & Summary Card**:
  - Line-item breakdown: Per-page rate, page count, copies multiplier, binding fee.
  - Prominent Total Price Display: `Total Amount: ₹105.00`.
- **Step 4: Order Submission**:
  - Action Button: `[ Submit Print Order ]` (Primary green, shows spinner on click).

### 3.3 Student Order Confirmation & Payment Display Screen (`/orders/:id/confirmation`)
- **Layout**: Order summary card + Payment Instructions.
- **Elements**:
  - Order Display ID: `CC-2026-0042` (Large monospace text).
  - Assigned Pickup Code: `K8P2N9` (Prominent highlighted box with hint: "Show this code at shop counter during pickup").
  - Order Status Badge: `PENDING_PAYMENT` (Yellow badge).
  - Payment Instructions Panel:
    - Total Payable: `₹105.00`.
    - Shop UPI ID: `6381056942@upi` (With `[ Copy UPI ID ]` button).
    - Note: "Pay via any UPI App (GPay, PhonePe, Paytm) OR pay by Physical Cash at shop counter. Admin will verify payment at counter."
  - Action Buttons: `[ Track Order Status ]` | `[ Submit Another Order ]`.

### 3.4 Student My Orders / Order History Screen (`/orders`)
- **Layout**: Chronological order card list (Newest first).
- **Card Elements**:
  - Header: Display ID (`CC-2026-0042`), Timestamp, Status Badge.
  - Body: Filenames list, Print config summary (`Single Side · B&W · 2 Copies · Spiral`), Total Price (`₹105.00`).
  - Action: `[ View Order Details → ]`.

### 3.5 Student Order Detail / Track Screen (`/orders/:id`)
- **Layout**: Order status timeline progress bar + Complete Configuration Detail.
- **Timeline Component**:
  - Step 1: `Submitted` (Checkmark)
  - Step 2: `Payment Verified` (Active / Pending)
  - Step 3: `Printing` (Active / Pending)
  - Step 4: `Ready for Pickup` (Active / Pending)
  - Step 5: `Completed` (Active / Pending)
- **Elements**: Display ID, Pickup Code, Print Configuration, File Download Links (for student reference), Payment status summary.

---

## 4. Admin Dashboard Screens

### 4.1 Admin Login Screen (`/admin/login`)
- **Layout**: Centered secure card layout.
- **Elements**:
  - App Logo: "Campus Copies — Admin Portal".
  - Fields: `Username` (text), `Password` (password with toggle show/hide).
  - Button: `[ Admin Sign In ]`.
  - Security Notice: "Authorized operator access only. All actions are audit-logged."

### 4.2 Admin Dashboard Overview (`/admin`)
- **Layout**: Grid layout (Top Stat Cards → Middle Action Banners → Bottom Recent Orders Table).
- **Stat Cards Grid**:
  1. `Pending Payment`: Count badge (Yellow).
  2. `Paid (Queued)`: Count badge (Blue).
  3. `Printing`: Count badge (Purple).
  4. `Ready for Pickup`: Count badge (Orange).
  5. `Completed Today`: Count & Revenue total (Green).
- **Alert Banners**: Low Stock Warning cards if any inventory item `current_stock < min_threshold`.
- **Quick Action Bar**: `[ View Pending Orders ]` | `[ Record Cash Expense ]` | `[ Update Stock ]`.
- **Recent Orders Table**: Real-time updating list of latest 10 orders via SSE.

### 4.3 Admin Order Management Screen (`/admin/orders`)
- **Layout**: Full-width data table with multi-filter sidebar/toolbar.
- **Toolbar**:
  - Search Input: Filter by Display ID, Student Name, Mobile Number, or Pickup Code.
  - Status Filter Tabs: `[ All ]` | `[ Pending Payment (4) ]` | `[ Paid (8) ]` | `[ Printing (2) ]` | `[ Ready (5) ]` | `[ Completed ]`.
  - Date Picker Filter: Start & End date range.
- **Table Columns**:
  1. `Display ID` (Clickable link to detail).
  2. `Student Name & Mobile`.
  3. `Department`.
  4. `Files Count & Names`.
  5. `Configuration` (Side, Color, Copies, Binding).
  6. `Price` (₹).
  7. `Status` (Color-coded badge).
  8. `Submitted At`.
  9. `Actions`: `[ Advance Status ]` button / `[ View Detail ]`.

### 4.4 Admin Order Detail & File Operations Screen (`/admin/orders/:id`)
- **Layout**: Two-column layout (Left: Order Info & Actions | Right: File List & Previewer).
- **Left Panel**:
  - Student Details: Name, Mobile (`+91 98765 43210`), Department.
  - Order Metadata: Display ID, Pickup Code (`K8P2N9`), Submitted Timestamp.
  - Configuration Card: Print Side, Color Mode, Copies, Pages, Binding.
  - Financial Card: Price breakdown, Payment Method (`UPI` / `CASH`), Payment Verification Admin.
  - **Status Control Box**:
    - Current Status: `PAID` (Blue Badge).
    - Next Allowed Transition Button: `[ Start Printing → ]`.
    - Payment Verification Modal Trigger (if `PENDING_PAYMENT`): `[ Mark as Paid ]` (Radio choice: `UPI` / `CASH`).
- **Right Panel (File Management)**:
  - Uploaded File Cards:
    - Filename, File size (MB), Mime type, Magic-bytes verified status (`✓ Valid`).
    - Action Buttons: `[ Preview PDF Inline ]` (Opens PDF viewer in browser tab) | `[ Download File ]` (Generates 1-hour signed URL).

### 4.5 Admin Inventory Management Screen (`/admin/inventory`)
- **Layout**: Stock Catalog Cards / Table + Restock Modal.
- **Elements**:
  - Master Stock Table: Item Code, Item Name, Category, Sub-Category, Current Stock, Min Threshold, Unit Cost (₹), Status (`OK` / `LOW STOCK`).
  - Action Buttons: `[ + Restock Item ]` | `[ Record Wastage ]` | `[ Add New Stock Item ]`.

### 4.6 Admin Finance & Expenses Screen (`/admin/finance`)
- **Layout**: Financial Summary Cards + Expenses Table + Expense Form Modal.
- **Summary Cards**:
  - `Gross Revenue` (Total, UPI split, Cash split).
  - `Total Expenses` (Month to date).
  - `Net Profit` (Revenue - Expenses).
  - `Physical Cash in Hand` (Current cash balance).
- **Action**: `[ + Record New Expense ]` (Amount, Category, Description, Payment Method: Cash/UPI).

### 4.7 Admin Reports Screen (`/admin/reports`)
- **Layout**: Report Period Controls + High-Density Data Tables.
- **Period Tabs**: `[ Daily ]` | `[ Weekly ]` | `[ Monthly ]` | `[ Yearly ]` | `[ Custom Date Range ]`.
- **Report Tables**:
  - Table 1: Financial & Order Metrics Summary.
  - Table 2: Department-wise Volume & Revenue Breakdown.
  - Table 3: Inventory Material Consumption Units.

### 4.8 Admin Settings Screen (`/admin/settings`)
- **Layout**: Tabbed settings form (`[ Pricing Rates ]` | `[ General Settings ]` | `[ Admin Users ]`).
- **Pricing Rates Tab**: Form inputs for `bw_single_side`, `bw_double_side`, `color_single_side`, `spiral_binding_price`, `soft_binding_price`, `hard_binding_price`, `stapling_price`. Button: `[ Update Pricing Rates ]`.
- **General Settings Tab**: UPI ID input (`6381056942@upi`), Department list tags manager.
- **Admin Users Tab**: List of active admins (Max 3), `[ + Add Admin Account ]`, `[ Deactivate Admin ]`.

### 4.9 Admin Audit Logs Screen (`/admin/audit-logs`)
- **Layout**: High-density query table for security auditing.
- **Columns**: Timestamp, Actor (Admin/Student ID), Action (`order.status_changed`), Resource Type (`orders`), Resource ID, Old/New Value JSON drawer viewer, IP Address.

---

## 5. Table Design & Data Controls

- **Standard Table Features**:
  - Fixed table header with sticky scrolling.
  - Compact row height for high data density on admin screens.
  - Hover state on rows.
  - Multi-column sort indicators (`▲` / `▼`).
- **Pagination Component**:
  - Displays: `Showing 1–20 of 342 orders`.
  - Controls: `[ First ]` `[ Prev ]` Page Buttons `[ Next ]` `[ Last ]` + Rows per page selector `[ 20 ▼ ]`.
- **Filter Bar**:
  - Multi-select dropdowns, date pickers, and clear filters button (`[ ✕ Reset Filters ]`).

---

## 6. Form Design & Interactive Feedback

- **Input Field Anatomy**: Label + Required Star (`*`) + Input Field + Helper Text / Field Validation Error.
- **Validation Feedback**:
  - Immediate inline validation on field blur (e.g., Red border + "Invalid Indian mobile number").
  - Form submit disabled until all required fields pass validation.
- **Interactive States**:
  - Default / Idle state.
  - Hover & Focus states (High-contrast focus ring for keyboard navigation).
  - Loading state: Button text replaced with spinner (`[ ⏳ Processing... ]`), button disabled.
  - Success state: Toast message + green confirmation check.

---

## 7. Dialogs & Modal Specifications

All modals render over an accessible backdrop overlay (`aria-modal="true"`) with trap focus and ESC key close:

1. **Payment Verification Modal**:
   - Header: "Verify Order Payment — CC-2026-0042".
   - Body: Displays total price (`₹105.00`). Select Payment Method: `( ) UPI Payment` | `( ) Cash Payment`. Notes input field.
   - Actions: `[ Cancel ]` | `[ Confirm Payment & Mark Paid ]`.
2. **Stock Restock Modal**:
   - Fields: Item Select, Quantity to Add, Unit Cost (₹), Supplier Notes.
   - Actions: `[ Cancel ]` | `[ Save Restock ]`.
3. **Deactivate Admin Confirmation Modal**:
   - Danger Alert: "Deactivating this admin will revoke their access immediately. Proceed?"
   - Actions: `[ Cancel ]` | `[ Deactivate Admin ]` (Red button).
4. **Order Cancellation Modal**:
   - Fields: Cancellation Reason dropdown.
   - Actions: `[ Keep Order ]` | `[ Cancel Order ]` (Danger button).

---

## 8. Status Colors & Indicator Standards

System-wide color tokens for order lifecycle states:

| Order Status | Badge Background | Text Color | Icon / Meaning |
|--------------|------------------|------------|----------------|
| `PENDING_PAYMENT` | Amber / Yellow (`#FEF3C7`) | Amber Dark (`#92400E`) | ⏳ Awaiting Student Payment |
| `PAID` | Blue (`#DBEAFE`) | Blue Dark (`#1E40AF`) | ✓ Payment Verified by Admin |
| `PRINTING` | Purple (`#F3E8FF`) | Purple Dark (`#6B21A8`) | 🖨 Physical Printing Active |
| `READY_FOR_PICKUP` | Orange (`#FFEDD5`) | Orange Dark (`#9A3412`) | 📦 Held at Counter for Pickup |
| `COMPLETED` | Green (`#DCFCE7`) | Green Dark (`#166534`) | 🎉 Picked up & Closed |
| `CANCELLED` | Gray / Red (`#FEE2E2`) | Red Dark (`#991B1B`) | ✕ Order Cancelled |

---

## 9. Component System: Icons, Buttons, Badges & Cards

- **Button Variants**:
  - `Primary`: Solid Dark Blue (`#1E3A8A`) — Main actions (Submit, Save).
  - `Secondary`: Outline Gray (`#374151`) — Secondary choices (Cancel, Back).
  - `Success`: Solid Green (`#16A34A`) — Positive actions (Mark Paid, Complete).
  - `Danger`: Solid Red (`#DC2626`) — Destructive actions (Deactivate, Delete file).
- **Badges**: Rounded pill tags for status, role (`Admin` / `Student`), and stock health (`OK` / `LOW STOCK`).
- **Cards**: Flat white containers with 1px subtle gray border and soft box shadow (`shadow-sm`). Zero decorative gradients.

---

## 10. Responsive Layout & Viewport Behavior

| Breakpoint | Viewport Width | Target User | Layout Behavior |
|------------|----------------|-------------|-----------------|
| **Mobile** | `< 768px` | Student Portal | Single column, full-width buttons, sticky bottom nav, touch-friendly tap targets (minimum 44x44px). |
| **Tablet** | `768px – 1024px` | Admin / Student | 2-column grid, responsive tables with horizontal scroll. |
| **Desktop** | `> 1024px` | Admin Dashboard | Fixed 250px left sidebar, high-density multi-column data tables, side-by-side order detail panels. |

---

## 11. Accessibility (a11y) Standards

- **Keyboard Navigation**: Full application navigable via `Tab`, `Shift+Tab`, `Enter`, and `Space`. Modals trap focus and close on `ESC`.
- **Focus States**: High-contrast outline focus ring (`ring-2 ring-blue-600`) on all interactive elements.
- **ARIA Attributes**:
  - Form fields include `aria-invalid`, `aria-describedby` pointing to error messages.
  - Modals use `role="dialog"`, `aria-modal="true"`, `aria-labelledby`.
  - Status updates use `aria-live="polite"` for screen reader announcements.
- **Color Contrast**: All text elements satisfy WCAG 2.1 AA minimum contrast ratio of 4.5:1 against background.

---

## 12. Notification & SSE User Experience

- **Browser Notifications**:
  - Triggered when server emits `event: new_order` over SSE stream.
  - Notification Title: `New Order Received — CC-2026-0042`.
  - Notification Body: `From Arun Kumar — ₹105.00`. Clicking notification focuses Admin Dashboard tab.
- **In-App Toast Notifications**:
  - Non-modal slide-in alert at top-right corner.
  - Auto-dismisses after 5 seconds or on manual close click (`✕`).
- **SSE Connection Status Indicator**:
  - Visible in Admin Sidebar: `● Live` (Green dot when SSE connected) | `○ Reconnecting...` (Yellow dot when network drops).

---

## 13. Future UI Blueprint

- **Printer Queue Panel**: Real-time progress bar showing physical print job execution from Shop Printer Agent.
- **Interactive Analytics Charts**: Recharts/Chart.js integration for revenue and order volume trends.
- **QR Code Pickup Scanner**: Camera scanner modal allowing admin to scan student's QR code for instant order completion.

---

## 14. UI/UX Specification Self-Review

| Review Criteria | Verification Status | Resolution Details |
|---|---|---|
| **No duplicate pages?** | Verified | Unique URL paths assigned for every student and admin workflow screen. |
| **No missing workflows?** | Verified | Complete flow mapped: Login → Upload → Config → Pay → Print → Pickup → Complete → Reports. |
| **Consistent navigation?** | Verified | Unified Header/Bottom-nav for Students; Unified Sidebar/Topbar for Admins. |
| **Minimal click depth?** | Verified | Admin can verify payment or advance order status in exactly 2 clicks from Dashboard. |
| **Usability & Clarity?** | Verified | Color-coded status badges, high-contrast inputs, explicit loading/error states. |

---

*End of UI/UX Specification — Version 1.0.0-draft*

*This document is awaiting stakeholder review and approval before proceeding to project implementation.*

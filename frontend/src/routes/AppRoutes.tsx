import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthLayout } from '../layouts/AuthLayout';
import { AdminLayout } from '../layouts/AdminLayout';
import { ProtectedRoute } from './ProtectedRoute';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

// Lazy-loaded pages for code splitting
const AdminLoginPage = React.lazy(() =>
  import('../pages/admin/AdminLoginPage').then((m) => ({ default: m.AdminLoginPage }))
);
const DashboardPage = React.lazy(() =>
  import('../features/dashboard/DashboardPage').then((m) => ({ default: m.DashboardPage }))
);
const OrdersPage = React.lazy(() =>
  import('../features/orders/OrdersPage').then((m) => ({ default: m.OrdersPage }))
);
const OrderDetailPage = React.lazy(() =>
  import('../features/orders/OrderDetailPage').then((m) => ({ default: m.OrderDetailPage }))
);
const InventoryPage = React.lazy(() =>
  import('../features/inventory/InventoryPage').then((m) => ({ default: m.InventoryPage }))
);
const FinancePage = React.lazy(() =>
  import('../features/finance/FinancePage').then((m) => ({ default: m.FinancePage }))
);
const ReportsPage = React.lazy(() =>
  import('../features/reports/ReportsPage').then((m) => ({ default: m.ReportsPage }))
);
const SettingsPage = React.lazy(() =>
  import('../features/settings/SettingsPage').then((m) => ({ default: m.SettingsPage }))
);
const AuditLogsPage = React.lazy(() =>
  import('../features/audit-logs/AuditLogsPage').then((m) => ({ default: m.AuditLogsPage }))
);

const PageSuspense: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <Suspense
    fallback={
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner className="h-8 w-8 text-indigo-600" />
      </div>
    }
  >
    {children}
  </Suspense>
);

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route element={<AuthLayout />}>
        <Route
          path="/admin/login"
          element={
            <PageSuspense>
              <AdminLoginPage />
            </PageSuspense>
          }
        />
      </Route>

      {/* Admin Protected routes */}
      <Route element={<ProtectedRoute requireAdmin={true} />}>
        <Route element={<AdminLayout />}>
          <Route
            path="/admin"
            element={
              <PageSuspense>
                <DashboardPage />
              </PageSuspense>
            }
          />
          <Route
            path="/admin/orders"
            element={
              <PageSuspense>
                <OrdersPage />
              </PageSuspense>
            }
          />
          <Route
            path="/admin/orders/:id"
            element={
              <PageSuspense>
                <OrderDetailPage />
              </PageSuspense>
            }
          />
          <Route
            path="/admin/inventory"
            element={
              <PageSuspense>
                <InventoryPage />
              </PageSuspense>
            }
          />
          <Route
            path="/admin/finance"
            element={
              <PageSuspense>
                <FinancePage />
              </PageSuspense>
            }
          />
          <Route
            path="/admin/reports"
            element={
              <PageSuspense>
                <ReportsPage />
              </PageSuspense>
            }
          />
          <Route
            path="/admin/settings"
            element={
              <PageSuspense>
                <SettingsPage />
              </PageSuspense>
            }
          />
          <Route
            path="/admin/audit-logs"
            element={
              <PageSuspense>
                <AuditLogsPage />
              </PageSuspense>
            }
          />
        </Route>
      </Route>

      {/* Redirects */}
      <Route path="*" element={<Navigate to="/admin/login" replace />} />
    </Routes>
  );
};

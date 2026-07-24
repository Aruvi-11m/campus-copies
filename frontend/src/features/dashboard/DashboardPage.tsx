import React from 'react';
import { useDashboardStats } from './hooks';
import { DashboardCards, DashboardCardsSkeleton } from './components/DashboardCards';
import { RevenueChart } from './components/RevenueChart';
import { RecentOrders } from './components/RecentOrders';
import { LowStockWidget } from './components/LowStockWidget';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { data: stats, isLoading, isError, refetch, isFetching } = useDashboardStats();

  if (isError) {
    return (
      <div className="rounded-md bg-red-50 p-4 mt-6">
        <div className="flex">
          <div className="flex-shrink-0">
            <AlertTriangle className="h-5 w-5 text-red-400" aria-hidden="true" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error loading dashboard</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>Failed to communicate with the server. Please try again.</p>
            </div>
            <div className="mt-4">
              <div className="-mx-2 -my-1.5 flex">
                <button
                  onClick={() => refetch()}
                  className="rounded-md bg-red-50 px-2 py-1.5 text-sm font-medium text-red-800 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2 focus:ring-offset-red-50"
                >
                  Retry Now
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">
            Overview of today&apos;s business metrics and alerts.
          </p>
        </div>
        <div>
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="inline-flex items-center gap-2 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 disabled:opacity-50"
          >
            <RefreshCw
              className={`h-4 w-4 ${isFetching ? 'animate-spin text-gray-400' : 'text-gray-500'}`}
            />
            Refresh
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      {isLoading || !stats ? <DashboardCardsSkeleton /> : <DashboardCards stats={stats} />}

      {/* Main Grid: Charts and Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (Chart & Orders) */}
        <div className="lg:col-span-2 space-y-6">
          <RevenueChart />
          <RecentOrders />
        </div>

        {/* Right Column (Widgets) */}
        <div className="space-y-6">
          <LowStockWidget alerts={stats?.low_stock_alerts || []} />
        </div>
      </div>
    </div>
  );
};

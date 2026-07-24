import React, { useState } from 'react';
import { useOrders, useOrder } from './hooks';
import { OrderQueryOptions, Order } from './types';
import { OrdersTable } from './components/OrdersTable';
import { OrdersFilterBar } from './components/OrdersFilterBar';
import { OrderDetailDrawer } from './components/OrderDetailDrawer';
import { BulkActions } from './components/BulkActions';
import { ErrorBoundary } from 'react-error-boundary';

export const OrdersPage: React.FC = () => {
  // Query State
  const [queryOptions, setQueryOptions] = useState<OrderQueryOptions>({
    page: 1,
    limit: 50,
    status: '',
    search: '',
    start_date: '',
    end_date: '',
  });

  // Fetch paginated list
  const { data, isLoading } = useOrders(queryOptions);

  // Selection state
  const [selectedRowIds, setSelectedRowIds] = useState<Set<string>>(new Set());

  // Drawer state
  const [drawerOrderId, setDrawerOrderId] = useState<string | null>(null);
  const { data: drawerOrder } = useOrder(drawerOrderId);

  // Handlers
  const handleToggleRow = (id: string) => {
    const newSet = new Set(selectedRowIds);
    if (newSet.has(id)) newSet.delete(id);
    else newSet.add(id);
    setSelectedRowIds(newSet);
  };

  const handleToggleAll = (ids: string[]) => {
    if (selectedRowIds.size === ids.length && ids.length > 0) {
      setSelectedRowIds(new Set());
    } else {
      setSelectedRowIds(new Set(ids));
    }
  };

  const ErrorFallback = ({ error, resetErrorBoundary }: any) => (
    <div className="bg-red-50 p-6 rounded-lg border border-red-200">
      <h2 className="text-red-800 font-semibold mb-2">Failed to render orders module</h2>
      <pre className="text-xs text-red-600 mb-4 overflow-auto">{error.message}</pre>
      <button
        onClick={resetErrorBoundary}
        className="bg-red-100 text-red-800 px-4 py-2 rounded-md font-medium hover:bg-red-200"
      >
        Try again
      </button>
    </div>
  );

  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onReset={() => setQueryOptions({ ...queryOptions, page: 1 })}
    >
      <div className="space-y-4 relative pb-20">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Orders Management</h1>
            <p className="mt-1 text-sm text-gray-500">
              View, search, and manage all print orders in real-time.
            </p>
          </div>
        </div>

        <OrdersFilterBar
          search={queryOptions.search || ''}
          onSearchChange={(val) => setQueryOptions({ ...queryOptions, search: val, page: 1 })}
          status={queryOptions.status || ''}
          onStatusChange={(val) => setQueryOptions({ ...queryOptions, status: val, page: 1 })}
          startDate={queryOptions.start_date || ''}
          onStartDateChange={(val) =>
            setQueryOptions({ ...queryOptions, start_date: val, page: 1 })
          }
          endDate={queryOptions.end_date || ''}
          onEndDateChange={(val) => setQueryOptions({ ...queryOptions, end_date: val, page: 1 })}
        />

        <OrdersTable
          orders={data?.data || []}
          isLoading={isLoading}
          onRowClick={(order) => setDrawerOrderId(order.id)}
          selectedRowIds={selectedRowIds}
          onToggleRow={handleToggleRow}
          onToggleAll={handleToggleAll}
        />

        {/* Server-side Pagination Controls */}
        {data && data.total_pages > 1 && (
          <div className="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6 shadow-sm sm:rounded-lg">
            <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700">
                  Showing <span className="font-medium">{(data.page - 1) * data.limit + 1}</span> to{' '}
                  <span className="font-medium">
                    {Math.min(data.page * data.limit, data.total)}
                  </span>{' '}
                  of <span className="font-medium">{data.total}</span> results
                </p>
              </div>
              <div>
                <nav
                  className="isolate inline-flex -space-x-px rounded-md shadow-sm"
                  aria-label="Pagination"
                >
                  <button
                    onClick={() =>
                      setQueryOptions({ ...queryOptions, page: Math.max(1, queryOptions.page - 1) })
                    }
                    disabled={queryOptions.page === 1}
                    className="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() =>
                      setQueryOptions({
                        ...queryOptions,
                        page: Math.min(data.total_pages, queryOptions.page + 1),
                      })
                    }
                    disabled={queryOptions.page === data.total_pages}
                    className="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50"
                  >
                    Next
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}

        <OrderDetailDrawer
          isOpen={!!drawerOrderId}
          onClose={() => setDrawerOrderId(null)}
          order={drawerOrder || null}
        />

        <BulkActions
          selectedIds={Array.from(selectedRowIds)}
          onClearSelection={() => setSelectedRowIds(new Set())}
        />
      </div>
    </ErrorBoundary>
  );
};

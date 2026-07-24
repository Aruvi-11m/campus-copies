import React, { useState } from 'react';
import { PageHeader } from '../../components/common/PageHeader';
import { useAuditLogs } from './hooks';
import { AuditLogFilters } from './types';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorFallback } from '../../components/common/ErrorFallback';
import { Badge } from '../../components/common/Badge';
import { formatDate } from '../../utils/formatters';

export const AuditLogsPage = () => {
  const [filters, setFilters] = useState<AuditLogFilters>({
    page: 1,
    size: 20,
  });

  const { data, isLoading, isError, error, refetch } = useAuditLogs(filters);

  const handleNextPage = () => setFilters((prev) => ({ ...prev, page: prev.page + 1 }));
  const handlePrevPage = () =>
    setFilters((prev) => ({ ...prev, page: Math.max(1, prev.page - 1) }));

  return (
    <div className="space-y-6">
      <PageHeader
        title="Audit Logs"
        description="Track system events, user actions, and administrative changes."
      />

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Event History</h3>

            <div className="flex gap-2">
              {/* Minimal filters for now */}
              <input
                type="text"
                placeholder="Filter by Resource Type..."
                className="block w-full sm:w-64 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                value={filters.resource_type || ''}
                onChange={(e) =>
                  setFilters((prev) => ({
                    ...prev,
                    resource_type: e.target.value || undefined,
                    page: 1,
                  }))
                }
              />
              <input
                type="text"
                placeholder="Filter by Action..."
                className="block w-full sm:w-64 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                value={filters.action || ''}
                onChange={(e) =>
                  setFilters((prev) => ({ ...prev, action: e.target.value || undefined, page: 1 }))
                }
              />
            </div>
          </div>

          {isLoading ? (
            <div className="flex justify-center py-12">
              <LoadingSpinner className="h-8 w-8 text-indigo-600" />
            </div>
          ) : isError ? (
            <ErrorFallback
              error={error instanceof Error ? error : new Error('Failed to load audit logs')}
              resetErrorBoundary={() => refetch()}
            />
          ) : (
            <div className="mt-4 flow-root">
              <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
                <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
                  <table className="min-w-full divide-y divide-gray-300">
                    <thead>
                      <tr>
                        <th
                          scope="col"
                          className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-0"
                        >
                          Timestamp
                        </th>
                        <th
                          scope="col"
                          className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
                        >
                          Actor
                        </th>
                        <th
                          scope="col"
                          className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
                        >
                          Action
                        </th>
                        <th
                          scope="col"
                          className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
                        >
                          Resource
                        </th>
                        <th
                          scope="col"
                          className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900"
                        >
                          IP Address
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 bg-white">
                      {data?.items.map((log: import('./types').AuditLog) => (
                        <tr key={log.id}>
                          <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm text-gray-500 sm:pl-0">
                            {formatDate(log.timestamp)}
                          </td>
                          <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-900">
                            <Badge variant={log.actor_type === 'SYSTEM' ? 'warning' : 'info'}>
                              {log.actor_type}
                            </Badge>
                          </td>
                          <td className="whitespace-nowrap px-3 py-4 text-sm font-medium text-gray-900">
                            {log.action}
                          </td>
                          <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                            {log.resource_type}{' '}
                            {log.resource_id ? (
                              <span className="text-xs text-gray-400">
                                ({log.resource_id.substring(0, 8)}...)
                              </span>
                            ) : null}
                          </td>
                          <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                            {log.ip_address || '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Pagination */}
              <div className="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6 mt-4">
                <div className="flex flex-1 justify-between sm:hidden">
                  <button
                    onClick={handlePrevPage}
                    disabled={filters.page === 1}
                    className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    onClick={handleNextPage}
                    disabled={filters.page >= (data?.pages || 1)}
                    className="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
                <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-gray-700">
                      Showing page <span className="font-medium">{data?.page}</span> of{' '}
                      <span className="font-medium">{data?.pages}</span> ({data?.total} total
                      results)
                    </p>
                  </div>
                  <div>
                    <nav
                      className="isolate inline-flex -space-x-px rounded-md shadow-sm"
                      aria-label="Pagination"
                    >
                      <button
                        onClick={handlePrevPage}
                        disabled={filters.page === 1}
                        className="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50"
                      >
                        <span className="sr-only">Previous</span>
                        &larr;
                      </button>
                      <button
                        onClick={handleNextPage}
                        disabled={filters.page >= (data?.pages || 1)}
                        className="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50"
                      >
                        <span className="sr-only">Next</span>
                        &rarr;
                      </button>
                    </nav>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuditLogsPage;

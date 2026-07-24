import React, { useRef } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  getSortedRowModel,
  SortingState,
  ColumnDef,
} from '@tanstack/react-table';
import { TableVirtuoso } from 'react-virtuoso';
import { Order } from '../types';
import { Badge } from '../../../components/common/Badge';
import { formatCurrency } from '../../../utils/formatters';
import { ArrowUpDown } from 'lucide-react';
import { format } from 'date-fns';

interface OrdersTableProps {
  orders: Order[];
  isLoading: boolean;
  onRowClick: (order: Order) => void;
  selectedRowIds: Set<string>;
  onToggleRow: (id: string) => void;
  onToggleAll: (ids: string[]) => void;
}

export const OrdersTable: React.FC<OrdersTableProps> = ({
  orders,
  isLoading,
  onRowClick,
  selectedRowIds,
  onToggleRow,
  onToggleAll,
}) => {
  const [sorting, setSorting] = React.useState<SortingState>([]);
  const tableContainerRef = useRef<HTMLDivElement>(null);

  const columns = React.useMemo<ColumnDef<Order>[]>(
    () => [
      {
        id: 'select',
        header: () => (
          <input
            type="checkbox"
            className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            checked={orders.length > 0 && selectedRowIds.size === orders.length}
            onChange={() => onToggleAll(orders.map((o) => o.id))}
          />
        ),
        cell: ({ row }) => (
          <input
            type="checkbox"
            className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            checked={selectedRowIds.has(row.original.id)}
            onChange={() => onToggleRow(row.original.id)}
            onClick={(e) => e.stopPropagation()}
          />
        ),
        size: 50,
      },
      {
        accessorKey: 'display_id',
        header: ({ column }) => (
          <button
            type="button"
            className="flex items-center cursor-pointer select-none font-semibold text-gray-900"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Order ID <ArrowUpDown className="ml-2 h-4 w-4" />
          </button>
        ),
        cell: (info) => (
          <span className="font-medium text-gray-900">{info.getValue() as string}</span>
        ),
      },
      {
        accessorKey: 'student_email',
        header: 'Student',
        cell: (info) => <span className="text-gray-500">{info.getValue() as string}</span>,
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: (info) => {
          const val = info.getValue() as string;
          let variant: 'info' | 'warning' | 'success' | 'default' = 'default';
          if (val === 'PAID') variant = 'info';
          if (val === 'PRINTING') variant = 'warning';
          if (val === 'READY_FOR_PICKUP') variant = 'success';
          if (val === 'COMPLETED') variant = 'default';
          return <Badge variant={variant}>{val.replace(/_/g, ' ')}</Badge>;
        },
      },
      {
        accessorKey: 'created_at',
        header: 'Date',
        cell: (info) => (
          <span className="text-gray-500">
            {format(new Date(info.getValue() as string), 'MMM d, yyyy HH:mm')}
          </span>
        ),
      },
      {
        accessorKey: 'total_price',
        header: () => <div className="text-right">Total</div>,
        cell: (info) => (
          <div className="text-right font-medium">{formatCurrency(info.getValue() as number)}</div>
        ),
      },
    ],
    [orders, selectedRowIds, onToggleAll, onToggleRow]
  );

  const table = useReactTable({
    data: orders,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  if (isLoading && orders.length === 0) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <div className="text-center py-12 bg-white border border-gray-200 rounded-lg shadow-sm">
        <h3 className="mt-2 text-sm font-semibold text-gray-900">No orders found</h3>
        <p className="mt-1 text-sm text-gray-500">Try adjusting your filters or search query.</p>
      </div>
    );
  }

  const { rows } = table.getRowModel();

  return (
    <div
      className="bg-white border border-gray-200 rounded-lg shadow-sm h-[600px]"
      ref={tableContainerRef}
    >
      <TableVirtuoso
        style={{ height: '100%', width: '100%' }}
        totalCount={rows.length}
        components={{
          Table: ({ style, ...props }) => (
            <table
              {...props}
              className="min-w-full divide-y divide-gray-200"
              style={{ ...style, width: '100%' }}
            />
          ),
          TableHead: React.forwardRef(({ style, ...props }, ref) => (
            <thead {...props} ref={ref} className="bg-gray-50 sticky top-0 z-10" />
          )),
          TableRow: (props) => {
            const index = props['data-index'];
            const row = rows[index];
            if (!row) return <tr {...props} />;
            return (
              <tr
                {...props}
                className="hover:bg-gray-50 cursor-pointer border-b border-gray-200"
                onClick={() => onRowClick(row.original)}
              />
            );
          },
        }}
        fixedHeaderContent={() => (
          <>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50 shadow-sm"
                    style={{ width: header.getSize() }}
                  >
                    {flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </>
        )}
        itemContent={(index) => {
          const row = rows[index];
          if (!row) return null;
          return (
            <>
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="px-6 py-4 whitespace-nowrap text-sm bg-white">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </>
          );
        }}
      />
    </div>
  );
};

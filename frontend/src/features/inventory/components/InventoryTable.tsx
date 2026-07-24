import React, { useMemo } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  getSortedRowModel,
  SortingState,
  ColumnDef,
} from '@tanstack/react-table';
import { InventoryItem } from '../types';
import { formatCurrency } from '../../../utils/formatters';
import { ArrowUpDown, AlertCircle, CheckCircle2, XCircle, Package } from 'lucide-react';

interface InventoryTableProps {
  data: InventoryItem[];
  isLoading: boolean;
  onRowClick: (item: InventoryItem) => void;
}

export const InventoryTable: React.FC<InventoryTableProps> = ({ data, isLoading, onRowClick }) => {
  const [sorting, setSorting] = React.useState<SortingState>([]);

  const columns = useMemo<ColumnDef<InventoryItem>[]>(
    () => [
      {
        accessorKey: 'item_code',
        header: 'SKU',
        cell: (info) => (
          <span className="font-medium text-gray-900">{info.getValue() as string}</span>
        ),
      },
      {
        accessorKey: 'description',
        header: ({ column }) => (
          <button
            type="button"
            className="flex items-center cursor-pointer select-none font-semibold text-gray-900"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Item <ArrowUpDown className="ml-2 h-4 w-4" />
          </button>
        ),
        cell: (info) => <span className="text-gray-900">{info.getValue() as string}</span>,
      },
      {
        accessorKey: 'category',
        header: 'Category',
        cell: (info) => <span className="text-gray-500">{info.getValue() as string}</span>,
      },
      {
        accessorKey: 'current_stock',
        header: ({ column }) => (
          <button
            type="button"
            className="flex items-center cursor-pointer select-none text-right justify-end font-semibold text-gray-900"
            onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          >
            Stock <ArrowUpDown className="ml-2 h-4 w-4" />
          </button>
        ),
        cell: ({ row }) => {
          const item = row.original;
          let colorClass = 'text-green-600';
          let bgClass = 'bg-green-50';
          if (item.status === 'LOW_STOCK') {
            colorClass = 'text-amber-600';
            bgClass = 'bg-amber-50';
          } else if (item.status === 'OUT_OF_STOCK') {
            colorClass = 'text-red-600';
            bgClass = 'bg-red-50';
          }

          return (
            <div className="flex justify-end">
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${bgClass} ${colorClass}`}
              >
                {item.current_stock} {item.unit}
              </span>
            </div>
          );
        },
      },
      {
        accessorKey: 'min_threshold',
        header: () => <div className="text-right">Min Threshold</div>,
        cell: (info) => <div className="text-right text-gray-500">{info.getValue() as number}</div>,
      },
      {
        accessorKey: 'unit_cost',
        header: () => <div className="text-right">Unit Cost</div>,
        cell: (info) => (
          <div className="text-right text-gray-500">
            {formatCurrency(info.getValue() as number)}
          </div>
        ),
      },
      {
        accessorKey: 'status',
        header: () => <div className="text-center">Status</div>,
        cell: ({ row }) => {
          const status = row.original.status;
          if (status === 'IN_STOCK')
            return (
              <div className="flex justify-center">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
              </div>
            );
          if (status === 'LOW_STOCK')
            return (
              <div className="flex justify-center">
                <AlertCircle className="h-5 w-5 text-amber-500" />
              </div>
            );
          return (
            <div className="flex justify-center">
              <XCircle className="h-5 w-5 text-red-500" />
            </div>
          );
        },
      },
    ],
    []
  );

  const table = useReactTable({
    data,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  if (isLoading) {
    return (
      <div className="flex justify-center py-12 bg-white border border-gray-200 rounded-lg">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="text-center py-12 bg-white border border-gray-200 rounded-lg shadow-sm">
        <Package className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-semibold text-gray-900">No inventory items</h3>
        <p className="mt-1 text-sm text-gray-500">Get started by creating a new inventory item.</p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                  >
                    {flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {table.getRowModel().rows.map((row) => (
              <tr
                key={row.id}
                onClick={() => onRowClick(row.original)}
                className="hover:bg-gray-50 cursor-pointer transition-colors"
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-6 py-4 whitespace-nowrap text-sm">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

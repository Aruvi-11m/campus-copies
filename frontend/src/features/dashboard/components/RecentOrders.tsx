import React from 'react';
import { Card } from '../../../components/common/Card';
import { Badge } from '../../../components/common/Badge';
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  createColumnHelper,
} from '@tanstack/react-table';

interface RecentOrder {
  order_number: string;
  student_email: string;
  status: string;
  total: number;
}

const mockOrders: RecentOrder[] = [
  {
    order_number: 'CC-2026-0001',
    student_email: 'student@example.com',
    status: 'PAID',
    total: 15.5,
  },
  {
    order_number: 'CC-2026-0002',
    student_email: 'test@college.edu',
    status: 'PRINTING',
    total: 2.25,
  },
  {
    order_number: 'CC-2026-0003',
    student_email: 'hello@world.edu',
    status: 'READY_FOR_PICKUP',
    total: 8.0,
  },
  {
    order_number: 'CC-2026-0004',
    student_email: 'another@student.com',
    status: 'COMPLETED',
    total: 4.5,
  },
];

const columnHelper = createColumnHelper<RecentOrder>();

const columns = [
  columnHelper.accessor('order_number', {
    header: 'Order',
    cell: (info) => <span className="font-medium text-gray-900">{info.getValue()}</span>,
  }),
  columnHelper.accessor('student_email', {
    header: 'Student',
    cell: (info) => <span className="text-gray-500">{info.getValue()}</span>,
  }),
  columnHelper.accessor('status', {
    header: 'Status',
    cell: (info) => {
      const val = info.getValue();
      let variant: 'info' | 'warning' | 'success' | 'default' = 'default';
      if (val === 'PAID') variant = 'info';
      if (val === 'PRINTING') variant = 'warning';
      if (val === 'READY_FOR_PICKUP') variant = 'success';
      if (val === 'COMPLETED') variant = 'default';
      return <Badge variant={variant}>{val.replace(/_/g, ' ')}</Badge>;
    },
  }),
  columnHelper.accessor('total', {
    header: () => <div className="text-right">Total</div>,
    cell: (info) => <div className="text-right font-medium">${info.getValue().toFixed(2)}</div>,
  }),
];

export const RecentOrders: React.FC = () => {
  const table = useReactTable({
    data: mockOrders,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <Card className="flex flex-col h-full">
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-medium leading-6 text-gray-900">Recent Orders</h3>
      </div>
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
              <tr key={row.id} className="hover:bg-gray-50">
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
    </Card>
  );
};

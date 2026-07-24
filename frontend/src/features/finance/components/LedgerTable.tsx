import React, { useMemo } from 'react';
import { DataTable } from '../../../components/common/DataTable';
import { Badge } from '../../../components/common/Badge';
import { LedgerEntry } from '../types';
import { formatCurrency, formatDate } from '../../../utils/formatters';
import { ColumnDef } from '@tanstack/react-table';
import { Receipt } from 'lucide-react';

interface LedgerTableProps {
  entries?: LedgerEntry[];
  isLoading: boolean;
}

export const LedgerTable: React.FC<LedgerTableProps> = ({ entries, isLoading }) => {
  const columns = useMemo<ColumnDef<LedgerEntry>[]>(
    () => [
      {
        accessorKey: 'display_id',
        header: 'Order / Ref',
        cell: (info) => (
          <span className="font-medium text-gray-900">{info.getValue() as string}</span>
        ),
      },
      {
        accessorKey: 'entry_type',
        header: 'Type',
        cell: (info) => {
          const type = info.getValue() as string;
          return <Badge variant={type === 'CREDIT' ? 'success' : 'error'}>{type}</Badge>;
        },
      },
      {
        accessorKey: 'payment_method',
        header: 'Method',
        cell: (info) => info.getValue(),
      },
      {
        accessorKey: 'amount',
        header: 'Amount',
        cell: (info) => {
          const amount = info.getValue() as number;
          const type = info.row.original.entry_type;
          return (
            <span
              className={`font-medium ${type === 'CREDIT' ? 'text-green-600' : 'text-red-600'}`}
            >
              {type === 'CREDIT' ? '+' : '-'}
              {formatCurrency(amount)}
            </span>
          );
        },
      },
      {
        accessorKey: 'created_at',
        header: 'Date',
        cell: (info) => formatDate(info.getValue() as string),
      },
      {
        accessorKey: 'notes',
        header: 'Notes',
        cell: (info) => (
          <span className="text-gray-500 truncate max-w-[200px] inline-block">
            {(info.getValue() as string) || '-'}
          </span>
        ),
      },
    ],
    []
  );

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Payment Ledger</h3>
      <DataTable
        columns={columns}
        data={entries || []}
        isLoading={isLoading}
        emptyIcon={Receipt}
        emptyTitle="No transactions found"
        emptyDescription="No payments have been recorded yet."
      />
    </div>
  );
};

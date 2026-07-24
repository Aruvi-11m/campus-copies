import React, { useMemo } from 'react';
import { DataTable } from '../../../components/common/DataTable';
import { Expense } from '../types';
import { formatCurrency, formatDate } from '../../../utils/formatters';
import { ColumnDef } from '@tanstack/react-table';
import { FileText, Plus } from 'lucide-react';
import { Button } from '../../../components/common/Button';

interface ExpensesTableProps {
  expenses?: Expense[];
  isLoading: boolean;
  onAddExpense: () => void;
}

export const ExpensesTable: React.FC<ExpensesTableProps> = ({
  expenses,
  isLoading,
  onAddExpense,
}) => {
  const columns = useMemo<ColumnDef<Expense>[]>(
    () => [
      {
        accessorKey: 'category',
        header: 'Category',
        cell: (info) => (
          <span className="font-medium text-gray-900">{info.getValue() as string}</span>
        ),
      },
      {
        accessorKey: 'description',
        header: 'Description',
      },
      {
        accessorKey: 'amount',
        header: 'Amount',
        cell: (info) => (
          <span className="font-medium text-red-600">
            -{formatCurrency(info.getValue() as number)}
          </span>
        ),
      },
      {
        accessorKey: 'recorded_by',
        header: 'Recorded By',
      },
      {
        accessorKey: 'created_at',
        header: 'Date',
        cell: (info) => formatDate(info.getValue() as string),
      },
    ],
    []
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Expenses</h3>
        <Button onClick={onAddExpense} size="sm" className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Record Expense
        </Button>
      </div>

      <DataTable
        columns={columns}
        data={expenses || []}
        isLoading={isLoading}
        emptyIcon={FileText}
        emptyTitle="No expenses found"
        emptyDescription="There are no expenses recorded for this period."
      />
    </div>
  );
};

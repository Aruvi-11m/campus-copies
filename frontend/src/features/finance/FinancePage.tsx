import React, { useState } from 'react';
import { PageHeader } from '../../components/common/PageHeader';
import { FinanceCards } from './components/FinanceCards';
import { RevenueChart } from './components/RevenueChart';
import { LedgerTable } from './components/LedgerTable';
import { ExpensesTable } from './components/ExpensesTable';
import { ExpenseDialog } from './components/ExpenseDialog';
import { useFinanceSummary, useLedger, useExpenses, useCreateExpense } from './hooks';
import { FinancePeriod } from './types';
import { Calendar } from 'lucide-react';
import { ErrorBoundary } from 'react-error-boundary';
import { ErrorFallback } from '../../components/common/ErrorFallback';

export const FinancePage: React.FC = () => {
  const [period, setPeriod] = useState<FinancePeriod>('monthly');
  const [isExpenseDialogOpen, setIsExpenseDialogOpen] = useState(false);

  // Queries
  const { data: summary, isLoading: isLoadingSummary } = useFinanceSummary({ period });
  const { data: ledger, isLoading: isLoadingLedger } = useLedger();
  const { data: expenses, isLoading: isLoadingExpenses } = useExpenses();

  // Mutations
  const createExpense = useCreateExpense();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Finance & Ledger"
        description="Monitor revenue, expenses, and transaction history."
        actions={
          <div className="flex items-center gap-2 bg-white border border-gray-300 rounded-md shadow-sm px-3 py-2">
            <Calendar className="h-4 w-4 text-gray-500" />
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value as FinancePeriod)}
              className="block w-full border-0 p-0 text-gray-900 sm:text-sm focus:ring-0"
            >
              <option value="daily">Today</option>
              <option value="weekly">This Week</option>
              <option value="monthly">This Month</option>
              <option value="yearly">This Year</option>
            </select>
          </div>
        }
      />

      <ErrorBoundary FallbackComponent={ErrorFallback}>
        <FinanceCards summary={summary} isLoading={isLoadingSummary} />
      </ErrorBoundary>

      <ErrorBoundary FallbackComponent={ErrorFallback}>
        <RevenueChart summary={summary} />
      </ErrorBoundary>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ErrorBoundary FallbackComponent={ErrorFallback}>
          <LedgerTable entries={ledger} isLoading={isLoadingLedger} />
        </ErrorBoundary>

        <ErrorBoundary FallbackComponent={ErrorFallback}>
          <ExpensesTable
            expenses={expenses}
            isLoading={isLoadingExpenses}
            onAddExpense={() => setIsExpenseDialogOpen(true)}
          />
        </ErrorBoundary>
      </div>

      <ExpenseDialog
        isOpen={isExpenseDialogOpen}
        onClose={() => setIsExpenseDialogOpen(false)}
        isSubmitting={createExpense.isPending}
        onSubmit={async (data) => {
          await createExpense.mutateAsync(data);
          setIsExpenseDialogOpen(false);
        }}
      />
    </div>
  );
};

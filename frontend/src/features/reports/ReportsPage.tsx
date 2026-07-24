import React, { useState } from 'react';
import { PageHeader } from '../../components/common/PageHeader';
import { ErrorBoundary } from 'react-error-boundary';
import { ErrorFallback } from '../../components/common/ErrorFallback';
import { ReportSummaryCards } from './components/ReportSummaryCards';
import { ExportControls } from './components/ExportControls';
import { useReportSummary } from './hooks';
import { ReportPeriod } from './types';
import { BarChart3 } from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const [period, setPeriod] = useState<ReportPeriod>('monthly');
  // In a full implementation, we'd add DatePickers to set these custom dates
  const [customDates] = useState<{ start_date: string; end_date: string } | undefined>(undefined);

  const { data: summary, isLoading, refetch } = useReportSummary(period, customDates);

  return (
    <div className="space-y-6">
      <div className="print:hidden">
        <PageHeader
          title="Reports & Analytics"
          description="Aggregate business performance and data exports."
        />
      </div>

      {/* Print-only Header */}
      <div className="hidden print:block mb-8 border-b pb-4">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <BarChart3 className="w-6 h-6" /> Campus Copies ERP
        </h1>
        <p className="text-gray-500">Business Report - {new Date().toLocaleDateString()}</p>
      </div>

      <div className="bg-white p-4 rounded-xl border shadow-sm flex items-center gap-4 print:hidden">
        <span className="text-sm font-medium text-gray-700">Reporting Period:</span>
        <select
          className="border-gray-300 rounded-md text-sm py-1.5 pl-3 pr-8 focus:ring-primary-500 focus:border-primary-500"
          value={period}
          onChange={(e) => setPeriod(e.target.value as ReportPeriod)}
        >
          <option value="daily">Today (Daily)</option>
          <option value="weekly">This Week</option>
          <option value="monthly">This Month</option>
          <option value="yearly">This Year</option>
        </select>
      </div>

      <ErrorBoundary FallbackComponent={ErrorFallback} onReset={() => refetch()}>
        {/* We pass empty metrics if loading or error to keep UI layout stable */}
        <ReportSummaryCards
          metrics={
            summary?.metrics || {
              total_orders: 0,
              completed_orders: 0,
              gross_revenue: 0,
              upi_revenue: 0,
              cash_revenue: 0,
              total_expenses: 0,
              net_profit: 0,
              cash_in_hand: 0,
              avg_order_value: 0,
            }
          }
          isLoading={isLoading}
        />
      </ErrorBoundary>

      <ExportControls startDate={customDates?.start_date} endDate={customDates?.end_date} />
    </div>
  );
};

export default ReportsPage;

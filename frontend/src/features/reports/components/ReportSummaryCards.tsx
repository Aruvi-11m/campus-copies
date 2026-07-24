import React from 'react';
import { StatCard } from '../../../components/common/StatCard';
import { formatCurrency } from '../../../utils/formatters';
import { ReportMetrics } from '../types';
import {
  IndianRupee,
  ShoppingCart,
  TrendingUp,
  Wallet,
  ArrowUpRight,
  ArrowDownRight,
  PackageCheck,
} from 'lucide-react';

interface ReportSummaryCardsProps {
  metrics: ReportMetrics;
  isLoading: boolean;
}

export const ReportSummaryCards: React.FC<ReportSummaryCardsProps> = ({ metrics, isLoading }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 print:grid-cols-4">
      <StatCard
        label="Gross Revenue"
        value={formatCurrency(metrics?.gross_revenue || 0)}
        icon={IndianRupee}
        trend={metrics?.gross_revenue > 0 ? { value: '100%', positive: true } : undefined}
      />
      <StatCard
        label="Net Profit"
        value={formatCurrency(metrics?.net_profit || 0)}
        icon={TrendingUp}
        trend={metrics?.net_profit > 0 ? { value: '100%', positive: true } : undefined}
      />
      <StatCard
        label="Total Orders"
        value={String(metrics?.total_orders || 0)}
        icon={ShoppingCart}
      />
      <StatCard
        label="Completed Orders"
        value={String(metrics?.completed_orders || 0)}
        icon={PackageCheck}
      />
      <StatCard
        label="UPI Revenue"
        value={formatCurrency(metrics?.upi_revenue || 0)}
        icon={Wallet}
      />
      <StatCard
        label="Cash Revenue"
        value={formatCurrency(metrics?.cash_revenue || 0)}
        icon={IndianRupee}
      />
      <StatCard
        label="Total Expenses"
        value={formatCurrency(metrics?.total_expenses || 0)}
        icon={ArrowDownRight}
      />
      <StatCard
        label="Avg Order Value"
        value={formatCurrency(metrics?.avg_order_value || 0)}
        icon={ArrowUpRight}
      />
    </div>
  );
};

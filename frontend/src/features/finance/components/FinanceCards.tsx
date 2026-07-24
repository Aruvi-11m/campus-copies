import React from 'react';
import { StatCard } from '../../../components/common/StatCard';
import { SkeletonCards } from '../../../components/common/Skeleton';
import { FinanceSummary } from '../types';
import { formatCurrency } from '../../../utils/formatters';
import { IndianRupee, TrendingDown, TrendingUp, ShoppingCart } from 'lucide-react';

interface FinanceCardsProps {
  summary?: FinanceSummary;
  isLoading: boolean;
}

export const FinanceCards: React.FC<FinanceCardsProps> = ({ summary, isLoading }) => {
  if (isLoading || !summary) {
    return <SkeletonCards count={4} />;
  }

  const { metrics } = summary;

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard
        label="Gross Revenue"
        value={formatCurrency(metrics.gross_revenue)}
        icon={IndianRupee}
        iconColor="text-blue-600"
        iconBg="bg-blue-100"
      />
      <StatCard
        label="Total Expenses"
        value={formatCurrency(metrics.total_expenses)}
        icon={TrendingDown}
        iconColor="text-red-600"
        iconBg="bg-red-100"
      />
      <StatCard
        label="Net Profit"
        value={formatCurrency(metrics.net_profit)}
        icon={TrendingUp}
        iconColor="text-emerald-600"
        iconBg="bg-emerald-100"
        trend={{
          value: `${((metrics.net_profit / (metrics.gross_revenue || 1)) * 100).toFixed(1)}% margin`,
          positive: metrics.net_profit > 0,
        }}
      />
      <StatCard
        label="Completed Orders"
        value={metrics.completed_orders.toString()}
        icon={ShoppingCart}
        iconColor="text-indigo-600"
        iconBg="bg-indigo-100"
      />
    </div>
  );
};

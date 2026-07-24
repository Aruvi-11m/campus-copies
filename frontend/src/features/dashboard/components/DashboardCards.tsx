import React from 'react';
import { Card } from '../../../components/common/Card';
import { DashboardStats } from '../types';
import { DollarSign, ShoppingCart, Clock, Printer, CheckCircle } from 'lucide-react';
import { formatCurrency } from '../../../utils/formatters';

interface DashboardCardsProps {
  stats: DashboardStats;
}

export const DashboardCards: React.FC<DashboardCardsProps> = ({ stats }) => {
  const cards = [
    {
      name: 'Pending Payment',
      value: stats.pending_payment_count,
      icon: Clock,
      color: 'text-yellow-600',
      bg: 'bg-yellow-100',
    },
    {
      name: 'Paid / In Queue',
      value: stats.paid_count,
      icon: ShoppingCart,
      color: 'text-blue-600',
      bg: 'bg-blue-100',
    },
    {
      name: 'Printing',
      value: stats.printing_count,
      icon: Printer,
      color: 'text-indigo-600',
      bg: 'bg-indigo-100',
    },
    {
      name: 'Ready for Pickup',
      value: stats.ready_for_pickup_count,
      icon: CheckCircle,
      color: 'text-green-600',
      bg: 'bg-green-100',
    },
    {
      name: 'Completed Today',
      value: stats.completed_today_count,
      icon: CheckCircle,
      color: 'text-gray-600',
      bg: 'bg-gray-100',
    },
    {
      name: 'Revenue Today',
      value: formatCurrency(stats.today_revenue),
      icon: DollarSign,
      color: 'text-emerald-600',
      bg: 'bg-emerald-100',
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
      {cards.map((card) => (
        <Card key={card.name} className="px-4 py-5 sm:p-6 flex items-center">
          <div className={`flex-shrink-0 rounded-md p-3 ${card.bg}`}>
            <card.icon className={`h-6 w-6 ${card.color}`} aria-hidden="true" />
          </div>
          <div className="ml-5 w-0 flex-1">
            <dt className="text-sm font-medium text-gray-500 truncate">{card.name}</dt>
            <dd className="flex items-baseline">
              <div className="text-2xl font-semibold text-gray-900">{card.value}</div>
            </dd>
          </div>
        </Card>
      ))}
    </div>
  );
};

export const DashboardCardsSkeleton: React.FC = () => {
  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
      {[...Array(6)].map((_, i) => (
        <Card key={i} className="px-4 py-5 sm:p-6 flex items-center animate-pulse">
          <div className="flex-shrink-0 rounded-md p-3 bg-gray-200 h-12 w-12"></div>
          <div className="ml-5 w-0 flex-1">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          </div>
        </Card>
      ))}
    </div>
  );
};

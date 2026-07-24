import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  iconColor?: string; // e.g. 'text-indigo-600'
  iconBg?: string; // e.g. 'bg-indigo-100'
  trend?: {
    value: string; // e.g. '+12%'
    positive: boolean;
  };
}

/**
 * Reusable metric card for dashboards and summary sections.
 * Used by Dashboard, Finance, Inventory, and any module that displays KPI cards.
 */
export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  icon: Icon,
  iconColor = 'text-indigo-600',
  iconBg = 'bg-indigo-100',
  trend,
}) => {
  return (
    <div className="relative overflow-hidden rounded-lg bg-white p-5 shadow-sm border border-gray-200">
      <dt>
        <div className={`absolute rounded-md p-3 ${iconBg}`}>
          <Icon className={`h-6 w-6 ${iconColor}`} aria-hidden="true" />
        </div>
        <p className="ml-16 truncate text-sm font-medium text-gray-500">{label}</p>
      </dt>
      <dd className="ml-16 flex items-baseline pt-1">
        <p className="text-2xl font-semibold text-gray-900">{value}</p>
        {trend && (
          <p
            className={`ml-2 flex items-baseline text-sm font-semibold ${trend.positive ? 'text-green-600' : 'text-red-600'}`}
          >
            {trend.value}
          </p>
        )}
      </dd>
    </div>
  );
};

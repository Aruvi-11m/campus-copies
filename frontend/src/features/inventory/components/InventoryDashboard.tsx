import React from 'react';
import { Package, AlertTriangle, XOctagon, DollarSign } from 'lucide-react';
import { formatCurrency } from '../../../utils/formatters';

interface InventoryDashboardProps {
  totalItems: number;
  lowStockCount: number;
  outOfStockCount: number;
  inventoryValue: number;
}

export const InventoryDashboard: React.FC<InventoryDashboardProps> = ({
  totalItems,
  lowStockCount,
  outOfStockCount,
  inventoryValue,
}) => {
  const cards = [
    {
      name: 'Total Items',
      value: totalItems,
      icon: Package,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100',
    },
    {
      name: 'Low Stock',
      value: lowStockCount,
      icon: AlertTriangle,
      color: 'text-amber-600',
      bgColor: 'bg-amber-100',
    },
    {
      name: 'Out of Stock',
      value: outOfStockCount,
      icon: XOctagon,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
    },
    {
      name: 'Inventory Value',
      value: formatCurrency(inventoryValue),
      icon: DollarSign,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-6">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div
            key={card.name}
            className="relative overflow-hidden rounded-lg bg-white p-5 shadow-sm border border-gray-200"
          >
            <dt>
              <div className={`absolute rounded-md p-3 ${card.bgColor}`}>
                <Icon className={`h-6 w-6 ${card.color}`} aria-hidden="true" />
              </div>
              <p className="ml-16 truncate text-sm font-medium text-gray-500">{card.name}</p>
            </dt>
            <dd className="ml-16 flex items-baseline pb-1 sm:pb-2">
              <p className="text-2xl font-semibold text-gray-900">{card.value}</p>
            </dd>
          </div>
        );
      })}
    </div>
  );
};

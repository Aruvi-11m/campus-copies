import React from 'react';
import { Card } from '../../../components/common/Card';
import { Badge } from '../../../components/common/Badge';
import { LowStockAlert } from '../types';
import { AlertTriangle } from 'lucide-react';

interface LowStockWidgetProps {
  alerts: LowStockAlert[];
}

export const LowStockWidget: React.FC<LowStockWidgetProps> = ({ alerts }) => {
  return (
    <Card className="flex flex-col h-full">
      <div className="p-6 border-b border-gray-200 flex items-center justify-between">
        <h3 className="text-lg font-medium leading-6 text-gray-900 flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-amber-500" />
          Low Stock Alerts
        </h3>
        {alerts.length > 0 && <Badge variant="warning">{alerts.length} Items</Badge>}
      </div>
      <div className="p-0 overflow-y-auto max-h-[300px]">
        {alerts.length === 0 ? (
          <div className="p-6 text-center text-sm text-gray-500">Inventory levels are healthy.</div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {alerts.map((alert) => (
              <li
                key={alert.item_code}
                className="p-4 hover:bg-gray-50 flex items-center justify-between"
              >
                <div className="flex flex-col">
                  <span className="text-sm font-medium text-gray-900">{alert.item_code}</span>
                  <span className="text-xs text-gray-500">
                    Min Threshold: {alert.min_threshold}
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-sm font-bold text-red-600">{alert.current_stock}</span>
                  <span className="text-xs text-gray-500 ml-1">in stock</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </Card>
  );
};

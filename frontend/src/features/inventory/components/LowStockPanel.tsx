import React from 'react';
import { InventoryItem } from '../types';
import { AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface LowStockPanelProps {
  items: InventoryItem[];
  onItemClick: (item: InventoryItem) => void;
}

export const LowStockPanel: React.FC<LowStockPanelProps> = ({ items, onItemClick }) => {
  const criticalItems = items.filter(
    (item) => item.status === 'LOW_STOCK' || item.status === 'OUT_OF_STOCK'
  );

  if (criticalItems.length === 0) return null;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-red-200 overflow-hidden mt-6">
      <div className="bg-red-50 px-4 py-3 border-b border-red-200 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-red-800 flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          Critical Stock Alerts
        </h3>
        <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full font-medium">
          {criticalItems.length} items need attention
        </span>
      </div>
      <ul className="divide-y divide-gray-200 max-h-64 overflow-y-auto">
        <AnimatePresence>
          {criticalItems.map((item) => (
            <motion.li
              key={item.id}
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="px-4 py-3 hover:bg-gray-50 cursor-pointer flex items-center justify-between transition-colors"
              onClick={() => onItemClick(item)}
            >
              <div>
                <p className="text-sm font-medium text-gray-900">{item.description}</p>
                <p className="text-xs text-gray-500">SKU: {item.item_code}</p>
              </div>
              <div className="text-right">
                <p
                  className={`text-sm font-bold ${item.status === 'OUT_OF_STOCK' ? 'text-red-600' : 'text-amber-600'}`}
                >
                  {item.current_stock} {item.unit}
                </p>
                <p className="text-xs text-gray-500">Min: {item.min_threshold}</p>
              </div>
            </motion.li>
          ))}
        </AnimatePresence>
      </ul>
    </div>
  );
};

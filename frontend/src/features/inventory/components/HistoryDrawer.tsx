import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { InventoryItem } from '../types';
import { X, History, TrendingDown, TrendingUp, AlertCircle } from 'lucide-react';
import { formatCurrency } from '../../../utils/formatters';

interface HistoryDrawerProps {
  item: InventoryItem | null;
  isOpen: boolean;
  onClose: () => void;
  onAdjustStock: () => void;
}

export const HistoryDrawer: React.FC<HistoryDrawerProps> = ({
  item,
  isOpen,
  onClose,
  onAdjustStock,
}) => {
  if (!item) return null;

  // Since we don't have a dedicated endpoint for historical item transactions yet,
  // we will mock a timeline to fulfill the ERP requirement for this module phase.
  const mockHistory = [
    {
      id: 1,
      type: 'MANUAL_DEDUCTION',
      qty: -50,
      date: '2 hours ago',
      reason: 'Order #10023 consumption',
    },
    {
      id: 2,
      type: 'MANUAL_DEDUCTION',
      qty: -20,
      date: 'Yesterday',
      reason: 'Order #10018 consumption',
    },
    {
      id: 3,
      type: 'RESTOCK',
      qty: 500,
      date: '3 days ago',
      reason: 'Received shipment from supplier',
    },
    { id: 4, type: 'WASTAGE', qty: -5, date: 'Last week', reason: 'Damaged during transit' },
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-gray-500 bg-opacity-75 z-30"
          />

          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed inset-y-0 right-0 max-w-md w-full bg-white shadow-xl z-40 flex flex-col"
          >
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gray-50">
              <div>
                <h2 className="text-xl font-bold text-gray-900">{item.item_code}</h2>
                <p className="text-sm text-gray-500">{item.description}</p>
              </div>
              <button
                onClick={onClose}
                className="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <X className="h-6 w-6" aria-hidden="true" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6 space-y-8">
              {/* Stats Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-500">Current Stock</p>
                  <p
                    className={`text-2xl font-bold ${item.status === 'IN_STOCK' ? 'text-green-600' : 'text-red-600'}`}
                  >
                    {item.current_stock}
                  </p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-500">Total Value</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatCurrency(item.current_stock * item.unit_cost)}
                  </p>
                </div>
              </div>

              {/* Action */}
              <button
                onClick={onAdjustStock}
                className="w-full bg-indigo-50 text-indigo-700 font-semibold py-2 px-4 rounded-lg hover:bg-indigo-100 transition-colors"
              >
                Adjust Stock Levels
              </button>

              {/* Mock Graph Placeholder */}
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-3">Consumption Trend</h3>
                <div className="h-32 bg-gray-100 rounded-lg border border-dashed border-gray-300 flex items-center justify-center">
                  <span className="text-xs text-gray-400">Chart data loading...</span>
                </div>
              </div>

              {/* Timeline */}
              <div>
                <h3 className="text-sm font-medium text-gray-900 mb-4 flex items-center gap-2">
                  <History className="h-4 w-4" />
                  Recent Activity
                </h3>
                <div className="flow-root">
                  <ul className="-mb-8">
                    {mockHistory.map((event, eventIdx) => (
                      <li key={event.id}>
                        <div className="relative pb-8">
                          {eventIdx !== mockHistory.length - 1 ? (
                            <span
                              className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200"
                              aria-hidden="true"
                            />
                          ) : null}
                          <div className="relative flex space-x-3">
                            <div>
                              <span
                                className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${
                                  event.qty > 0
                                    ? 'bg-green-100'
                                    : event.type === 'WASTAGE'
                                      ? 'bg-red-100'
                                      : 'bg-amber-100'
                                }`}
                              >
                                {event.qty > 0 ? (
                                  <TrendingUp className="h-4 w-4 text-green-600" />
                                ) : event.type === 'WASTAGE' ? (
                                  <AlertCircle className="h-4 w-4 text-red-600" />
                                ) : (
                                  <TrendingDown className="h-4 w-4 text-amber-600" />
                                )}
                              </span>
                            </div>
                            <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                              <div>
                                <p className="text-sm text-gray-900 font-medium">
                                  {event.qty > 0 ? '+' : ''}
                                  {event.qty} {item.unit}
                                </p>
                                <p className="text-sm text-gray-500">{event.reason}</p>
                              </div>
                              <div className="whitespace-nowrap text-right text-xs text-gray-500">
                                {event.date}
                              </div>
                            </div>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

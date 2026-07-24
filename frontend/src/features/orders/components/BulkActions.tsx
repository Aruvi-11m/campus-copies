import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { OrderStatus } from '../types';
import { useBulkUpdateOrders } from '../hooks';
import { Printer, CheckCircle } from 'lucide-react';

interface BulkActionsProps {
  selectedIds: string[];
  onClearSelection: () => void;
}

export const BulkActions: React.FC<BulkActionsProps> = ({ selectedIds, onClearSelection }) => {
  const { mutateAsync, isPending } = useBulkUpdateOrders();

  const handleBulkUpdate = async (status: OrderStatus) => {
    await mutateAsync({ ids: selectedIds, status });
    onClearSelection();
  };

  return (
    <AnimatePresence>
      {selectedIds.length > 0 && (
        <motion.div
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 50, opacity: 0 }}
          className="fixed bottom-6 left-1/2 -translate-x-1/2 z-30 bg-white shadow-2xl rounded-full px-6 py-4 border border-gray-200 flex items-center gap-6"
        >
          <div className="flex flex-col">
            <span className="text-sm font-semibold text-gray-900">
              {selectedIds.length} orders selected
            </span>
            <button
              onClick={onClearSelection}
              className="text-xs text-indigo-600 hover:text-indigo-800 text-left"
            >
              Clear selection
            </button>
          </div>

          <div className="h-8 w-px bg-gray-200" />

          <div className="flex gap-2">
            <button
              onClick={() => handleBulkUpdate('PRINTING')}
              disabled={isPending}
              className="inline-flex items-center gap-2 rounded-full bg-indigo-50 px-4 py-2 text-sm font-medium text-indigo-700 hover:bg-indigo-100 disabled:opacity-50"
            >
              <Printer className="h-4 w-4" />
              Mark Printing
            </button>
            <button
              onClick={() => handleBulkUpdate('READY_FOR_PICKUP')}
              disabled={isPending}
              className="inline-flex items-center gap-2 rounded-full bg-green-50 px-4 py-2 text-sm font-medium text-green-700 hover:bg-green-100 disabled:opacity-50"
            >
              <CheckCircle className="h-4 w-4" />
              Mark Ready
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

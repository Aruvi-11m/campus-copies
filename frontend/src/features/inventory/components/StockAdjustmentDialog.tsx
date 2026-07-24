import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { InventoryItem, TransactionType } from '../types';
import { useStockAdjustment } from '../hooks';
import { X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const adjustmentSchema = z.object({
  transaction_type: z.enum(['RESTOCK', 'MANUAL_DEDUCTION', 'WASTAGE', 'CORRECTION']),
  quantity_change: z.number().int().min(1, 'Quantity must be at least 1'),
  reason: z.string().min(3, 'Please provide a valid reason'),
});

type AdjustmentFormData = z.infer<typeof adjustmentSchema>;

interface StockAdjustmentDialogProps {
  item: InventoryItem | null;
  isOpen: boolean;
  onClose: () => void;
}

export const StockAdjustmentDialog: React.FC<StockAdjustmentDialogProps> = ({
  item,
  isOpen,
  onClose,
}) => {
  const { mutateAsync, isPending } = useStockAdjustment();

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<AdjustmentFormData>({
    resolver: zodResolver(adjustmentSchema),
    defaultValues: {
      transaction_type: 'RESTOCK',
      quantity_change: 1,
      reason: '',
    },
  });

  const transactionType = watch('transaction_type');

  const onSubmit = async (data: AdjustmentFormData) => {
    if (!item) return;

    // Negate quantity if it's a deduction
    const finalQuantity =
      data.transaction_type === 'RESTOCK' || data.transaction_type === 'CORRECTION'
        ? data.quantity_change
        : -data.quantity_change;

    await mutateAsync({
      item_id: item.id,
      transaction_type: data.transaction_type,
      quantity_change: finalQuantity,
      reason: data.reason,
    });
    reset();
    onClose();
  };

  if (!item) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-gray-500 bg-opacity-75 z-40"
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-0"
          >
            <div className="bg-white rounded-lg shadow-xl max-w-lg w-full overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Adjust Stock</h3>
                <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
                <p className="text-sm font-medium text-gray-900">{item.description}</p>
                <p className="text-sm text-gray-500">
                  Current Stock: {item.current_stock} {item.unit}
                </p>
              </div>

              <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-4">
                <div>
                  <label
                    htmlFor="transaction_type"
                    className="block text-sm font-medium leading-6 text-gray-900"
                  >
                    Action Type
                  </label>
                  <select
                    id="transaction_type"
                    {...register('transaction_type')}
                    className="mt-2 block w-full rounded-md border-0 py-1.5 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6"
                  >
                    <option value="RESTOCK">Add Stock (Restock)</option>
                    <option value="MANUAL_DEDUCTION">Remove Stock (Manual)</option>
                    <option value="WASTAGE">Record Wastage</option>
                    <option value="CORRECTION">Inventory Correction</option>
                  </select>
                  {errors.transaction_type && (
                    <p className="mt-1 text-sm text-red-600">{errors.transaction_type.message}</p>
                  )}
                </div>

                <div>
                  <label
                    htmlFor="quantity_change"
                    className="block text-sm font-medium leading-6 text-gray-900"
                  >
                    Quantity {transactionType === 'RESTOCK' ? 'to Add' : 'to Remove'}
                  </label>
                  <input
                    id="quantity_change"
                    type="number"
                    {...register('quantity_change', { valueAsNumber: true })}
                    className="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                  />
                  {errors.quantity_change && (
                    <p className="mt-1 text-sm text-red-600">{errors.quantity_change.message}</p>
                  )}
                </div>

                <div>
                  <label
                    htmlFor="reason"
                    className="block text-sm font-medium leading-6 text-gray-900"
                  >
                    Reason / Notes
                  </label>
                  <textarea
                    id="reason"
                    {...register('reason')}
                    rows={3}
                    className="mt-2 block w-full rounded-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                    placeholder="E.g., Received shipment from supplier..."
                  />
                  {errors.reason && (
                    <p className="mt-1 text-sm text-red-600">{errors.reason.message}</p>
                  )}
                </div>

                <div className="mt-6 flex justify-end gap-3">
                  <button
                    type="button"
                    onClick={onClose}
                    className="rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isPending}
                    className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50"
                  >
                    {isPending ? 'Saving...' : 'Confirm Adjustment'}
                  </button>
                </div>
              </form>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Order, OrderStatus } from '../types';
import { X, Printer, CheckCircle, FileText, ArrowRight } from 'lucide-react';
import { Badge } from '../../../components/common/Badge';
import { formatCurrency } from '../../../utils/formatters';
import { format } from 'date-fns';
import { useFileUrl, useUpdateOrderStatus } from '../hooks';

interface OrderDetailDrawerProps {
  order: Order | null;
  isOpen: boolean;
  onClose: () => void;
}

const statusOptions: { value: OrderStatus; label: string }[] = [
  { value: 'PENDING_PAYMENT', label: 'Pending Payment' },
  { value: 'PAID', label: 'Paid' },
  { value: 'PRINTING', label: 'Printing' },
  { value: 'READY_FOR_PICKUP', label: 'Ready for Pickup' },
  { value: 'COMPLETED', label: 'Completed' },
];

export const OrderDetailDrawer: React.FC<OrderDetailDrawerProps> = ({ order, isOpen, onClose }) => {
  const fileId = order?.files?.[0]?.id || null;
  const { data: fileData, isLoading: isFileLoading } = useFileUrl(fileId);
  const { mutateAsync: updateStatus, isPending } = useUpdateOrderStatus();

  if (!order) return null;

  const handleStatusAdvance = async (newStatus: OrderStatus) => {
    await updateStatus({ id: order.id, status: newStatus });
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-gray-500 bg-opacity-75 z-40"
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed inset-y-0 right-0 max-w-2xl w-full bg-white shadow-xl z-50 flex flex-col"
          >
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gray-50">
              <div>
                <h2 className="text-xl font-bold text-gray-900">{order.display_id}</h2>
                <p className="text-sm text-gray-500">{order.student_email}</p>
              </div>
              <button
                onClick={onClose}
                className="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <span className="sr-only">Close panel</span>
                <X className="h-6 w-6" aria-hidden="true" />
              </button>
            </div>

            {/* Scrollable Body */}
            <div className="flex-1 overflow-y-auto p-6 space-y-8">
              {/* Order Meta */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Total Price</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {formatCurrency(order.total_price)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Current Status</p>
                  <Badge variant="info">{order.status.replace(/_/g, ' ')}</Badge>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Print Specs</p>
                  <p className="text-sm text-gray-900 font-medium">
                    {order.color_mode}, {order.print_side}, {order.binding_type}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Pages / Copies</p>
                  <p className="text-sm text-gray-900 font-medium">
                    {order.page_count} pages × {order.copies} copies
                  </p>
                </div>
              </div>

              {/* Action Bar */}
              <div className="bg-indigo-50 rounded-lg p-4 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-indigo-800">Quick Actions</h3>
                  <p className="text-xs text-indigo-600 mt-1">Advance this order in the queue.</p>
                </div>
                <div className="flex gap-2">
                  {order.status === 'PAID' && (
                    <button
                      onClick={() => handleStatusAdvance('PRINTING')}
                      disabled={isPending}
                      className="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50"
                    >
                      <Printer className="h-4 w-4" />
                      Start Printing
                    </button>
                  )}
                  {order.status === 'PRINTING' && (
                    <button
                      onClick={() => handleStatusAdvance('READY_FOR_PICKUP')}
                      disabled={isPending}
                      className="inline-flex items-center gap-2 rounded-md bg-green-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-green-500 disabled:opacity-50"
                    >
                      <CheckCircle className="h-4 w-4" />
                      Ready for Pickup
                    </button>
                  )}
                  {order.status === 'READY_FOR_PICKUP' && (
                    <button
                      onClick={() => handleStatusAdvance('COMPLETED')}
                      disabled={isPending}
                      className="inline-flex items-center gap-2 rounded-md bg-gray-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-gray-500 disabled:opacity-50"
                    >
                      Complete Order
                    </button>
                  )}
                </div>
              </div>

              {/* File Preview */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
                  <FileText className="h-5 w-5 text-gray-400" />
                  Document Preview
                </h3>
                <div className="bg-gray-100 border border-gray-200 rounded-lg h-[400px] flex items-center justify-center overflow-hidden">
                  {isFileLoading ? (
                    <div className="animate-pulse flex flex-col items-center">
                      <FileText className="h-8 w-8 text-gray-300 mb-2" />
                      <span className="text-sm text-gray-500">Loading secure preview...</span>
                    </div>
                  ) : fileData?.signed_url ? (
                    <iframe
                      src={`${fileData.signed_url}#toolbar=0`}
                      className="w-full h-full"
                      title="PDF Preview"
                    />
                  ) : (
                    <span className="text-sm text-gray-500">No document available</span>
                  )}
                </div>
              </div>

              {/* Timeline */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Order Timeline</h3>
                <div className="flow-root">
                  <ul className="-mb-8">
                    {order.history &&
                      order.history.map((event, eventIdx) => (
                        <li key={event.id}>
                          <div className="relative pb-8">
                            {eventIdx !== order.history.length - 1 ? (
                              <span
                                className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200"
                                aria-hidden="true"
                              />
                            ) : null}
                            <div className="relative flex space-x-3">
                              <div>
                                <span className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center ring-8 ring-white">
                                  <ArrowRight
                                    className="h-4 w-4 text-indigo-600"
                                    aria-hidden="true"
                                  />
                                </span>
                              </div>
                              <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                                <div>
                                  <p className="text-sm text-gray-500">
                                    Status changed to{' '}
                                    <span className="font-medium text-gray-900">
                                      {event.status.replace(/_/g, ' ')}
                                    </span>
                                  </p>
                                  {event.notes && (
                                    <p className="mt-1 text-sm text-gray-600">{event.notes}</p>
                                  )}
                                </div>
                                <div className="whitespace-nowrap text-right text-sm text-gray-500">
                                  {format(new Date(event.created_at), 'MMM d, h:mm a')}
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

import React, { useState, useEffect } from 'react';
import { Input } from '../../../components/common/Input';
import { OrderStatus } from '../types';
import { Search, Filter, Calendar } from 'lucide-react';

interface OrdersFilterBarProps {
  search: string;
  onSearchChange: (val: string) => void;
  status: OrderStatus | '';
  onStatusChange: (val: OrderStatus | '') => void;
  startDate: string;
  onStartDateChange: (val: string) => void;
  endDate: string;
  onEndDateChange: (val: string) => void;
}

export const OrdersFilterBar: React.FC<OrdersFilterBarProps> = ({
  search,
  onSearchChange,
  status,
  onStatusChange,
  startDate,
  onStartDateChange,
  endDate,
  onEndDateChange,
}) => {
  // Local state for debounced search
  const [localSearch, setLocalSearch] = useState(search);

  useEffect(() => {
    const handler = setTimeout(() => {
      onSearchChange(localSearch);
    }, 500); // 500ms debounce
    return () => clearTimeout(handler);
  }, [localSearch, onSearchChange]);

  return (
    <div className="bg-white p-4 shadow-sm border border-gray-200 sm:rounded-lg mb-6 flex flex-col sm:flex-row gap-4 items-center">
      <div className="relative flex-1 w-full">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search className="h-5 w-5 text-gray-400" />
        </div>
        <input
          type="text"
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
          placeholder="Search by Order ID or Student Email..."
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
        />
      </div>

      <div className="flex w-full sm:w-auto gap-4">
        <div className="relative flex items-center w-full sm:w-auto">
          <Filter className="absolute left-3 h-4 w-4 text-gray-400 pointer-events-none" />
          <select
            className="pl-9 pr-8 py-2 block w-full text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            value={status}
            onChange={(e) => onStatusChange(e.target.value as OrderStatus | '')}
          >
            <option value="">All Statuses</option>
            <option value="PENDING_PAYMENT">Pending Payment</option>
            <option value="PAID">Paid</option>
            <option value="PRINTING">Printing</option>
            <option value="READY_FOR_PICKUP">Ready for Pickup</option>
            <option value="COMPLETED">Completed</option>
            <option value="CANCELLED">Cancelled</option>
            <option value="REFUNDED">Refunded</option>
          </select>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto border border-gray-300 rounded-md px-2 bg-white">
          <Calendar className="h-4 w-4 text-gray-400" />
          <input
            type="date"
            className="py-2 border-0 focus:ring-0 sm:text-sm bg-transparent w-full"
            value={startDate}
            onChange={(e) => onStartDateChange(e.target.value)}
          />
          <span className="text-gray-400">-</span>
          <input
            type="date"
            className="py-2 border-0 focus:ring-0 sm:text-sm bg-transparent w-full"
            value={endDate}
            onChange={(e) => onEndDateChange(e.target.value)}
          />
        </div>
      </div>
    </div>
  );
};

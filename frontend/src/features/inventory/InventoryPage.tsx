import React, { useState, useMemo } from 'react';
import { useInventoryItems } from './hooks';
import { InventoryItem } from './types';
import { InventoryDashboard } from './components/InventoryDashboard';
import { InventoryFilterBar } from './components/InventoryFilterBar';
import { InventoryTable } from './components/InventoryTable';
import { HistoryDrawer } from './components/HistoryDrawer';
import { StockAdjustmentDialog } from './components/StockAdjustmentDialog';
import { LowStockPanel } from './components/LowStockPanel';
import { ErrorBoundary, FallbackProps } from 'react-error-boundary';

export const InventoryPage: React.FC = () => {
  const { data, isLoading } = useInventoryItems();
  const items = useMemo(() => data?.data || [], [data?.data]);

  // Filter State
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [status, setStatus] = useState('');

  // UI State
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isAdjustmentOpen, setIsAdjustmentOpen] = useState(false);

  // Derived Data
  const categories = useMemo(() => Array.from(new Set(items.map((i) => i.category))), [items]);

  const filteredItems = useMemo(() => {
    return items.filter((item) => {
      const matchesSearch =
        item.description.toLowerCase().includes(search.toLowerCase()) ||
        item.item_code.toLowerCase().includes(search.toLowerCase());
      const matchesCategory = category ? item.category === category : true;
      const matchesStatus = status ? item.status === status : true;
      return matchesSearch && matchesCategory && matchesStatus;
    });
  }, [items, search, category, status]);

  const summary = useMemo(() => {
    return {
      totalItems: items.length,
      lowStockCount: items.filter((i) => i.status === 'LOW_STOCK').length,
      outOfStockCount: items.filter((i) => i.status === 'OUT_OF_STOCK').length,
      inventoryValue: items.reduce((acc, item) => acc + item.current_stock * item.unit_cost, 0),
    };
  }, [items]);

  // Handlers
  const handleRowClick = (item: InventoryItem) => {
    setSelectedItem(item);
    setIsDrawerOpen(true);
  };

  const handleAdjustStock = () => {
    setIsDrawerOpen(false);
    setIsAdjustmentOpen(true);
  };

  const ErrorFallback = ({ error, resetErrorBoundary }: FallbackProps) => (
    <div className="bg-red-50 p-6 rounded-lg border border-red-200">
      <h2 className="text-red-800 font-semibold mb-2">Failed to render inventory module</h2>
      <pre className="text-xs text-red-600 mb-4 overflow-auto">{error.message}</pre>
      <button
        onClick={resetErrorBoundary}
        className="bg-red-100 text-red-800 px-4 py-2 rounded-md font-medium hover:bg-red-200"
      >
        Try again
      </button>
    </div>
  );

  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onReset={() => {
        setSearch('');
        setCategory('');
        setStatus('');
      }}
    >
      <div className="space-y-4 pb-12">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Inventory Management</h1>
          <p className="mt-1 text-sm text-gray-500">
            Monitor stock levels, track consumption, and manage adjustments.
          </p>
        </div>

        <InventoryDashboard
          totalItems={summary.totalItems}
          lowStockCount={summary.lowStockCount}
          outOfStockCount={summary.outOfStockCount}
          inventoryValue={summary.inventoryValue}
        />

        <div className="flex flex-col lg:flex-row gap-6 items-start">
          <div className="flex-1 w-full space-y-4">
            <InventoryFilterBar
              search={search}
              onSearchChange={setSearch}
              category={category}
              onCategoryChange={setCategory}
              status={status}
              onStatusChange={setStatus}
              categories={categories}
            />

            <InventoryTable
              data={filteredItems}
              isLoading={isLoading}
              onRowClick={handleRowClick}
            />
          </div>

          <div className="w-full lg:w-80 shrink-0">
            <LowStockPanel
              items={items}
              onItemClick={(item) => {
                setSelectedItem(item);
                setIsAdjustmentOpen(true);
              }}
            />
          </div>
        </div>

        <HistoryDrawer
          item={selectedItem}
          isOpen={isDrawerOpen}
          onClose={() => setIsDrawerOpen(false)}
          onAdjustStock={handleAdjustStock}
        />

        <StockAdjustmentDialog
          item={selectedItem}
          isOpen={isAdjustmentOpen}
          onClose={() => setIsAdjustmentOpen(false)}
        />
      </div>
    </ErrorBoundary>
  );
};

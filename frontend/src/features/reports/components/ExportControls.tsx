import React, { useState } from 'react';
import { Button } from '../../../components/common/Button';
import { useExportData } from '../hooks';
import { Download, FileSpreadsheet, Printer } from 'lucide-react';

interface ExportControlsProps {
  startDate?: string;
  endDate?: string;
}

export const ExportControls: React.FC<ExportControlsProps> = ({ startDate, endDate }) => {
  const { mutate: exportData, isPending } = useExportData();
  const [exportingType, setExportingType] = useState<string | null>(null);

  const handleExport = (
    type: 'orders' | 'payments' | 'expenses' | 'inventory',
    format: 'csv' | 'excel'
  ) => {
    setExportingType(`${type}-${format}`);
    exportData(
      { type, format, start_date: startDate, end_date: endDate },
      {
        onSettled: () => setExportingType(null),
      }
    );
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm print:hidden">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Export & Actions</h3>

      <div className="flex flex-col gap-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="space-y-3 border p-4 rounded-lg">
            <h4 className="font-medium text-gray-900 text-sm">Orders Data</h4>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                size="sm"
                className="w-full"
                onClick={() => handleExport('orders', 'csv')}
                isLoading={exportingType === 'orders-csv'}
              >
                <Download className="w-4 h-4 mr-2" /> CSV
              </Button>
              <Button
                variant="secondary"
                size="sm"
                className="w-full"
                onClick={() => handleExport('orders', 'excel')}
                isLoading={exportingType === 'orders-excel'}
              >
                <FileSpreadsheet className="w-4 h-4 mr-2" /> Excel
              </Button>
            </div>
          </div>

          <div className="space-y-3 border p-4 rounded-lg">
            <h4 className="font-medium text-gray-900 text-sm">Revenue & Ledger</h4>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                size="sm"
                className="w-full"
                onClick={() => handleExport('payments', 'csv')}
                isLoading={exportingType === 'payments-csv'}
              >
                <Download className="w-4 h-4 mr-2" /> CSV
              </Button>
              <Button
                variant="secondary"
                size="sm"
                className="w-full"
                onClick={() => handleExport('payments', 'excel')}
                isLoading={exportingType === 'payments-excel'}
              >
                <FileSpreadsheet className="w-4 h-4 mr-2" /> Excel
              </Button>
            </div>
          </div>

          <div className="space-y-3 border p-4 rounded-lg">
            <h4 className="font-medium text-gray-900 text-sm">Expenses</h4>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                size="sm"
                className="w-full"
                onClick={() => handleExport('expenses', 'csv')}
                isLoading={exportingType === 'expenses-csv'}
              >
                <Download className="w-4 h-4 mr-2" /> CSV
              </Button>
              <Button
                variant="secondary"
                size="sm"
                className="w-full"
                onClick={() => handleExport('expenses', 'excel')}
                isLoading={exportingType === 'expenses-excel'}
              >
                <FileSpreadsheet className="w-4 h-4 mr-2" /> Excel
              </Button>
            </div>
          </div>

          <div className="space-y-3 border p-4 rounded-lg">
            <h4 className="font-medium text-gray-900 text-sm">Inventory</h4>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                size="sm"
                className="w-full"
                onClick={() => handleExport('inventory', 'csv')}
                isLoading={exportingType === 'inventory-csv'}
              >
                <Download className="w-4 h-4 mr-2" /> CSV
              </Button>
              <Button
                variant="secondary"
                size="sm"
                className="w-full"
                onClick={() => handleExport('inventory', 'excel')}
                isLoading={exportingType === 'inventory-excel'}
              >
                <FileSpreadsheet className="w-4 h-4 mr-2" /> Excel
              </Button>
            </div>
          </div>
        </div>

        <div className="flex justify-end pt-4 border-t">
          <Button variant="secondary" onClick={handlePrint}>
            <Printer className="w-4 h-4 mr-2" /> Print Report View
          </Button>
        </div>
      </div>
    </div>
  );
};

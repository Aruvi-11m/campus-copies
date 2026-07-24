import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { printSettingsSchema, PrintSettings } from '../../types';
import { useUpdateSettings } from '../../hooks';
import { Button } from '../../../../components/common/Button';
import { Input } from '../../../../components/common/Input';
import { Card } from './../../../../components/common/Card';

interface Props {
  initialData: Partial<PrintSettings>;
}

export const PrintSettingsForm: React.FC<Props> = ({ initialData }) => {
  const updateSettings = useUpdateSettings();

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm<PrintSettings>({
    resolver: zodResolver(printSettingsSchema),
    defaultValues: {
      print_default_color: initialData?.print_default_color ?? 'BW',
      print_default_side: initialData?.print_default_side ?? 'DOUBLE_SIDE',
      print_max_file_size_mb: initialData?.print_max_file_size_mb ?? 20,
    },
  });

  const onSubmit = (data: PrintSettings) => {
    updateSettings.mutate(data);
  };

  return (
    <Card>
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Printing Defaults & Limits</h3>
      </div>
      <div className="p-6">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label
                htmlFor="print_default_color"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Default Color Mode
              </label>
              <select
                id="print_default_color"
                {...register('print_default_color')}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="BW">Black & White</option>
                <option value="COLOR">Color</option>
              </select>
              {errors.print_default_color && (
                <p className="mt-1 text-sm text-red-600">{errors.print_default_color.message}</p>
              )}
            </div>

            <div>
              <label
                htmlFor="print_default_side"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Default Print Side
              </label>
              <select
                id="print_default_side"
                {...register('print_default_side')}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              >
                <option value="SINGLE_SIDE">Single Side</option>
                <option value="DOUBLE_SIDE">Double Side</option>
              </select>
              {errors.print_default_side && (
                <p className="mt-1 text-sm text-red-600">{errors.print_default_side.message}</p>
              )}
            </div>

            <Input
              label="Max File Size (MB)"
              type="number"
              {...register('print_max_file_size_mb', { valueAsNumber: true })}
              error={errors.print_max_file_size_mb?.message}
            />
          </div>
          <div className="flex justify-end">
            <Button
              type="submit"
              disabled={!isDirty || updateSettings.isPending}
              isLoading={updateSettings.isPending}
            >
              Save Print Settings
            </Button>
          </div>
        </form>
      </div>
    </Card>
  );
};

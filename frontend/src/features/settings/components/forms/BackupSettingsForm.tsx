import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { backupSettingsSchema, BackupSettings } from '../../types';
import { useUpdateSettings, useResetSettings } from '../../hooks';
import { Button } from '../../../../components/common/Button';
import { Input } from '../../../../components/common/Input';
import { Card } from './../../../../components/common/Card';
import { AlertTriangle } from 'lucide-react';

interface Props {
  initialData: Partial<BackupSettings>;
}

export const BackupSettingsForm: React.FC<Props> = ({ initialData }) => {
  const updateSettings = useUpdateSettings();
  const resetSettings = useResetSettings();

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm<BackupSettings>({
    resolver: zodResolver(backupSettingsSchema),
    defaultValues: {
      backup_frequency: initialData?.backup_frequency ?? 'DAILY',
      backup_retention_days: initialData?.backup_retention_days ?? 30,
    },
  });

  const onSubmit = (data: BackupSettings) => {
    updateSettings.mutate(data);
  };

  const handleFactoryReset = () => {
    if (
      window.confirm(
        'Are you sure you want to reset all settings to their factory defaults? This action cannot be undone.'
      )
    ) {
      resetSettings.mutate();
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Database Backup Schedule</h3>
        </div>
        <div className="p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label
                  htmlFor="backup_frequency"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Backup Frequency
                </label>
                <select
                  id="backup_frequency"
                  {...register('backup_frequency')}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="DAILY">Daily</option>
                  <option value="WEEKLY">Weekly</option>
                  <option value="MONTHLY">Monthly</option>
                </select>
                {errors.backup_frequency && (
                  <p className="mt-1 text-sm text-red-600">{errors.backup_frequency.message}</p>
                )}
              </div>

              <Input
                label="Retention Period (Days)"
                type="number"
                {...register('backup_retention_days', { valueAsNumber: true })}
                error={errors.backup_retention_days?.message}
              />
            </div>
            <div className="flex justify-end">
              <Button
                type="submit"
                disabled={!isDirty || updateSettings.isPending}
                isLoading={updateSettings.isPending}
              >
                Save Backup Settings
              </Button>
            </div>
          </form>
        </div>
      </Card>

      <Card>
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg leading-6 font-medium text-red-600 flex items-center">
            <AlertTriangle className="w-5 h-5 mr-2" />
            Danger Zone
          </h3>
        </div>
        <div className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-sm font-medium text-gray-900">Factory Reset</h4>
              <p className="text-sm text-gray-500">
                Reset all application settings across all categories back to default values.
              </p>
            </div>
            <Button
              variant="danger"
              onClick={handleFactoryReset}
              isLoading={resetSettings.isPending}
            >
              Reset Settings
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

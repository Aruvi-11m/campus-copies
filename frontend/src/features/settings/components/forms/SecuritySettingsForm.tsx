import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { securitySettingsSchema, SecuritySettings } from '../../types';
import { useUpdateSettings } from '../../hooks';
import { Button } from '../../../../components/common/Button';
import { Input } from '../../../../components/common/Input';
import { Card } from './../../../../components/common/Card';

interface Props {
  initialData: Partial<SecuritySettings>;
}

export const SecuritySettingsForm: React.FC<Props> = ({ initialData }) => {
  const updateSettings = useUpdateSettings();

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm<SecuritySettings>({
    resolver: zodResolver(securitySettingsSchema),
    defaultValues: {
      sec_admin_timeout_mins: initialData?.sec_admin_timeout_mins ?? 30,
      sec_require_2fa: initialData?.sec_require_2fa ?? false,
    },
  });

  const onSubmit = (data: SecuritySettings) => {
    updateSettings.mutate(data);
  };

  return (
    <Card>
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Security Configuration</h3>
      </div>
      <div className="p-6">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Input
              label="Admin Session Timeout (Mins)"
              type="number"
              {...register('sec_admin_timeout_mins', { valueAsNumber: true })}
              error={errors.sec_admin_timeout_mins?.message}
            />
          </div>
          <div className="space-y-4">
            <div className="flex items-center">
              <input
                id="sec_require_2fa"
                type="checkbox"
                {...register('sec_require_2fa')}
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <label
                htmlFor="sec_require_2fa"
                className="ml-3 block text-sm font-medium text-gray-700"
              >
                Require Two-Factor Authentication (2FA) for Admins
              </label>
            </div>
          </div>
          <div className="flex justify-end">
            <Button
              type="submit"
              disabled={!isDirty || updateSettings.isPending}
              isLoading={updateSettings.isPending}
            >
              Save Security Settings
            </Button>
          </div>
        </form>
      </div>
    </Card>
  );
};

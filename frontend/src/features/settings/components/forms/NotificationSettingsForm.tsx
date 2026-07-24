import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { notificationSettingsSchema, NotificationSettings } from '../../types';
import { useUpdateSettings } from '../../hooks';
import { Button } from '../../../../components/common/Button';
import { Card } from './../../../../components/common/Card';

interface Props {
  initialData: Partial<NotificationSettings>;
}

export const NotificationSettingsForm: React.FC<Props> = ({ initialData }) => {
  const updateSettings = useUpdateSettings();

  const {
    register,
    handleSubmit,
    formState: { isDirty },
  } = useForm<NotificationSettings>({
    resolver: zodResolver(notificationSettingsSchema),
    defaultValues: {
      notify_email_on_order: initialData?.notify_email_on_order ?? true,
      notify_sms_on_ready: initialData?.notify_sms_on_ready ?? true,
      notify_admin_on_new_order: initialData?.notify_admin_on_new_order ?? true,
    },
  });

  const onSubmit = (data: NotificationSettings) => {
    updateSettings.mutate(data);
  };

  return (
    <Card>
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Notification Preferences</h3>
      </div>
      <div className="p-6">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="space-y-4">
            <div className="flex items-center">
              <input
                id="notify_email_on_order"
                type="checkbox"
                {...register('notify_email_on_order')}
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <label
                htmlFor="notify_email_on_order"
                className="ml-3 block text-sm font-medium text-gray-700"
              >
                Email Student on Order Confirmation
              </label>
            </div>
            <div className="flex items-center">
              <input
                id="notify_sms_on_ready"
                type="checkbox"
                {...register('notify_sms_on_ready')}
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <label
                htmlFor="notify_sms_on_ready"
                className="ml-3 block text-sm font-medium text-gray-700"
              >
                SMS Student when Order is Ready for Pickup
              </label>
            </div>
            <div className="flex items-center">
              <input
                id="notify_admin_on_new_order"
                type="checkbox"
                {...register('notify_admin_on_new_order')}
                className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <label
                htmlFor="notify_admin_on_new_order"
                className="ml-3 block text-sm font-medium text-gray-700"
              >
                Notify Admins on New Order (In-App)
              </label>
            </div>
          </div>
          <div className="flex justify-end">
            <Button
              type="submit"
              disabled={!isDirty || updateSettings.isPending}
              isLoading={updateSettings.isPending}
            >
              Save Notification Settings
            </Button>
          </div>
        </form>
      </div>
    </Card>
  );
};

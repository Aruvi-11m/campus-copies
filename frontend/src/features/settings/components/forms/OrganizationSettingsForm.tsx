import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { organizationSettingsSchema, OrganizationSettings } from '../../types';
import { useUpdateSettings } from '../../hooks';
import { Button } from '../../../../components/common/Button';
import { Input } from '../../../../components/common/Input';
import { Card } from './../../../../components/common/Card';

interface Props {
  initialData: Partial<OrganizationSettings>;
}

export const OrganizationSettingsForm: React.FC<Props> = ({ initialData }) => {
  const updateSettings = useUpdateSettings();

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm<OrganizationSettings>({
    resolver: zodResolver(organizationSettingsSchema),
    defaultValues: {
      org_name: initialData?.org_name ?? '',
      org_upi_id: initialData?.org_upi_id ?? '',
      org_contact_email: initialData?.org_contact_email ?? '',
      org_contact_phone: initialData?.org_contact_phone ?? '',
      org_address: initialData?.org_address ?? '',
    },
  });

  const onSubmit = (data: OrganizationSettings) => {
    updateSettings.mutate(data);
  };

  return (
    <Card>
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Organization Details</h3>
      </div>
      <div className="p-6">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Input
              label="Organization Name"
              {...register('org_name')}
              error={errors.org_name?.message}
            />
            <Input label="UPI ID" {...register('org_upi_id')} error={errors.org_upi_id?.message} />
            <Input
              label="Contact Email"
              type="email"
              {...register('org_contact_email')}
              error={errors.org_contact_email?.message}
            />
            <Input
              label="Contact Phone"
              {...register('org_contact_phone')}
              error={errors.org_contact_phone?.message}
            />
            <div className="md:col-span-2">
              <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-1">
                Address
              </label>
              <textarea
                id="address"
                {...register('org_address')}
                rows={3}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:bg-gray-100"
              />
              {errors.org_address && (
                <p className="mt-1 text-sm text-red-600">{errors.org_address.message}</p>
              )}
            </div>
          </div>
          <div className="flex justify-end">
            <Button
              type="submit"
              disabled={!isDirty || updateSettings.isPending}
              isLoading={updateSettings.isPending}
            >
              Save Organization Settings
            </Button>
          </div>
        </form>
      </div>
    </Card>
  );
};

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { pricingSettingsSchema, PricingSettings } from '../../types';
import { useUpdateSettings } from '../../hooks';
import { Button } from '../../../../components/common/Button';
import { Input } from '../../../../components/common/Input';
import { Card } from './../../../../components/common/Card';

interface Props {
  initialData: Partial<PricingSettings>;
}

export const PricingSettingsForm: React.FC<Props> = ({ initialData }) => {
  const updateSettings = useUpdateSettings();

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm<PricingSettings>({
    resolver: zodResolver(pricingSettingsSchema),
    defaultValues: {
      pricing_bw_single: initialData?.pricing_bw_single ?? 1.5,
      pricing_bw_double: initialData?.pricing_bw_double ?? 1.0,
      pricing_color: initialData?.pricing_color ?? 5.0,
      pricing_spiral_binding: initialData?.pricing_spiral_binding ?? 30.0,
      pricing_soft_binding: initialData?.pricing_soft_binding ?? 40.0,
      pricing_hard_binding: initialData?.pricing_hard_binding ?? 70.0,
      pricing_stapling: initialData?.pricing_stapling ?? 5.0,
    },
  });

  const onSubmit = (data: PricingSettings) => {
    updateSettings.mutate(data);
  };

  return (
    <Card>
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Pricing Configuration</h3>
      </div>
      <div className="p-6">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Input
              label="B&W Single Side (₹)"
              type="number"
              step="0.01"
              {...register('pricing_bw_single', { valueAsNumber: true })}
              error={errors.pricing_bw_single?.message}
            />
            <Input
              label="B&W Double Side (₹)"
              type="number"
              step="0.01"
              {...register('pricing_bw_double', { valueAsNumber: true })}
              error={errors.pricing_bw_double?.message}
            />
            <Input
              label="Color (₹)"
              type="number"
              step="0.01"
              {...register('pricing_color', { valueAsNumber: true })}
              error={errors.pricing_color?.message}
            />
            <Input
              label="Spiral Binding (₹)"
              type="number"
              step="0.01"
              {...register('pricing_spiral_binding', { valueAsNumber: true })}
              error={errors.pricing_spiral_binding?.message}
            />
            <Input
              label="Soft Binding (₹)"
              type="number"
              step="0.01"
              {...register('pricing_soft_binding', { valueAsNumber: true })}
              error={errors.pricing_soft_binding?.message}
            />
            <Input
              label="Hard Binding (₹)"
              type="number"
              step="0.01"
              {...register('pricing_hard_binding', { valueAsNumber: true })}
              error={errors.pricing_hard_binding?.message}
            />
            <Input
              label="Stapling (₹)"
              type="number"
              step="0.01"
              {...register('pricing_stapling', { valueAsNumber: true })}
              error={errors.pricing_stapling?.message}
            />
          </div>
          <div className="flex justify-end">
            <Button
              type="submit"
              disabled={!isDirty || updateSettings.isPending}
              isLoading={updateSettings.isPending}
            >
              Save Pricing Settings
            </Button>
          </div>
        </form>
      </div>
    </Card>
  );
};

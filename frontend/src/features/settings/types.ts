import { z } from 'zod';

export const pricingSettingsSchema = z.object({
  pricing_bw_single: z.number().min(0, 'Must be positive'),
  pricing_bw_double: z.number().min(0, 'Must be positive'),
  pricing_color: z.number().min(0, 'Must be positive'),
  pricing_spiral_binding: z.number().min(0, 'Must be positive'),
  pricing_soft_binding: z.number().min(0, 'Must be positive'),
  pricing_hard_binding: z.number().min(0, 'Must be positive'),
  pricing_stapling: z.number().min(0, 'Must be positive'),
});

export const organizationSettingsSchema = z.object({
  org_name: z.string().min(1, 'Organization name is required'),
  org_upi_id: z.string().min(1, 'UPI ID is required'),
  org_contact_email: z.string().email('Invalid email address'),
  org_contact_phone: z.string().min(10, 'Invalid phone number'),
  org_address: z.string().min(1, 'Address is required'),
});

export const notificationSettingsSchema = z.object({
  notify_email_on_order: z.boolean(),
  notify_sms_on_ready: z.boolean(),
  notify_admin_on_new_order: z.boolean(),
});

export const printSettingsSchema = z.object({
  print_default_color: z.enum(['BW', 'COLOR']),
  print_default_side: z.enum(['SINGLE_SIDE', 'DOUBLE_SIDE']),
  print_max_file_size_mb: z.number().min(1, 'Min 1 MB').max(200, 'Max 200 MB'),
});

export const securitySettingsSchema = z.object({
  sec_admin_timeout_mins: z.number().min(5, 'Minimum 5 minutes'),
  sec_require_2fa: z.boolean(),
});

export const backupSettingsSchema = z.object({
  backup_frequency: z.enum(['DAILY', 'WEEKLY', 'MONTHLY']),
  backup_retention_days: z.number().min(1, 'Min 1 day'),
});

export const aboutSettingsSchema = z.object({
  app_version: z.string(),
});

export const appSettingsSchema = z
  .object({})
  .merge(pricingSettingsSchema)
  .merge(organizationSettingsSchema)
  .merge(notificationSettingsSchema)
  .merge(printSettingsSchema)
  .merge(securitySettingsSchema)
  .merge(backupSettingsSchema)
  .merge(aboutSettingsSchema);

export type AppSettings = z.infer<typeof appSettingsSchema>;
export type PricingSettings = z.infer<typeof pricingSettingsSchema>;
export type OrganizationSettings = z.infer<typeof organizationSettingsSchema>;
export type NotificationSettings = z.infer<typeof notificationSettingsSchema>;
export type PrintSettings = z.infer<typeof printSettingsSchema>;
export type SecuritySettings = z.infer<typeof securitySettingsSchema>;
export type BackupSettings = z.infer<typeof backupSettingsSchema>;
export type AboutSettings = z.infer<typeof aboutSettingsSchema>;

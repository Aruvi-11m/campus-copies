import { z } from 'zod';
import { PaginatedData } from '../../types/api';

export const notificationSchema = z.object({
  id: z.number(),
  target_user: z.enum(['SYSTEM', 'ADMIN', 'STUDENT']),
  type: z.enum(['SYSTEM_ALERT', 'ORDER_UPDATE', 'PAYMENT_ALERT', 'INVENTORY_ALERT', 'GENERAL']),
  event_type: z.string(),
  title: z.string(),
  message: z.string(),
  is_read: z.boolean(),
  created_at: z.string(),
  target_user_id: z.string().uuid().nullable(),
  order_id: z.number().nullable(),
});

export type Notification = z.infer<typeof notificationSchema>;

export interface NotificationFilters {
  page: number;
  size: number;
}

export type NotificationPaginatedResponse = PaginatedData<Notification>;

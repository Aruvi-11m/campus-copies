import { apiRequest } from '../../api/client';
import { Notification, NotificationFilters, NotificationPaginatedResponse } from './types';

export const getAdminNotifications = async (
  filters: NotificationFilters
): Promise<NotificationPaginatedResponse> => {
  const skip = (filters.page - 1) * filters.size;
  const params = new URLSearchParams({
    skip: skip.toString(),
    limit: filters.size.toString(),
  });

  return apiRequest<NotificationPaginatedResponse>(
    `/api/v1/admin/notifications?${params.toString()}`,
    {
      method: 'GET',
    }
  );
};

export const markNotificationRead = async (id: number): Promise<Notification> => {
  return apiRequest<Notification>(`/api/v1/admin/notifications/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ is_read: true }),
  });
};

export const deleteNotification = async (id: number): Promise<{ status: string }> => {
  return apiRequest<{ status: string }>(`/api/v1/admin/notifications/${id}`, {
    method: 'DELETE',
  });
};

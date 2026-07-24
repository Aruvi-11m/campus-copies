import { apiRequest } from '../../api/client';
import { storage } from '../../utils/storage';
import { Order, PaginatedOrdersResponse, OrderQueryOptions, OrderStatus } from './types';

export const fetchOrders = async (options: OrderQueryOptions): Promise<PaginatedOrdersResponse> => {
  const token = storage.getToken();

  // Build query string
  const params = new URLSearchParams();
  params.append('page', options.page.toString());
  params.append('limit', options.limit.toString());

  if (options.status) params.append('status', options.status);
  if (options.search) params.append('search', options.search);
  if (options.start_date) params.append('start_date', options.start_date);
  if (options.end_date) params.append('end_date', options.end_date);

  return apiRequest<PaginatedOrdersResponse>(`/api/v1/orders?${params.toString()}`, {
    method: 'GET',
    token,
  });
};

export const fetchOrderById = async (id: string): Promise<Order> => {
  const token = storage.getToken();
  return apiRequest<Order>(`/api/v1/orders/${id}`, {
    method: 'GET',
    token,
  });
};

export const updateOrderStatus = async ({
  id,
  status,
  notes,
}: {
  id: string;
  status: OrderStatus;
  notes?: string;
}): Promise<Order> => {
  const token = storage.getToken();
  return apiRequest<Order>(`/api/v1/orders/${id}/status`, {
    method: 'PATCH',
    token,
    body: JSON.stringify({ status, notes }),
  });
};

export const fetchFileSignedUrl = async (
  fileId: string
): Promise<{ signed_url: string; expires_in_seconds: number }> => {
  const token = storage.getToken();
  return apiRequest<{ signed_url: string; expires_in_seconds: number }>(
    `/api/v1/files/${fileId}/signed-url`,
    {
      method: 'GET',
      token,
    }
  );
};

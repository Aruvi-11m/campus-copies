import { apiRequest } from '../../api/client';
import { storage } from '../../utils/storage';
import { InventoryItem, StockTransactionRequest } from './types';

// The API endpoints as defined in docs/API.md
export const fetchInventoryItems = async (): Promise<{
  success: boolean;
  data: InventoryItem[];
}> => {
  const token = storage.getToken();
  // We assume the API returns { success: true, data: InventoryItem[] }
  return apiRequest<{ success: boolean; data: InventoryItem[] }>(`/api/v1/inventory/items`, {
    method: 'GET',
    token,
  });
};

export const submitStockTransaction = async (
  request: StockTransactionRequest
): Promise<{ success: boolean; data: any }> => {
  const token = storage.getToken();
  return apiRequest<{ success: boolean; data: any }>(`/api/v1/inventory/transactions`, {
    method: 'POST',
    token,
    body: JSON.stringify(request),
  });
};

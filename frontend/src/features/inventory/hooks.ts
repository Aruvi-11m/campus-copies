import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchInventoryItems, submitStockTransaction } from './api';
import toast from 'react-hot-toast';

export const useInventoryItems = () => {
  return useQuery({
    queryKey: ['inventory'],
    queryFn: fetchInventoryItems,
    refetchInterval: 60000, // Auto-refresh every minute for low stock panel
  });
};

export const useStockAdjustment = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: submitStockTransaction,
    onSuccess: () => {
      toast.success('Stock transaction recorded successfully');
      // Invalidate inventory cache to immediately refetch and update UI
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
    },
    onError: (error) => {
      toast.error('Failed to record transaction. Please try again.');
      console.error(error);
    },
  });
};

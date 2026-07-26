import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchOrders, fetchOrderById, updateOrderStatus, fetchFileSignedUrl } from './api';
import { OrderQueryOptions, OrderStatus, Order } from './types';
import toast from 'react-hot-toast';

export const useOrders = (options: OrderQueryOptions) => {
  return useQuery({
    queryKey: ['orders', options],
    queryFn: () => fetchOrders(options),
    placeholderData: (previousData) => previousData, // keep previous data while fetching new page
  });
};

export const useOrder = (id: string | null) => {
  return useQuery({
    queryKey: ['order', id],
    queryFn: () => fetchOrderById(id!),
    enabled: !!id,
  });
};

export const useUpdateOrderStatus = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateOrderStatus,
    onMutate: async (variables) => {
      // Cancel any outgoing refetches so they don't overwrite optimistic update
      await queryClient.cancelQueries({ queryKey: ['orders'] });
      await queryClient.cancelQueries({ queryKey: ['order', variables.id] });

      // Snapshot the previous values (we can't easily get the specific page it was on,
      // but we can invalidate later. A true optimistic update on a paginated list is complex.
      // We'll optimistically update the single 'order' cache if it exists.)
      const previousOrder = queryClient.getQueryData<Order>(['order', variables.id]);

      if (previousOrder) {
        queryClient.setQueryData<Order>(['order', variables.id], {
          ...previousOrder,
          status: variables.status,
        });
      }

      return { previousOrder };
    },
    onError: (err, variables, context) => {
      // Rollback
      if (context?.previousOrder) {
        queryClient.setQueryData(['order', variables.id], context.previousOrder);
      }
      toast.error('Failed to update order status');
    },
    onSettled: (data, error, variables) => {
      // Invalidate both lists and specific order
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      queryClient.invalidateQueries({ queryKey: ['order', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['dashboardStats'] }); // refresh dashboard
    },
    onSuccess: (data) => {
      toast.success(`Order ${data.display_id} updated to ${data.status.replace(/_/g, ' ')}`);
    },
  });
};

// Wrapper hook for bulk updates using Promise.all
export const useBulkUpdateOrders = () => {
  const queryClient = useQueryClient();
  const updateMutation = useMutation({ mutationFn: updateOrderStatus });

  const mutateAsync = async ({ ids, status }: { ids: string[]; status: OrderStatus }) => {
    const promises = ids.map((id) => updateMutation.mutateAsync({ id, status }));

    toast.promise(Promise.all(promises), {
      loading: `Updating ${ids.length} orders...`,
      success: `Successfully updated ${ids.length} orders to ${status.replace(/_/g, ' ')}`,
      error: 'Failed to update some orders. Please check the list.',
    });

    try {
      await Promise.all(promises);
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
    } catch (error) {
      console.error('Bulk update error', error);
      queryClient.invalidateQueries({ queryKey: ['orders'] }); // force refresh to get true state
    }
  };

  return { mutateAsync, isPending: updateMutation.isPending };
};

export const useFileUrl = (fileId: string | null) => {
  return useQuery({
    queryKey: ['fileUrl', fileId],
    queryFn: () => fetchFileSignedUrl(fileId!),
    enabled: !!fileId,
    staleTime: 1000 * 60 * 30, // 30 minutes
  });
};

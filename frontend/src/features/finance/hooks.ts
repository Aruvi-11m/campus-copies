import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchFinanceSummary, fetchLedger, fetchExpenses, createExpense } from './api';
import { FinanceFilters } from './types';
import toast from 'react-hot-toast';

export const useFinanceSummary = (filters: FinanceFilters) => {
  return useQuery({
    queryKey: ['financeSummary', filters],
    queryFn: () => fetchFinanceSummary(filters),
  });
};

export const useLedger = () => {
  return useQuery({
    queryKey: ['ledger'],
    queryFn: fetchLedger,
  });
};

export const useExpenses = () => {
  return useQuery({
    queryKey: ['expenses'],
    queryFn: fetchExpenses,
  });
};

export const useCreateExpense = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createExpense,
    onSuccess: () => {
      toast.success('Expense recorded successfully');
      queryClient.invalidateQueries({ queryKey: ['expenses'] });
      queryClient.invalidateQueries({ queryKey: ['financeSummary'] });
    },
    onError: () => {
      toast.error('Failed to record expense');
    },
  });
};

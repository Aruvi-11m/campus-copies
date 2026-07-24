import { apiRequest } from '../../api/client';
import { storage } from '../../utils/storage';
import { FinanceSummary, FinanceFilters, LedgerEntry, Expense, ExpenseFormData } from './types';

export const fetchFinanceSummary = async (filters: FinanceFilters): Promise<FinanceSummary> => {
  const token = storage.getToken();
  const params = new URLSearchParams();
  params.append('period', filters.period);
  if (filters.date) params.append('date', filters.date);
  if (filters.month) params.append('month', filters.month.toString());
  if (filters.year) params.append('year', filters.year.toString());
  if (filters.start_date) params.append('start_date', filters.start_date);
  if (filters.end_date) params.append('end_date', filters.end_date);

  return apiRequest<FinanceSummary>(`/api/v1/reports/summary?${params.toString()}`, {
    method: 'GET',
    token,
  });
};

export const fetchLedger = async (): Promise<LedgerEntry[]> => {
  const token = storage.getToken();
  return apiRequest<LedgerEntry[]>('/api/v1/payments/ledger', {
    method: 'GET',
    token,
  });
};

export const fetchExpenses = async (): Promise<Expense[]> => {
  const token = storage.getToken();
  return apiRequest<Expense[]>('/api/v1/reports/expenses', {
    method: 'GET',
    token,
  });
};

export const createExpense = async (data: ExpenseFormData): Promise<Expense> => {
  const token = storage.getToken();
  return apiRequest<Expense>('/api/v1/reports/expenses', {
    method: 'POST',
    token,
    body: JSON.stringify(data),
  });
};

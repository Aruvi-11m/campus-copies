import { useQuery, useMutation } from '@tanstack/react-query';
import { reportsApi } from './api';
import { ExportParams, ReportPeriod } from './types';
import toast from 'react-hot-toast';

export const useReportSummary = (
  period: ReportPeriod,
  customDates?: { start_date: string; end_date: string }
) => {
  return useQuery({
    queryKey: ['reportSummary', period, customDates],
    queryFn: () => reportsApi.getSummary({ period, ...customDates }),
    staleTime: 5 * 60 * 1000, // 5 minutes cache
  });
};

export const useExportData = () => {
  return useMutation({
    mutationFn: (params: ExportParams) => reportsApi.exportData(params),
    onSuccess: (_, variables) => {
      toast.success(
        `${variables.type} exported to ${variables.format.toUpperCase()} successfully.`
      );
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Failed to export data');
    },
  });
};

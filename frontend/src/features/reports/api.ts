import { apiRequest } from '../../api/client';
import { ReportSummaryResponse, ExportParams, ReportPeriod } from './types';

interface SummaryParams {
  period?: ReportPeriod;
  date?: string;
  year?: number;
  month?: number;
  start_date?: string;
  end_date?: string;
}

export const reportsApi = {
  getSummary: async (params: SummaryParams = {}): Promise<ReportSummaryResponse> => {
    // Construct query string
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        query.append(key, String(value));
      }
    });

    return apiRequest<ReportSummaryResponse>(`/api/v1/reports/summary?${query.toString()}`);
  },

  exportData: async ({ type, format, start_date, end_date }: ExportParams): Promise<void> => {
    const url = new URL(
      `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/admin/export/${type}`
    );
    url.searchParams.append('format', format);

    if (start_date) url.searchParams.append('start_date', start_date);
    if (end_date) url.searchParams.append('end_date', end_date);

    const token = localStorage.getItem('auth_token');

    const response = await fetch(url.toString(), {
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });

    if (!response.ok) {
      throw new Error(`Export failed: ${response.statusText}`);
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;

    const contentDisposition = response.headers.get('content-disposition');
    let filename = `${type}_export.${format === 'excel' ? 'xlsx' : format}`;
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?([^"]+)"?/);
      if (match && match[1]) {
        filename = match[1];
      }
    }

    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);
  },
};

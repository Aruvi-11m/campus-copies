import { apiRequest } from '../../api/client';
import { AppSettings } from './types';

export const settingsApi = {
  getSettings: () => {
    return apiRequest<AppSettings>('/admin/settings', {
      method: 'GET',
    });
  },

  updateSettings: (data: Partial<AppSettings>) => {
    return apiRequest<AppSettings>('/admin/settings', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  resetSettings: () => {
    return apiRequest<AppSettings>('/admin/settings/reset', {
      method: 'POST',
    });
  },
};

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { settingsApi } from './api';
import toast from 'react-hot-toast';

export const useSettingsKeys = {
  all: ['settings'] as const,
};

export const useSettings = () => {
  return useQuery({
    queryKey: useSettingsKeys.all,
    queryFn: () => settingsApi.getSettings(),
  });
};

export const useUpdateSettings = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: settingsApi.updateSettings,
    onSuccess: (data) => {
      queryClient.setQueryData(useSettingsKeys.all, data);
      toast.success('Settings updated successfully');
    },
    onError: () => {
      toast.error('Failed to update settings');
    },
  });
};

export const useResetSettings = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: settingsApi.resetSettings,
    onSuccess: (data) => {
      queryClient.setQueryData(useSettingsKeys.all, data);
      toast.success('Settings reset to defaults');
    },
    onError: () => {
      toast.error('Failed to reset settings');
    },
  });
};

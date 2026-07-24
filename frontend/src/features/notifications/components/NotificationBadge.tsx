import React from 'react';
import { useAdminNotifications } from '../hooks';
import { Bell } from 'lucide-react';

export const NotificationBadge: React.FC = () => {
  const { data } = useAdminNotifications({ page: 1, size: 50 });
  const unreadCount = data?.items.filter((n) => !n.is_read).length || 0;

  return (
    <div className="relative p-2 text-gray-400 hover:text-gray-500 cursor-pointer">
      <span className="sr-only">View notifications</span>
      <Bell className="h-6 w-6" aria-hidden="true" />
      {unreadCount > 0 && (
        <span className="absolute top-1 right-1 inline-flex items-center justify-center px-1.5 py-0.5 rounded-full text-xs font-bold leading-none text-white bg-red-600 transform translate-x-1/4 -translate-y-1/4">
          {unreadCount > 9 ? '9+' : unreadCount}
        </span>
      )}
    </div>
  );
};

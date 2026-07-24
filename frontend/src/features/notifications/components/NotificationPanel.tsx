import React from 'react';
import { useAdminNotifications, useMarkNotificationRead, useDeleteNotification } from '../hooks';
import { formatDate } from '../../../utils/formatters';
import { Check, Trash2, Info, AlertCircle, Package } from 'lucide-react';
import { LoadingSpinner } from '../../../components/common/LoadingSpinner';

export const NotificationPanel: React.FC = () => {
  const { data, isLoading } = useAdminNotifications({ page: 1, size: 20 });
  const markRead = useMarkNotificationRead();
  const deleteNotif = useDeleteNotification();

  const getIcon = (type: string) => {
    switch (type) {
      case 'SYSTEM_ALERT':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'ORDER_UPDATE':
        return <Package className="h-5 w-5 text-blue-500" />;
      default:
        return <Info className="h-5 w-5 text-gray-400" />;
    }
  };

  return (
    <div className="w-80 bg-white shadow-lg rounded-md overflow-hidden border border-gray-200 flex flex-col max-h-96">
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
        <h3 className="text-sm font-medium text-gray-900">Notifications</h3>
      </div>
      <div className="overflow-y-auto flex-1">
        {isLoading ? (
          <div className="flex justify-center py-6">
            <LoadingSpinner className="h-6 w-6 text-indigo-600" />
          </div>
        ) : data?.items.length === 0 ? (
          <div className="px-4 py-6 text-center text-sm text-gray-500">
            No notifications right now.
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {data?.items.map((notification) => (
              <li
                key={notification.id}
                className={`px-4 py-3 hover:bg-gray-50 flex items-start space-x-3 ${!notification.is_read ? 'bg-indigo-50/50' : ''}`}
              >
                <div className="flex-shrink-0 mt-0.5">{getIcon(notification.type)}</div>
                <div className="flex-1 min-w-0">
                  <p
                    className={`text-sm ${!notification.is_read ? 'font-semibold text-gray-900' : 'text-gray-600'}`}
                  >
                    {notification.title}
                  </p>
                  <p className="text-sm text-gray-500 mt-0.5 line-clamp-2">
                    {notification.message}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    {formatDate(notification.created_at)}
                  </p>
                </div>
                <div className="flex flex-col space-y-2 flex-shrink-0">
                  {!notification.is_read && (
                    <button
                      onClick={() => markRead.mutate(notification.id)}
                      className="text-gray-400 hover:text-indigo-600"
                      title="Mark as read"
                    >
                      <Check className="h-4 w-4" />
                    </button>
                  )}
                  <button
                    onClick={() => deleteNotif.mutate(notification.id)}
                    className="text-gray-400 hover:text-red-600"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

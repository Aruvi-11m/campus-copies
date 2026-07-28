import React, { useState, useRef, useEffect } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  ShoppingCart,
  Package,
  DollarSign,
  BarChart2,
  Settings,
  ShieldAlert,
  LogOut,
  Menu,
  X,
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { adminLogin } from '../api/auth';
import { NotificationBadge } from '../features/notifications/components/NotificationBadge';
import { NotificationPanel } from '../features/notifications/components/NotificationPanel';

const navigation = [
  { name: 'Dashboard', href: '/admin', icon: LayoutDashboard },
  { name: 'Orders', href: '/admin/orders', icon: ShoppingCart },
  { name: 'Inventory', href: '/admin/inventory', icon: Package },
  { name: 'Finance', href: '/admin/finance', icon: DollarSign },
  { name: 'Reports', href: '/admin/reports', icon: BarChart2 },
  { name: 'Settings', href: '/admin/settings', icon: Settings },
  { name: 'Audit Logs', href: '/admin/audit-logs', icon: ShieldAlert },
];

export const AdminLayout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { logout, login, admin } = useAuth();
  const notifRef = useRef<HTMLDivElement>(null);

  const handleLogout = () => {
    logout();
    navigate('/admin/login');
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 z-40 lg:hidden ${sidebarOpen ? '' : 'hidden'}`}>
        {/* eslint-disable-next-line jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions */}
        <div
          className="fixed inset-0 bg-gray-600 bg-opacity-75"
          onClick={() => setSidebarOpen(false)}
        ></div>
        <div className="relative flex-1 flex flex-col max-w-xs w-full bg-white h-full">
          <div className="absolute top-0 right-0 -mr-12 pt-2">
            <button
              className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="h-6 w-6 text-white" />
            </button>
          </div>
          <div className="flex-1 h-0 pt-5 pb-4 overflow-y-auto">
            <div className="flex-shrink-0 flex items-center px-4 font-bold text-xl text-blue-900">
              Campus Copies
            </div>
            <nav className="mt-5 px-2 space-y-1">
              {navigation.map((item) => {
                const isActive =
                  location.pathname === item.href ||
                  (item.href !== '/admin' && location.pathname.startsWith(item.href));
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`${
                      isActive
                        ? 'bg-blue-50 text-blue-900'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    } group flex items-center px-2 py-2 text-base font-medium rounded-md`}
                  >
                    <item.icon
                      className={`${isActive ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'} mr-4 flex-shrink-0 h-6 w-6`}
                    />
                    {item.name}
                  </Link>
                );
              })}
            </nav>
          </div>
          <div className="flex-shrink-0 flex border-t border-gray-200 p-4">
            <button
              onClick={handleLogout}
              className="flex-shrink-0 group block text-gray-600 w-full text-left"
            >
              <div className="flex items-center">
                <LogOut className="inline-block h-5 w-5 mr-3 text-gray-400 group-hover:text-gray-500" />
                <span className="text-base font-medium text-gray-700 group-hover:text-gray-900">
                  Sign out
                </span>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:flex lg:flex-shrink-0">
        <div className="flex flex-col w-64">
          <div className="flex-1 flex flex-col min-h-0 border-r border-gray-200 bg-white">
            <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
              <div className="flex items-center flex-shrink-0 px-4 font-bold text-xl text-blue-900">
                Campus Copies
              </div>
              <nav className="mt-5 flex-1 px-2 bg-white space-y-1">
                {navigation.map((item) => {
                  const isActive =
                    location.pathname === item.href ||
                    (item.href !== '/admin' && location.pathname.startsWith(item.href));
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`${
                        isActive
                          ? 'bg-blue-50 text-blue-900'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      } group flex items-center px-2 py-2 text-sm font-medium rounded-md`}
                    >
                      <item.icon
                        className={`${isActive ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'} mr-3 flex-shrink-0 h-5 w-5`}
                      />
                      {item.name}
                    </Link>
                  );
                })}
              </nav>
            </div>
            <div className="flex-shrink-0 flex border-t border-gray-200 p-4">
              <div className="flex-shrink-0 w-full group block">
                <div className="flex items-center">
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-700">{admin?.full_name}</p>
                    <button
                      onClick={handleLogout}
                      className="text-xs font-medium text-gray-500 group-hover:text-gray-700 flex items-center mt-1"
                    >
                      <LogOut className="h-4 w-4 mr-1" />
                      Sign out
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-col w-0 flex-1 overflow-hidden">
        <div className="relative z-10 flex-shrink-0 flex h-16 bg-white shadow">
          <button
            type="button"
            className="px-4 border-r border-gray-200 text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <span className="sr-only">Open sidebar</span>
            <Menu className="h-6 w-6" aria-hidden="true" />
          </button>

          <div className="flex-1 px-4 flex justify-between items-center">
            {/* Active Admin Profile Badge & Quick Dual Switcher */}
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2 bg-slate-100 px-3 py-1.5 rounded-full border border-slate-200">
                <span className={`w-3 h-3 rounded-full ${admin?.username === 'barathwaj' ? 'bg-emerald-500' : 'bg-indigo-600'}`}></span>
                <span className="text-xs font-semibold text-gray-800">
                  {admin?.full_name || 'Admin'} ({admin?.role || 'Co-Admin'})
                </span>
              </div>
              <button
                type="button"
                onClick={async () => {
                  const targetUser = admin?.username === 'barathwaj' ? 'thamizaruvi' : 'barathwaj';
                  const res = await adminLogin(targetUser, 'admin123');
                  login(res, true);
                }}
                className="text-xs font-medium text-indigo-600 hover:text-indigo-800 bg-indigo-50 hover:bg-indigo-100 px-2.5 py-1.5 rounded-lg border border-indigo-200 transition-colors flex items-center gap-1.5"
                title="Switch to other Co-Admin session"
              >
                <span>Switch to {admin?.username === 'barathwaj' ? 'Thamizaruvi' : 'Barathwaj'}</span>
              </button>
            </div>

            <div className="ml-4 flex items-center md:ml-6 relative" ref={notifRef}>
              <button
                className="bg-white p-1 rounded-full text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                onClick={() => setShowNotifications(!showNotifications)}
              >
                <NotificationBadge />
              </button>

              {showNotifications && (
                <div className="origin-top-right absolute right-0 top-12 mt-2 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
                  <NotificationPanel />
                </div>
              )}
            </div>
          </div>
        </div>

        <main className="flex-1 relative z-0 overflow-y-auto focus:outline-none">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
              <Outlet />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

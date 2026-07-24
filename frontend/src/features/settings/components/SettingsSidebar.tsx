import React from 'react';
import { IndianRupee, Building, Bell, Printer, Shield, Database, Info } from 'lucide-react';

export type SettingsTab =
  'pricing' | 'organization' | 'notifications' | 'printing' | 'security' | 'backup' | 'about';

interface SidebarProps {
  activeTab: SettingsTab;
  onTabChange: (tab: SettingsTab) => void;
}

const navItems = [
  { id: 'pricing', label: 'Pricing', icon: IndianRupee },
  { id: 'organization', label: 'Organization', icon: Building },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'printing', label: 'Printing', icon: Printer },
  { id: 'security', label: 'Security', icon: Shield },
  { id: 'backup', label: 'Backup', icon: Database },
  { id: 'about', label: 'About', icon: Info },
] as const;

export const SettingsSidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  return (
    <nav className="flex flex-col space-y-1" aria-label="Settings Sidebar">
      {navItems.map((item) => {
        const isActive = activeTab === item.id;
        const Icon = item.icon;

        return (
          <button
            key={item.id}
            onClick={() => onTabChange(item.id)}
            className={`
              flex items-center px-3 py-2 text-sm font-medium rounded-md w-full transition-colors
              ${
                isActive
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'text-gray-900 hover:bg-gray-50 hover:text-gray-900'
              }
            `}
            aria-current={isActive ? 'page' : undefined}
          >
            <Icon
              className={`
                flex-shrink-0 -ml-1 mr-3 h-5 w-5
                ${isActive ? 'text-indigo-500' : 'text-gray-400 group-hover:text-gray-500'}
              `}
              aria-hidden="true"
            />
            <span className="truncate">{item.label}</span>
          </button>
        );
      })}
    </nav>
  );
};

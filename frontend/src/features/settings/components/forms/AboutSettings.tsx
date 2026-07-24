import React from 'react';
import { AboutSettings as AboutSettingsType } from '../../types';
import { Card } from './../../../../components/common/Card';

interface Props {
  initialData: Partial<AboutSettingsType>;
}

export const AboutSettings: React.FC<Props> = ({ initialData }) => {
  return (
    <Card>
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg leading-6 font-medium text-gray-900">About System</h3>
      </div>
      <div className="p-6">
        <div className="space-y-6">
          <div>
            <h3 className="text-sm font-medium text-gray-500">System Name</h3>
            <p className="mt-1 text-sm text-gray-900">Campus Copies ERP</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500">Version</h3>
            <p className="mt-1 text-sm text-gray-900">
              {initialData?.app_version || '1.0.0-draft'}
            </p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500">Environment</h3>
            <p className="mt-1 text-sm text-gray-900">
              <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">
                Production
              </span>
            </p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500">Backend API</h3>
            <p className="mt-1 text-sm text-gray-900">FastAPI / PostgreSQL</p>
          </div>
          <div className="pt-4 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">
              &copy; {new Date().getFullYear()} Campus Copies. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </Card>
  );
};

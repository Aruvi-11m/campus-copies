import React, { useState } from 'react';
import { PageHeader } from '../../components/common/PageHeader';
import { SettingsSidebar, SettingsTab } from './components/SettingsSidebar';
import { PricingSettingsForm } from './components/forms/PricingSettingsForm';
import { OrganizationSettingsForm } from './components/forms/OrganizationSettingsForm';
import { NotificationSettingsForm } from './components/forms/NotificationSettingsForm';
import { PrintSettingsForm } from './components/forms/PrintSettingsForm';
import { SecuritySettingsForm } from './components/forms/SecuritySettingsForm';
import { BackupSettingsForm } from './components/forms/BackupSettingsForm';
import { AboutSettings } from './components/forms/AboutSettings';
import { useSettings } from './hooks';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorBoundary } from 'react-error-boundary';
import { ErrorFallback } from '../../components/common/ErrorFallback';

export const SettingsPage = () => {
  const [activeTab, setActiveTab] = useState<SettingsTab>('pricing');
  const { data: settings, isLoading, isError, error, refetch } = useSettings();

  if (isLoading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <LoadingSpinner className="h-8 w-8 text-indigo-600" />
      </div>
    );
  }

  if (isError) {
    return (
      <ErrorFallback
        error={error instanceof Error ? error : new Error('Failed to load settings')}
        resetErrorBoundary={() => refetch()}
      />
    );
  }

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'pricing':
        return <PricingSettingsForm initialData={settings || {}} />;
      case 'organization':
        return <OrganizationSettingsForm initialData={settings || {}} />;
      case 'notifications':
        return <NotificationSettingsForm initialData={settings || {}} />;
      case 'printing':
        return <PrintSettingsForm initialData={settings || {}} />;
      case 'security':
        return <SecuritySettingsForm initialData={settings || {}} />;
      case 'backup':
        return <BackupSettingsForm initialData={settings || {}} />;
      case 'about':
        return <AboutSettings initialData={settings || {}} />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Settings"
        description="Manage application configuration, pricing, and administrative preferences."
      />

      <div className="flex flex-col md:flex-row gap-8">
        <aside className="w-full md:w-64 flex-shrink-0">
          <SettingsSidebar activeTab={activeTab} onTabChange={setActiveTab} />
        </aside>

        <main className="flex-1 max-w-4xl">
          <ErrorBoundary FallbackComponent={ErrorFallback} onReset={() => refetch()}>
            {renderActiveTab()}
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
};

export default SettingsPage;

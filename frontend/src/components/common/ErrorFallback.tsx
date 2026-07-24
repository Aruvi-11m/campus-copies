import React from 'react';
import { FallbackProps } from 'react-error-boundary';

/**
 * Standardized error boundary fallback.
 * Displays the error message and a retry button.
 */
export const ErrorFallback: React.FC<FallbackProps> = ({ error, resetErrorBoundary }) => {
  return (
    <div className="bg-red-50 p-6 rounded-lg border border-red-200">
      <h2 className="text-red-800 font-semibold mb-2">Something went wrong</h2>
      <pre className="text-xs text-red-600 mb-4 overflow-auto max-h-32 whitespace-pre-wrap">
        {error instanceof Error ? error.message : String(error)}
      </pre>
      <button
        onClick={resetErrorBoundary}
        className="inline-flex items-center rounded-md bg-red-100 px-3 py-2 text-sm font-medium text-red-800 hover:bg-red-200 transition-colors"
      >
        Try again
      </button>
    </div>
  );
};

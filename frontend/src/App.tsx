import React from 'react';

export const App: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full text-center">
        <h1 className="text-2xl font-bold text-blue-900 mb-2">Campus Copies ERP</h1>
        <p className="text-gray-600 text-sm mb-4">Phase 1 Foundation Shell Initialized</p>
        <span className="inline-block bg-green-100 text-green-800 px-3 py-1 rounded-full text-xs font-semibold">
          ● API Client & Setup Ready
        </span>
      </div>
    </div>
  );
};

export default App;

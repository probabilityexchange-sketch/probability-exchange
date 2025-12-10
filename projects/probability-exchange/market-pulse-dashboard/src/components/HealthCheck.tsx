import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { dflowClient } from '../lib/dflow-api-client';

export const HealthCheck: React.FC = () => {
  const { data, isError, error, isLoading } = useQuery({
    queryKey: ['dflowHealth'],
    queryFn: () => dflowClient.healthCheck(),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  if (isLoading) {
    return (
      <div className="w-full bg-blue-900/50 border-b border-blue-500/50 p-4 text-center">
        <span className="animate-pulse text-blue-200">Checking API connectivity...</span>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="w-full bg-red-900/80 border-b border-red-500 p-4 text-center">
        <div className="flex flex-col items-center gap-2">
          <span className="font-bold text-red-200 text-lg">⚠️ Backend Connection Error</span>
          <span className="text-red-300 text-sm">
            {error instanceof Error ? error.message : 'Unknown error occurred'}
          </span>
          <div className="text-xs text-red-400 mt-2 font-mono">
            Ensure backend is running on {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full bg-green-900/80 border-b border-green-500 p-4">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse" />
          <span className="font-bold text-green-100">System Operational</span>
        </div>

        <div className="flex flex-col text-xs text-green-200 font-mono text-right">
          <span>Service: {data?.service}</span>
          <span>Version: {data?.version}</span>
          <span>Chain: {data?.chain}</span>
          <span>Status: {data?.status}</span>
        </div>
      </div>

      {/* Debug Data Toggle (Optional) */}
      <details className="mt-2 text-xs text-green-300/50">
        <summary className="cursor-pointer hover:text-green-300">View Raw Response</summary>
        <pre className="mt-2 p-2 bg-black/50 rounded overflow-x-auto">
          {JSON.stringify(data, null, 2)}
        </pre>
      </details>
    </div>
  );
};

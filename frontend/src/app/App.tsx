import React from 'react';
import { RouterProvider } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '../contexts/AuthContext';
import { DemoModeProvider } from '../contexts/DemoModeContext';
import { ToastProvider } from '../contexts/ToastContext';
import { ErrorBoundary } from '../components/ui/ErrorBoundary';
import { router } from './routes';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000,
    },
  },
});

export const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <DemoModeProvider>
            <ToastProvider>
              <RouterProvider router={router} />
            </ToastProvider>
          </DemoModeProvider>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

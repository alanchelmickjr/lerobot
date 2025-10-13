import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { SnackbarProvider } from 'notistack';
import { Workbox } from 'workbox-window';
import App from './App';
import './styles/global.css';

// Initialize React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
    },
    mutations: {
      retry: 1,
    },
  },
});

// Service Worker Registration
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  const wb = new Workbox('/sw.js');

  wb.addEventListener('installed', (event) => {
    if (!event.isUpdate) {
      console.log('Service worker installed for the first time!');
    }
  });

  wb.addEventListener('waiting', () => {
    const shouldUpdate = window.confirm(
      'A new version is available! Click OK to update and refresh.'
    );
    if (shouldUpdate) {
      wb.addEventListener('controlling', () => {
        window.location.reload();
      });
      wb.messageSkipWaiting();
    }
  });

  wb.register();
}

// Hide loading screen
window.addEventListener('DOMContentLoaded', () => {
  const loadingScreen = document.getElementById('loading-screen');
  if (loadingScreen) {
    setTimeout(() => {
      loadingScreen.classList.add('fade-out');
      setTimeout(() => {
        loadingScreen.style.display = 'none';
      }, 300);
    }, 100);
  }
});

// Render the app
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <SnackbarProvider
        maxSnack={3}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'center',
        }}
        autoHideDuration={4000}
        preventDuplicate
        dense
        iconVariant={{
          success: '✓',
          error: '✕',
          warning: '⚠',
          info: 'ℹ',
        }}
      >
        <App />
      </SnackbarProvider>
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  </React.StrictMode>
);

// Enable hot module replacement in development
if (import.meta.hot) {
  import.meta.hot.accept();
}
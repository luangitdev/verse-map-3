/**
 * Next.js App Component
 * 
 * Global providers and initialization.
 */

import type { AppProps } from 'next/app';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuthStore } from '@/store/auth';
import Layout from '@/components/Layout';
import '@/styles/globals.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function MyApp({ Component, pageProps }: AppProps) {
  const router = useRouter();
  const { user, token, checkAuth, isLoading } = useAuthStore();

  // Check auth on mount
  useEffect(() => {
    checkAuth();
  }, []);

  // Redirect to login if not authenticated (except for login page)
  useEffect(() => {
    if (!isLoading && !token && router.pathname !== '/login') {
      router.push('/login');
    }
  }, [token, isLoading, router]);

  return (
    <QueryClientProvider client={queryClient}>
      <Layout>
        <Component {...pageProps} />
      </Layout>
    </QueryClientProvider>
  );
}

export default MyApp;

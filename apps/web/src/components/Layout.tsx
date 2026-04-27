/**
 * Main Layout Component
 * 
 * Provides navigation and common layout structure.
 */

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useAuthStore } from '@/store/auth';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  if (router.pathname === '/login' || router.pathname === '/live/[id]') {
    // Don't show layout for login and live pages
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      {/* Navigation */}
      <nav className="bg-slate-900 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">🎵</span>
            <span className="text-xl font-bold text-white">Music Analysis</span>
          </Link>

          <div className="flex items-center gap-6">
            <Link
              href="/library"
              className={`font-semibold transition ${
                router.pathname === '/library'
                  ? 'text-blue-400'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Library
            </Link>
            <Link
              href="/setlists"
              className={`font-semibold transition ${
                router.pathname === '/setlists' || router.pathname.startsWith('/setlists/')
                  ? 'text-blue-400'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Setlists
            </Link>

            {user && (
              <div className="flex items-center gap-4 border-l border-slate-700 pl-6">
                <div className="text-right">
                  <p className="text-white font-semibold">{user.name}</p>
                  <p className="text-slate-400 text-sm capitalize">{user.role}</p>
                </div>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded font-semibold transition"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main>{children}</main>
    </div>
  );
}

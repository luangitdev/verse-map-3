/**
 * Login Page
 * 
 * User authentication with email and password.
 */

import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { useAuthStore } from '@/store/auth';

export default function LoginPage() {
  const router = useRouter();
  const { login, error, isLoading } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [organizationId, setOrganizationId] = useState('');
  const [localError, setLocalError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError('');

    if (!email || !password || !organizationId) {
      setLocalError('Please fill in all fields');
      return;
    }

    try {
      await login(email, password, organizationId);
      router.push('/library');
    } catch (err: any) {
      setLocalError(err.message || 'Login failed');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-4">🎵</div>
          <h1 className="text-4xl font-bold text-white mb-2">Music Analysis</h1>
          <p className="text-slate-400">Sign in to your account</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-slate-700 rounded-lg p-8">
          {/* Error */}
          {(error || localError) && (
            <div className="mb-6 p-4 bg-red-900 text-red-200 rounded">
              {error || localError}
            </div>
          )}

          {/* Email */}
          <div className="mb-6">
            <label className="block text-white font-semibold mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 rounded bg-slate-600 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="your@email.com"
            />
          </div>

          {/* Password */}
          <div className="mb-6">
            <label className="block text-white font-semibold mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded bg-slate-600 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••••"
            />
          </div>

          {/* Organization ID */}
          <div className="mb-6">
            <label className="block text-white font-semibold mb-2">Organization ID</label>
            <input
              type="text"
              value={organizationId}
              onChange={(e) => setOrganizationId(e.target.value)}
              className="w-full px-4 py-3 rounded bg-slate-600 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="org-123456"
            />
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-semibold rounded transition"
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {/* Demo Info */}
        <div className="mt-8 p-4 bg-slate-700 rounded text-slate-400 text-sm">
          <p className="font-semibold mb-2">Demo Credentials:</p>
          <p>Email: demo@example.com</p>
          <p>Password: demo123</p>
          <p>Organization: demo-org</p>
        </div>
      </div>
    </div>
  );
}

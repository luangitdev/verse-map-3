/**
 * Setlist Manager Page
 * 
 * Create, edit, and manage setlists.
 */

import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { useAuthStore } from '@/store/auth';
import Link from 'next/link';

export default function SetlistsPage() {
  const { user } = useAuthStore();
  const [newSetlistName, setNewSetlistName] = useState('');

  // Fetch setlists
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['setlists', user?.organization_id],
    queryFn: () => {
      if (!user) throw new Error('Not authenticated');
      return apiClient.listSetlists(user.organization_id);
    },
    enabled: !!user,
  });

  // Create setlist mutation
  const createMutation = useMutation({
    mutationFn: (name: string) => apiClient.createSetlist(name),
    onSuccess: () => {
      setNewSetlistName('');
      refetch();
    },
  });

  if (!user) return <div>Please log in</div>;
  if (isLoading) return <div className="p-8">Loading setlists...</div>;

  const setlists = data?.items || [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Setlists</h1>
          <p className="text-slate-400">Create and manage worship setlists</p>
        </div>

        {/* Create New Setlist */}
        <div className="bg-slate-700 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-white mb-4">Create New Setlist</h2>
          <div className="flex gap-4">
            <input
              type="text"
              value={newSetlistName}
              onChange={(e) => setNewSetlistName(e.target.value)}
              placeholder="Setlist name (e.g., Sunday Service)"
              className="flex-1 px-4 py-3 rounded bg-slate-600 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={() => createMutation.mutate(newSetlistName)}
              disabled={!newSetlistName.trim() || createMutation.isPending}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-semibold rounded transition"
            >
              Create
            </button>
          </div>
        </div>

        {/* Setlists Grid */}
        {setlists.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-slate-400 text-lg">No setlists yet. Create your first one!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {setlists.map((setlist: any) => (
              <Link
                key={setlist.id}
                href={`/setlists/${setlist.id}`}
                className="group"
              >
                <div className="bg-slate-700 rounded-lg p-6 hover:bg-slate-600 transition cursor-pointer">
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-xl font-semibold text-white group-hover:text-blue-400">
                      {setlist.name}
                    </h3>
                    <span
                      className={`px-3 py-1 rounded text-sm font-semibold ${
                        setlist.status === 'executed'
                          ? 'bg-green-900 text-green-200'
                          : 'bg-blue-900 text-blue-200'
                      }`}
                    >
                      {setlist.status === 'executed' ? 'Executed' : 'Draft'}
                    </span>
                  </div>
                  <p className="text-slate-400 text-sm">
                    Created {new Date(setlist.created_at).toLocaleDateString()}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

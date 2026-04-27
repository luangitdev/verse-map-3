/**
 * Music Library Page
 * 
 * Browse and manage songs in the organization library.
 */

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient, Song } from '@/services/api';
import { useAuthStore } from '@/store/auth';
import Link from 'next/link';

export default function LibraryPage() {
  const { user } = useAuthStore();
  const [skip, setSkip] = useState(0);
  const limit = 20;

  const { data, isLoading, error } = useQuery({
    queryKey: ['songs', user?.organization_id, skip],
    queryFn: () => {
      if (!user) throw new Error('Not authenticated');
      return apiClient.listSongs(user.organization_id, skip, limit);
    },
    enabled: !!user,
  });

  if (!user) {
    return <div>Please log in</div>;
  }

  if (isLoading) {
    return <div className="p-8">Loading songs...</div>;
  }

  if (error) {
    return <div className="p-8 text-red-600">Error loading songs</div>;
  }

  const songs = data?.items || [];
  const total = data?.total || 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Music Library</h1>
          <p className="text-slate-400">
            {total} songs in your organization's library
          </p>
        </div>

        {/* Import Button */}
        <div className="mb-8">
          <Link
            href="/import"
            className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition"
          >
            + Import from YouTube
          </Link>
        </div>

        {/* Songs Grid */}
        {songs.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-slate-400 text-lg">No songs yet. Import your first song!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {songs.map((song: Song) => (
              <Link
                key={song.id}
                href={`/songs/${song.id}`}
                className="group"
              >
                <div className="bg-slate-700 rounded-lg p-6 hover:bg-slate-600 transition cursor-pointer">
                  <h3 className="text-xl font-semibold text-white mb-2 group-hover:text-blue-400">
                    {song.title}
                  </h3>
                  <p className="text-slate-400 mb-4">{song.artist}</p>
                  <div className="flex justify-between items-center text-sm text-slate-500">
                    <span>{Math.round(song.duration_seconds / 60)}m</span>
                    <span>{new Date(song.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}

        {/* Pagination */}
        {total > limit && (
          <div className="mt-8 flex justify-center gap-4">
            <button
              onClick={() => setSkip(Math.max(0, skip - limit))}
              disabled={skip === 0}
              className="px-4 py-2 bg-slate-700 text-white rounded disabled:opacity-50"
            >
              Previous
            </button>
            <span className="text-slate-400 py-2">
              {skip + 1} - {Math.min(skip + limit, total)} of {total}
            </span>
            <button
              onClick={() => setSkip(skip + limit)}
              disabled={skip + limit >= total}
              className="px-4 py-2 bg-slate-700 text-white rounded disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

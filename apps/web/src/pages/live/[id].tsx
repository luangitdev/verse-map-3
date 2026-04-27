/**
 * Live Mode Page
 * 
 * Stage presentation mode with large typography and navigation.
 */

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import { apiClient } from '@/services/api';

export default function LiveModePage() {
  const router = useRouter();
  const { id: setlistId } = router.query;
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isStarted, setIsStarted] = useState(false);

  // Fetch setlist
  const { data: setlist, isLoading } = useQuery({
    queryKey: ['setlist-live', setlistId],
    queryFn: () => {
      if (!setlistId) throw new Error('No setlist ID');
      return apiClient.getSetlist(setlistId as string);
    },
    enabled: !!setlistId,
  });

  // Fetch live status
  const { data: liveStatus } = useQuery({
    queryKey: ['live-status', setlistId],
    queryFn: () => {
      if (!setlistId) throw new Error('No setlist ID');
      return apiClient.getLiveStatus(setlistId as string);
    },
    enabled: !!setlistId && isStarted,
    refetchInterval: 1000, // Update every second
  });

  const handleStartLive = async () => {
    if (!setlistId) return;
    try {
      await apiClient.startLiveMode(setlistId as string);
      setIsStarted(true);
    } catch (error) {
      alert('Failed to start live mode');
    }
  };

  const handlePrevious = () => {
    setCurrentIndex(Math.max(0, currentIndex - 1));
  };

  const handleNext = () => {
    const items = setlist?.items || [];
    setCurrentIndex(Math.min(items.length - 1, currentIndex + 1));
  };

  if (isLoading) return <div className="p-8">Loading...</div>;
  if (!setlist) return <div className="p-8">Setlist not found</div>;

  const items = setlist.items || [];
  const currentItem = items[currentIndex];

  if (!isStarted) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-6xl font-bold text-white mb-8">{setlist.name}</h1>
          <p className="text-2xl text-slate-400 mb-8">{items.length} songs</p>
          <button
            onClick={handleStartLive}
            className="px-12 py-6 bg-red-600 hover:bg-red-700 text-white text-2xl font-bold rounded transition"
          >
            Start Live Mode
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white flex flex-col">
      {/* Current Song */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center">
          {currentItem ? (
            <>
              <p className="text-2xl text-slate-400 mb-4">
                Song {currentIndex + 1} of {items.length}
              </p>
              <h1 className="text-8xl font-bold mb-4">
                {currentItem.arrangement_id}
              </h1>
              <p className="text-4xl text-slate-300 mb-8">
                Key: {currentItem.key}
              </p>
              {currentItem.notes && (
                <p className="text-2xl text-slate-400">{currentItem.notes}</p>
              )}
            </>
          ) : (
            <p className="text-4xl text-slate-400">No songs in setlist</p>
          )}
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-slate-900 p-6 flex justify-between items-center">
        <button
          onClick={handlePrevious}
          disabled={currentIndex === 0}
          className="px-8 py-4 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 text-white text-xl font-bold rounded transition"
        >
          ← Previous
        </button>

        <div className="text-center">
          <p className="text-slate-400">
            {currentIndex + 1} / {items.length}
          </p>
        </div>

        <button
          onClick={handleNext}
          disabled={currentIndex === items.length - 1}
          className="px-8 py-4 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 text-white text-xl font-bold rounded transition"
        >
          Next →
        </button>

        <button
          onClick={() => router.back()}
          className="px-8 py-4 bg-red-600 hover:bg-red-700 text-white text-xl font-bold rounded transition"
        >
          Exit
        </button>
      </div>

      {/* Upcoming Songs */}
      <div className="bg-slate-800 p-4 max-h-32 overflow-y-auto">
        <p className="text-slate-400 font-semibold mb-2">Upcoming:</p>
        <div className="flex gap-4">
          {items.slice(currentIndex + 1, currentIndex + 4).map((item, idx) => (
            <div key={idx} className="bg-slate-700 px-4 py-2 rounded text-sm">
              {item.arrangement_id}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

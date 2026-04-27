/**
 * YouTube Import Page
 * 
 * Import songs from YouTube with real-time progress tracking.
 */

import React, { useState, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { apiClient, AnalysisStatus } from '@/services/api';
import { useAuthStore } from '@/store/auth';
import Link from 'next/link';

const PHASES = [
  { id: 'queued', label: 'Queued', icon: '⏳' },
  { id: 'extracting_metadata', label: 'Extracting Metadata', icon: '📥' },
  { id: 'fetching_text', label: 'Fetching Lyrics', icon: '📝' },
  { id: 'separating_sources', label: 'Separating Audio', icon: '🎵' },
  { id: 'analyzing_audio', label: 'Analyzing Audio', icon: '📊' },
  { id: 'postprocessing_structure', label: 'Processing Structure', icon: '🔧' },
  { id: 'ready', label: 'Ready', icon: '✅' },
];

export default function ImportPage() {
  const { user } = useAuthStore();
  const [url, setUrl] = useState('');
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [status, setStatus] = useState<AnalysisStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Import mutation
  const importMutation = useMutation({
    mutationFn: (youtubeUrl: string) => apiClient.importYoutube(youtubeUrl),
    onSuccess: (data) => {
      setAnalysisId(data.analysis_id);
      setError(null);
    },
    onError: (error: any) => {
      setError(error.message || 'Import failed');
    },
  });

  // Poll for status
  useEffect(() => {
    if (!analysisId) return;

    const interval = setInterval(async () => {
      try {
        const newStatus = await apiClient.getAnalysisStatus(analysisId);
        setStatus(newStatus);

        if (newStatus.phase === 'ready' || newStatus.phase === 'failed') {
          clearInterval(interval);
        }
      } catch (err) {
        console.error('Error polling status:', err);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }, [analysisId]);

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) {
      setError('Please enter a YouTube URL');
      return;
    }
    await importMutation.mutateAsync(url);
  };

  const currentPhaseIndex = PHASES.findIndex((p) => p.id === status?.phase) || 0;
  const progress = status?.progress || 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="max-w-2xl mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-2">Import from YouTube</h1>
          <p className="text-slate-400">
            Paste a YouTube URL to analyze the song
          </p>
        </div>

        {/* Import Form */}
        {!analysisId ? (
          <form onSubmit={handleImport} className="bg-slate-700 rounded-lg p-8 mb-8">
            <div className="mb-6">
              <label className="block text-white font-semibold mb-2">
                YouTube URL
              </label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                className="w-full px-4 py-3 rounded bg-slate-600 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-900 text-red-200 rounded">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={importMutation.isPending}
              className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-semibold rounded transition"
            >
              {importMutation.isPending ? 'Importing...' : 'Import Song'}
            </button>
          </form>
        ) : null}

        {/* Progress Tracking */}
        {analysisId && status && (
          <div className="bg-slate-700 rounded-lg p-8">
            <h2 className="text-2xl font-bold text-white mb-6">Analysis Progress</h2>

            {/* Phase Timeline */}
            <div className="mb-8">
              {PHASES.map((phase, index) => (
                <div key={phase.id} className="flex items-center mb-4">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold mr-4 ${
                      index < currentPhaseIndex
                        ? 'bg-green-600 text-white'
                        : index === currentPhaseIndex
                          ? 'bg-blue-600 text-white animate-pulse'
                          : 'bg-slate-600 text-slate-400'
                    }`}
                  >
                    {phase.icon}
                  </div>
                  <div>
                    <p
                      className={`font-semibold ${
                        index <= currentPhaseIndex ? 'text-white' : 'text-slate-400'
                      }`}
                    >
                      {phase.label}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Progress Bar */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-slate-400">Overall Progress</span>
                <span className="text-white font-semibold">{progress}%</span>
              </div>
              <div className="w-full bg-slate-600 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-blue-600 h-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            {/* Status Message */}
            <p className="text-slate-400 text-center mb-6">
              {status.message}
            </p>

            {/* Completion */}
            {status.phase === 'ready' && (
              <div className="text-center">
                <p className="text-green-400 font-semibold mb-4">✓ Analysis Complete!</p>
                <Link
                  href={`/songs/${status.song_id}`}
                  className="inline-block px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded transition"
                >
                  View Song Details
                </Link>
              </div>
            )}

            {status.phase === 'failed' && (
              <div className="text-center">
                <p className="text-red-400 font-semibold mb-4">✗ Analysis Failed</p>
                <button
                  onClick={() => {
                    setAnalysisId(null);
                    setStatus(null);
                    setUrl('');
                  }}
                  className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded transition"
                >
                  Try Again
                </button>
              </div>
            )}
          </div>
        )}

        {/* Back Link */}
        <div className="mt-8 text-center">
          <Link href="/library" className="text-blue-400 hover:text-blue-300">
            ← Back to Library
          </Link>
        </div>
      </div>
    </div>
  );
}

/**
 * Arrangement Editor Page
 * 
 * Edit sections, chords, and arrangement details.
 */

import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import { apiClient } from '@/services/api';
import { useAuthStore } from '@/store/auth';

export default function ArrangementEditorPage() {
  const router = useRouter();
  const { id: arrangementId } = router.query;
  const { user } = useAuthStore();
  const [sections, setSections] = useState<any[]>([]);
  const [chords, setChords] = useState<any[]>([]);
  const [key, setKey] = useState('');

  // Fetch arrangement
  const { data: arrangement, isLoading } = useQuery({
    queryKey: ['arrangement', arrangementId],
    queryFn: () => {
      if (!arrangementId) throw new Error('No arrangement ID');
      return apiClient.getArrangement(arrangementId as string);
    },
    enabled: !!arrangementId,
    onSuccess: (data) => {
      setSections(data.sections || []);
      setChords(data.chords || []);
      setKey(data.key);
    },
  });

  // Update sections mutation
  const updateSectionsMutation = useMutation({
    mutationFn: (newSections: any[]) => {
      if (!arrangementId) throw new Error('No arrangement ID');
      return apiClient.updateSections(arrangementId as string, newSections);
    },
    onSuccess: () => {
      alert('Sections updated successfully');
    },
  });

  // Update chords mutation
  const updateChordsMutation = useMutation({
    mutationFn: (newChords: any[]) => {
      if (!arrangementId) throw new Error('No arrangement ID');
      return apiClient.updateChords(arrangementId as string, newChords, key);
    },
    onSuccess: () => {
      alert('Chords updated successfully');
    },
  });

  // Publish mutation
  const publishMutation = useMutation({
    mutationFn: () => {
      if (!arrangementId) throw new Error('No arrangement ID');
      return apiClient.publishArrangement(arrangementId as string);
    },
    onSuccess: () => {
      alert('Arrangement published successfully');
      router.push('/library');
    },
  });

  if (isLoading) return <div className="p-8">Loading...</div>;
  if (!arrangement) return <div className="p-8">Arrangement not found</div>;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">{arrangement.name}</h1>
          <p className="text-slate-400">Key: {key} | Version: {arrangement.version}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Sections Editor */}
          <div className="bg-slate-700 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-white mb-4">Sections</h2>
            <div className="space-y-4">
              {sections.length === 0 ? (
                <p className="text-slate-400">No sections detected</p>
              ) : (
                sections.map((section, idx) => (
                  <div key={idx} className="bg-slate-600 p-4 rounded">
                    <input
                      type="text"
                      value={section.label || ''}
                      onChange={(e) => {
                        const newSections = [...sections];
                        newSections[idx].label = e.target.value;
                        setSections(newSections);
                      }}
                      className="w-full px-3 py-2 bg-slate-500 text-white rounded mb-2"
                      placeholder="Section name"
                    />
                    <div className="text-sm text-slate-400">
                      {section.type} • {section.start_time}s - {section.end_time}s
                    </div>
                  </div>
                ))
              )}
            </div>
            <button
              onClick={() => updateSectionsMutation.mutate(sections)}
              disabled={updateSectionsMutation.isPending}
              className="mt-4 w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-semibold"
            >
              Save Sections
            </button>
          </div>

          {/* Chords Editor */}
          <div className="bg-slate-700 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-white mb-4">Chords</h2>
            <div className="mb-4">
              <label className="block text-white font-semibold mb-2">Key</label>
              <input
                type="text"
                value={key}
                onChange={(e) => setKey(e.target.value)}
                className="w-full px-3 py-2 bg-slate-600 text-white rounded"
                placeholder="e.g., G major"
              />
            </div>
            <div className="space-y-2">
              {chords.length === 0 ? (
                <p className="text-slate-400">No chords detected</p>
              ) : (
                chords.slice(0, 5).map((chord, idx) => (
                  <div key={idx} className="flex justify-between items-center bg-slate-600 p-3 rounded">
                    <span className="text-white font-semibold">{chord.chord}</span>
                    <span className="text-slate-400 text-sm">{chord.time}s (confidence: {(chord.confidence * 100).toFixed(0)}%)</span>
                  </div>
                ))
              )}
            </div>
            <button
              onClick={() => updateChordsMutation.mutate(chords)}
              disabled={updateChordsMutation.isPending}
              className="mt-4 w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-semibold"
            >
              Save Chords
            </button>
          </div>
        </div>

        {/* Actions */}
        <div className="mt-8 flex gap-4">
          {!arrangement.published && (
            <button
              onClick={() => publishMutation.mutate()}
              disabled={publishMutation.isPending}
              className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded"
            >
              Publish Arrangement
            </button>
          )}
          <button
            onClick={() => router.back()}
            className="px-6 py-3 bg-slate-600 hover:bg-slate-700 text-white font-semibold rounded"
          >
            Back
          </button>
        </div>
      </div>
    </div>
  );
}

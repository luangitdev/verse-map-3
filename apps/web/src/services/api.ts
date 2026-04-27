/**
 * API Client Service
 * 
 * Centralized API communication with type safety and error handling.
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// Types
export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

export interface AnalysisStatus {
  analysis_id: string;
  song_id: string;
  phase: string;
  progress: number;
  status: string;
  message: string;
  started_at: string;
  estimated_completion?: string;
}

export interface Song {
  id: string;
  title: string;
  artist: string;
  duration_seconds: number;
  created_at: string;
  updated_at: string;
}

export interface Arrangement {
  id: string;
  song_id: string;
  name: string;
  key: string;
  published: boolean;
  version: number;
  created_at: string;
}

export interface Setlist {
  id: string;
  name: string;
  status: 'draft' | 'executed';
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface SetlistItem {
  id: string;
  arrangement_id: string;
  order: number;
  key: string;
  notes?: string;
  duration_seconds?: number;
  created_at: string;
}

// API Client
class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor(baseURL: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add token to requests
    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    // Handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => this.handleError(error),
    );
  }

  setToken(token: string | null) {
    this.token = token;
  }

  private handleError(error: AxiosError): Promise<never> {
    const apiError: ApiError = {
      code: 'UNKNOWN_ERROR',
      message: 'An unexpected error occurred',
    };

    if (error.response) {
      const data = error.response.data as any;
      apiError.code = data.code || `HTTP_${error.response.status}`;
      apiError.message = data.message || error.message;
      apiError.details = data.details;
    } else if (error.request) {
      apiError.code = 'NETWORK_ERROR';
      apiError.message = 'Network error. Please check your connection.';
    }

    return Promise.reject(apiError);
  }

  // Health
  async getHealth() {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Auth
  async login(email: string, password: string, organizationId: string) {
    const response = await this.client.post('/auth/login', {
      email,
      password,
      organization_id: organizationId,
    });
    return response.data;
  }

  async logout() {
    return this.client.post('/auth/logout');
  }

  async getCurrentUser() {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  // Songs
  async importYoutube(url: string, title?: string) {
    const response = await this.client.post('/songs/import-youtube', {
      url,
      title,
    });
    return response.data;
  }

  async getAnalysisStatus(analysisId: string): Promise<AnalysisStatus> {
    const response = await this.client.get(`/analyses/${analysisId}`);
    return response.data;
  }

  async getSong(songId: string): Promise<Song> {
    const response = await this.client.get(`/songs/${songId}`);
    return response.data;
  }

  async listSongs(organizationId: string, skip: number = 0, limit: number = 20) {
    const response = await this.client.get(`/organizations/${organizationId}/library`, {
      params: { skip, limit },
    });
    return response.data;
  }

  // Arrangements
  async createArrangement(songId: string, data: {
    name?: string;
    key?: string;
    sections?: any[];
    chords?: any;
    notes?: string;
  }) {
    const response = await this.client.post(`/songs/${songId}/arrangements`, data);
    return response.data;
  }

  async getArrangement(arrangementId: string): Promise<Arrangement> {
    const response = await this.client.get(`/arrangements/${arrangementId}`);
    return response.data;
  }

  async updateSections(arrangementId: string, sections: any[]) {
    const response = await this.client.patch(`/arrangements/${arrangementId}/sections`, {
      sections,
    });
    return response.data;
  }

  async updateChords(arrangementId: string, chords: any[], newKey?: string) {
    const response = await this.client.patch(`/arrangements/${arrangementId}/chords`, {
      chords,
      new_key: newKey,
    });
    return response.data;
  }

  async publishArrangement(arrangementId: string) {
    const response = await this.client.post(`/arrangements/${arrangementId}/publish`);
    return response.data;
  }

  async listArrangements(songId: string) {
    const response = await this.client.get(`/songs/${songId}/arrangements`);
    return response.data;
  }

  // Setlists
  async createSetlist(name: string): Promise<Setlist> {
    const response = await this.client.post('/setlists', { name });
    return response.data;
  }

  async getSetlist(setlistId: string) {
    const response = await this.client.get(`/setlists/${setlistId}`);
    return response.data;
  }

  async addSetlistItem(setlistId: string, data: {
    arrangement_id: string;
    key: string;
    notes?: string;
    duration_seconds?: number;
  }) {
    const response = await this.client.post(`/setlists/${setlistId}/items`, data);
    return response.data;
  }

  async updateSetlistItem(itemId: string, data: {
    order?: number;
    key?: string;
    notes?: string;
  }) {
    const response = await this.client.patch(`/setlist-items/${itemId}`, data);
    return response.data;
  }

  async startLiveMode(setlistId: string) {
    const response = await this.client.post(`/setlists/${setlistId}/live/start`);
    return response.data;
  }

  async getLiveStatus(setlistId: string) {
    const response = await this.client.get(`/setlists/${setlistId}/live/status`);
    return response.data;
  }

  async listSetlists(organizationId: string, skip: number = 0, limit: number = 20) {
    const response = await this.client.get(`/organizations/${organizationId}/setlists`, {
      params: { skip, limit },
    });
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

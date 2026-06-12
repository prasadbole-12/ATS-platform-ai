/**
 * src/services/rankingService.ts
 * API service for rankings and ML pipeline operations.
 */

import apiClient from './api'
import { Ranking, DashboardStats } from '@/types'

export const rankingService = {
  getAll: async (): Promise<Ranking[]> => {
    const response = await apiClient.get<Ranking[]>('/rankings')
    return response.data
  },

  getByJobId: async (jobId: string): Promise<Ranking[]> => {
    const response = await apiClient.get<Ranking[]>(`/rankings/job/${jobId}`)
    return response.data
  },

  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await apiClient.get<DashboardStats>('/dashboard/stats')
    return response.data
  },

  seedMockData: async (): Promise<{ message: string; candidates: number; jobs: number; rankings: number }> => {
    const response = await apiClient.post('/seed', {})
    return response.data
  },

  // ── ML Pipeline ──────────────────────────────────────────────────────────

  /** Run ML ranking for a specific job — scores all candidates */
  runRankingForJob: async (jobId: string): Promise<Ranking[]> => {
    const response = await apiClient.post<Ranking[]>(`/ml/rank/job/${jobId}`)
    return response.data
  },

  /** Run ML ranking for ALL active jobs */
  runRankingForAll: async (): Promise<{ status: string; jobs_processed: number; total_rankings: number }> => {
    const response = await apiClient.post('/ml/rank/all')
    return response.data
  },

  /** Score a single candidate against a single job */
  scoreSingle: async (candidateId: string, jobId: string): Promise<Ranking> => {
    const response = await apiClient.get<Ranking>(`/ml/score/${candidateId}/${jobId}`)
    return response.data
  },

  /** Get TF-IDF engine status */
  getEngineStatus: async (): Promise<{ tfidf_fitted: boolean; vocab_size: number; weights: Record<string, string> }> => {
    const response = await apiClient.get('/ml/engine/status')
    return response.data
  },
}

/**
 * src/services/candidateService.ts
 *
 * API service for candidate-related operations.
 */

import apiClient from './api'
import { Candidate, CandidateListResponse } from '@/types'

export const candidateService = {
  /**
   * Upload a resume file and create a candidate
   */
  uploadResume: async (file: File): Promise<Candidate> => {
    const formData = new FormData()
    formData.append('file', file)

    const response = await apiClient.post<Candidate>('/upload-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  /**
   * Fetch paginated list of candidates with optional search/filter
   */
  listCandidates: async (
    page: number = 1,
    per_page: number = 20,
    search?: string,
    status?: string,
  ): Promise<CandidateListResponse> => {
    const response = await apiClient.get<CandidateListResponse>('/candidates', {
      params: { page, per_page, search, status },
    })
    return response.data
  },

  /**
   * Fetch a single candidate by ID
   */
  getCandidate: async (candidateId: string): Promise<Candidate> => {
    const response = await apiClient.get<Candidate>(`/candidates/${candidateId}`)
    return response.data
  },

  /**
   * Update candidate details
   */
  updateCandidate: async (
    candidateId: string,
    data: Partial<Candidate>,
  ): Promise<Candidate> => {
    const response = await apiClient.patch<Candidate>(`/candidates/${candidateId}`, data)
    return response.data
  },

  /**
   * Delete a candidate
   */
  deleteCandidate: async (candidateId: string): Promise<void> => {
    await apiClient.delete(`/candidates/${candidateId}`)
  },
}

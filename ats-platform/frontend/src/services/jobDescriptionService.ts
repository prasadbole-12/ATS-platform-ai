/**
 * src/services/jobDescriptionService.ts
 *
 * API service for job description-related operations.
 */

import apiClient from './api'
import { JobDescription, JobDescriptionListResponse } from '@/types'

export const jobDescriptionService = {
  /**
   * Create a new job description
   */
  create: async (data: Partial<JobDescription>): Promise<JobDescription> => {
    const response = await apiClient.post<JobDescription>('/job-description', data)
    return response.data
  },

  /**
   * Fetch all job descriptions
   */
  list: async (activeOnly: boolean = false): Promise<JobDescriptionListResponse> => {
    const response = await apiClient.get<JobDescriptionListResponse>(
      '/job-descriptions',
      { params: { active_only: activeOnly } },
    )
    return response.data
  },

  /**
   * Fetch a single job description by ID
   */
  getById: async (jdId: string): Promise<JobDescription> => {
    const response = await apiClient.get<JobDescription>(`/job-descriptions/${jdId}`)
    return response.data
  },

  /**
   * Update a job description
   */
  update: async (
    jdId: string,
    data: Partial<JobDescription>,
  ): Promise<JobDescription> => {
    const response = await apiClient.patch<JobDescription>(
      `/job-descriptions/${jdId}`,
      data,
    )
    return response.data
  },

  /**
   * Delete a job description
   */
  delete: async (jdId: string): Promise<void> => {
    await apiClient.delete(`/job-descriptions/${jdId}`)
  },
}

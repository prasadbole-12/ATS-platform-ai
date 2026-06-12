/**
 * src/hooks/queries.ts
 *
 * React Query hooks for API data fetching and caching.
 * These wrap the service functions and add automatic refetching, caching, etc.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { candidateService } from '@/services/candidateService'
import { jobDescriptionService } from '@/services/jobDescriptionService'
import { rankingService } from '@/services/rankingService'
import { Candidate, JobDescription, Ranking, DashboardStats, CandidateListResponse, JobDescriptionListResponse } from '@/types'

// ============================================================================
// Candidate Queries
// ============================================================================

export const useCandidates = (
  page: number = 1,
  per_page: number = 20,
  search?: string,
  status?: string,
) => {
  return useQuery({
    queryKey: ['candidates', page, per_page, search, status],
    queryFn: () => candidateService.listCandidates(page, per_page, search, status),
    staleTime: 30000, // 30 seconds
  })
}

export const useCandidate = (candidateId: string | null) => {
  return useQuery({
    queryKey: ['candidate', candidateId],
    queryFn: () => candidateService.getCandidate(candidateId!),
    enabled: !!candidateId,
    staleTime: 30000,
  })
}

export const useUploadResume = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (file: File) => candidateService.uploadResume(file),
    onSuccess: () => {
      // Invalidate candidates list so it refetches
      queryClient.invalidateQueries({ queryKey: ['candidates'] })
    },
  })
}

export const useUpdateCandidate = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ candidateId, data }: { candidateId: string; data: Partial<Candidate> }) =>
      candidateService.updateCandidate(candidateId, data),
    onSuccess: (data) => {
      queryClient.setQueryData(['candidate', data.id], data)
      queryClient.invalidateQueries({ queryKey: ['candidates'] })
    },
  })
}

export const useDeleteCandidate = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (candidateId: string) => candidateService.deleteCandidate(candidateId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates'] })
    },
  })
}

// ============================================================================
// Job Description Queries
// ============================================================================

export const useJobDescriptions = (activeOnly: boolean = false) => {
  return useQuery({
    queryKey: ['job_descriptions', activeOnly],
    queryFn: () => jobDescriptionService.list(activeOnly),
    staleTime: 30000,
  })
}

export const useJobDescription = (jdId: string | null) => {
  return useQuery({
    queryKey: ['job_description', jdId],
    queryFn: () => jobDescriptionService.getById(jdId!),
    enabled: !!jdId,
    staleTime: 30000,
  })
}

export const useCreateJobDescription = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<JobDescription>) => jobDescriptionService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job_descriptions'] })
    },
  })
}

export const useUpdateJobDescription = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ jdId, data }: { jdId: string; data: Partial<JobDescription> }) =>
      jobDescriptionService.update(jdId, data),
    onSuccess: (data) => {
      queryClient.setQueryData(['job_description', data.id], data)
      queryClient.invalidateQueries({ queryKey: ['job_descriptions'] })
    },
  })
}

// ============================================================================
// Ranking Queries
// ============================================================================

export const useAllRankings = () => {
  return useQuery({
    queryKey: ['rankings'],
    queryFn: () => rankingService.getAll(),
    staleTime: 30000,
  })
}

export const useRankingsByJob = (jobId: string | null) => {
  return useQuery({
    queryKey: ['rankings', jobId],
    queryFn: () => rankingService.getByJobId(jobId!),
    enabled: !!jobId,
    staleTime: 30000,
  })
}

export const useDashboardStats = () => {
  return useQuery({
    queryKey: ['dashboard_stats'],
    queryFn: () => rankingService.getDashboardStats(),
    staleTime: 30000,
  })
}

export const useSeedMockData = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => rankingService.seedMockData(),
    onSuccess: () => {
      queryClient.invalidateQueries()
    },
  })
}

// ============================================================================
// ML Pipeline Mutations
// ============================================================================

export const useRunRankingForJob = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (jobId: string) => rankingService.runRankingForJob(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rankings'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard_stats'] })
    },
  })
}

export const useRunRankingForAll = () => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => rankingService.runRankingForAll(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rankings'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard_stats'] })
    },
  })
}

export const useEngineStatus = () => {
  return useQuery({
    queryKey: ['engine_status'],
    queryFn: () => rankingService.getEngineStatus(),
    staleTime: 10000,
  })
}

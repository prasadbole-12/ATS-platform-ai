/**
 * src/types/index.ts
 *
 * Shared TypeScript types across the frontend.
 * These match the Pydantic schemas from the backend.
 */

export interface Candidate {
  id: string
  name: string
  email: string
  phone?: string
  skills?: string
  status: 'new' | 'reviewed' | 'shortlisted' | 'rejected'
  resume_text?: string
  resume_file_name?: string
  created_at: string
  updated_at: string
}

export interface JobDescription {
  id: string
  title: string
  department?: string
  location?: string
  description: string
  required_skills?: string
  experience_years?: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Ranking {
  id: string
  rank_position?: number
  score?: number
  skill_match_score?: number
  semantic_score?: number
  experience_score?: number
  score_explanation?: string
  scored_at: string
  candidate_id: string
  candidate_name: string
  candidate_email: string
  candidate_skills?: string
  job_id: string
  job_title: string
}

export interface DashboardStats {
  total_candidates: number
  candidates_by_status: Record<string, number>
  total_job_descriptions: number
  active_job_descriptions: number
  average_ats_score: number
}

export interface CandidateListResponse {
  items: Candidate[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface JobDescriptionListResponse {
  items: JobDescription[]
  total: number
}

import { useState } from 'react'
import { Search, Filter, UserPlus, Trash2, Eye, Users } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { CandidateDrawer } from '@/components/shared/CandidateDrawer'
import { EmptyState } from '@/components/shared/EmptyState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Skeleton } from '@/components/ui/skeleton'
import { useCandidates, useDeleteCandidate } from '@/hooks/queries'
import { Candidate } from '@/types'
import { formatDate } from '@/lib/utils'
import { useNavigate } from 'react-router-dom'

const STATUS_OPTIONS = [
  { value: '', label: 'All Statuses' },
  { value: 'new', label: 'New' },
  { value: 'reviewed', label: 'Reviewed' },
  { value: 'shortlisted', label: 'Shortlisted' },
  { value: 'rejected', label: 'Rejected' },
]

const PER_PAGE_OPTIONS = [
  { value: '10', label: '10 / page' },
  { value: '20', label: '20 / page' },
  { value: '50', label: '50 / page' },
]

export default function CandidatesPage() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [status, setStatus] = useState('')
  const [page, setPage] = useState(1)
  const [perPage, setPerPage] = useState(20)
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null)
  const [drawerOpen, setDrawerOpen] = useState(false)

  const { data, isLoading, isError, refetch } = useCandidates(page, perPage, search || undefined, status || undefined)
  const deleteMutation = useDeleteCandidate()

  const handleSearch = () => {
    setSearch(searchInput)
    setPage(1)
  }

  const handleOpenDrawer = (candidate: Candidate) => {
    setSelectedCandidate(candidate)
    setDrawerOpen(true)
  }

  const handleDelete = (e: React.MouseEvent, candidateId: string) => {
    e.stopPropagation()
    if (confirm('Delete this candidate? This cannot be undone.')) {
      deleteMutation.mutate(candidateId)
    }
  }

  const candidates = data?.items ?? []
  const total = data?.total ?? 0
  const pages = data?.pages ?? 1

  return (
    <>
      <div className="space-y-5">
        {/* Header */}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-sm font-medium text-muted-foreground">
              {isLoading ? '...' : `${total} candidate${total !== 1 ? 's' : ''} found`}
            </h2>
          </div>
          <Button size="sm" onClick={() => navigate('/upload')}>
            <UserPlus className="mr-2 h-3.5 w-3.5" />
            Add Candidate
          </Button>
        </div>

        {/* Filters */}
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="relative flex-1 max-w-xs">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground pointer-events-none" />
            <Input
              placeholder="Search name, email, skills…"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="pl-8 h-9 text-sm"
            />
          </div>
          <Button variant="outline" size="sm" onClick={handleSearch} className="shrink-0">
            <Search className="mr-2 h-3.5 w-3.5" />
            Search
          </Button>
          <Select
            options={STATUS_OPTIONS}
            value={status}
            onChange={(e) => { setStatus(e.target.value); setPage(1) }}
            className="w-40 h-9 text-sm"
          />
          <Select
            options={PER_PAGE_OPTIONS}
            value={String(perPage)}
            onChange={(e) => { setPerPage(Number(e.target.value)); setPage(1) }}
            className="w-32 h-9 text-sm"
          />
        </div>

        {/* Table */}
        <div className="rounded-xl border border-border bg-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-muted/40">
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                    Candidate
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-muted-foreground hidden md:table-cell">
                    Contact
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-muted-foreground hidden lg:table-cell">
                    Skills
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-muted-foreground hidden sm:table-cell">
                    Added
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {isLoading ? (
                  Array.from({ length: 8 }).map((_, i) => (
                    <tr key={i}>
                      {Array.from({ length: 6 }).map((_, j) => (
                        <td key={j} className="px-4 py-3">
                          <Skeleton className="h-4 w-full" />
                        </td>
                      ))}
                    </tr>
                  ))
                ) : isError ? (
                  <tr>
                    <td colSpan={6} className="py-12">
                      <ErrorState onRetry={refetch} />
                    </td>
                  </tr>
                ) : candidates.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-12">
                      <EmptyState
                        icon={Users}
                        title="No candidates found"
                        description="Upload some resumes or seed mock data from the dashboard."
                        action={{ label: 'Upload Resume', onClick: () => navigate('/upload') }}
                      />
                    </td>
                  </tr>
                ) : (
                  candidates.map((candidate) => (
                    <tr
                      key={candidate.id}
                      onClick={() => handleOpenDrawer(candidate)}
                      className="hover:bg-muted/30 cursor-pointer transition-colors"
                    >
                      {/* Name + avatar */}
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary font-semibold text-xs">
                            {candidate.name.charAt(0)}
                          </div>
                          <div>
                            <p className="font-medium text-foreground leading-tight">{candidate.name}</p>
                            {candidate.resume_file_name && (
                              <p className="text-xs text-muted-foreground truncate max-w-[150px]">
                                {candidate.resume_file_name}
                              </p>
                            )}
                          </div>
                        </div>
                      </td>

                      {/* Contact */}
                      <td className="px-4 py-3 hidden md:table-cell">
                        <p className="text-foreground">{candidate.email}</p>
                        {candidate.phone && (
                          <p className="text-xs text-muted-foreground">{candidate.phone}</p>
                        )}
                      </td>

                      {/* Skills */}
                      <td className="px-4 py-3 hidden lg:table-cell">
                        {candidate.skills ? (
                          <div className="flex flex-wrap gap-1 max-w-xs">
                            {candidate.skills
                              .split(',')
                              .slice(0, 3)
                              .map((s) => (
                                <span
                                  key={s}
                                  className="inline-flex items-center rounded bg-secondary px-1.5 py-0.5 text-xs text-secondary-foreground"
                                >
                                  {s.trim()}
                                </span>
                              ))}
                            {candidate.skills.split(',').length > 3 && (
                              <span className="text-xs text-muted-foreground">
                                +{candidate.skills.split(',').length - 3}
                              </span>
                            )}
                          </div>
                        ) : (
                          <span className="text-xs text-muted-foreground">—</span>
                        )}
                      </td>

                      {/* Status */}
                      <td className="px-4 py-3">
                        <StatusBadge status={candidate.status} />
                      </td>

                      {/* Date */}
                      <td className="px-4 py-3 text-sm text-muted-foreground hidden sm:table-cell">
                        {formatDate(candidate.created_at)}
                      </td>

                      {/* Actions */}
                      <td className="px-4 py-3 text-right" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-end gap-1">
                          <button
                            onClick={() => handleOpenDrawer(candidate)}
                            className="p-1.5 rounded hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
                          >
                            <Eye className="h-3.5 w-3.5" />
                          </button>
                          <button
                            onClick={(e) => handleDelete(e, candidate.id)}
                            className="p-1.5 rounded hover:bg-red-50 text-muted-foreground hover:text-red-500 transition-colors"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {!isLoading && pages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 border-t border-border">
              <p className="text-xs text-muted-foreground">
                Page {page} of {pages} · {total} total
              </p>
              <div className="flex gap-1.5">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="h-8 px-3 text-xs"
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.min(pages, p + 1))}
                  disabled={page === pages}
                  className="h-8 px-3 text-xs"
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Candidate drawer */}
      <CandidateDrawer
        candidate={selectedCandidate}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />
    </>
  )
}

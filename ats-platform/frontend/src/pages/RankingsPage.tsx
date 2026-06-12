import { useState } from 'react'
import { Trophy, Filter, Zap, RefreshCw, CheckCircle2 } from 'lucide-react'
import { Select } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { ScoreRing } from '@/components/shared/ScoreRing'
import { EmptyState } from '@/components/shared/EmptyState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Skeleton } from '@/components/ui/skeleton'
import { useAllRankings, useJobDescriptions, useRunRankingForJob, useRunRankingForAll, useEngineStatus } from '@/hooks/queries'
import { cn } from '@/lib/utils'

function RankBadge({ rank }: { rank: number }) {
  const medals: Record<number, { icon: string; className: string }> = {
    1: { icon: '🥇', className: 'bg-amber-50 text-amber-700 border-amber-200' },
    2: { icon: '🥈', className: 'bg-slate-50 text-slate-600 border-slate-200' },
    3: { icon: '🥉', className: 'bg-orange-50 text-orange-700 border-orange-200' },
  }
  const m = medals[rank]
  if (m) return (
    <span className={cn('inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-semibold', m.className)}>
      {m.icon} #{rank}
    </span>
  )
  return (
    <span className="inline-flex items-center rounded-full border border-border bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground">
      #{rank}
    </span>
  )
}

function ScoreBar({ label, value }: { label: string; value: number | null | undefined }) {
  if (value === null || value === undefined) return null
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between">
        <span className="text-xs text-muted-foreground">{label}</span>
        <span className="text-xs font-semibold text-foreground">{Math.round(value)}%</span>
      </div>
      <Progress value={value} />
    </div>
  )
}

export default function RankingsPage() {
  const [jobFilter, setJobFilter] = useState('')
  const [expanded, setExpanded] = useState<string | null>(null)

  const { data: rankings, isLoading, isError, refetch } = useAllRankings()
  const { data: jobsData } = useJobDescriptions()
  const { data: engineStatus } = useEngineStatus()
  const runForJobMutation = useRunRankingForJob()
  const runAllMutation = useRunRankingForAll()

  const jobOptions = [
    { value: '', label: 'All Jobs' },
    ...(jobsData?.items ?? []).map((j) => ({ value: j.id, label: j.title })),
  ]

  const filtered = (rankings ?? []).filter((r) => jobFilter ? r.job_id === jobFilter : true)
  const sorted = [...filtered].sort((a, b) => (b.score ?? 0) - (a.score ?? 0))

  const handleRunML = () => {
    if (jobFilter) {
      runForJobMutation.mutate(jobFilter)
    } else {
      runAllMutation.mutate()
    }
  }

  const isRunning = runForJobMutation.isPending || runAllMutation.isPending

  return (
    <div className="space-y-5">
      {/* ML Engine status bar */}
      <div className="rounded-xl border border-border bg-card px-5 py-3 flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2">
          <div className={cn('h-2 w-2 rounded-full', engineStatus?.tfidf_fitted ? 'bg-emerald-500' : 'bg-amber-400')} />
          <span className="text-xs text-muted-foreground">
            TF-IDF Engine: {engineStatus?.tfidf_fitted ? `Ready · ${engineStatus.vocab_size.toLocaleString()} terms` : 'Not fitted'}
          </span>
        </div>
        <div className="hidden sm:flex items-center gap-3 text-xs text-muted-foreground">
          <span>Skills 45%</span><span>·</span>
          <span>Semantic 35%</span><span>·</span>
          <span>Experience 20%</span>
        </div>
      </div>

      {/* Header + controls */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-muted-foreground">
          {isLoading ? '…' : `${filtered.length} ranking${filtered.length !== 1 ? 's' : ''}`}
        </p>
        <div className="flex items-center gap-2 flex-wrap">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <Select
            options={jobOptions}
            value={jobFilter}
            onChange={(e) => setJobFilter(e.target.value)}
            className="w-48 h-9 text-sm"
          />
          <Button
            size="sm"
            onClick={handleRunML}
            disabled={isRunning}
            className="gap-2"
          >
            {isRunning
              ? <><RefreshCw className="h-3.5 w-3.5 animate-spin" />Running…</>
              : <><Zap className="h-3.5 w-3.5" />Run ML Ranking</>
            }
          </Button>
        </div>
      </div>

      {(runForJobMutation.isSuccess || runAllMutation.isSuccess) && (
        <div className="flex items-center gap-2 rounded-lg bg-emerald-50 border border-emerald-200 px-4 py-2.5 text-sm text-emerald-700">
          <CheckCircle2 className="h-4 w-4" />
          ML ranking complete. Results updated with real ATS scores.
        </div>
      )}

      {/* Rankings table */}
      <div className="rounded-xl border border-border bg-card overflow-hidden">
        {isLoading ? (
          <div className="p-4 space-y-3">
            {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-16 rounded-lg" />)}
          </div>
        ) : isError ? (
          <ErrorState onRetry={refetch} />
        ) : sorted.length === 0 ? (
          <EmptyState
            icon={Trophy}
            title="No rankings yet"
            description="Click 'Run ML Ranking' to score all candidates against job descriptions."
            action={{ label: 'Run ML Ranking', onClick: handleRunML }}
          />
        ) : (
          <>
            <div className="hidden sm:grid grid-cols-12 px-5 py-3 border-b border-border bg-muted/40">
              <div className="col-span-1 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Rank</div>
              <div className="col-span-4 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Candidate</div>
              <div className="col-span-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground hidden lg:block">Job</div>
              <div className="col-span-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">ATS Score</div>
              <div className="col-span-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground hidden md:block">Skill Match</div>
            </div>

            <ul className="divide-y divide-border">
              {sorted.map((r, idx) => {
                const rank = r.rank_position ?? idx + 1
                const isExpanded = expanded === r.id

                return (
                  <li key={r.id}>
                    <div
                      className="grid grid-cols-12 items-center px-5 py-4 hover:bg-muted/30 cursor-pointer transition-colors"
                      onClick={() => setExpanded(isExpanded ? null : r.id)}
                    >
                      <div className="col-span-2 sm:col-span-1"><RankBadge rank={rank} /></div>

                      <div className="col-span-10 sm:col-span-4 flex items-center gap-3">
                        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary font-semibold text-sm">
                          {r.candidate_name.charAt(0)}
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-semibold text-foreground truncate">{r.candidate_name}</p>
                          <p className="text-xs text-muted-foreground truncate">{r.candidate_email}</p>
                        </div>
                      </div>

                      <div className="hidden lg:block lg:col-span-3">
                        <p className="text-sm text-foreground truncate">{r.job_title}</p>
                      </div>

                      <div className="hidden sm:flex sm:col-span-2 items-center gap-2">
                        <ScoreRing score={r.score ?? 0} size="sm" showLabel={false} />
                        <span className="text-sm font-bold text-foreground">{Math.round(r.score ?? 0)}%</span>
                      </div>

                      <div className="hidden md:block md:col-span-2 pr-4">
                        <Progress value={r.skill_match_score ?? 0} />
                        <p className="mt-1 text-xs text-muted-foreground text-right">{Math.round(r.skill_match_score ?? 0)}%</p>
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="px-5 pb-5 bg-muted/20 border-t border-border">
                        <div className="pt-4 grid gap-5 sm:grid-cols-2">
                          <div className="space-y-3">
                            <h4 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">Score Breakdown</h4>
                            <ScoreBar label="Overall ATS Score" value={r.score} />
                            <ScoreBar label="Skill Match (45%)" value={r.skill_match_score} />
                            <ScoreBar label="Semantic / TF-IDF (35%)" value={r.semantic_score} />
                            <ScoreBar label="Experience Match (20%)" value={r.experience_score} />
                          </div>
                          <div className="space-y-3">
                            <h4 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">Details</h4>
                            <div className="space-y-2">
                              {r.candidate_skills && (
                                <div className="flex items-start gap-2 text-sm">
                                  <span className="text-muted-foreground w-20 shrink-0">Skills:</span>
                                  <div className="flex flex-wrap gap-1">
                                    {r.candidate_skills.split(',').slice(0, 6).map((s) => (
                                      <span key={s} className="rounded bg-secondary px-1.5 py-0.5 text-xs text-secondary-foreground">{s.trim()}</span>
                                    ))}
                                    {r.candidate_skills.split(',').length > 6 && (
                                      <span className="text-xs text-muted-foreground">+{r.candidate_skills.split(',').length - 6} more</span>
                                    )}
                                  </div>
                                </div>
                              )}
                              {r.score_explanation && (
                                <div className="flex items-start gap-2 text-sm">
                                  <span className="text-muted-foreground w-20 shrink-0 mt-0.5">Analysis:</span>
                                  <p className="text-foreground text-xs leading-relaxed">{r.score_explanation}</p>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </li>
                )
              })}
            </ul>
          </>
        )}
      </div>
    </div>
  )
}

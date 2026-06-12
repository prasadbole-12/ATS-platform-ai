import { Users, Briefcase, Trophy, TrendingUp, Clock, CheckCircle, Eye, XCircle } from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import { StatsCard } from '@/components/shared/StatsCard'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { ScoreRing } from '@/components/shared/ScoreRing'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorState } from '@/components/shared/ErrorState'
import { EmptyState } from '@/components/shared/EmptyState'
import { Button } from '@/components/ui/button'
import { useDashboardStats, useAllRankings, useCandidates, useSeedMockData } from '@/hooks/queries'
import { formatDate } from '@/lib/utils'

const PIE_COLORS = ['#3b82f6', '#f59e0b', '#10b981', '#ef4444']

const SCORE_DISTRIBUTION = [
  { range: '0–20', count: 0 },
  { range: '21–40', count: 0 },
  { range: '41–60', count: 0 },
  { range: '61–80', count: 0 },
  { range: '81–100', count: 0 },
]

export default function DashboardPage() {
  const statsQuery = useDashboardStats()
  const rankingsQuery = useAllRankings()
  const candidatesQuery = useCandidates(1, 5)
  const seedMutation = useSeedMockData()

  const stats = statsQuery.data
  const topRankings = (rankingsQuery.data ?? []).slice(0, 5)
  const recentCandidates = candidatesQuery.data?.items ?? []

  // Build score distribution from rankings data
  const distribution = [...SCORE_DISTRIBUTION]
  if (rankingsQuery.data) {
    rankingsQuery.data.forEach((r) => {
      const s = r.score ?? 0
      if (s <= 20) distribution[0].count++
      else if (s <= 40) distribution[1].count++
      else if (s <= 60) distribution[2].count++
      else if (s <= 80) distribution[3].count++
      else distribution[4].count++
    })
  }

  // Build pie data from status breakdown
  const pieData = stats
    ? Object.entries(stats.candidates_by_status).map(([status, count]) => ({
        name: status.charAt(0).toUpperCase() + status.slice(1),
        value: count,
      }))
    : []

  const isLoading = statsQuery.isLoading || rankingsQuery.isLoading

  if (statsQuery.isError) {
    return (
      <ErrorState
        message="Could not load dashboard. Make sure the backend is running and mock data is seeded."
        onRetry={() => statsQuery.refetch()}
      />
    )
  }

  return (
    <div className="space-y-6">
      {/* Seed Button (dev only) */}
      <div className="flex items-center justify-between">
        <div />
        <Button
          variant="outline"
          size="sm"
          onClick={() => seedMutation.mutate()}
          disabled={seedMutation.isPending}
        >
          {seedMutation.isPending ? 'Seeding...' : '⚡ Seed Mock Data'}
        </Button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-xl" />
          ))
        ) : (
          <>
            <StatsCard
              title="Total Candidates"
              value={stats?.total_candidates ?? 0}
              subtitle="All uploaded resumes"
              icon={Users}
              iconColor="text-blue-600"
              iconBg="bg-blue-50"
            />
            <StatsCard
              title="Active Jobs"
              value={stats?.active_job_descriptions ?? 0}
              subtitle={`of ${stats?.total_job_descriptions ?? 0} total`}
              icon={Briefcase}
              iconColor="text-violet-600"
              iconBg="bg-violet-50"
            />
            <StatsCard
              title="Avg. ATS Score"
              value={`${stats?.average_ats_score ?? 0}%`}
              subtitle="Across all rankings"
              icon={Trophy}
              iconColor="text-amber-600"
              iconBg="bg-amber-50"
            />
            <StatsCard
              title="Shortlisted"
              value={stats?.candidates_by_status?.shortlisted ?? 0}
              subtitle="Ready for interview"
              icon={TrendingUp}
              iconColor="text-emerald-600"
              iconBg="bg-emerald-50"
            />
          </>
        )}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Score distribution bar chart */}
        <div className="lg:col-span-2 rounded-xl border border-border bg-card p-5">
          <h2 className="text-sm font-semibold text-foreground mb-4">ATS Score Distribution</h2>
          {isLoading ? (
            <Skeleton className="h-48 w-full" />
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={distribution} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                <XAxis dataKey="range" tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} />
                <YAxis tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} />
                <Tooltip
                  contentStyle={{
                    background: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="count" name="Candidates" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Candidate status pie */}
        <div className="rounded-xl border border-border bg-card p-5">
          <h2 className="text-sm font-semibold text-foreground mb-4">Pipeline Status</h2>
          {isLoading ? (
            <Skeleton className="h-48 w-full" />
          ) : pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="45%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {pieData.map((_, index) => (
                    <Cell key={index} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: '11px' }} />
                <Tooltip
                  contentStyle={{
                    background: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-sm text-muted-foreground">
              No data yet
            </div>
          )}
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Top ranked candidates */}
        <div className="rounded-xl border border-border bg-card p-5">
          <h2 className="text-sm font-semibold text-foreground mb-4">Top Ranked Candidates</h2>
          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-12" />)}
            </div>
          ) : topRankings.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">No rankings yet. Seed mock data to get started.</p>
          ) : (
            <div className="space-y-2">
              {topRankings.map((r, idx) => (
                <div key={r.id} className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-muted/50 transition-colors">
                  <span className="text-xs font-bold text-muted-foreground w-5 text-center">
                    #{idx + 1}
                  </span>
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary font-semibold text-xs">
                    {r.candidate_name.charAt(0)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">{r.candidate_name}</p>
                    <p className="text-xs text-muted-foreground truncate">{r.job_title}</p>
                  </div>
                  <ScoreRing score={r.score ?? 0} size="sm" showLabel={false} />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent candidates */}
        <div className="rounded-xl border border-border bg-card p-5">
          <h2 className="text-sm font-semibold text-foreground mb-4">Recent Candidates</h2>
          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-12" />)}
            </div>
          ) : recentCandidates.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">No candidates yet.</p>
          ) : (
            <div className="space-y-2">
              {recentCandidates.map((c) => (
                <div key={c.id} className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-muted/50 transition-colors">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary text-secondary-foreground font-semibold text-xs">
                    {c.name.charAt(0)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">{c.name}</p>
                    <p className="text-xs text-muted-foreground">{formatDate(c.created_at)}</p>
                  </div>
                  <StatusBadge status={c.status} />
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

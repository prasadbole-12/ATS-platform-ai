import { Database, Server, Zap } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useSeedMockData } from '@/hooks/queries'

export default function SettingsPage() {
  const seedMutation = useSeedMockData()
  const apiUrl = (import.meta.env as Record<string, string>)['VITE_API_BASE_URL'] ?? 'http://localhost:8000'

  return (
    <div className="max-w-2xl space-y-6">
      {/* API Config */}
      <section className="rounded-xl border border-border bg-card p-5">
        <div className="flex items-center gap-2.5 mb-4">
          <Server className="h-4 w-4 text-muted-foreground" />
          <h2 className="text-sm font-semibold text-foreground">API Configuration</h2>
        </div>
        <div className="space-y-3">
          <div>
            <Label>Backend URL</Label>
            <Input value={apiUrl} className="mt-1.5" readOnly />
            <p className="mt-1 text-xs text-muted-foreground">
              Set via VITE_API_BASE_URL in frontend/.env.local
            </p>
          </div>
          <div>
            <Label>API Version</Label>
            <Input value="v1" className="mt-1.5 w-24" readOnly />
          </div>
        </div>
      </section>

      {/* Dev Tools */}
      <section className="rounded-xl border border-border bg-card p-5">
        <div className="flex items-center gap-2.5 mb-4">
          <Zap className="h-4 w-4 text-muted-foreground" />
          <h2 className="text-sm font-semibold text-foreground">Developer Tools</h2>
        </div>
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">
            Seed the database with 8 candidates, 2 jobs, and 7 mock ATS rankings.
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => seedMutation.mutate()}
            disabled={seedMutation.isPending}
          >
            <Database className="mr-2 h-3.5 w-3.5" />
            {seedMutation.isPending ? 'Seeding…' : 'Seed Mock Data'}
          </Button>
          {seedMutation.isSuccess && (
            <p className="text-xs text-emerald-600">
              ✓ Seeded — {seedMutation.data.candidates} candidates, {seedMutation.data.jobs} jobs, {seedMutation.data.rankings} rankings.
            </p>
          )}
          {seedMutation.isError && (
            <p className="text-xs text-red-500">Failed. Check backend is running.</p>
          )}
        </div>
      </section>

      {/* Platform Info */}
      <section className="rounded-xl border border-border bg-card p-5">
        <div className="flex items-center gap-2.5 mb-4">
          <Zap className="h-4 w-4 text-muted-foreground" />
          <h2 className="text-sm font-semibold text-foreground">Platform Information</h2>
        </div>
        <dl className="space-y-2 text-sm">
          {[
            ['Platform', 'ATS Candidate Ranking System'],
            ['Version', '1.0.0 — Day 1 Foundation'],
            ['Frontend', 'React 18 + TypeScript + Vite + Tailwind'],
            ['Backend', 'FastAPI + Python 3.11 + SQLAlchemy 2.0'],
            ['Database', 'PostgreSQL 15'],
            ['Next Phase', 'Phase 2 — NLP + TF-IDF scoring'],
          ].map(([label, value]) => (
            <div key={label} className="flex gap-3">
              <dt className="w-28 shrink-0 text-muted-foreground">{label}</dt>
              <dd className="text-foreground font-medium">{value}</dd>
            </div>
          ))}
        </dl>
      </section>
    </div>
  )
}

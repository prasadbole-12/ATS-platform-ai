import { X, Mail, Phone, Briefcase, Calendar, FileText } from 'lucide-react'
import { Candidate } from '@/types'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { Button } from '@/components/ui/button'
import { Select } from '@/components/ui/select'
import { formatDate } from '@/lib/utils'
import { useUpdateCandidate } from '@/hooks/queries'

interface CandidateDrawerProps {
  candidate: Candidate | null
  open: boolean
  onClose: () => void
}

const statusOptions = [
  { value: 'new', label: 'New' },
  { value: 'reviewed', label: 'Reviewed' },
  { value: 'shortlisted', label: 'Shortlisted' },
  { value: 'rejected', label: 'Rejected' },
]

export function CandidateDrawer({ candidate, open, onClose }: CandidateDrawerProps) {
  const updateMutation = useUpdateCandidate()

  const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    if (!candidate) return
    updateMutation.mutate({ candidateId: candidate.id, data: { status: e.target.value as any } })
  }

  return (
    <>
      {/* Backdrop */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm"
          onClick={onClose}
        />
      )}

      {/* Drawer */}
      <aside
        className={`fixed top-0 right-0 z-50 h-full w-full max-w-md bg-card border-l border-border shadow-2xl transition-transform duration-300 ease-in-out flex flex-col ${
          open && candidate ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {candidate && (
          <>
            {/* Header */}
            <div className="flex items-start justify-between p-6 border-b border-border">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-primary-foreground font-bold text-lg">
                  {candidate.name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <h2 className="font-semibold text-foreground text-base">{candidate.name}</h2>
                  <StatusBadge status={candidate.status} />
                </div>
              </div>
              <button onClick={onClose} className="text-muted-foreground hover:text-foreground p-1">
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Body */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Contact info */}
              <section>
                <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">
                  Contact
                </h3>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="h-3.5 w-3.5 text-muted-foreground" />
                    <span className="text-foreground">{candidate.email}</span>
                  </div>
                  {candidate.phone && (
                    <div className="flex items-center gap-2 text-sm">
                      <Phone className="h-3.5 w-3.5 text-muted-foreground" />
                      <span className="text-foreground">{candidate.phone}</span>
                    </div>
                  )}
                  <div className="flex items-center gap-2 text-sm">
                    <Calendar className="h-3.5 w-3.5 text-muted-foreground" />
                    <span className="text-muted-foreground">Added {formatDate(candidate.created_at)}</span>
                  </div>
                  {candidate.resume_file_name && (
                    <div className="flex items-center gap-2 text-sm">
                      <FileText className="h-3.5 w-3.5 text-muted-foreground" />
                      <span className="text-foreground">{candidate.resume_file_name}</span>
                    </div>
                  )}
                </div>
              </section>

              {/* Skills */}
              {candidate.skills && (
                <section>
                  <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">
                    Skills
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {candidate.skills.split(',').map((s) => (
                      <span
                        key={s.trim()}
                        className="inline-flex items-center rounded-md bg-secondary px-2 py-1 text-xs font-medium text-secondary-foreground"
                      >
                        {s.trim()}
                      </span>
                    ))}
                  </div>
                </section>
              )}

              {/* Resume text */}
              {candidate.resume_text && (
                <section>
                  <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">
                    Resume Preview
                  </h3>
                  <div className="rounded-lg bg-muted/50 p-3 text-xs text-muted-foreground leading-relaxed max-h-48 overflow-y-auto font-mono">
                    {candidate.resume_text}
                  </div>
                </section>
              )}

              {/* Status update */}
              <section>
                <h3 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">
                  Pipeline Status
                </h3>
                <Select
                  options={statusOptions}
                  value={candidate.status}
                  onChange={handleStatusChange}
                  disabled={updateMutation.isPending}
                />
              </section>
            </div>

            {/* Footer */}
            <div className="border-t border-border p-4 flex gap-2">
              <Button
                variant="outline"
                size="sm"
                className="flex-1"
                onClick={onClose}
              >
                Close
              </Button>
              <Button
                size="sm"
                className="flex-1"
                onClick={() => updateMutation.mutate({
                  candidateId: candidate.id,
                  data: { status: 'shortlisted' },
                })}
                disabled={candidate.status === 'shortlisted' || updateMutation.isPending}
              >
                Shortlist
              </Button>
            </div>
          </>
        )}
      </aside>
    </>
  )
}

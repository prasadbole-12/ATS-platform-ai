import { useState } from 'react'
import { Plus, Briefcase, Pencil, Trash2, CheckCircle, XCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogClose, DialogFooter } from '@/components/ui/dialog'
import { EmptyState } from '@/components/shared/EmptyState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Skeleton } from '@/components/ui/skeleton'
import { useJobDescriptions, useCreateJobDescription, useUpdateJobDescription } from '@/hooks/queries'
import { jobDescriptionService } from '@/services/jobDescriptionService'
import { useQueryClient } from '@tanstack/react-query'
import { JobDescription } from '@/types'
import { formatDate } from '@/lib/utils'

interface FormState {
  title: string
  department: string
  location: string
  description: string
  required_skills: string
  experience_years: string
}

const EMPTY_FORM: FormState = {
  title: '',
  department: '',
  location: '',
  description: '',
  required_skills: '',
  experience_years: '',
}

export default function JobDescriptionsPage() {
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<JobDescription | null>(null)
  const [form, setForm] = useState<FormState>(EMPTY_FORM)
  const [errors, setErrors] = useState<Partial<FormState>>({})

  const { data, isLoading, isError, refetch } = useJobDescriptions()
  const createMutation = useCreateJobDescription()
  const updateMutation = useUpdateJobDescription()
  const queryClient = useQueryClient()

  const openCreate = () => {
    setEditTarget(null)
    setForm(EMPTY_FORM)
    setErrors({})
    setDialogOpen(true)
  }

  const openEdit = (jd: JobDescription) => {
    setEditTarget(jd)
    setForm({
      title: jd.title,
      department: jd.department ?? '',
      location: jd.location ?? '',
      description: jd.description,
      required_skills: jd.required_skills ?? '',
      experience_years: String(jd.experience_years ?? ''),
    })
    setErrors({})
    setDialogOpen(true)
  }

  const validate = (): boolean => {
    const e: Partial<FormState> = {}
    if (!form.title.trim()) e.title = 'Title is required'
    if (form.description.trim().length < 10) e.description = 'Description must be at least 10 characters'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = async () => {
    if (!validate()) return

    const payload = {
      title: form.title.trim(),
      department: form.department.trim() || undefined,
      location: form.location.trim() || undefined,
      description: form.description.trim(),
      required_skills: form.required_skills.trim() || undefined,
      experience_years: form.experience_years ? Number(form.experience_years) : undefined,
    }

    if (editTarget) {
      await updateMutation.mutateAsync({ jdId: editTarget.id, data: payload })
    } else {
      await createMutation.mutateAsync(payload)
    }

    setDialogOpen(false)
    setForm(EMPTY_FORM)
  }

  const handleDelete = async (jdId: string) => {
    if (!confirm('Delete this job description? This will also remove all rankings for this job.')) return
    await jobDescriptionService.delete(jdId)
    queryClient.invalidateQueries({ queryKey: ['job_descriptions'] })
  }

  const jobs = data?.items ?? []
  const isMutating = createMutation.isPending || updateMutation.isPending

  return (
    <>
      <div className="space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            {isLoading ? '…' : `${data?.total ?? 0} job description${data?.total !== 1 ? 's' : ''}`}
          </p>
          <Button size="sm" onClick={openCreate}>
            <Plus className="mr-2 h-3.5 w-3.5" />
            New Job Description
          </Button>
        </div>

        {/* Grid */}
        {isLoading ? (
          <div className="grid gap-4 sm:grid-cols-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-44 rounded-xl" />
            ))}
          </div>
        ) : isError ? (
          <ErrorState onRetry={refetch} />
        ) : jobs.length === 0 ? (
          <EmptyState
            icon={Briefcase}
            title="No job descriptions yet"
            description="Create your first job description to start ranking candidates against it."
            action={{ label: 'Create Job Description', onClick: openCreate }}
          />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {jobs.map((jd) => (
              <div
                key={jd.id}
                className="group rounded-xl border border-border bg-card p-5 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2.5">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-50">
                      <Briefcase className="h-4 w-4 text-violet-600" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-foreground leading-tight">{jd.title}</h3>
                      {jd.department && (
                        <p className="text-xs text-muted-foreground">{jd.department}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => openEdit(jd)}
                      className="p-1.5 rounded hover:bg-muted text-muted-foreground hover:text-foreground"
                    >
                      <Pencil className="h-3.5 w-3.5" />
                    </button>
                    <button
                      onClick={() => handleDelete(jd.id)}
                      className="p-1.5 rounded hover:bg-red-50 text-muted-foreground hover:text-red-500"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>

                <p className="text-xs text-muted-foreground line-clamp-2 mb-3">
                  {jd.description}
                </p>

                <div className="flex flex-wrap gap-1 mb-3">
                  {jd.required_skills?.split(',').slice(0, 4).map((s) => (
                    <span key={s} className="inline-flex items-center rounded bg-secondary px-1.5 py-0.5 text-xs text-secondary-foreground">
                      {s.trim()}
                    </span>
                  ))}
                </div>

                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <div className="flex items-center gap-3">
                    {jd.location && <span>📍 {jd.location}</span>}
                    {jd.experience_years && <span>⏱ {jd.experience_years}+ yrs</span>}
                  </div>
                  <div className="flex items-center gap-1">
                    {jd.is_active ? (
                      <><CheckCircle className="h-3 w-3 text-emerald-500" /><span className="text-emerald-600">Active</span></>
                    ) : (
                      <><XCircle className="h-3 w-3 text-red-400" /><span className="text-red-500">Inactive</span></>
                    )}
                  </div>
                </div>
                <p className="mt-2 text-[10px] text-muted-foreground">Created {formatDate(jd.created_at)}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create / Edit Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogClose onClose={() => setDialogOpen(false)} />
          <DialogHeader>
            <DialogTitle>{editTarget ? 'Edit Job Description' : 'New Job Description'}</DialogTitle>
            <DialogDescription>
              {editTarget ? 'Update the details below.' : 'Fill in the job details. Required skills are used for ATS matching.'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Job Title *</Label>
              <Input
                id="title"
                placeholder="e.g. Senior Backend Engineer"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                className={`mt-1.5 ${errors.title ? 'border-red-400' : ''}`}
              />
              {errors.title && <p className="mt-1 text-xs text-red-500">{errors.title}</p>}
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label htmlFor="dept">Department</Label>
                <Input
                  id="dept"
                  placeholder="Engineering"
                  value={form.department}
                  onChange={(e) => setForm({ ...form, department: e.target.value })}
                  className="mt-1.5"
                />
              </div>
              <div>
                <Label htmlFor="loc">Location</Label>
                <Input
                  id="loc"
                  placeholder="Bangalore, India"
                  value={form.location}
                  onChange={(e) => setForm({ ...form, location: e.target.value })}
                  className="mt-1.5"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="desc">Description *</Label>
              <Textarea
                id="desc"
                placeholder="Describe the role, responsibilities, and requirements…"
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                className={`mt-1.5 min-h-[100px] ${errors.description ? 'border-red-400' : ''}`}
              />
              {errors.description && <p className="mt-1 text-xs text-red-500">{errors.description}</p>}
            </div>

            <div>
              <Label htmlFor="skills">Required Skills</Label>
              <Input
                id="skills"
                placeholder="Python, FastAPI, PostgreSQL, Docker"
                value={form.required_skills}
                onChange={(e) => setForm({ ...form, required_skills: e.target.value })}
                className="mt-1.5"
              />
              <p className="mt-1 text-xs text-muted-foreground">Comma-separated</p>
            </div>

            <div>
              <Label htmlFor="exp">Min. Experience (years)</Label>
              <Input
                id="exp"
                type="number"
                placeholder="3"
                min={0}
                max={30}
                value={form.experience_years}
                onChange={(e) => setForm({ ...form, experience_years: e.target.value })}
                className="mt-1.5 w-32"
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)} disabled={isMutating}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={isMutating}>
              {isMutating ? 'Saving…' : editTarget ? 'Update' : 'Create'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

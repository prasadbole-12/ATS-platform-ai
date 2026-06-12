import { cn } from '@/lib/utils'

type Status = 'new' | 'reviewed' | 'shortlisted' | 'rejected'

const config: Record<Status, { label: string; className: string }> = {
  new: { label: 'New', className: 'bg-blue-50 text-blue-700 border-blue-200' },
  reviewed: { label: 'Reviewed', className: 'bg-amber-50 text-amber-700 border-amber-200' },
  shortlisted: { label: 'Shortlisted', className: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  rejected: { label: 'Rejected', className: 'bg-red-50 text-red-700 border-red-200' },
}

export function StatusBadge({ status }: { status: string }) {
  const s = config[status as Status] ?? { label: status, className: 'bg-gray-50 text-gray-700 border-gray-200' }
  return (
    <span className={cn('inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium', s.className)}>
      <span className="mr-1.5 h-1.5 w-1.5 rounded-full bg-current" />
      {s.label}
    </span>
  )
}

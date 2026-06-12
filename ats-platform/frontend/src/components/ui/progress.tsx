import * as React from 'react'
import { cn } from '@/lib/utils'

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number
  max?: number
  colorClass?: string
}

export function Progress({ value, max = 100, colorClass, className, ...props }: ProgressProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100))

  const autoColor =
    colorClass ??
    (pct >= 80
      ? 'bg-emerald-500'
      : pct >= 60
        ? 'bg-blue-500'
        : pct >= 40
          ? 'bg-amber-500'
          : 'bg-red-500')

  return (
    <div
      className={cn('relative h-2 w-full overflow-hidden rounded-full bg-secondary', className)}
      {...props}
    >
      <div
        className={cn('h-full rounded-full transition-all duration-500', autoColor)}
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}

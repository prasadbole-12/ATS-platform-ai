import { cn } from '@/lib/utils'

interface ScoreRingProps {
  score: number
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}

const sizeMap = {
  sm: { outer: 48, stroke: 4, r: 18, textSize: 'text-xs' },
  md: { outer: 72, stroke: 5, r: 28, textSize: 'text-sm' },
  lg: { outer: 96, stroke: 6, r: 38, textSize: 'text-base' },
}

function scoreColor(score: number): string {
  if (score >= 80) return '#10b981'
  if (score >= 60) return '#3b82f6'
  if (score >= 40) return '#f59e0b'
  return '#ef4444'
}

export function ScoreRing({ score, size = 'md', showLabel = true }: ScoreRingProps) {
  const { outer, stroke, r, textSize } = sizeMap[size]
  const cx = outer / 2
  const cy = outer / 2
  const circumference = 2 * Math.PI * r
  const dash = (score / 100) * circumference
  const color = scoreColor(score)

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={outer} height={outer} className="-rotate-90">
        <circle cx={cx} cy={cy} r={r} stroke="#e5e7eb" strokeWidth={stroke} fill="none" />
        <circle
          cx={cx}
          cy={cy}
          r={r}
          stroke={color}
          strokeWidth={stroke}
          fill="none"
          strokeDasharray={`${dash} ${circumference}`}
          strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 0.6s ease' }}
        />
        <text
          x={cx}
          y={cy}
          textAnchor="middle"
          dominantBaseline="central"
          className={cn('rotate-90 origin-center font-bold fill-current', textSize)}
          style={{ transform: `rotate(90deg)`, transformOrigin: `${cx}px ${cy}px`, fill: color }}
        >
          {Math.round(score)}
        </text>
      </svg>
      {showLabel && (
        <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wide">
          ATS Score
        </span>
      )}
    </div>
  )
}

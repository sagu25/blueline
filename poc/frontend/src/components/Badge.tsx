interface BadgeProps {
  label: string
  variant?: 'severity' | 'classification' | 'urgency' | 'risk' | 'recommendation'
}

const SEVERITY_COLORS: Record<string, string> = {
  error:   'bg-red-600 text-white',
  major:   'bg-red-500 text-white',
  warning: 'bg-orange-500 text-white',
  minor:   'bg-orange-400 text-white',
  info:    'bg-blue-500 text-white',
}

const CLASS_COLORS: Record<string, string> = {
  CRITICAL:       'bg-red-600 text-white',
  HIGH:           'bg-red-500 text-white',
  NEEDS_REVIEW:   'bg-orange-500 text-white',
  FALSE_POSITIVE: 'bg-emerald-600 text-white',
}

const URGENCY_COLORS: Record<string, string> = {
  EXPIRED:        'bg-red-700 text-white',
  CRITICAL:       'bg-red-600 text-white',
  URGENT:         'bg-orange-600 text-white',
  RENEWAL_NEEDED: 'bg-orange-500 text-white',
  MONITOR:        'bg-blue-500 text-white',
  OK:             'bg-emerald-600 text-white',
}

const REC_COLORS: Record<string, string> = {
  BLOCK:           'bg-red-600 text-white',
  REQUEST_CHANGES: 'bg-orange-500 text-white',
  APPROVE:         'bg-emerald-600 text-white',
}

const RISK_COLORS: Record<string, string> = {
  CRITICAL: 'bg-red-600 text-white',
  HIGH:     'bg-red-500 text-white',
  MEDIUM:   'bg-orange-500 text-white',
  LOW:      'bg-emerald-600 text-white',
}

export function Badge({ label, variant = 'severity' }: BadgeProps) {
  let colorClass = 'bg-gray-600 text-white'
  const key = label?.toUpperCase()

  if (variant === 'severity')         colorClass = SEVERITY_COLORS[label?.toLowerCase()] ?? colorClass
  else if (variant === 'classification') colorClass = CLASS_COLORS[key] ?? colorClass
  else if (variant === 'urgency')     colorClass = URGENCY_COLORS[key] ?? colorClass
  else if (variant === 'recommendation') colorClass = REC_COLORS[key] ?? colorClass
  else if (variant === 'risk')        colorClass = RISK_COLORS[key] ?? colorClass

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded text-xs font-bold tracking-wide uppercase ${colorClass}`}>
      {label}
    </span>
  )
}

export function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  const color = pct >= 80 ? '#22c55e' : pct >= 60 ? '#f97316' : '#ef4444'
  return (
    <div className="mt-1">
      <div className="h-1.5 rounded-full bg-blu-600 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
      <span className="text-xs text-slate-500 mt-0.5 block">{pct}% confidence</span>
    </div>
  )
}

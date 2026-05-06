import { CheckCircle, Loader2, Clock, XCircle, SkipForward } from 'lucide-react'
import type { AgentStatus } from '../types'

export interface PipelineStep {
  id: string
  name: string
  description: string
  status: AgentStatus
}

interface Props {
  steps: PipelineStep[]
}

const STATUS_CONFIG: Record<AgentStatus, { icon: React.ReactNode; border: string; text: string; bg: string }> = {
  idle: {
    icon: <Clock size={16} className="text-slate-500" />,
    border: 'border-blu-600',
    text: 'text-slate-400',
    bg: 'bg-blu-800',
  },
  running: {
    icon: <Loader2 size={16} className="text-blu-primary animate-spin" />,
    border: 'border-blu-primary',
    text: 'text-blu-primary',
    bg: 'bg-blu-800',
  },
  done: {
    icon: <CheckCircle size={16} className="text-emerald-500" />,
    border: 'border-emerald-600',
    text: 'text-emerald-400',
    bg: 'bg-emerald-950/30',
  },
  error: {
    icon: <XCircle size={16} className="text-red-500" />,
    border: 'border-red-600',
    text: 'text-red-400',
    bg: 'bg-red-950/30',
  },
  skipped: {
    icon: <SkipForward size={16} className="text-slate-600" />,
    border: 'border-slate-700',
    text: 'text-slate-500',
    bg: 'bg-blu-900',
  },
}

export function AgentPipeline({ steps }: Props) {
  return (
    <div className="flex items-stretch gap-0 w-full overflow-x-auto pb-1">
      {steps.map((step, i) => {
        const cfg = STATUS_CONFIG[step.status]
        const isRunning = step.status === 'running'
        return (
          <div key={step.id} className="flex items-center flex-1 min-w-0">
            {/* Node */}
            <div
              className={`
                flex-1 min-w-0 rounded-lg border px-3 py-2.5
                transition-all duration-300
                ${cfg.bg} ${cfg.border}
                ${isRunning ? 'shadow-[0_0_12px_rgba(74,158,255,0.25)]' : ''}
              `}
            >
              <div className="flex items-center gap-1.5 mb-0.5">
                {cfg.icon}
                <span className={`text-xs font-bold tracking-widest uppercase ${cfg.text}`}>
                  {step.name}
                </span>
              </div>
              <p className="text-xs text-slate-500 truncate leading-tight">{step.description}</p>
            </div>

            {/* Connector arrow */}
            {i < steps.length - 1 && (
              <div className="flex items-center px-1 shrink-0">
                <svg width="20" height="10" viewBox="0 0 20 10">
                  <path d="M0 5 H16 M12 1 L20 5 L12 9" stroke="#243d5c" strokeWidth="1.5" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

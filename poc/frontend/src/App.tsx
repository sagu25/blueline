import { useState } from 'react'
import { Sidebar } from './components/Sidebar'
import { QualityGate } from './tabs/QualityGate'
import { SecurityLoop } from './tabs/SecurityLoop'
import { CertificateLoop } from './tabs/CertificateLoop'
import { LivePRReview } from './tabs/LivePRReview'
import type { AppStatus } from './types'

type Tab = 'quality' | 'security' | 'certificate' | 'live'

const TABS: { id: Tab; label: string; icon: string; sub: string }[] = [
  { id: 'quality',     label: 'Quality Gate',      icon: '🧑‍💻', sub: 'CLARION · LUMEN · VECTOR · ASCENT' },
  { id: 'security',    label: 'Security Loop',      icon: '🔒', sub: 'WATCHTOWER · BULWARK · FORGE · STEWARD' },
  { id: 'certificate', label: 'Certificate Loop',   icon: '📜', sub: 'REGENT · TIMELINE · COURIER · HARBOUR' },
  { id: 'live',        label: 'Live PR Review',     icon: '🔗', sub: 'Azure DevOps Integration' },
]

export default function App() {
  const [tab, setTab] = useState<Tab>('quality')
  const [status, setStatus] = useState<AppStatus>({ ai_provider: 'none', ado_configured: false })

  return (
    <div className="flex h-screen overflow-hidden bg-blu-950 text-slate-200">
      <Sidebar status={status} onStatusChange={setStatus} />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top nav */}
        <header className="shrink-0 bg-blu-900 border-b border-blu-600 px-6 py-0">
          <nav className="flex items-end gap-1 overflow-x-auto">
            {TABS.map(t => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={`
                  group flex flex-col items-start px-4 py-3.5 text-left border-b-2 transition-all whitespace-nowrap
                  ${tab === t.id
                    ? 'border-blu-primary text-white'
                    : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-blu-600'
                  }
                `}
              >
                <span className="text-sm font-semibold">{t.icon} {t.label}</span>
                <span className={`text-xs mt-0.5 font-mono ${tab === t.id ? 'text-slate-400' : 'text-slate-600 group-hover:text-slate-500'}`}>
                  {t.sub}
                </span>
              </button>
            ))}
          </nav>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto bg-blu-950">
          <div className="max-w-[1400px] mx-auto p-6">
            {tab === 'quality'     && <QualityGate />}
            {tab === 'security'    && <SecurityLoop />}
            {tab === 'certificate' && <CertificateLoop />}
            {tab === 'live'        && <LivePRReview />}
          </div>
        </main>
      </div>
    </div>
  )
}

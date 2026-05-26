import { useState, useEffect } from 'react'
import { Play, RefreshCw, CheckCircle, Clock, AlertTriangle } from 'lucide-react'
import { api } from '../api'
import { AgentPipeline, type PipelineStep } from '../components/AgentPipeline'
import { Badge } from '../components/Badge'
import type { AgentStatus, Certificate, TimelineResult, CourierResult, HarbourResult } from '../types'

const INITIAL_STEPS: PipelineStep[] = [
  { id: 'regent',   name: 'REGENT',   description: 'Cert Inventory',  status: 'idle' },
  { id: 'timeline', name: 'TIMELINE', description: 'Expiry Analysis', status: 'idle' },
  { id: 'courier',  name: 'COURIER',  description: 'CA Renewal',      status: 'idle' },
  { id: 'harbour',  name: 'HARBOUR',  description: 'Deployment',      status: 'idle' },
]

function setStep(steps: PipelineStep[], id: string, status: AgentStatus): PipelineStep[] {
  return steps.map(s => s.id === id ? { ...s, status } : s)
}

const STATUS_COLORS: Record<string, string> = {
  EXPIRED:        'text-red-400 bg-red-950/40 border-red-700',
  CRITICAL:       'text-red-400 bg-red-950/40 border-red-700',
  URGENT:         'text-orange-400 bg-orange-950/40 border-orange-700',
  RENEWAL_NEEDED: 'text-orange-300 bg-orange-950/30 border-orange-800',
  MONITOR:        'text-blue-400 bg-blue-950/40 border-blue-700',
  OK:             'text-emerald-400 bg-emerald-950/40 border-emerald-700',
}

const TRIGGER_STATUSES = new Set(['EXPIRED', 'CRITICAL', 'URGENT', 'RENEWAL_NEEDED'])

export function CertificateLoop() {
  const [certs, setCerts]           = useState<Certificate[]>([])
  const [selected, setSelected]     = useState<Certificate | null>(null)
  const [loadingCerts, setLoadingCerts] = useState(true)
  const [steps, setSteps]           = useState<PipelineStep[]>(INITIAL_STEPS)
  const [running, setRunning]       = useState(false)
  const [error, setError]           = useState('')

  const [timeline, setTimeline] = useState<TimelineResult | null>(null)
  const [courier,  setCourier]  = useState<CourierResult  | null>(null)
  const [harbour,  setHarbour]  = useState<HarbourResult  | null>(null)

  async function loadCerts() {
    setLoadingCerts(true)
    try {
      const inv = await api.certificates()
      setCerts(inv)
      if (inv.length > 0) setSelected(inv[0])
    } catch { setError('Could not load certificate inventory.') }
    finally { setLoadingCerts(false) }
  }

  useEffect(() => { loadCerts() }, [])

  async function run() {
    if (!selected) return
    setError(''); setRunning(true)
    setTimeline(null); setCourier(null); setHarbour(null)
    setSteps(INITIAL_STEPS)

    try {
      // REGENT
      setSteps(s => setStep(s, 'regent', 'running'))
      await new Promise(r => setTimeout(r, 400))
      setSteps(s => setStep(setStep(s, 'regent', 'done'), 'timeline', 'running'))

      // TIMELINE
      const tr = await api.timeline({
        subject:      selected.subject,
        expiry_date:  selected.expiry_date,
        environments: selected.environments.join(', '),
        ca_type:      selected.ca_type,
      })
      setTimeline(tr)
      const urgency = tr.urgency ?? 'OK'

      if (TRIGGER_STATUSES.has(urgency)) {
        setSteps(s => setStep(setStep(s, 'timeline', 'done'), 'courier', 'running'))

        const cr = await api.courier({
          subject:        selected.subject,
          ca_type:        selected.ca_type,
          environments:   selected.environments.join(', '),
          days_remaining: selected.days_remaining,
        })
        setCourier(cr)
        setSteps(s => setStep(setStep(s, 'courier', 'done'), 'harbour', 'running'))

        const hr = await api.harbour({
          subject:                 selected.subject,
          ca_type:                 selected.ca_type,
          environments:            selected.environments,
          deployment_targets:      selected.deployment_targets,
          cert_thumbprint:         cr.simulated_thumbprint ?? 'SIMULATED',
          days_remaining_old_cert: selected.days_remaining,
        })
        setHarbour(hr)
        setSteps(s => setStep(s, 'harbour', 'done'))
      } else {
        setSteps(s => setStep(setStep(s, 'timeline', 'done'), 'courier', 'skipped'))
        setSteps(s => setStep(s, 'harbour', 'skipped'))
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'An error occurred')
      setSteps(s => s.map(st => st.status === 'running' ? { ...st, status: 'error' } : st))
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-bold text-white">Certificate Loop</h1>
        <p className="text-sm text-slate-400 mt-1">
          REGENT maintains the inventory → TIMELINE analyses expiry → COURIER requests renewal from the CA → HARBOUR deploys and gates Production on human approval.
        </p>
      </div>

      <div className="bg-blu-900 border border-blu-600 rounded-xl p-4">
        <AgentPipeline steps={steps} />
      </div>

      {/* Inventory table */}
      <div className="bg-blu-900 border border-blu-600 rounded-xl overflow-hidden">
        <div className="flex items-center justify-between px-5 py-3 border-b border-blu-600">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">REGENT — Certificate Inventory</span>
            <span className="text-xs text-slate-500">(POC: 4 sample certificates)</span>
          </div>
          <button
            onClick={loadCerts}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
          >
            <RefreshCw size={12} /> Refresh
          </button>
        </div>

        {loadingCerts ? (
          <div className="px-5 py-8 text-center text-slate-500 text-sm">Loading inventory…</div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-blu-700">
                {['Certificate', 'Expiry', 'Days', 'Status', 'Owner', 'Environments'].map(h => (
                  <th key={h} className="text-left px-5 py-2.5 text-xs font-semibold text-slate-500 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {certs.map(cert => {
                const colors = STATUS_COLORS[cert.status] ?? 'text-slate-400 bg-transparent border-slate-700'
                const isSel = selected?.name === cert.name
                return (
                  <tr
                    key={cert.name}
                    onClick={() => setSelected(cert)}
                    className={`border-b border-blu-700/50 cursor-pointer transition-colors ${
                      isSel ? 'bg-blu-primary/10' : 'hover:bg-blu-800'
                    }`}
                  >
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-2">
                        {isSel && <div className="w-1.5 h-1.5 rounded-full bg-blu-primary" />}
                        <span className="text-xs font-mono text-slate-200">{cert.name}</span>
                      </div>
                    </td>
                    <td className="px-5 py-3 text-xs text-slate-300 font-mono">{cert.expiry_date}</td>
                    <td className="px-5 py-3">
                      <span className={`text-xs font-bold ${
                        cert.days_remaining <= 7  ? 'text-red-400'    :
                        cert.days_remaining <= 30 ? 'text-orange-400' : 'text-emerald-400'
                      }`}>{cert.days_remaining}</span>
                    </td>
                    <td className="px-5 py-3">
                      <span className={`text-xs font-bold px-2 py-0.5 rounded border ${colors}`}>
                        {cert.status}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-xs text-slate-400">{cert.owner}</td>
                    <td className="px-5 py-3">
                      <div className="flex gap-1 flex-wrap">
                        {cert.environments.map(e => (
                          <span key={e} className="text-xs bg-blu-800 border border-blu-600 px-1.5 py-0.5 rounded text-slate-400">{e}</span>
                        ))}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Selected cert + run */}
      {selected && (
        <div className="flex items-center justify-between bg-blu-900 border border-blu-primary/30 rounded-xl px-5 py-3.5">
          <div>
            <p className="text-xs text-slate-400">Selected Certificate</p>
            <p className="text-sm font-mono font-semibold text-white mt-0.5">{selected.name}</p>
            <p className="text-xs text-slate-500 mt-0.5">CA: {selected.ca_type} · {selected.environments.join(', ')}</p>
          </div>
          <button
            onClick={run}
            disabled={running}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blu-primary hover:bg-blue-400 disabled:opacity-50 text-white font-semibold text-sm transition-colors"
          >
            <Play size={15} /> {running ? 'Running…' : 'Run Pipeline'}
          </button>
        </div>
      )}

      {error && (
        <div className="bg-red-950/40 border border-red-700 rounded-lg px-4 py-2.5 text-sm text-red-300">{error}</div>
      )}

      {/* Results */}
      {timeline && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* TIMELINE */}
          <div className="bg-blu-900 border border-blu-600 rounded-xl p-5">
            <p className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-4">TIMELINE — Expiry Analysis</p>
            <div className="flex items-center gap-4 mb-4">
              <div>
                <p className="text-xs text-slate-500 mb-1">Urgency</p>
                <Badge label={timeline.urgency ?? 'OK'} variant="urgency" />
              </div>
              <div>
                <p className="text-xs text-slate-500 mb-1">Days Remaining</p>
                <p className={`text-2xl font-black ${
                  (timeline.days_until_expiry ?? 99) <= 7  ? 'text-red-400'    :
                  (timeline.days_until_expiry ?? 99) <= 14 ? 'text-orange-400' : 'text-slate-200'
                }`}>{timeline.days_until_expiry ?? '?'}</p>
              </div>
              <div>
                <p className="text-xs text-slate-500 mb-1">Renewal Path</p>
                <p className="text-sm text-slate-200 capitalize">{(timeline.renewal_path ?? '').replace(/_/g, ' ')}</p>
              </div>
            </div>

            {timeline.summary && (
              <p className="text-sm text-slate-300 italic mb-3">{timeline.summary}</p>
            )}

            {(timeline.action_plan ?? []).length > 0 && (
              <div>
                <p className="text-xs text-slate-500 mb-1.5">Action Plan</p>
                <ol className="space-y-1">
                  {timeline.action_plan!.map((step, i) => (
                    <li key={i} className="flex gap-2 text-xs text-slate-300">
                      <span className="text-blu-primary shrink-0">{i + 1}.</span> {step}
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {(timeline.risks ?? []).map((r, i) => (
              <div key={i} className="mt-2 flex gap-2 bg-orange-950/30 border border-orange-800/40 rounded-lg px-3 py-2">
                <AlertTriangle size={13} className="text-orange-400 shrink-0 mt-0.5" />
                <p className="text-xs text-orange-200">{r}</p>
              </div>
            ))}
          </div>

          {/* COURIER */}
          {courier ? (
            <div className="bg-blu-900 border border-blu-600 rounded-xl p-5">
              <p className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-4">COURIER — CA Renewal Request</p>
              <div className="space-y-3">
                <p className="text-sm text-slate-300">{courier.request_summary}</p>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { label: 'Order ID',   value: courier.ca_order_id },
                    { label: 'Delivery',   value: courier.estimated_delivery },
                    { label: 'Validation', value: courier.validation_method },
                    { label: 'Format',     value: courier.cert_format },
                  ].map(r => r.value ? (
                    <div key={r.label} className="bg-blu-800 rounded-lg px-3 py-2">
                      <p className="text-xs text-slate-500">{r.label}</p>
                      <p className="text-xs font-mono text-slate-200 mt-0.5">{r.value}</p>
                    </div>
                  ) : null)}
                </div>
                {courier.simulated_thumbprint && (
                  <div>
                    <p className="text-xs text-slate-500 mb-0.5">New Thumbprint</p>
                    <p className="text-xs font-mono text-blu-primary">{courier.simulated_thumbprint.slice(0, 32)}…</p>
                  </div>
                )}
                {courier.simulation_note && (
                  <p className="text-xs text-slate-600 italic">{courier.simulation_note}</p>
                )}
              </div>
            </div>
          ) : timeline.urgency && !TRIGGER_STATUSES.has(timeline.urgency) ? (
            <div className="bg-blu-900 border border-blu-600 rounded-xl p-5 flex flex-col items-center justify-center text-center">
              <CheckCircle size={32} className="text-emerald-500 mb-2" />
              <p className="text-sm text-slate-300 font-semibold">No renewal needed</p>
              <p className="text-xs text-slate-500 mt-1">Urgency is <strong>{timeline.urgency}</strong> — COURIER and HARBOUR are skipped.</p>
            </div>
          ) : null}
        </div>
      )}

      {/* HARBOUR deployment plan */}
      {harbour && (
        <div className="bg-blu-900 border border-blu-600 rounded-xl p-5">
          <p className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-4">HARBOUR — Deployment Plan</p>

          <div className="space-y-2 mb-4">
            {(harbour.deployment_plan ?? []).map((env, i) => {
              const isProd = env.environment === 'Production'
              return (
                <div key={i} className={`flex items-center justify-between rounded-lg border px-4 py-3 ${
                  isProd ? 'bg-orange-950/30 border-orange-800/50' : 'bg-emerald-950/20 border-emerald-900'
                }`}>
                  <div>
                    <p className="text-sm font-semibold text-white">{env.environment}</p>
                    <p className="text-xs text-slate-400">{env.target}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {isProd ? (
                      <span className="flex items-center gap-1.5 text-xs text-orange-400 font-semibold">
                        <Clock size={13} /> Awaiting Approval
                      </span>
                    ) : (
                      <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-semibold">
                        <CheckCircle size={13} /> Simulated Success
                      </span>
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Teams approval card */}
          {harbour.teams_approval_card && (
            <div className="mt-4">
              <p className="text-xs text-slate-500 mb-2 uppercase tracking-wider">Teams Approval Card — Sent to Channel</p>
              <div className="bg-[#1a1f3a] border border-[#4A9EFF]/40 rounded-xl p-5">
                <div className="flex items-start gap-3 mb-3">
                  <div className="w-8 h-8 rounded bg-[#4A9EFF]/20 flex items-center justify-center text-lg shrink-0">📜</div>
                  <div>
                    <p className="text-sm font-bold text-white">{harbour.teams_approval_card.title}</p>
                    {harbour.teams_approval_card.body && (
                      <p className="text-xs text-slate-300 mt-1">{harbour.teams_approval_card.body}</p>
                    )}
                    {harbour.teams_approval_card.domain && (
                      <p className="text-xs text-slate-400 mt-1">
                        Domain: <span className="font-mono text-slate-200">{harbour.teams_approval_card.domain}</span>
                        {harbour.teams_approval_card.new_expiry && ` · New expiry: ${harbour.teams_approval_card.new_expiry}`}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button className="px-4 py-1.5 rounded bg-emerald-600 text-white text-xs font-bold">
                    {harbour.teams_approval_card.approve_action ?? 'APPROVE'}
                  </button>
                  <button className="px-4 py-1.5 rounded bg-slate-600 text-white text-xs font-bold">
                    {harbour.teams_approval_card.reject_action ?? 'HOLD'}
                  </button>
                </div>
              </div>
              <div className="mt-2 flex gap-2 bg-orange-950/30 border border-orange-700/40 rounded-lg px-3 py-2">
                <span className="text-orange-400 text-sm">⚠</span>
                <div>
                  <p className="text-xs font-bold text-orange-400">Production Gate — Human Approval Required</p>
                  <p className="text-xs text-slate-400">HARBOUR will not deploy to Production until a human clicks Approve in Teams.</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

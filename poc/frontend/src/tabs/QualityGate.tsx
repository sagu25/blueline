import { useState } from 'react'
import { Play, FolderOpen, ChevronDown, ChevronRight, AlertTriangle, ShieldAlert, Lightbulb } from 'lucide-react'
import { api } from '../api'
import { AgentPipeline, type PipelineStep } from '../components/AgentPipeline'
import { Badge, ConfidenceBar } from '../components/Badge'
import type { AgentStatus, ClarionResult, LumenResult, VectorResult, AscentResult } from '../types'

const INITIAL_STEPS: PipelineStep[] = [
  { id: 'clarion', name: 'CLARION', description: 'Coding Standards', status: 'idle' },
  { id: 'lumen',   name: 'LUMEN',   description: 'Code Smells',      status: 'idle' },
  { id: 'vector',  name: 'VECTOR',  description: 'Risk Scoring',     status: 'idle' },
  { id: 'ascent',  name: 'ASCENT',  description: 'Aggregation',      status: 'idle' },
]

function setStep(steps: PipelineStep[], id: string, status: AgentStatus): PipelineStep[] {
  return steps.map(s => s.id === id ? { ...s, status } : s)
}

const REC_CONFIG = {
  APPROVE:         { color: 'text-emerald-400', bg: 'bg-emerald-950/40', border: 'border-emerald-700', glow: 'shadow-[0_0_24px_rgba(34,197,94,0.2)]' },
  REQUEST_CHANGES: { color: 'text-orange-400',  bg: 'bg-orange-950/40',  border: 'border-orange-700',  glow: 'shadow-[0_0_24px_rgba(249,115,22,0.2)]' },
  BLOCK:           { color: 'text-red-400',      bg: 'bg-red-950/40',     border: 'border-red-700',     glow: 'shadow-[0_0_24px_rgba(239,68,68,0.2)]'  },
}

function scoreColor(score: number) {
  if (score >= 7) return 'text-emerald-400'
  if (score >= 4) return 'text-orange-400'
  return 'text-red-400'
}

export function QualityGate() {
  const [lang, setLang] = useState<'csharp' | 'typescript'>('csharp')
  const [code, setCode] = useState('')
  const [steps, setSteps] = useState<PipelineStep[]>(INITIAL_STEPS)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')

  const [clarion, setClarion] = useState<ClarionResult | null>(null)
  const [lumen,   setLumen]   = useState<LumenResult   | null>(null)
  const [vector,  setVector]  = useState<VectorResult  | null>(null)
  const [ascent,  setAscent]  = useState<AscentResult  | null>(null)

  const [openSections, setOpenSections] = useState({ clarion: false, lumen: false, vector: false })

  async function loadSample() {
    const filename = lang === 'csharp' ? 'bad_csharp.cs' : 'bad_typescript.ts'
    try {
      const { content } = await api.sample(filename)
      setCode(content)
    } catch { setError('Could not load sample file.') }
  }

  async function run() {
    if (!code.trim()) { setError('Paste some code first.'); return }
    setError(''); setRunning(true)
    setClarion(null); setLumen(null); setVector(null); setAscent(null)

    const reset = INITIAL_STEPS
    setSteps(reset)

    try {
      setSteps(s => setStep(s, 'clarion', 'running'))
      const cr = await api.clarion(code, lang)
      setClarion(cr)
      setSteps(s => setStep(setStep(s, 'clarion', 'done'), 'lumen', 'running'))

      const lr = await api.lumen(code, lang)
      setLumen(lr)
      setSteps(s => setStep(setStep(s, 'lumen', 'done'), 'vector', 'running'))

      const vr = await api.vector(code, lang)
      setVector(vr)
      setSteps(s => setStep(setStep(s, 'vector', 'done'), 'ascent', 'running'))

      const ar = await api.ascent(cr, lr, vr, lang)
      setAscent(ar)
      setSteps(s => setStep(s, 'ascent', 'done'))
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'An error occurred')
      setSteps(s => s.map(st => st.status === 'running' ? { ...st, status: 'error' } : st))
    } finally {
      setRunning(false)
    }
  }

  const hasResults = !!ascent

  return (
    <div className="space-y-5">
      {/* Page header */}
      <div>
        <h1 className="text-xl font-bold text-white">Quality Gate</h1>
        <p className="text-sm text-slate-400 mt-1">
          Four agents run in sequence: CLARION checks standards → LUMEN detects smells → VECTOR scores risk → ASCENT consolidates one final recommendation.
        </p>
      </div>

      {/* Pipeline status */}
      <div className="bg-blu-900 border border-blu-600 rounded-xl p-4">
        <AgentPipeline steps={steps} />
      </div>

      <div className="grid grid-cols-[minmax(340px,420px)_1fr] gap-5">
        {/* Left: code input */}
        <div className="space-y-3">
          {/* Controls */}
          <div className="flex gap-2">
            <div className="flex rounded-lg overflow-hidden border border-blu-600 flex-1">
              {(['csharp', 'typescript'] as const).map(l => (
                <button
                  key={l}
                  onClick={() => setLang(l)}
                  className={`flex-1 py-2 text-xs font-semibold transition-colors ${
                    lang === l ? 'bg-blu-primary text-white' : 'text-slate-400 hover:text-white bg-blu-900'
                  }`}
                >
                  {l === 'csharp' ? 'C# / .NET' : 'TypeScript'}
                </button>
              ))}
            </div>
            <button
              onClick={loadSample}
              className="flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-slate-300 bg-blu-800 border border-blu-600 rounded-lg hover:bg-blu-700 transition-colors"
            >
              <FolderOpen size={13} /> Sample
            </button>
          </div>

          {/* Code area */}
          <div className="bg-blu-900 border border-blu-600 rounded-xl overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-2 border-b border-blu-600 bg-blu-800">
              <div className="flex gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full bg-red-500/60" />
                <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/60" />
                <div className="w-2.5 h-2.5 rounded-full bg-green-500/60" />
              </div>
              <span className="text-xs text-slate-500 font-mono">
                {lang === 'csharp' ? 'review.cs' : 'review.ts'}
              </span>
            </div>
            <textarea
              value={code}
              onChange={e => setCode(e.target.value)}
              placeholder={`Paste your ${lang === 'csharp' ? 'C#' : 'TypeScript'} code here…`}
              className="w-full h-80 bg-transparent px-4 py-3 text-xs font-mono text-slate-300 placeholder:text-slate-700 resize-none focus:outline-none"
              spellCheck={false}
            />
          </div>

          <button
            onClick={run}
            disabled={running}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-blu-primary hover:bg-blue-400 disabled:opacity-50 text-white font-semibold text-sm transition-colors"
          >
            <Play size={16} /> {running ? 'Running agents…' : 'Run Full Review'}
          </button>

          {error && (
            <div className="bg-red-950/40 border border-red-700 rounded-lg px-4 py-2.5 text-sm text-red-300">
              {error}
            </div>
          )}
        </div>

        {/* Right: results */}
        <div className="space-y-4 min-w-0">
          {!hasResults && !running && (
            <div className="flex flex-col items-center justify-center h-64 text-slate-600 border border-blu-700 rounded-xl border-dashed">
              <span className="text-4xl mb-3">🔍</span>
              <p className="text-sm">Load sample code or paste your own, then click Run.</p>
            </div>
          )}

          {running && !ascent && (
            <div className="flex flex-col items-center justify-center h-64 gap-3">
              <div className="w-10 h-10 rounded-full border-2 border-blu-primary border-t-transparent animate-spin" />
              <p className="text-sm text-slate-400">Agents are reviewing your code…</p>
            </div>
          )}

          {/* ASCENT recommendation card */}
          {ascent && (() => {
            const rec = ascent.recommendation ?? 'REQUEST_CHANGES'
            const cfg = REC_CONFIG[rec]
            const score = ascent.overall_score ?? 0
            const t1 = ascent.tier1_must_fix ?? []
            const t2 = ascent.tier2_should_fix ?? []
            const t3 = ascent.tier3_consider ?? []
            return (
              <>
                <div className={`rounded-xl border p-5 ${cfg.bg} ${cfg.border} ${cfg.glow}`}>
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-xs text-slate-400 uppercase tracking-widest mb-1">ASCENT Recommendation</p>
                      <p className={`text-3xl font-black ${cfg.color}`}>{rec.replace('_', ' ')}</p>
                      {ascent.summary && <p className="text-sm text-slate-300 mt-2 leading-relaxed">{ascent.summary}</p>}
                    </div>
                    <div className="text-right shrink-0">
                      <p className="text-xs text-slate-400 uppercase tracking-widest mb-1">Score</p>
                      <p className={`text-3xl font-black ${scoreColor(score)}`}>{score}<span className="text-lg text-slate-500">/10</span></p>
                    </div>
                  </div>

                  {/* Finding counts */}
                  <div className="flex gap-4 mt-4 pt-4 border-t border-white/10">
                    <Pill count={t1.length} label="Must Fix"   color="text-red-400" />
                    <Pill count={t2.length} label="Should Fix" color="text-orange-400" />
                    <Pill count={t3.length} label="Consider"   color="text-blue-400" />
                  </div>

                  {ascent.biggest_risk && (
                    <div className="mt-3 flex gap-2 bg-red-900/30 border border-red-700/40 rounded-lg px-3 py-2">
                      <AlertTriangle size={14} className="text-red-400 shrink-0 mt-0.5" />
                      <p className="text-xs text-red-300"><span className="font-semibold">Biggest Risk:</span> {ascent.biggest_risk}</p>
                    </div>
                  )}
                </div>

                {/* Tier 1 */}
                {t1.length > 0 && (
                  <FindingList
                    icon={<ShieldAlert size={15} className="text-red-400" />}
                    title={`Must Fix Before Merge`}
                    count={t1.length}
                    colorClass="border-red-700/40 bg-red-950/20"
                    items={t1}
                    expanded
                  />
                )}

                {/* Tier 2 */}
                {t2.length > 0 && (
                  <FindingList
                    icon={<AlertTriangle size={15} className="text-orange-400" />}
                    title="Should Fix"
                    count={t2.length}
                    colorClass="border-orange-700/40 bg-orange-950/20"
                    items={t2}
                  />
                )}

                {/* Tier 3 */}
                {t3.length > 0 && (
                  <FindingList
                    icon={<Lightbulb size={15} className="text-blue-400" />}
                    title="Consider Fixing"
                    count={t3.length}
                    colorClass="border-blu-600 bg-blu-800"
                    items={t3}
                  />
                )}

                {/* Reviewer checklist */}
                {(ascent.reviewer_checklist ?? []).length > 0 && (
                  <div className="bg-blu-900 border border-blu-600 rounded-xl p-4">
                    <p className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">Reviewer Checklist</p>
                    <ul className="space-y-1.5">
                      {ascent.reviewer_checklist!.map((item, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                          <span className="mt-0.5 w-4 h-4 rounded border border-slate-600 shrink-0" />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Individual agent reports */}
                <div className="space-y-2">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Individual Agent Reports</p>

                  {clarion && (
                    <Collapsible
                      open={openSections.clarion}
                      onToggle={() => setOpenSections(s => ({ ...s, clarion: !s.clarion }))}
                      title={`CLARION — ${(clarion.violations ?? []).length} violation(s)`}
                      score={clarion.overall_score}
                    >
                      <div className="space-y-3 pt-3">
                        {(clarion.violations ?? []).length === 0
                          ? <p className="text-sm text-emerald-400">No violations found.</p>
                          : (clarion.violations ?? []).map((v, i) => (
                            <div key={i} className="border border-blu-600 rounded-lg p-3 bg-blu-800">
                              <div className="flex items-center gap-2 mb-1">
                                <Badge label={v.severity} variant="severity" />
                                <span className="text-xs font-mono text-slate-300">{v.rule}</span>
                                {v.line && <span className="text-xs text-slate-500">Line {v.line}</span>}
                              </div>
                              <p className="text-xs text-slate-300 mb-2">{v.message}</p>
                              {v.fix && <pre className="text-xs bg-blu-950 rounded px-3 py-2 text-emerald-300 overflow-x-auto">{v.fix}</pre>}
                              {v.confidence !== undefined && <ConfidenceBar value={v.confidence} />}
                            </div>
                          ))
                        }
                      </div>
                    </Collapsible>
                  )}

                  {lumen && (
                    <Collapsible
                      open={openSections.lumen}
                      onToggle={() => setOpenSections(s => ({ ...s, lumen: !s.lumen }))}
                      title={`LUMEN — ${(lumen.smells ?? []).length} smell(s)`}
                      score={lumen.maintainability_score}
                    >
                      <div className="space-y-3 pt-3">
                        {(lumen.smells ?? []).length === 0
                          ? <p className="text-sm text-emerald-400">No smells detected.</p>
                          : (lumen.smells ?? []).map((s, i) => (
                            <div key={i} className="border border-blu-600 rounded-lg p-3 bg-blu-800">
                              <div className="flex items-center gap-2 mb-1">
                                <Badge label={s.severity} variant="severity" />
                                <span className="text-xs font-semibold text-slate-200">{s.type}</span>
                                {s.location && <span className="text-xs text-slate-500">{s.location}</span>}
                              </div>
                              {s.description && <p className="text-xs text-slate-400 mb-1">{s.description}</p>}
                              {s.refactor   && <p className="text-xs text-slate-300"><span className="text-slate-500">Refactor:</span> {s.refactor}</p>}
                            </div>
                          ))
                        }
                      </div>
                    </Collapsible>
                  )}

                  {vector && (
                    <Collapsible
                      open={openSections.vector}
                      onToggle={() => setOpenSections(s => ({ ...s, vector: !s.vector }))}
                      title={`VECTOR — Risk: ${vector.overall_risk_level ?? '?'}`}
                      score={vector.overall_risk_score ? +(vector.overall_risk_score * 10).toFixed(1) : undefined}
                    >
                      <div className="pt-3 space-y-3">
                        {vector.static_metrics && (
                          <div className="grid grid-cols-3 gap-2">
                            {[
                              { label: 'Complexity', value: vector.static_metrics.cyclomatic_complexity },
                              { label: 'Nesting',    value: vector.static_metrics.max_nesting_depth },
                              { label: 'Lines',      value: vector.static_metrics.lines_of_code },
                              { label: 'Methods',    value: vector.static_metrics.method_count },
                              { label: 'Deps',       value: vector.static_metrics.dependency_count },
                              { label: 'Sec Ops',    value: vector.static_metrics.has_security_ops ? 'Yes' : 'No' },
                            ].map(m => (
                              <div key={m.label} className="bg-blu-950 rounded-lg px-3 py-2 text-center">
                                <p className="text-xs text-slate-500">{m.label}</p>
                                <p className="text-sm font-bold text-slate-200">{m.value ?? '—'}</p>
                              </div>
                            ))}
                          </div>
                        )}
                        {(vector.hotspots ?? []).map((h, i) => (
                          <div key={i} className="flex items-start gap-2 border border-blu-600 rounded-lg p-3 bg-blu-800">
                            <Badge label={h.risk_level ?? 'LOW'} variant="risk" />
                            <div>
                              {h.name && <p className="text-xs font-semibold text-slate-200">{h.name}</p>}
                              {h.reason && <p className="text-xs text-slate-400">{h.reason}</p>}
                            </div>
                          </div>
                        ))}
                        {vector.reviewer_focus && (
                          <div className="bg-blu-800 border border-blu-primary/30 rounded-lg px-3 py-2 text-xs text-slate-300">
                            <span className="text-blu-primary font-semibold">Focus: </span>{vector.reviewer_focus}
                          </div>
                        )}
                      </div>
                    </Collapsible>
                  )}
                </div>
              </>
            )
          })()}
        </div>
      </div>
    </div>
  )
}

function Pill({ count, label, color }: { count: number; label: string; color: string }) {
  return (
    <div className="text-center">
      <p className={`text-xl font-black ${color}`}>{count}</p>
      <p className="text-xs text-slate-500">{label}</p>
    </div>
  )
}

function FindingList({ icon, title, count, colorClass, items, expanded = false }: {
  icon: React.ReactNode; title: string; count: number; colorClass: string
  items: { source?: string; issue?: string; action?: string }[]; expanded?: boolean
}) {
  const [open, setOpen] = useState(expanded)
  return (
    <div className={`border rounded-xl overflow-hidden ${colorClass}`}>
      <button
        className="w-full flex items-center justify-between px-4 py-3 hover:opacity-90"
        onClick={() => setOpen(v => !v)}
      >
        <div className="flex items-center gap-2">
          {icon}
          <span className="text-sm font-semibold text-white">{title}</span>
          <span className="bg-white/10 text-xs px-2 py-0.5 rounded-full text-slate-300">{count}</span>
        </div>
        {open ? <ChevronDown size={14} className="text-slate-400" /> : <ChevronRight size={14} className="text-slate-400" />}
      </button>
      {open && (
        <div className="px-4 pb-4 space-y-2 border-t border-white/5">
          {items.map((item, i) => (
            <div key={i} className="bg-black/20 rounded-lg p-3">
              <p className="text-xs text-slate-400 mb-0.5 font-mono">[{item.source ?? '?'}]</p>
              <p className="text-sm text-slate-200">{item.issue}</p>
              {item.action && <p className="text-xs text-slate-400 mt-1"><span className="text-slate-500">Action:</span> {item.action}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function Collapsible({ open, onToggle, title, score, children }: {
  open: boolean; onToggle: () => void; title: string
  score?: number; children: React.ReactNode
}) {
  return (
    <div className="bg-blu-900 border border-blu-600 rounded-xl overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-blu-800 transition-colors"
      >
        <span className="text-sm font-semibold text-slate-300">{title}</span>
        <div className="flex items-center gap-3">
          {score !== undefined && (
            <span className={`text-sm font-bold ${scoreColor(score)}`}>{score}/10</span>
          )}
          {open ? <ChevronDown size={14} className="text-slate-500" /> : <ChevronRight size={14} className="text-slate-500" />}
        </div>
      </button>
      {open && <div className="px-4 pb-4 border-t border-blu-600">{children}</div>}
    </div>
  )
}

import { useState } from 'react'
import { Play, FolderOpen, Lock, GitBranch, FileText, Shield } from 'lucide-react'
import { api } from '../api'
import { AgentPipeline, type PipelineStep } from '../components/AgentPipeline'
import { Badge, ConfidenceBar } from '../components/Badge'
import type { AgentStatus, BulwarkResult, ForgeResult, StewardResult } from '../types'

const INITIAL_STEPS: PipelineStep[] = [
  { id: 'watchtower', name: 'WATCHTOWER', description: 'Finding Discovery', status: 'idle' },
  { id: 'bulwark',    name: 'BULWARK',    description: 'Triage & Classify', status: 'idle' },
  { id: 'forge',      name: 'FORGE',      description: 'Fix PR Generation', status: 'idle' },
  { id: 'steward',    name: 'STEWARD',    description: 'Audit Log',         status: 'idle' },
]

function setStep(steps: PipelineStep[], id: string, status: AgentStatus): PipelineStep[] {
  return steps.map(s => s.id === id ? { ...s, status } : s)
}

export function SecurityLoop() {
  const [finding, setFinding]   = useState('')
  const [codeSnip, setCodeSnip] = useState('')
  const [affectedFile, setAffectedFile] = useState('OrdersController.cs')
  const [steps, setSteps]       = useState<PipelineStep[]>(INITIAL_STEPS)
  const [running, setRunning]   = useState(false)
  const [error, setError]       = useState('')

  const [bulwark, setBulwark] = useState<BulwarkResult | null>(null)
  const [forge,   setForge]   = useState<ForgeResult   | null>(null)
  const [steward, setSteward] = useState<StewardResult | null>(null)

  async function loadSample() {
    try {
      const { content } = await api.sample('fortify_finding.txt')
      setFinding(content)
    } catch { setError('Could not load sample.') }
  }

  async function run() {
    if (!finding.trim()) { setError('Enter a finding first.'); return }
    setError(''); setRunning(true)
    setBulwark(null); setForge(null); setSteward(null)
    setSteps(INITIAL_STEPS)

    try {
      // WATCHTOWER — simulated
      setSteps(s => setStep(s, 'watchtower', 'running'))
      await new Promise(r => setTimeout(r, 600))
      setSteps(s => setStep(setStep(s, 'watchtower', 'done'), 'bulwark', 'running'))

      // BULWARK
      const br = await api.bulwark(finding, codeSnip || undefined)
      setBulwark(br)
      const cls = br.classification ?? 'NEEDS_REVIEW'

      if (['CRITICAL', 'HIGH'].includes(cls)) {
        setSteps(s => setStep(setStep(s, 'bulwark', 'done'), 'forge', 'running'))
        // FORGE
        const fr = await api.forge({
          finding,
          classification:  cls,
          owasp_category:  br.owasp_category  ?? '',
          secure_code_fix: br.secure_code_example ?? '',
          affected_file:   affectedFile,
        })
        setForge(fr)
        setSteps(s => setStep(setStep(s, 'forge', 'done'), 'steward', 'running'))

        const sr = await api.steward({
          pipeline:           'Security Loop',
          finding_summary:    finding.slice(0, 200),
          classification:     cls,
          confidence:         br.confidence ?? 0,
          action_taken:       `FORGE created draft PR: ${fr.branch_name ?? 'N/A'}`,
          agents_involved:    ['WATCHTOWER', 'BULWARK', 'FORGE', 'STEWARD'],
          human_gate_required: true,
        })
        setSteward(sr)
      } else {
        setSteps(s => setStep(setStep(s, 'bulwark', 'done'), 'forge', 'skipped'))
        setSteps(s => setStep(s, 'steward', 'running'))
        const sr = await api.steward({
          pipeline:           'Security Loop',
          finding_summary:    finding.slice(0, 200),
          classification:     cls,
          confidence:         br.confidence ?? 0,
          action_taken:       `Classification: ${cls} — no FORGE action required`,
          agents_involved:    ['WATCHTOWER', 'BULWARK', 'STEWARD'],
          human_gate_required: false,
        })
        setSteward(sr)
      }

      setSteps(s => setStep(s, 'steward', 'done'))
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'An error occurred')
      setSteps(s => s.map(st => st.status === 'running' ? { ...st, status: 'error' } : st))
    } finally {
      setRunning(false)
    }
  }

  const cls = bulwark?.classification

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-bold text-white">Security Loop</h1>
        <p className="text-sm text-slate-400 mt-1">
          WATCHTOWER discovers the finding → BULWARK triages and classifies it → FORGE creates a draft fix PR → STEWARD writes the immutable audit entry.
        </p>
      </div>

      <div className="bg-blu-900 border border-blu-600 rounded-xl p-4">
        <AgentPipeline steps={steps} />
      </div>

      <div className="grid grid-cols-[minmax(340px,420px)_1fr] gap-5">
        {/* Left: input */}
        <div className="space-y-3">
          <div>
            <label className="block text-xs text-slate-400 mb-1.5 font-medium uppercase tracking-wider">
              Fortify Finding Description
            </label>
            <div className="bg-blu-900 border border-blu-600 rounded-xl overflow-hidden">
              <div className="flex items-center gap-2 px-4 py-2 border-b border-blu-600 bg-blu-800 justify-between">
                <div className="flex items-center gap-2">
                  <Lock size={12} className="text-slate-500" />
                  <span className="text-xs text-slate-500 font-mono">fortify_finding.txt</span>
                </div>
                <button
                  onClick={loadSample}
                  className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200 transition-colors"
                >
                  <FolderOpen size={12} /> Sample
                </button>
              </div>
              <textarea
                value={finding}
                onChange={e => setFinding(e.target.value)}
                placeholder="Paste the Fortify finding description or describe the vulnerability…"
                className="w-full h-48 bg-transparent px-4 py-3 text-xs font-mono text-slate-300 placeholder:text-slate-700 resize-none focus:outline-none"
                spellCheck={false}
              />
            </div>
          </div>

          <div>
            <label className="block text-xs text-slate-400 mb-1.5 font-medium uppercase tracking-wider">
              Vulnerable Code Snippet <span className="text-slate-600 normal-case">(optional)</span>
            </label>
            <textarea
              value={codeSnip}
              onChange={e => setCodeSnip(e.target.value)}
              placeholder="Paste the vulnerable code here for a more precise fix…"
              className="w-full h-28 bg-blu-900 border border-blu-600 rounded-xl px-4 py-3 text-xs font-mono text-slate-300 placeholder:text-slate-700 resize-none focus:outline-none focus:border-blu-primary transition-colors"
              spellCheck={false}
            />
          </div>

          <div>
            <label className="block text-xs text-slate-400 mb-1.5 font-medium uppercase tracking-wider">
              Affected File
            </label>
            <input
              value={affectedFile}
              onChange={e => setAffectedFile(e.target.value)}
              className="w-full bg-blu-900 border border-blu-600 rounded-lg px-3 py-2 text-xs font-mono text-slate-300 focus:outline-none focus:border-blu-primary transition-colors"
            />
          </div>

          <button
            onClick={run}
            disabled={running}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-blu-primary hover:bg-blue-400 disabled:opacity-50 text-white font-semibold text-sm transition-colors"
          >
            <Play size={16} /> {running ? 'Running pipeline…' : 'Run Security Pipeline'}
          </button>

          {error && (
            <div className="bg-red-950/40 border border-red-700 rounded-lg px-4 py-2.5 text-sm text-red-300">
              {error}
            </div>
          )}
        </div>

        {/* Right: results */}
        <div className="space-y-4 min-w-0">
          {!bulwark && !running && (
            <div className="flex flex-col items-center justify-center h-64 text-slate-600 border border-blu-700 rounded-xl border-dashed">
              <span className="text-4xl mb-3">🔒</span>
              <p className="text-sm">Load a sample finding or paste one, then click Run.</p>
            </div>
          )}

          {running && !bulwark && (
            <div className="flex flex-col items-center justify-center h-64 gap-3">
              <div className="w-10 h-10 rounded-full border-2 border-blu-primary border-t-transparent animate-spin" />
              <p className="text-sm text-slate-400">Running security pipeline…</p>
            </div>
          )}

          {/* WATCHTOWER card */}
          {bulwark && (
            <div className="bg-emerald-950/30 border border-emerald-800 rounded-xl px-4 py-3">
              <div className="flex items-center gap-2">
                <Shield size={14} className="text-emerald-400" />
                <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">WATCHTOWER</span>
              </div>
              <p className="text-sm text-slate-300 mt-1">1 new finding received from Fortify SSC → published to Service Bus → BULWARK picked up</p>
            </div>
          )}

          {/* BULWARK result */}
          {bulwark && (
            <div className="bg-blu-900 border border-blu-600 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <Shield size={15} className="text-blu-primary" />
                <span className="text-sm font-bold text-white uppercase tracking-wider">BULWARK — Triage Result</span>
              </div>

              <div className="flex items-start gap-6 mb-4">
                <div>
                  <p className="text-xs text-slate-500 mb-1">Classification</p>
                  <Badge label={bulwark.classification ?? 'UNKNOWN'} variant="classification" />
                </div>
                {bulwark.owasp_category && (
                  <div>
                    <p className="text-xs text-slate-500 mb-1">OWASP Category</p>
                    <span className="text-xs font-mono text-slate-300 bg-blu-800 px-2 py-1 rounded">
                      {bulwark.owasp_category}
                    </span>
                  </div>
                )}
              </div>

              {bulwark.confidence !== undefined && (
                <div className="mb-4">
                  <p className="text-xs text-slate-500 mb-1">AI Confidence</p>
                  <ConfidenceBar value={bulwark.confidence} />
                </div>
              )}

              {bulwark.attack_scenario && (
                <div className="bg-red-950/40 border border-red-800/40 rounded-lg px-3 py-2.5 mb-3">
                  <p className="text-xs font-semibold text-red-400 mb-1">Attack Scenario</p>
                  <p className="text-sm text-slate-300">{bulwark.attack_scenario}</p>
                </div>
              )}

              {bulwark.affected_systems && (
                <p className="text-sm text-slate-300 mb-3">
                  <span className="text-slate-500">At Risk: </span>{bulwark.affected_systems}
                </p>
              )}

              {bulwark.false_positive_reason && (
                <div className="bg-emerald-950/40 border border-emerald-800/40 rounded-lg px-3 py-2.5 mb-3">
                  <p className="text-xs font-semibold text-emerald-400 mb-1">Why False Positive</p>
                  <p className="text-sm text-slate-300">{bulwark.false_positive_reason}</p>
                </div>
              )}

              {bulwark.secure_code_example && (
                <div>
                  <p className="text-xs text-slate-500 mb-1.5">Secure Code Example</p>
                  <pre className="bg-blu-950 rounded-lg px-4 py-3 text-xs font-mono text-emerald-300 overflow-x-auto">
                    {bulwark.secure_code_example}
                  </pre>
                </div>
              )}
            </div>
          )}

          {/* FORGE result */}
          {forge && (
            <div className="bg-blu-900 border border-blu-600 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <GitBranch size={15} className="text-blu-primary" />
                <span className="text-sm font-bold text-white uppercase tracking-wider">FORGE — Draft Pull Request</span>
              </div>

              <div className="space-y-3">
                <InfoRow label="Branch" value={forge.branch_name} mono />
                <InfoRow label="Commit" value={forge.commit_message} mono />
                <InfoRow label="PR Title" value={forge.pr_title} />
                {forge.files_to_modify && forge.files_to_modify.length > 0 && (
                  <div>
                    <p className="text-xs text-slate-500 mb-1">Files to Modify</p>
                    <div className="flex flex-wrap gap-1">
                      {forge.files_to_modify.map((f, i) => (
                        <span key={i} className="text-xs font-mono bg-blu-800 border border-blu-600 px-2 py-0.5 rounded text-slate-300">{f}</span>
                      ))}
                    </div>
                  </div>
                )}
                {forge.reviewer_note && (
                  <div className="bg-orange-950/30 border border-orange-800/40 rounded-lg px-3 py-2">
                    <p className="text-xs text-orange-300">{forge.reviewer_note}</p>
                  </div>
                )}
              </div>

              <div className="mt-4 bg-orange-950/20 border border-orange-700/40 rounded-lg px-3 py-2.5 flex items-start gap-2">
                <span className="text-orange-400 text-lg leading-none">⚠</span>
                <div>
                  <p className="text-xs font-bold text-orange-400">DRAFT PR — Human Approval Required</p>
                  <p className="text-xs text-slate-400 mt-0.5">FORGE never merges code. The developer reviews this draft before anything is merged.</p>
                </div>
              </div>
            </div>
          )}

          {/* STEWARD audit log */}
          {steward && (
            <div className="bg-blu-900 border border-blu-600 rounded-xl p-5">
              <div className="flex items-center gap-2 mb-4">
                <FileText size={15} className="text-blu-primary" />
                <span className="text-sm font-bold text-white uppercase tracking-wider">STEWARD — Audit Log Entry</span>
              </div>
              <div className="bg-blu-950 rounded-lg p-4 font-mono text-xs space-y-1.5 overflow-x-auto">
                {Object.entries(steward).map(([k, v]) => (
                  <div key={k} className="flex gap-3">
                    <span className="text-slate-600 shrink-0 w-36">{k}:</span>
                    <span className="text-emerald-400">{JSON.stringify(v)}</span>
                  </div>
                ))}
              </div>
              <p className="text-xs text-slate-600 mt-2">In production: Azure Blob Storage (immutable, 7-year retention)</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function InfoRow({ label, value, mono = false }: { label: string; value?: string; mono?: boolean }) {
  if (!value) return null
  return (
    <div>
      <p className="text-xs text-slate-500 mb-0.5">{label}</p>
      <p className={`text-sm text-slate-200 ${mono ? 'font-mono' : ''}`}>{value}</p>
    </div>
  )
}

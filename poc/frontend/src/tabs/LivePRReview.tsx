import { useState, useEffect } from 'react'
import { Play, RefreshCw, Eye, EyeOff, AlertTriangle, ShieldAlert, Lightbulb, ChevronDown, ChevronRight } from 'lucide-react'
import { api } from '../api'
import { Badge } from '../components/Badge'
import type { PR, LiveReviewResult, AscentResult } from '../types'

const REC_CONFIG = {
  APPROVE:         { color: 'text-emerald-400', bg: 'bg-emerald-950/40', border: 'border-emerald-700' },
  REQUEST_CHANGES: { color: 'text-orange-400',  bg: 'bg-orange-950/40',  border: 'border-orange-700' },
  BLOCK:           { color: 'text-red-400',      bg: 'bg-red-950/40',     border: 'border-red-700' },
}

function scoreColor(score: number) {
  if (score >= 7) return 'text-emerald-400'
  if (score >= 4) return 'text-orange-400'
  return 'text-red-400'
}

export function LivePRReview() {
  const [prs, setPrs]           = useState<PR[]>([])
  const [selectedPR, setSelectedPR] = useState<PR | null>(null)
  const [shadowMode, setShadowMode] = useState(true)
  const [loading, setLoading]   = useState(false)
  const [running, setRunning]   = useState(false)
  const [error, setError]       = useState('')
  const [result, setResult]     = useState<LiveReviewResult | null>(null)
  const [adoReady, setAdoReady] = useState(false)
  const [checkingStatus, setCheckingStatus] = useState(true)

  useEffect(() => {
    api.status().then(s => {
      setAdoReady(s.ado_configured)
      setCheckingStatus(false)
    }).catch(() => setCheckingStatus(false))
  }, [])

  async function loadPRs() {
    setLoading(true); setError('')
    try {
      const list = await api.prs()
      setPrs(list)
      if (list.length > 0 && !selectedPR) setSelectedPR(list[0])
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Could not load PRs')
    } finally { setLoading(false) }
  }

  async function runReview() {
    if (!selectedPR) return
    setRunning(true); setResult(null); setError('')
    try {
      const r = await api.liveReview(selectedPR.id, shadowMode)
      setResult(r)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Review failed')
    } finally { setRunning(false) }
  }

  if (checkingStatus) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 rounded-full border-2 border-blu-primary border-t-transparent animate-spin" />
      </div>
    )
  }

  if (!adoReady) {
    return (
      <div className="space-y-5">
        <div>
          <h1 className="text-xl font-bold text-white">Live PR Review</h1>
          <p className="text-sm text-slate-400 mt-1">Connect to your Azure DevOps repository to review real pull requests.</p>
        </div>
        <div className="bg-red-950/30 border border-red-700 rounded-xl p-6">
          <p className="text-sm font-semibold text-red-300 mb-2">Azure DevOps not configured</p>
          <p className="text-sm text-slate-400 mb-4">Enter your Org URL, PAT, Project, and Repo in the sidebar, then click Apply Config.</p>
          <pre className="bg-blu-950 rounded-lg px-4 py-3 text-xs font-mono text-slate-400">
{`# .env — fill in these 4 values
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/your-org
AZURE_DEVOPS_PAT=your-pat-here
AZURE_DEVOPS_PROJECT=YourProject
AZURE_DEVOPS_REPO=YourRepo`}
          </pre>
        </div>
      </div>
    )
  }

  const ascent = result?.ascent

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-bold text-white">Live PR Review</h1>
        <p className="text-sm text-slate-400 mt-1">
          Select an open PR from your Azure DevOps repo. Agents fetch the real diff, run the full Quality Gate, and post findings back as PR comments.
        </p>
      </div>

      {/* Shadow mode + load PRs */}
      <div className="flex items-center gap-4 bg-blu-900 border border-blu-600 rounded-xl px-5 py-4">
        <div className="flex items-center gap-3 flex-1">
          <button
            onClick={() => setShadowMode(v => !v)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-semibold transition-colors ${
              shadowMode
                ? 'bg-orange-950/40 border-orange-700 text-orange-300'
                : 'bg-red-950/40 border-red-700 text-red-300'
            }`}
          >
            {shadowMode ? <Eye size={15} /> : <EyeOff size={15} />}
            Shadow Mode: {shadowMode ? 'ON' : 'OFF'}
          </button>
          <p className="text-xs text-slate-500">
            {shadowMode
              ? 'Agents analyse the PR but post no comments to Azure DevOps.'
              : 'Agents will post real inline comments to the PR.'}
          </p>
        </div>
        <button
          onClick={loadPRs}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 text-sm text-slate-300 bg-blu-800 border border-blu-600 rounded-lg hover:bg-blu-700 transition-colors"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          {loading ? 'Loading…' : 'Load PRs'}
        </button>
      </div>

      {error && (
        <div className="bg-red-950/40 border border-red-700 rounded-lg px-4 py-2.5 text-sm text-red-300">{error}</div>
      )}

      {/* PR list */}
      {prs.length > 0 && (
        <div className="space-y-3">
          <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
            {prs.map(pr => (
              <div
                key={pr.id}
                onClick={() => setSelectedPR(pr)}
                className={`flex items-start gap-4 p-4 rounded-xl border cursor-pointer transition-all ${
                  selectedPR?.id === pr.id
                    ? 'bg-blu-primary/10 border-blu-primary/50'
                    : 'bg-blu-900 border-blu-600 hover:bg-blu-800'
                }`}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-500 font-mono">#{pr.id}</span>
                    <p className="text-sm font-semibold text-white truncate">{pr.title}</p>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    <span className="font-mono text-slate-400">{pr.source_branch}</span>
                    {' → '}
                    <span className="font-mono text-slate-400">{pr.target_branch}</span>
                    {' · '}
                    {pr.created_by}
                  </p>
                </div>
                {selectedPR?.id === pr.id && (
                  <div className="w-2 h-2 rounded-full bg-blu-primary shrink-0 mt-1.5" />
                )}
              </div>
            ))}
          </div>

          {selectedPR && (
            <button
              onClick={runReview}
              disabled={running}
              className="flex items-center justify-center gap-2 w-full py-3 rounded-xl bg-blu-primary hover:bg-blue-400 disabled:opacity-50 text-white font-semibold text-sm transition-colors"
            >
              <Play size={16} />
              {running
                ? 'Running Quality Gate on this PR…'
                : `Run Quality Gate — PR #${selectedPR.id}`}
            </button>
          )}
        </div>
      )}

      {prs.length === 0 && !loading && (
        <div className="flex flex-col items-center justify-center h-40 text-slate-600 border border-blu-700 rounded-xl border-dashed">
          <p className="text-sm">Click "Load PRs" to fetch open pull requests from your repo.</p>
        </div>
      )}

      {/* Running spinner */}
      {running && (
        <div className="flex flex-col items-center justify-center h-48 gap-3">
          <div className="w-10 h-10 rounded-full border-2 border-blu-primary border-t-transparent animate-spin" />
          <p className="text-sm text-slate-400">Fetching PR diff and running all 4 agents…</p>
          <p className="text-xs text-slate-600">This may take 30–60 seconds depending on file count.</p>
        </div>
      )}

      {/* Results */}
      {ascent && (() => {
        const rec = ascent.recommendation ?? 'REQUEST_CHANGES'
        const cfg = REC_CONFIG[rec]
        const score = ascent.overall_score ?? 0
        return (
          <div className="space-y-4">
            {/* Result errors */}
            {(result?.errors ?? []).map((e, i) => (
              <div key={i} className="bg-orange-950/30 border border-orange-700 rounded-lg px-4 py-2.5 text-sm text-orange-300">{e}</div>
            ))}

            {/* ASCENT card */}
            <div className={`rounded-xl border p-5 ${cfg.bg} ${cfg.border}`}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs text-slate-400 uppercase tracking-widest mb-1">ASCENT Recommendation</p>
                  <p className={`text-3xl font-black ${cfg.color}`}>{rec.replace('_', ' ')}</p>
                  {ascent.summary && <p className="text-sm text-slate-300 mt-2">{ascent.summary}</p>}
                </div>
                <div className="text-right shrink-0">
                  <p className="text-xs text-slate-400 uppercase tracking-widest mb-1">Score</p>
                  <p className={`text-3xl font-black ${scoreColor(score)}`}>{score}<span className="text-lg text-slate-500">/10</span></p>
                </div>
              </div>
              <div className="flex gap-4 mt-4 pt-4 border-t border-white/10">
                <div className="text-center">
                  <p className="text-xl font-black text-red-400">{(ascent.tier1_must_fix ?? []).length}</p>
                  <p className="text-xs text-slate-500">Must Fix</p>
                </div>
                <div className="text-center">
                  <p className="text-xl font-black text-orange-400">{(ascent.tier2_should_fix ?? []).length}</p>
                  <p className="text-xs text-slate-500">Should Fix</p>
                </div>
                <div className="text-center">
                  <p className="text-xl font-black text-blue-400">{(ascent.tier3_consider ?? []).length}</p>
                  <p className="text-xs text-slate-500">Consider</p>
                </div>
              </div>
            </div>

            {/* Tiers */}
            {TierBlock({
              items: ascent.tier1_must_fix ?? [],
              icon: <ShieldAlert size={14} className="text-red-400" />,
              title: 'Must Fix Before Merge',
              cls: 'border-red-700/40 bg-red-950/20',
              defaultOpen: true,
            })}
            {TierBlock({
              items: ascent.tier2_should_fix ?? [],
              icon: <AlertTriangle size={14} className="text-orange-400" />,
              title: 'Should Fix',
              cls: 'border-orange-700/40 bg-orange-950/20',
            })}
            {TierBlock({
              items: ascent.tier3_consider ?? [],
              icon: <Lightbulb size={14} className="text-blue-400" />,
              title: 'Consider Fixing',
              cls: 'border-blu-600 bg-blu-800',
            })}

            {/* Files reviewed */}
            {(result?.files ?? []).length > 0 && (
              <div className="bg-blu-900 border border-blu-600 rounded-xl overflow-hidden">
                <p className="px-5 py-3 text-xs font-bold text-slate-300 uppercase tracking-wider border-b border-blu-600">
                  Files Reviewed ({result!.files!.length})
                </p>
                <div className="divide-y divide-blu-700/50">
                  {result!.files!.map((f, i) => {
                    const fname = f.path.split('/').pop() ?? f.path
                    const vCount = (f.clarion.violations ?? []).length
                    const sCount = (f.lumen.smells ?? []).length
                    const risk   = f.vector.overall_risk_level ?? '?'
                    return (
                      <div key={i} className="flex items-center gap-4 px-5 py-3">
                        <span className="text-xs font-mono text-slate-200 flex-1 truncate">{fname}</span>
                        <span className="text-xs text-slate-500">{vCount} violation{vCount !== 1 ? 's' : ''}</span>
                        <span className="text-xs text-slate-500">{sCount} smell{sCount !== 1 ? 's' : ''}</span>
                        <Badge label={risk} variant="risk" />
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Shadow mode notice */}
            {shadowMode ? (
              <div className="bg-orange-950/30 border border-orange-700/50 rounded-xl px-4 py-3 flex items-start gap-2">
                <Eye size={15} className="text-orange-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-semibold text-orange-300">Shadow Mode ON — nothing posted to Azure DevOps</p>
                  <p className="text-xs text-slate-400 mt-0.5">Toggle Shadow Mode OFF and re-run to post real inline comments to this PR.</p>
                </div>
              </div>
            ) : result?.posted ? (
              <div className="bg-emerald-950/30 border border-emerald-700/50 rounded-xl px-4 py-3 text-sm text-emerald-300">
                Comments posted to PR #{selectedPR?.id} in Azure DevOps. Open your PR to see inline findings and summary.
              </div>
            ) : null}
          </div>
        )
      })()}
    </div>
  )
}

function TierBlock({ items, icon, title, cls, defaultOpen = false }: {
  items: AscentResult['tier1_must_fix']; icon: React.ReactNode
  title: string; cls: string; defaultOpen?: boolean
}) {
  const [open, setOpen] = useState(defaultOpen)
  if (!items || items.length === 0) return null
  return (
    <div className={`border rounded-xl overflow-hidden ${cls}`}>
      <button
        className="w-full flex items-center justify-between px-4 py-3"
        onClick={() => setOpen(v => !v)}
      >
        <div className="flex items-center gap-2">
          {icon}
          <span className="text-sm font-semibold text-white">{title}</span>
          <span className="bg-white/10 text-xs px-2 py-0.5 rounded-full text-slate-300">{items.length}</span>
        </div>
        {open ? <ChevronDown size={14} className="text-slate-400" /> : <ChevronRight size={14} className="text-slate-400" />}
      </button>
      {open && (
        <div className="px-4 pb-4 space-y-2 border-t border-white/5">
          {items.map((item, i) => (
            <div key={i} className="bg-black/20 rounded-lg p-3">
              <p className="text-xs text-slate-400 mb-0.5 font-mono">[{item?.source ?? '?'}]</p>
              <p className="text-sm text-slate-200">{item?.issue}</p>
              {item?.action && <p className="text-xs text-slate-400 mt-1"><span className="text-slate-500">Action:</span> {item.action}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

import { useState, useEffect } from 'react'
import { Settings, ChevronDown, ChevronUp, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import { api } from '../api'
import type { AppStatus } from '../types'

interface Props {
  status: AppStatus
  onStatusChange: (s: AppStatus) => void
}

export function Sidebar({ status, onStatusChange }: Props) {
  const [provider, setProvider] = useState<'azure_openai' | 'anthropic'>('azure_openai')
  const [azEndpoint, setAzEndpoint] = useState('')
  const [azKey, setAzKey] = useState('')
  const [azDeployment, setAzDeployment] = useState('gpt-4o')
  const [antKey, setAntKey] = useState('')
  const [adoOrg, setAdoOrg] = useState('')
  const [adoPat, setAdoPat] = useState('')
  const [adoProject, setAdoProject] = useState('')
  const [adoRepo, setAdoRepo] = useState('')
  const [saving, setSaving] = useState(false)
  const [aiOpen, setAiOpen] = useState(true)
  const [adoOpen, setAdoOpen] = useState(false)

  useEffect(() => {
    api.status().then(onStatusChange).catch(() => {})
  }, [])

  async function save() {
    setSaving(true)
    try {
      const payload: Record<string, unknown> = { provider }
      if (provider === 'azure_openai') {
        if (azEndpoint)   payload.azure_endpoint   = azEndpoint
        if (azKey)        payload.azure_key        = azKey
        if (azDeployment) payload.azure_deployment = azDeployment
      } else {
        if (antKey) payload.anthropic_key = antKey
      }
      if (adoOrg)     payload.ado_org     = adoOrg
      if (adoPat)     payload.ado_pat     = adoPat
      if (adoProject) payload.ado_project = adoProject
      if (adoRepo)    payload.ado_repo    = adoRepo
      const s = await api.setConfig(payload)
      onStatusChange(s)
    } catch (e) {
      console.error(e)
    } finally {
      setSaving(false)
    }
  }

  const aiOk  = status.ai_provider !== 'none'
  const adoOk = status.ado_configured

  return (
    <aside className="w-72 shrink-0 bg-blu-900 border-r border-blu-600 flex flex-col h-full overflow-y-auto">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-blu-600">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blu-primary/20 border border-blu-primary/40 flex items-center justify-center">
            <span className="text-blu-primary font-bold text-sm">BL</span>
          </div>
          <div>
            <div className="font-bold text-white text-sm leading-tight">Project BlueLine</div>
            <div className="text-xs text-slate-500 leading-tight">AI Engineering Automation</div>
          </div>
        </div>

        {/* Status pills */}
        <div className="flex gap-2 mt-3">
          <StatusPill
            ok={aiOk}
            label={
              status.ai_provider === 'azure_openai' ? 'Azure OpenAI' :
              status.ai_provider === 'anthropic'    ? 'Anthropic'    : 'AI'
            }
          />
          <StatusPill ok={adoOk} label="Azure DevOps" />
        </div>
      </div>

      {/* AI Provider */}
      <Section
        title="AI Provider"
        icon={<Settings size={13} />}
        open={aiOpen}
        onToggle={() => setAiOpen(v => !v)}
      >
        <div className="flex rounded-lg overflow-hidden border border-blu-600 mb-3">
          <ProviderBtn
            active={provider === 'azure_openai'}
            onClick={() => setProvider('azure_openai')}
            label="Azure OpenAI"
          />
          <ProviderBtn
            active={provider === 'anthropic'}
            onClick={() => setProvider('anthropic')}
            label="Anthropic"
          />
        </div>

        {provider === 'azure_openai' ? (
          <>
            <Field
              label="Endpoint"
              value={azEndpoint}
              onChange={setAzEndpoint}
              placeholder="https://YOUR.openai.azure.com/"
            />
            <Field
              label="API Key"
              value={azKey}
              onChange={setAzKey}
              type="password"
              placeholder="••••••••••••"
            />
            <Field
              label="Deployment"
              value={azDeployment}
              onChange={setAzDeployment}
              placeholder="gpt-4o"
            />
            <p className="text-xs text-emerald-500 mt-1">Data stays in your Azure tenant</p>
          </>
        ) : (
          <>
            <Field
              label="API Key"
              value={antKey}
              onChange={setAntKey}
              type="password"
              placeholder="sk-ant-••••••••"
            />
            <p className="text-xs text-orange-400 mt-1">Data sent to Anthropic servers</p>
          </>
        )}
      </Section>

      {/* Azure DevOps */}
      <Section
        title="Azure DevOps"
        icon={<Settings size={13} />}
        open={adoOpen}
        onToggle={() => setAdoOpen(v => !v)}
      >
        <Field label="Org URL"  value={adoOrg}     onChange={setAdoOrg}     placeholder="https://dev.azure.com/org" />
        <Field label="PAT"      value={adoPat}      onChange={setAdoPat}     type="password" placeholder="••••••••••" />
        <Field label="Project"  value={adoProject}  onChange={setAdoProject} placeholder="YourProject" />
        <Field label="Repo"     value={adoRepo}     onChange={setAdoRepo}    placeholder="YourRepo" />
      </Section>

      {/* Save */}
      <div className="px-4 pb-4 mt-auto">
        <button
          onClick={save}
          disabled={saving}
          className="w-full py-2 rounded-lg bg-blu-primary hover:bg-blue-400 disabled:opacity-50 text-white text-sm font-semibold transition-colors"
        >
          {saving ? 'Saving…' : 'Apply Config'}
        </button>
        <p className="text-center text-xs text-slate-600 mt-3">POC v1.0 · BlueLine Team</p>
      </div>
    </aside>
  )
}

function StatusPill({ ok, label }: { ok: boolean; label: string }) {
  return (
    <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs border ${
      ok
        ? 'bg-emerald-950/50 border-emerald-700 text-emerald-400'
        : 'bg-red-950/50 border-red-800 text-red-400'
    }`}>
      {ok
        ? <CheckCircle size={10} />
        : <XCircle size={10} />
      }
      {label}
    </div>
  )
}

function Section({ title, icon, open, onToggle, children }: {
  title: string; icon: React.ReactNode; open: boolean
  onToggle: () => void; children: React.ReactNode
}) {
  return (
    <div className="border-b border-blu-600">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between px-5 py-3 hover:bg-blu-800 transition-colors"
      >
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-300 uppercase tracking-wider">
          {icon} {title}
        </div>
        {open ? <ChevronUp size={14} className="text-slate-500" /> : <ChevronDown size={14} className="text-slate-500" />}
      </button>
      {open && <div className="px-5 pb-4 space-y-2">{children}</div>}
    </div>
  )
}

function ProviderBtn({ active, onClick, label }: { active: boolean; onClick: () => void; label: string }) {
  return (
    <button
      onClick={onClick}
      className={`flex-1 py-1.5 text-xs font-medium transition-colors ${
        active
          ? 'bg-blu-primary text-white'
          : 'text-slate-400 hover:text-white hover:bg-blu-700'
      }`}
    >
      {label}
    </button>
  )
}

function Field({ label, value, onChange, placeholder, type = 'text' }: {
  label: string; value: string; onChange: (v: string) => void
  placeholder?: string; type?: string
}) {
  return (
    <div>
      <label className="block text-xs text-slate-400 mb-1">{label}</label>
      <input
        type={type}
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full bg-blu-800 border border-blu-600 rounded px-2.5 py-1.5 text-xs text-slate-200 placeholder:text-slate-600 focus:border-blu-primary focus:outline-none transition-colors"
      />
    </div>
  )
}

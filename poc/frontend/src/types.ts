export type AgentStatus = 'idle' | 'running' | 'done' | 'error' | 'skipped'

// ── Quality Gate ──────────────────────────────────────────────────────────────

export interface Violation {
  rule: string
  severity: string
  line?: number
  message: string
  fix?: string
  confidence?: number
}

export interface ClarionResult {
  violations?: Violation[]
  overall_score?: number
  files_checked?: number
  language?: string
}

export interface Smell {
  type: string
  severity: string
  location?: string
  description?: string
  refactor?: string
  effort?: string
}

export interface LumenResult {
  smells?: Smell[]
  maintainability_score?: number
  summary?: string
}

export interface StaticMetrics {
  cyclomatic_complexity?: number
  max_nesting_depth?: number
  lines_of_code?: number
  method_count?: number
  dependency_count?: number
  has_security_ops?: boolean
}

export interface Hotspot {
  name?: string
  location?: string
  risk_level?: string
  reason?: string
  reviewer_focus?: string
}

export interface VectorResult {
  overall_risk_score?: number
  overall_risk_level?: string
  static_metrics?: StaticMetrics
  hotspots?: Hotspot[]
  reviewer_focus?: string
}

export interface TierItem {
  source?: string
  issue?: string
  action?: string
}

export interface AscentResult {
  recommendation?: 'APPROVE' | 'REQUEST_CHANGES' | 'BLOCK'
  overall_score?: number
  summary?: string
  biggest_risk?: string
  tier1_must_fix?: TierItem[]
  tier2_should_fix?: TierItem[]
  tier3_consider?: TierItem[]
  reviewer_checklist?: string[]
}

// ── Security Loop ─────────────────────────────────────────────────────────────

export interface BulwarkResult {
  classification?: string
  confidence?: number
  owasp_category?: string
  attack_scenario?: string
  affected_systems?: string
  false_positive_reason?: string
  recommendation?: string
  secure_code_example?: string
}

export interface ForgeResult {
  branch_name?: string
  commit_message?: string
  pr_title?: string
  pr_description?: string
  files_to_modify?: string[]
  reviewer_note?: string
}

export interface StewardResult {
  run_id?: string
  timestamp_utc?: string
  pipeline?: string
  classification?: string
  action_taken?: string
  human_gate_required?: boolean
  human_gate_status?: string
  immutable?: boolean
  [key: string]: unknown
}

// ── Certificate Loop ──────────────────────────────────────────────────────────

export interface Certificate {
  name: string
  subject: string
  expiry_date: string
  days_remaining: number
  status: string
  ca_type: string
  owner: string
  environments: string[]
  deployment_targets: Record<string, string>
}

export interface TimelineResult {
  urgency?: string
  days_until_expiry?: number
  risk_level?: string
  renewal_path?: string
  action_plan?: string[]
  risks?: string[]
  summary?: string
  automation_possible?: boolean
}

export interface CourierResult {
  request_summary?: string
  ca_order_id?: string
  validation_method?: string
  estimated_delivery?: string
  cert_format?: string
  simulated_thumbprint?: string
  cert_download_ready?: boolean
  simulation_note?: string
}

export interface DeploymentItem {
  environment: string
  target?: string
  method?: string
  commands?: string[]
  https_verification?: string
  status?: string
}

export interface TeamsCard {
  title?: string
  body?: string
  approve_action?: string
  reject_action?: string
  domain?: string
  new_expiry?: string
}

export interface HarbourResult {
  deployment_plan?: DeploymentItem[]
  teams_approval_card?: TeamsCard
  production_gate?: string
  simulation_note?: string
}

// ── Live PR Review ────────────────────────────────────────────────────────────

export interface PR {
  id: number
  title: string
  created_by: string
  source_branch: string
  target_branch: string
}

export interface LiveReviewFile {
  path: string
  lang: string
  clarion: ClarionResult
  lumen: LumenResult
  vector: VectorResult
}

export interface LiveReviewResult {
  ascent?: AscentResult
  files?: LiveReviewFile[]
  posted?: boolean
  summary_comment?: string
  errors?: string[]
}

// ── Config ────────────────────────────────────────────────────────────────────

export interface AppStatus {
  ai_provider: 'azure_openai' | 'anthropic' | 'none'
  ado_configured: boolean
}

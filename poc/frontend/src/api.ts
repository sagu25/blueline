import type {
  AppStatus, ClarionResult, LumenResult, VectorResult, AscentResult,
  BulwarkResult, ForgeResult, StewardResult, Certificate, TimelineResult,
  CourierResult, HarbourResult, PR, LiveReviewResult,
} from './types'

async function req<T>(method: string, path: string, body?: unknown): Promise<T> {
  const res = await fetch(`/api${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? 'Request failed')
  }
  return res.json() as Promise<T>
}

export const api = {
  // Status & config
  status: () => req<AppStatus>('GET', '/status'),
  setConfig: (data: Record<string, unknown>) => req<AppStatus>('POST', '/config', data),

  // Samples
  sample: (filename: string) => req<{ content: string }>('GET', `/sample/${filename}`),

  // Quality Gate
  clarion: (code: string, language: string) =>
    req<ClarionResult>('POST', '/clarion', { code, language }),
  lumen: (code: string, language: string) =>
    req<LumenResult>('POST', '/lumen', { code, language }),
  vector: (code: string, language: string) =>
    req<VectorResult>('POST', '/vector', { code, language }),
  ascent: (clarion: object, lumen: object, vector: object, language: string) =>
    req<AscentResult>('POST', '/ascent', { clarion, lumen, vector, language }),

  // Security Loop
  bulwark: (finding: string, code_snippet?: string) =>
    req<BulwarkResult>('POST', '/bulwark', { finding, code_snippet }),
  forge: (data: object) => req<ForgeResult>('POST', '/forge', data),
  steward: (data: object) => req<StewardResult>('POST', '/steward', data),

  // Certificate Loop
  certificates: () => req<Certificate[]>('GET', '/certificates'),
  timeline: (data: object) => req<TimelineResult>('POST', '/timeline', data),
  courier: (data: object) => req<CourierResult>('POST', '/courier', data),
  harbour: (data: object) => req<HarbourResult>('POST', '/harbour', data),

  // Live PR Review
  prs: () => req<PR[]>('GET', '/prs'),
  liveReview: (pr_id: number, shadow_mode: boolean) =>
    req<LiveReviewResult>('POST', '/live-review', { pr_id, shadow_mode }),
}

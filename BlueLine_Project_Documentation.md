# Project BlueLine — Project Documentation

**Version:** 1.0
**Date:** 2026-05-26
**Prepared by:** Project BlueLine Team
**Status:** In Progress

---

## Table of Contents

1. [Tech Stack & Environment](#1-tech-stack--environment)
2. [Governance & Execution](#2-governance--execution)
3. [Agent 1 — CLARION](#agent-1-clarion)
4. [Agent 2 — LUMEN](#agent-2-lumen)
5. [Agent 3 — VECTOR](#agent-3-vector)
6. [Agent 4 — ASCENT](#agent-4-ascent)
7. [Agent 5 — BULWARK](#agent-5-bulwark)
8. [Agent 6 — WATCHTOWER](#agent-6-watchtower)
9. [Agent 7 — FORGE](#agent-7-forge)
10. [Agent 8 — STEWARD](#agent-8-steward)
11. [Agent 9 — TIMELINE](#agent-9-timeline)
12. [Agent 10 — REGENT](#agent-10-regent)
13. [Agent 11 — COURIER](#agent-11-courier)
14. [Agent 12 — HARBOUR](#agent-12-harbour)
15. [Standard Documentation Folder Structure](#standard-documentation-folder-structure)

---

## 1. Tech Stack & Environment

### Frameworks, LLMs & Infrastructure

| Layer | Technology |
|---|---|
| AI / LLM | Claude (claude-sonnet-4-6) via Anthropic API |
| Agent Runtime | Azure Functions (Python 3.11) |
| Orchestration | Azure Durable Functions (Quality Gate parallel fan-out) |
| Messaging | Azure Service Bus (agent-to-agent communication) |
| Storage | Azure Blob Storage (audit logs, cert files), Azure Table Storage (inventory) |
| Secrets | Azure Key Vault (certificates, credentials, API keys) |
| Monitoring | Azure Monitor, Application Insights |
| Source Control | Azure DevOps / GitHub |
| Language | Python 3.11 (agent logic), C# .NET + TypeScript Angular (target codebases) |
| Security Scanning | Fortify Software Security Center (Fortify SSC) REST API |
| Certificate Deployment | IIS (WinRM / PowerShell), Azure App Service (Azure SDK) |

### Integration Landscape — External Systems

| System | Purpose | Track |
|---|---|---|
| Azure DevOps / GitHub | PR webhook trigger, inline PR comments, branch/PR creation | Quality Gate, Security |
| Fortify SSC | Fetch vulnerability findings, suppress false positives, trigger scans | Security |
| Azure Key Vault | Read/write certificate metadata and files | Certificate Loop |
| Certificate Authority (Internal C&M Portal / DigiCert) | Request and download renewed SSL/TLS certificates | Certificate Loop |
| IIS (WinRM) | Remote certificate deployment on Windows servers | Certificate Loop |
| Azure App Service | Certificate binding via Azure SDK | Certificate Loop |
| Azure Service Bus | Event-driven messaging between agents | All Tracks |
| Microsoft Teams / Email | Human approval notifications (Prod gate) | Certificate Loop, Security |

---

## 2. Governance & Execution

### Dependencies

| Dependency | Owner | Required For |
|---|---|---|
| Fortify SSC API access and credentials | InfoSec / Security Team | BULWARK, WATCHTOWER |
| Azure DevOps / GitHub webhook configuration | DevOps | CLARION, LUMEN, VECTOR, ASCENT, FORGE |
| Azure Key Vault access (read/write) | Ops / Platform | TIMELINE, REGENT, COURIER, HARBOUR |
| CA API credentials (Internal C&M or DigiCert) | InfoSec | COURIER |
| IIS / App Service deployment credentials | Ops | HARBOUR |
| Anthropic API key (Claude) | BlueLine Team | All agents |
| Azure Function App provisioning | Platform / DevOps | All agents |
| Azure Service Bus namespace and topics | Platform | All agents |
| Coding standards documentation | Engineering Lead | CLARION, LUMEN |
| Azure Monitor / App Insights workspace | Platform | All agents |

### Status Tracker

**Project Lifecycle:** Requirement → Design → Development → Testing → Deployment

| Track | Current Phase | Notes |
|---|---|---|
| Quality Gate (CLARION, LUMEN, VECTOR, ASCENT) | Development | POC agents built; integration pending |
| Security Loop (BULWARK, WATCHTOWER, FORGE, STEWARD) | Development | Fortify SSC API access being provisioned |
| Certificate Loop (TIMELINE, REGENT, COURIER, HARBOUR) | Design | Pending Key Vault audit and CA API access |

### Stakeholders

| Role | Name / Team | Interest |
|---|---|---|
| Project Sponsor | Core & Main Leadership | Delivery of automation, cost reduction |
| Primary Contact / Architect | Pankaj Pathak | Architecture and implementation oversight |
| Engineering Team | Core & Main Developers | Reduced review burden, consistent quality standards |
| InfoSec Team | Security / InfoSec | Fortify integration, vulnerability visibility, certificate governance |
| Operations Team | DevOps / Ops | Certificate deployment, IIS management, infrastructure |
| AI Agents (automated) | BlueLine Agent Suite | Execution of defined automation tasks |

### For Completed Projects

> **Status: In Progress** — Project BlueLine is currently in the Development phase across Quality Gate and Security tracks. This section will be completed upon full production rollout.

- **Project Completion Summary:** To be filled on project close.
- **Business Impact:** To be measured post-rollout (target: >60% reduction in manual review time, zero certificate expiry incidents).

---

---

# Agent-Level Documentation Checklist

> Required for each individual agent.

---

## Agent 1: CLARION

### Core Definition

| Field | Value |
|---|---|
| Agent Name | CLARION |
| Agent ID | BL-QG-001 |
| Project Mapping | Project BlueLine — Quality Gate Track |
| Status Lifecycle | Development → Testing |
| Trigger Type | Event-based (PR webhook) |
| Human Gate | No |

### Problem & Purpose (MANDATORY)

**Agent-Level Problem Statement:**
Pull request reviewers manually check every code change against .NET and Angular coding standards, producing inconsistent results that depend on individual reviewer experience and availability. There is no automated enforcement of naming conventions, structural patterns, or security smells at the PR stage.

**Executive Summary:**
CLARION is an AI-powered coding standards enforcement agent that automatically reviews every PR diff against established .NET (C#) and Angular (TypeScript) guidelines. It posts inline comments on specific lines with the exact violation, the rule breached, the reason it matters, and a corrected code snippet — giving human reviewers a pre-annotated PR so they can focus on logic and context rather than style checking.

**Business Value:** Eliminates inconsistent code quality enforcement; reduces reviewer cognitive load; catches standards violations before merge; produces a consistent, auditable review record on every PR.

### Functional Design

**Functional Flow (Step-by-Step):**

1. Developer opens or updates a PR in Azure DevOps / GitHub.
2. Webhook fires; CLARION receives the PR ID.
3. CLARION calls Claude with its system prompt (coding rules) and the PR context.
4. Claude calls tool `fetch_pr_diff` to retrieve the full code diff.
5. Claude analyses each changed file against .NET and Angular standards.
6. For each violation found, Claude calls `post_pr_comment` with: file path, line number, violation type, explanation, confidence score, and corrected code.
7. CLARION logs all actions to the audit trail and returns an AgentResult.

**Inputs / Outputs:**

| | Detail |
|---|---|
| Input | PR ID, PR diff (C# / TypeScript files), coding ruleset (loaded into system prompt) |
| Output | Inline PR comments (file, line, rule, explanation, fix, confidence score) |
| Output Format | Azure DevOps / GitHub PR review comments |

**Trigger Type:** Event-based (Azure DevOps PR webhook on PR opened / updated)

### Architecture (MANDATORY)

**Conceptual Diagram:**
```
PR Opened
    |
    v
Azure DevOps Webhook
    |
    v
CLARION (Azure Function)
    |
    +-- System Prompt: .NET + Angular coding rules (cached)
    +-- Tool: fetch_pr_diff  --> Azure DevOps API
    +-- Tool: post_pr_comment --> Azure DevOps API
    |
    v
Inline PR Comments posted
    |
    v
Audit Log written --> Azure Blob Storage
```

**HLD:** See Diagrams/HLD/CLARION_HLD.png

**LLD:** See Diagrams/LLD/CLARION_LLD.png (must be completed before Production)

### AI / Agent Configuration

**Model:** claude-sonnet-4-6 (Anthropic API)

**System Prompt Summary:**
"You are CLARION, a coding standards enforcement agent for a .NET (C#) and Angular (TypeScript) codebase. Check the provided PR diff for: naming convention violations, structural pattern issues, type safety problems, security anti-patterns, and maintainability smells. Only flag violations you are confident about (confidence >= 0.7). For every violation provide: the exact file and line, the rule breached, why it matters, and the corrected code. Never block a PR — your role is advisory."

**Prompt Caching:** Enabled — coding standards document cached after first call (~60% cost reduction on repeated PR reviews).

**Tools / API Specifications:**

| Tool | API | Description |
|---|---|---|
| `fetch_pr_diff` | Azure DevOps REST API / GitHub API | Fetches the full PR diff |
| `post_pr_comment` | Azure DevOps REST API / GitHub API | Posts inline comment on a specific file and line |

### Engineering & Access

| Field | Value |
|---|---|
| Repo Link | poc/agents/ (BlueLine monorepo) |
| Environment Mapping | Dev -> QA -> Prod |
| Dev Environment | Azure Function App (local emulator / dev slot) |
| QA Environment | Azure Function App (QA slot) |
| Prod Environment | Azure Function App (Premium plan, always-warm) |
| Credentials Required | Anthropic API key, Azure DevOps PAT / GitHub token |

### Operations & Visibility

- **Monitoring & Logging:** All agent runs logged to Azure Application Insights (run_id, PR ID, violation count, latency, confidence scores). Alert on error rate > 5%.
- **Support / Runbook:** If CLARION fails to post comments, check: (1) webhook delivery in Azure DevOps, (2) Function App health, (3) Anthropic API key validity. Retry is idempotent.
- **Catalogue / Nav:** Register in internal AI agent catalogue under "Quality Gate > CLARION."

### Knowledge & Training

- **Demo Recordings:** To be added after first live PR review demo.
- **KT / KM Session Links:** To be scheduled with Engineering Lead after QA validation.

### Lifecycle Operations

- **Pause / Restart:** Disable the Azure DevOps webhook subscription to pause CLARION without touching the Function App. Re-enable to restart.
- **Intern ID Deactivation / Access Cleanup:** Remove intern PAT tokens from Key Vault; rotate shared service principal credentials.

### For Completed Agents

> **Status: In Development** — To be completed upon production sign-off.

---

## Agent 2: LUMEN

### Core Definition

| Field | Value |
|---|---|
| Agent Name | LUMEN |
| Agent ID | BL-QG-002 |
| Project Mapping | Project BlueLine — Quality Gate Track |
| Status Lifecycle | Development -> Testing |
| Trigger Type | Event-based (PR webhook) |
| Human Gate | No |

### Problem & Purpose (MANDATORY)

**Agent-Level Problem Statement:**
Code smells and anti-patterns — duplicated logic, overly complex methods, poor separation of concerns, God classes — are identified inconsistently during PR review. No automated tooling currently flags these structural issues before a human reviewer sees the PR.

**Executive Summary:**
LUMEN detects code smells and anti-patterns in PR diffs for .NET and Angular codebases. It annotates PRs with identified smells, an explanation of the structural problem, its long-term impact, and a recommended refactor — without blocking the PR.

**Business Value:** Surfaces technical debt at the point of introduction rather than at refactor time; builds shared team understanding of clean-code standards; produces an auditable record of smell occurrences over time.

### Functional Design

**Functional Flow (Step-by-Step):**

1. PR opened/updated — webhook fires — LUMEN receives PR ID (same trigger as CLARION, runs in parallel via Azure Durable Functions fan-out).
2. LUMEN calls Claude with its code smell system prompt and the PR context.
3. Claude calls `fetch_pr_diff` to retrieve the full code diff.
4. Claude analyses the diff for structural issues: duplicated code, long methods, deep nesting, excessive coupling, feature envy, God objects, missing abstractions.
5. For each smell found, Claude calls `post_pr_comment` with: smell name, location, explanation, impact, refactor suggestion, and confidence score.
6. LUMEN logs actions and returns AgentResult.

**Inputs / Outputs:**

| | Detail |
|---|---|
| Input | PR ID, PR diff (C# / TypeScript files) |
| Output | Inline PR comments annotating code smells with explanations and refactor suggestions |
| Output Format | Azure DevOps / GitHub PR review comments |

**Trigger Type:** Event-based (Azure DevOps PR webhook, parallel with CLARION and VECTOR)

### Architecture (MANDATORY)

**Conceptual Diagram:**
```
PR Opened
    |
    v
Azure Durable Functions Fan-Out
    |
    +-- CLARION (parallel)
    +-- LUMEN   (parallel)   <- this agent
    +-- VECTOR  (parallel)
    |
    v
LUMEN analyses diff for code smells
    +-- Tool: fetch_pr_diff
    +-- Tool: post_pr_comment
    |
    v
Smell annotations posted to PR
```

**HLD:** See Diagrams/HLD/LUMEN_HLD.png

**LLD:** See Diagrams/LLD/LUMEN_LLD.png (must be completed before Production)

### AI / Agent Configuration

**Model:** claude-sonnet-4-6 (Anthropic API)

**System Prompt Summary:**
"You are LUMEN, a code smell and anti-pattern detection agent. Analyse the PR diff for: God classes, long methods (>40 lines), deep nesting (>3 levels), duplicated code blocks, feature envy, inappropriate intimacy, data clumps, and primitive obsession. For each smell found: name it, locate it precisely, explain why it is a smell, describe its long-term impact, and suggest a concrete refactor. Confidence must be >= 0.7 to flag."

**Prompt Caching:** Enabled.

**Tools / API Specifications:**

| Tool | API | Description |
|---|---|---|
| `fetch_pr_diff` | Azure DevOps REST API / GitHub API | Fetches the full PR diff |
| `post_pr_comment` | Azure DevOps REST API / GitHub API | Posts inline smell annotation |

### Engineering & Access

| Field | Value |
|---|---|
| Repo Link | poc/agents/ (BlueLine monorepo) |
| Environment Mapping | Dev -> QA -> Prod |
| Credentials Required | Anthropic API key, Azure DevOps PAT / GitHub token |

### Operations & Visibility

- **Monitoring & Logging:** Azure Application Insights — smell count per PR, confidence distribution, latency.
- **Support / Runbook:** Same runbook as CLARION (shared webhook and Function App).
- **Catalogue:** Register in internal AI agent catalogue under "Quality Gate > LUMEN."

### Knowledge & Training

- **Demo Recordings:** To be added.
- **KT / KM Session Links:** To be scheduled.

### Lifecycle Operations

- **Pause / Restart:** Disable from the Durable Functions orchestrator configuration. CLARION and VECTOR continue to operate independently.
- **Intern ID Deactivation / Access Cleanup:** Rotate shared service principal credentials.

### For Completed Agents

> **Status: In Development.**

---

## Agent 3: VECTOR

### Core Definition

| Field | Value |
|---|---|
| Agent Name | VECTOR |
| Agent ID | BL-QG-003 |
| Project Mapping | Project BlueLine — Quality Gate Track |
| Status Lifecycle | Development -> Testing |
| Trigger Type | Event-based (PR webhook) |
| Human Gate | No |

### Problem & Purpose (MANDATORY)

**Agent-Level Problem Statement:**
Human reviewers have no objective signal about which files in a PR carry the most risk or complexity. High-risk files are reviewed with the same attention as trivial ones, causing reviewers to miss critical areas.

**Executive Summary:**
VECTOR scores each changed file in a PR for risk and complexity using git history (churn rate, bug-fix frequency) and static analysis (cyclomatic complexity, coupling). It posts a per-file risk summary and flags high-risk files so the human reviewer knows where to focus attention.

**Business Value:** Concentrates human review effort on highest-risk code; quantifies risk objectively; reduces probability of critical bugs reaching production.

### Functional Design

**Functional Flow (Step-by-Step):**

1. PR webhook fires — VECTOR receives PR ID (runs in parallel with CLARION and LUMEN).
2. VECTOR calls Claude with risk scoring instructions.
3. Claude calls `fetch_pr_diff` to retrieve changed files.
4. Claude calls `query_git_history` for each changed file to get churn rate and bug-fix commit frequency.
5. Claude calculates a risk score (0.0-1.0) per file combining churn, complexity, and coupling signals.
6. Claude calls `post_pr_comment` with a risk summary table and attention flags on high-risk files (score >= 0.7).
7. VECTOR returns AgentResult with risk scores for ASCENT to consume.

**Inputs / Outputs:**

| | Detail |
|---|---|
| Input | PR ID, PR diff, git history for changed files |
| Output | Per-file risk score (0.0-1.0), reviewer attention flags on high-risk files |
| Output Format | PR comment with risk summary table |

**Trigger Type:** Event-based (parallel with CLARION and LUMEN)

### Architecture (MANDATORY)

**Conceptual Diagram:**
```
PR Opened
    |
    v
VECTOR (parallel in Durable Functions fan-out)
    +-- Tool: fetch_pr_diff
    +-- Tool: query_git_history --> Azure DevOps / GitHub API (per file)
    +-- Tool: post_pr_comment --> Risk table posted to PR
    |
    v
Risk scores returned to ASCENT orchestrator
```

**HLD:** See Diagrams/HLD/VECTOR_HLD.png

**LLD:** See Diagrams/LLD/VECTOR_LLD.png (must be completed before Production)

### AI / Agent Configuration

**Model:** claude-sonnet-4-6 (Anthropic API)

**System Prompt Summary:**
"You are VECTOR, a code risk and complexity scoring agent. For each file in the PR diff, calculate a risk score (0.0-1.0) based on: git churn rate (commits per month), bug-fix commit frequency, cyclomatic complexity of changed methods, and coupling to other modules. Score >= 0.7 = HIGH RISK (flag for reviewer attention). Output a risk table and flag high-risk files with a brief explanation of why they are high risk."

**Tools / API Specifications:**

| Tool | API | Description |
|---|---|---|
| `fetch_pr_diff` | Azure DevOps / GitHub API | Fetches changed files |
| `query_git_history` | Azure DevOps / GitHub API | Fetches commit history, churn rate per file |
| `post_pr_comment` | Azure DevOps / GitHub API | Posts risk summary table |

### Engineering & Access

| Field | Value |
|---|---|
| Repo Link | poc/agents/ (BlueLine monorepo) |
| Environment Mapping | Dev -> QA -> Prod |
| Credentials Required | Anthropic API key, Azure DevOps PAT / GitHub token |

### Operations & Visibility

- **Monitoring & Logging:** Azure Application Insights — risk score distribution, high-risk file count per PR, latency.
- **Support / Runbook:** Git history API calls may be rate-limited on large PRs — monitor for 429 responses and configure exponential backoff.
- **Catalogue:** Register under "Quality Gate > VECTOR."

### Knowledge & Training

- **Demo Recordings:** To be added.
- **KT / KM Session Links:** To be scheduled.

### Lifecycle Operations

- **Pause / Restart:** Disable from Durable Functions orchestrator. Other Quality Gate agents continue unaffected.
- **Intern ID Deactivation:** Rotate service principal.

### For Completed Agents

> **Status: In Development.**

---

## Agent 4: ASCENT

### Core Definition

| Field | Value |
|---|---|
| Agent Name | ASCENT |
| Agent ID | BL-QG-004 |
| Project Mapping | Project BlueLine — Quality Gate Track |
| Status Lifecycle | Development -> Testing |
| Trigger Type | Event-based (triggered after CLARION + LUMEN + VECTOR complete) |
| Human Gate | Yes — PR approval required before merge |

### Problem & Purpose (MANDATORY)

**Agent-Level Problem Statement:**
CLARION, LUMEN, and VECTOR each post separate comments to a PR, creating noise and requiring reviewers to mentally aggregate three different outputs. There is no consolidated summary telling the reviewer what to focus on or what the overall quality gate outcome is.

**Executive Summary:**
ASCENT aggregates the outputs of CLARION, LUMEN, and VECTOR after all three complete in parallel. It posts a single consolidated PR summary comment with: overall quality gate outcome (Pass / Review Required / Fail), prioritised findings list (critical first), key risk flags, and actionable next steps for the developer.

**Business Value:** Provides a single, clear quality gate signal per PR; reduces reviewer cognitive overhead; creates a machine-readable quality record for trend analysis and continuous improvement.

### Functional Design

**Functional Flow (Step-by-Step):**

1. Azure Durable Functions orchestrator confirms CLARION + LUMEN + VECTOR have all completed.
2. ASCENT receives all three AgentResult objects.
3. Claude aggregates findings: de-duplicates overlapping issues, prioritises by severity, assigns overall gate outcome.
4. Claude calls `post_pr_summary_comment` with the consolidated review.
5. Claude calls `read_ado_reactions` to collect developer feedback on past comments (for quality improvement loop).
6. ASCENT logs the aggregated result and publishes metrics to Application Insights.

**Inputs / Outputs:**

| | Detail |
|---|---|
| Input | AgentResult from CLARION, LUMEN, and VECTOR |
| Output | Consolidated PR summary comment; overall gate outcome; quality metrics |
| Output Format | PR summary comment; Application Insights metrics |

**Trigger Type:** Event-based (Durable Functions — waits for all three parallel agents to complete)

### Architecture (MANDATORY)

**Conceptual Diagram:**
```
CLARION result --+
LUMEN result    -+--> ASCENT (Azure Durable Functions aggregator)
VECTOR result  --+         |
                    +-- Aggregates, prioritises, de-duplicates
                    +-- Tool: post_pr_summary_comment
                    +-- Tool: read_ado_reactions (feedback loop)
                           |
                    Consolidated PR summary posted
                    Human reviewer approves/rejects
```

**HLD:** See Diagrams/HLD/ASCENT_HLD.png

**LLD:** See Diagrams/LLD/ASCENT_LLD.png (must be completed before Production)

### AI / Agent Configuration

**Model:** claude-sonnet-4-6 (Anthropic API)

**System Prompt Summary:**
"You are ASCENT, the Quality Gate aggregator. You receive structured findings from CLARION (standards violations), LUMEN (code smells), and VECTOR (risk scores). Your job: de-duplicate overlapping findings, prioritise by severity (CRITICAL > HIGH > MEDIUM > LOW), and produce one consolidated review summary. Assign an overall gate outcome: PASS (no critical/high findings), REVIEW REQUIRED (medium findings present), or FAIL (critical findings present)."

**Tools / API Specifications:**

| Tool | API | Description |
|---|---|---|
| `post_pr_summary_comment` | Azure DevOps / GitHub API | Posts the consolidated summary to the PR |
| `read_ado_reactions` | Azure DevOps API | Reads thumbs-up/down on existing comments for feedback loop |

### Engineering & Access

| Field | Value |
|---|---|
| Repo Link | poc/agents/ (BlueLine monorepo) |
| Environment Mapping | Dev -> QA -> Prod |
| Credentials Required | Anthropic API key, Azure DevOps PAT / GitHub token |

### Operations & Visibility

- **Monitoring & Logging:** Application Insights — gate outcome distribution (Pass/Review Required/Fail ratio), findings per PR, aggregation latency.
- **Support / Runbook:** If ASCENT times out waiting for parallel agents, check Durable Functions task hub state. Replay the orchestration from the last checkpoint.
- **Catalogue:** Register under "Quality Gate > ASCENT."

### Knowledge & Training

- **Demo Recordings:** To be added.
- **KT / KM Session Links:** To be scheduled.

### Lifecycle Operations

- **Pause / Restart:** Disable the Durable Functions orchestrator trigger. Individual agents will still run but no summary will be posted.
- **Intern ID Deactivation:** Rotate service principal credentials.

### For Completed Agents

> **Status: In Development.**

---

## Agent 5: BULWARK

### Core Definition

| Field | Value |
|---|---|
| Agent Name | BULWARK |
| Agent ID | BL-SEC-001 |
| Project Mapping | Project BlueLine — Security Track |
| Status Lifecycle | Development -> Testing |
| Trigger Type | Pipeline event (on commit) or Scheduled (WATCHTOWER trigger) |
| Human Gate | No |

### Problem & Purpose (MANDATORY)

**Agent-Level Problem Statement:**
Fortify SSC generates large lists of vulnerability findings that engineers must manually review, classify (real vs. false positive), and prioritise. This triage process is time-consuming and inconsistent — different engineers make different classification decisions for similar findings.

**Executive Summary:**
BULWARK fetches current Fortify SSC findings and uses AI reasoning to classify each finding as CRITICAL, HIGH, NEEDS_REVIEW, or FALSE_POSITIVE. It applies OWASP Top 10 knowledge, the specific codebase context, and triage rules to produce a structured, prioritised finding list — dramatically reducing the time engineers spend on manual triage.

**Business Value:** Eliminates manual Fortify triage; provides consistent, documented classification decisions; surfaces critical vulnerabilities immediately; creates an auditable triage record.

### Functional Design

**Functional Flow (Step-by-Step):**

1. CI/CD pipeline completes OR WATCHTOWER detects new findings and publishes to Service Bus topic `security.findings.new`.
2. BULWARK picks up the message from Service Bus.
3. BULWARK calls `fetch_fortify_findings` to retrieve the full finding list from Fortify SSC.
4. Claude analyses each finding: vulnerability class, CVSS score, affected component, exploitability context.
5. Claude classifies each finding: CRITICAL / HIGH / NEEDS_REVIEW / FALSE_POSITIVE with documented rationale.
6. BULWARK calls `suppress_fortify_issue` for FALSE_POSITIVE findings (with rationale written to Fortify).
7. CRITICAL findings are published to Service Bus topic `security.critical.fix-needed` for FORGE to consume.
8. All classified findings published to `security.findings.classified` for STEWARD.

**Inputs / Outputs:**

| | Detail |
|---|---|
| Input | Fortify SSC finding list (finding ID, vulnerability class, affected file/line, CVSS score) |
| Output | Classified finding list (CRITICAL / HIGH / NEEDS_REVIEW / FALSE_POSITIVE with rationale) |
| Output Format | Service Bus messages; Fortify SSC suppression records |

**Trigger Type:** Pipeline event + Scheduled (via WATCHTOWER)

### Architecture (MANDATORY)

**Conceptual Diagram:**
```
CI/CD Pipeline OR WATCHTOWER
    |
    v
Service Bus: security.findings.new
    |
    v
BULWARK (Azure Function)
    +-- Tool: fetch_fortify_findings --> Fortify SSC REST API
    +-- AI Triage: CRITICAL / HIGH / NEEDS_REVIEW / FALSE_POSITIVE
    +-- Tool: suppress_fortify_issue --> Fortify SSC REST API (FALSE_POSITIVEs)
    +-- Publish: security.critical.fix-needed --> FORGE
    +-- Publish: security.findings.classified --> STEWARD
```

**HLD:** See Diagrams/HLD/BULWARK_HLD.png

**LLD:** See Diagrams/LLD/BULWARK_LLD.png (must be completed before Production)

### AI / Agent Configuration

**Model:** claude-sonnet-4-6 (Anthropic API)

**System Prompt Summary:**
"You are BULWARK, a security vulnerability triage agent. For each Fortify finding, classify it as: CRITICAL (exploitable, high impact, confirmed), HIGH (likely real, significant impact), NEEDS_REVIEW (uncertain — escalate to human), or FALSE_POSITIVE (confirmed not exploitable with documented rationale). Never classify as FALSE_POSITIVE if uncertain — prefer NEEDS_REVIEW. Apply OWASP Top 10 knowledge. Always document your classification rationale."

**Prompt Caching:** Enabled — OWASP knowledge base and triage rules cached.

**Tools / API Specifications:**

| Tool | API | Description |
|---|---|---|
| `fetch_fortify_findings` | Fortify SSC REST API | Retrieves current finding list |
| `suppress_fortify_issue` | Fortify SSC REST API | Suppresses a finding with documented rationale |
| `publish_to_service_bus` | Azure Service Bus SDK | Publishes classified findings to downstream agents |

### Engineering & Access

| Field | Value |
|---|---|
| Repo Link | poc/agents/bulwark.py (BlueLine monorepo) |
| Environment Mapping | Dev -> QA -> Prod |
| Credentials Required | Anthropic API key, Fortify SSC API token, Azure Service Bus connection string |

### Operations & Visibility

- **Monitoring & Logging:** Application Insights — finding counts per classification, false positive rate, triage latency. Alert if CRITICAL finding count spikes unexpectedly.
- **Support / Runbook:** If Fortify SSC API is unavailable, BULWARK will retry with exponential backoff (3 retries). After exhaustion, publish to dead-letter queue for manual processing.
- **Catalogue:** Register under "Security Track > BULWARK."

### Knowledge & Training

- **Demo Recordings:** To be added.
- **KT / KM Session Links:** To be scheduled with InfoSec team.

### Lifecycle Operations

- **Pause / Restart:** Disable the Service Bus subscription trigger on the BULWARK Function. Messages will accumulate in the queue and be processed when re-enabled (no data loss).
- **Intern ID Deactivation:** Revoke Fortify SSC API token for intern accounts; rotate shared service principal.

### For Completed Agents

> **Status: In Development.**

---

## Agent 6: WATCHTOWER

### Core Definition

| Field | Value |
|---|---|
| Agent Name | WATCHTOWER |
| Agent ID | BL-SEC-002 |
| Project Mapping | Project BlueLine — Security Track |
| Status Lifecycle | Development -> Testing |
| Trigger Type | Scheduled (Azure Timer) |
| Human Gate | No |

### Problem & Purpose (MANDATORY)

**Agent-Level Problem Statement:**
Fortify scans are triggered manually or on an ad-hoc basis. There is no automated mechanism to ensure scans run on a regular schedule, detect when new findings have appeared since the last scan, or alert the team immediately when new vulnerabilities are introduced.

**Executive Summary:**
WATCHTOWER runs on a schedule, monitors Fortify SSC for scan completion and new findings, triggers scans when needed, and immediately notifies BULWARK via Service Bus when new findings appear — ensuring the security pipeline is continuously active without manual intervention.

**Business Value:** Ensures continuous security monitoring; eliminates the risk of findings going unnoticed between manual scan runs; provides real-time new-finding alerting.

### Functional Design

**Functional Flow (Step-by-Step):**

1. Azure Timer fires on schedule (configurable; default: every 4 hours).
2. WATCHTOWER calls `list_fortify_projects` to get the active project list.
3. For each project, WATCHTOWER calls `fetch_scan_status` to check last scan timestamp and completion status.
4. If scan is overdue (configurable threshold), WATCHTOWER calls `trigger_fortify_scan`.
5. WATCHTOWER calls `fetch_new_findings_since_last_run` — compares current findings with last stored snapshot.
6. If new findings exist, WATCHTOWER publishes to Service Bus topic `security.findings.new` to trigger BULWARK.
7. WATCHTOWER updates the stored snapshot in Azure Blob Storage.

**Inputs / Outputs:**

| | Detail |
|---|---|
| Input | Fortify SSC project list, scan status, finding snapshots (from Azure Blob) |
| Output | Service Bus message to BULWARK (if new findings); scan trigger (if overdue) |
| Trigger Type | Scheduled (Azure Timer — configurable interval) |

### Architecture (MANDATORY)

**Conceptual Diagram:**
```
Azure Timer (scheduled)
    |
    v
WATCHTOWER (Azure Function)
    +-- Tool: list_fortify_projects --> Fortify SSC REST API
    +-- Tool: fetch_scan_status --> Fortify SSC REST API
    +-- Tool: trigger_fortify_scan --> Fortify SSC REST API (if overdue)
    +-- Tool: fetch_new_findings_since_last_run --> Fortify SSC API + Blob snapshot
    +-- Publish: security.findings.new --> Service Bus --> BULWARK
```

**HLD:** See Diagrams/HLD/WATCHTOWER_HLD.png

**LLD:** See Diagrams/LLD/WATCHTOWER_LLD.png (must be completed before Production)

### AI / Agent Configuration

**Model:** claude-sonnet-4-6 (Anthropic API, lightweight usage)

**System Prompt Summary:**
"You are WATCHTOWER, a Fortify scan monitoring agent. Your job is to: (1) check whether scans are running on schedule, (2) detect new findings since the last run, (3) trigger scans if overdue. You are not responsible for triaging findings — that is BULWARK's role. When in doubt, alert rather than suppress."

**Tools / API Specifications:**

| Tool | API | Description |
|---|---|---|
| `list_fortify_projects` | Fortify SSC REST API | Lists active Fortify projects |
| `fetch_scan_status` | Fortify SSC REST API | Gets last scan timestamp and status |
| `trigger_fortify_scan` | Fortify SSC REST API | Triggers a new scan |
| `fetch_new_findings_since_last_run` | Fortify SSC REST API + Blob Storage | Compares current findings to last snapshot |
| `publish_to_service_bus` | Azure Service Bus SDK | Notifies BULWARK of new findings |

### Engineering & Access

| Field | Value |
|---|---|
| Repo Link | poc/agents/ (BlueLine monorepo) |
| Environment Mapping | Dev -> QA -> Prod |
| Credentials Required | Anthropic API key, Fortify SSC API token, Azure Service Bus connection string, Azure Blob Storage connection |

### Operations & Visibility

- **Monitoring & Logging:** Application Insights — scan frequency, new-finding detection events, trigger count, Service Bus publish success rate.
- **Support / Runbook:** If Fortify SSC is unavailable, WATCHTOWER logs the failure and skips the cycle (no alert storm). Manual fallback: trigger BULWARK directly via Service Bus test message.
- **Catalogue:** Register under "Security Track > WATCHTOWER."

### Knowledge & Training

- **Demo Recordings:** To be added.
- **KT / KM Session Links:** To be scheduled.

### Lifecycle Operations

- **Pause / Restart:** Disable the Azure Timer trigger on the Function. Re-enable to resume scheduled monitoring.
- **Intern ID Deactivation:** Revoke Fortify SSC API token; rotate service principal.

### For Completed Agents

> **Status: In Development.**

---

## Agent 7: FORGE

### Core Definition

| Field | Value |
|---|---|
| Agent Name | FORGE |
| Agent ID | BL-SEC-003 |
| Project Mapping | Project BlueLine — Security Track |
| Status Lifecycle | Development -> Testing |
| Trigger Type | Event-based (BULWARK Service Bus output) |
| Human Gate | Yes — draft fix PRs require human review and approval before merge |

### Problem & Purpose (MANDATORY)

**Agent-Level Problem Statement:**
When Fortify identifies a critical vulnerability, an engineer must manually read the finding, understand the vulnerable code, research the correct fix, implement it, write a test, and open a PR. This process is slow, expertise-dependent, and creates a backlog of unresolved security findings.

**Executive Summary:**
FORGE receives CRITICAL findings from BULWARK, reads the vulnerable source code, generates a targeted code fix applying the correct security pattern, writes a unit test covering the fix, commits to a new branch, and opens a draft PR — ready for human engineer review and approval.

**Business Value:** Dramatically accelerates remediation of critical vulnerabilities; produces consistent, documented fixes; reduces the expertise barrier for junior engineers; creates an auditable fix trail.

### Functional Design

**Functional Flow (Step-by-Step):**

1. BULWARK publishes CRITICAL finding to Service Bus topic `security.critical.fix-needed`.
2. FORGE picks up the message.
3. Claude calls `get_file_content` to read the vulnerable source file.
4. Claude analyses the vulnerability class and generates the corrected code.
5. Claude generates a unit test covering the fix.
6. FORGE calls `create_branch` (branch name: blueline/forge/fix-{finding-id}).
7. FORGE calls `commit_files` with the fixed source file and test file.
8. FORGE calls `create_pull_request` — creates a DRAFT PR (cannot be auto-merged).
9. FORGE publishes the fix event to `security.findings.classified` for STEWARD to log.

**Inputs / Outputs:**

| | Detail |
|---|---|
| Input | CRITICAL finding (finding ID, vulnerability class, affected file/line, CVSS score) from BULWARK |
| Output | Draft PR containing: fixed source file, unit test, PR description with finding reference |
| Output Format | Azure DevOps / GitHub draft PR |

**Trigger Type:** Event-based (Azure Service Bus `security.critical.fix-needed`)

### Architecture (MANDATORY)

**Conceptual Diagram:**
```
BULWARK --> Service Bus: security.critical.fix-needed
    |
    v
FORGE (Azure Function)
    +-- Tool: get_file_content --> Source control API
    +-- AI: Generate fix + unit test
    +-- Tool: create_branch --> Azure DevOps / GitHub API
    +-- Tool: commit_files --> Azure DevOps / GitHub API
    +-- Tool: create_pull_request (DRAFT) --> Azure DevOps / GitHub API
    |
    v
Draft PR created --> Human engineer reviews and approves
    |
    v
STEWARD logs the fix event
```

**HLD:** See Diagrams/HLD/FORGE_HLD.png

**LLD:** See Diagrams/LLD/FORGE_LLD.png (must be completed before Production)

### AI / Agent Configuration

**Model:** claude-sonnet-4-6 (Anthropic API)

**System Prompt Summary:**
"You are FORGE, a security fix generation agent. You receive a confirmed critical vulnerability finding and the vulnerable source code. Generate a correct, minimal fix that addresses the vulnerability without breaking existing functionality. Apply the correct security pattern for the vulnerability class (SQL injection: parameterised queries; XSS: output encoding; SSRF: allowlist validation). Also generate a unit test that proves the vulnerability is fixed. Never generate a fix you are not confident in — if uncertain, write a stub PR with a TODO and escalate."

**Tools / API Specifications:**

| Tool | API | Description |
|---|---|---|
| `get_file_content` | Azure DevOps / GitHub API | Reads vulnerable source file |
| `create_branch` | Azure DevOps / GitHub API | Creates fix branch |
| `commit_files` | Azure DevOps / GitHub API | Commits fixed file + test |
| `create_pull_request` | Azure DevOps / GitHub API | Opens draft PR |
| `publish_to_service_bus` | Azure Service Bus SDK | Notifies STEWARD |

### Engineering & Access

| Field | Value |
|---|---|
| Repo Link | poc/agents/ (BlueLine monorepo) |
| Environment Mapping | Dev -> QA -> Prod |
| Credentials Required | Anthropic API key, Azure DevOps PAT / GitHub token, Azure Service Bus connection string |

### Operations & Visibility

- **Monitoring & Logging:** Application Insights — fix generation success rate, PR creation count, latency per finding, confidence score distribution.
- **Support / Runbook:** If FORGE creates a PR that the engineer considers incorrect, the engineer closes the draft PR and adds a comment. ASCENT's feedback loop will use this rejection to improve future outputs.
- **Catalogue:** Register under "Security Track > FORGE."

### Knowledge & Training

- **Demo Recordings:** To be added.
- **KT / KM Session Links:** To be scheduled with InfoSec and Engineering Lead.

### Lifecycle Operations

- **Pause / Restart:** Disable the Service Bus subscription trigger. CRITICAL findings will accumulate in the queue and be processed when FORGE is re-enabled.
- **Intern ID Deactivation:** Revoke Azure DevOps PAT tokens; rotate service principal.

### For Completed Agents

> **Status: In Development.**

---

## Agent 8: STEWARD

### Core Definition

| Field | Value |
|---|---|
| Agent Name | STEWARD |
| Agent ID | BL-SEC-004 |
| Project Mapping | Project BlueLine — Security Track |
| Status Lifecycle | Development -> Testing |
| Trigger Type | Event-based (all Security Track Service Bus events) |
| Human Gate | No |

### Problem & Purpose (MANDATORY)

**Agent-Level Problem Statement:**
AI-driven security decisions (triage classifications, suppression rationale, fix generation) produce no auditable record in the current manual process. There is no structured log showing who (or what) decided to suppress a finding, why, and when.

**Executive Summary:**
STEWARD subscribes to all Security Track Service Bus events and writes an immutable, structured audit log entry for every security decision made by BULWARK, FORGE, and WATCHTOWER. Logs are written to Azure Blob Storage (append-only) and reviewed periodically by InfoSec.

**Business Value:** Provides a complete, immutable audit trail for all AI security decisions; satisfies compliance and governance requirements; enables InfoSec to review and validate AI triage accuracy over time.

### Functional Design

**Functional Flow (Step-by-Step):**

1. STEWARD subscribes to all Security Track topics on Azure Service Bus.
2. On receiving any security event, STEWARD parses the event type (triage result, suppression, fix PR created, scan triggered).
3. Claude formats the event into a structured audit log entry (JSON schema).
4. STEWARD calls `write_audit_log` — appends the entry to an immutable append-only blob in Azure Blob Storage.
5. STEWARD returns acknowledgement to Service Bus (message removed from queue).

**Inputs / Outputs:**

| | Detail |
|---|---|
| Input | All Security Track Service Bus events (from BULWARK, FORGE, WATCHTOWER) |
| Output | Structured JSON audit log entries in Azure Blob Storage (immutable, append-only) |
| Output Format | JSON log files in Azure Blob (one file per day) |

**Trigger Type:** Event-based (Azure Service Bus — all security topics)

### Architecture (MANDATORY)

**Conceptual Diagram:**
```
BULWARK events  --+
FORGE events      +--> Service Bus (all security topics)
WATCHTOWER events--+         |
                             v
                        STEWARD (Azure Function)
                        +-- Parses event type
                        +-- AI: Formats structured log entry
                        +-- Tool: write_audit_log --> Azure Blob Storage (append-only)
```

**HLD:** See Diagrams/HLD/STEWARD_HLD.png

**LLD:** See Diagrams/LLD/STEWARD_LLD.png (must be completed before Production)

### AI / Agent Configuration

**Model:** claude-sonnet-4-6 (Anthropic API, lightweight — primarily formatting)

**System Prompt Summary:**
"You are STEWARD, an audit log writer. Convert the incoming security event into a structured JSON audit log entry following the audit schema. Include: timestamp (UTC), event type, agent ID, finding ID (if applicable), decision made, rationale, confidence score, and outcome. Never omit fields. Never modify or reinterpret the decision — record it exactly as made."

**Tools / API Specifications:**

| Tool | API | Description |
|---|---|---|
| `write_audit_log` | Azure Blob Storage SDK | Appends structured JSON entry to daily audit log blob |

### Engineering & Access

| Field | Value |
|---|---|
| Repo Link | poc/agents/ (BlueLine monorepo) |
| Environment Mapping | Dev -> QA -> Prod |
| Credentials Required | Anthropic API key, Azure Blob Storage connection string, Azure Service Bus connection string |

### Operations & Visibility

- **Monitoring & Logging:** Application Insights — log write success rate, latency, message count per event type.
- **Support / Runbook:** If Blob Storage is unavailable, messages will dead-letter in Service Bus. On recovery, replay dead-letter messages — STEWARD processing is idempotent.
- **Catalogue:** Register under "Security Track > STEWARD."

### Knowledge & Training

- **Demo Recordings:** To be added.
- **KT / KM Session Links:** To be scheduled with InfoSec team.

### Lifecycle Operations

- **Pause / Restart:** Disable Service Bus subscription. Messages accumulate; replay on re-enable.
- **Intern ID Deactivation:** Rotate Azure Blob Storage access keys (use Managed Identity in production).

### For Completed Agents

> **Status: In Development.**

---

## Agent 9: TIMELINE

### Core Definition

| Field | Value |
|---|---|
| Agent Name | TIMELINE |
| Agent ID | BL-CERT-001 |
| Project Mapping | Project BlueLine — Certificate Loop Track |
| Status Lifecycle | Design -> Development |
| Trigger Type | Scheduled (Azure Timer — daily) |
| Human Gate | No |

### Problem & Purpose (MANDATORY)

**Agent-Level Problem Statement:**
SSL/TLS certificate expiry dates are tracked manually via spreadsheets and email alerts. Engineers often discover expiry risks late, leaving insufficient time for renewal — particularly for external certificates that require InfoSec involvement and can take days to weeks to issue.

**Executive Summary:**
TIMELINE runs daily, queries Azure Key Vault for all managed certificate metadata, identifies certificates expiring within a configurable threshold (default: 30 days), and generates renewal work items for REGENT to process — providing at least 30 days of buffer for all renewal actions to complete.

**Business Value:** Eliminates manual expiry tracking; provides automated early warning >= 30 days before expiry; prevents certificate expiry incidents.

### Functional Design

**Functional Flow (Step-by-Step):**

1. Azure Timer fires daily at a configured time (e.g., 06:00 UTC).
2. TIMELINE calls `list_keyvault_certificates` to get all certificates with metadata.
3. Claude evaluates each certificate's expiry date against the current date.
4. Certificates expiring within 30 days are flagged as RENEWAL_REQUIRED.
5. Certificates expiring within 7 days are flagged as URGENT.
6. TIMELINE generates a renewal work item for each flagged certificate.
7. Work items are published to Service Bus topic `cert.renewal.required` for REGENT.
8. TIMELINE logs the daily scan result to Application Insights.

**Inputs / Outputs:**

| | Detail |
|---|---|
| Input | Azure Key Vault certificate list (name, expiry date, subject, CA type, environment) |
| Output | Renewal work items (cert name, expiry date, urgency, CA type, environment list) |
| Output Format | Service Bus messages to REGENT |

**Trigger Type:** Scheduled (Azure Timer — daily)

### Architecture (MANDATORY)

**Conceptual Diagram:**
```
Azure Timer (daily)
    |
    v
TIMELINE (Azure Function)
    +-- Tool: list_keyvault_certificates --> Azure Key Vault API
    +-- AI: Evaluate expiry, classify urgency (NORMAL / URGENT)
    +-- Publish: cert.renewal.required --> Service Bus --> REGENT
```

**HLD:** See Diagrams/HLD/TIMELINE_HLD.png

**LLD:** See Diagrams/LLD/TIMELINE_LLD.png (must be completed before Production)

### AI / Agent Configuration

**Model:** claude-sonnet-4-6 (Anthropic API)

**System Prompt Summary:**
"You are TIMELINE, a certificate expiry monitoring agent. Query the certificate inventory and identify certificates expiring within 30 days. Mark certificates expiring within 7 days as URGENT. For each flagged certificate, produce a renewal work item containing: certificate name, current expiry date, CA type (internal/external), affected environments, and urgency level. Do not generate work items for certificates not yet within the threshold."

**Tools / API Specifications:**

| Tool | API | Description |
|---|---|---|
| `list_keyvault_certificates` | Azure Key Vault REST API | Lists all managed certificates with expiry metadata |
| `publish_to_service_bus` | Azure Service Bus SDK | Publishes renewal work items to REGENT |

### Engineering & Access

| Field | Value |
|---|---|
| Repo Link | poc/agents/timeline.py (BlueLine monorepo) |
| Environment Mapping | Dev -> QA -> Prod |
| Credentials Required | Anthropic API key, Azure Key Vault access (Managed Identity preferred), Azure Service Bus connection string |

### Operations & Visibility

- **Monitoring & Logging:** Application Insights — certificate count scanned, renewal work items generated, URGENT count, daily scan latency.
- **Support / Runbook:** If Key Vault is unavailable, TIMELINE logs the failure and sends an alert to the Operations team. Manual fallback: check Key Vault directly via Azure Portal.
- **Catalogue:** Register under "Certificate Loop > TIMELINE."

### Knowledge & Training

- **Demo Recordings:** To be added.
- **KT / KM Session Links:** To be scheduled with Operations team.

### Lifecycle Operations

- **Pause / Restart:** Disable the Azure Timer trigger. On resume, TIMELINE will run at the next scheduled interval and catch up with any certificates that entered the expiry window during the pause.
- **Intern ID Deactivation:** Revoke Key Vault access policy entries for intern accounts; prefer Managed Identity for service access.

### For Completed Agents

> **Status: In Design.**

---

## Agent 10: REGENT

### Core Definition

| Field | Value |
|---|---|
| Agent Name | REGENT |
| Agent ID | BL-CERT-002 |
| Project Mapping | Project BlueLine — Certificate Loop Track |
| Status Lifecycle | Design -> Development |
| Trigger Type | Event-based (TIMELINE Service Bus output) |
| Human Gate | No |

### Problem & Purpose (MANDATORY)

**Agent-Level Problem Statement:**
There is no centralised, machine-readable inventory of all SSL/TLS certificates — their owners, environments, CA type, and renewal history. This makes automated renewal orchestration impossible and forces engineers to rely on institutional knowledge.

**Executive Summary:**
REGENT maintains the structured certificate inventory in Azure Table Storage. On receiving a renewal work item from TIMELINE, REGENT enriches it with ownership, CA contact, environment list, and last-renewal history — producing a complete renewal record that COURIER can act on.

**Business Value:** Creates and maintains the single source of truth for certificate inventory; enables automated renewal orchestration; eliminates institutional-knowledge dependency.

### Functional Design

**Functional Flow (Step-by-Step):**

1. REGENT picks up a renewal work item from Service Bus `cert.renewal.required`.
2. REGENT calls `read_cert_inventory` to retrieve the existing inventory record for this certificate.
3. Claude enriches the work item: adds owner, CA type, CA contact details, renewal SLA, affected environments.
4. REGENT calls `update_cert_inventory` to record the renewal event in the inventory.
5. REGENT publishes the enriched renewal record to Service Bus `cert.renewal.enriched` for COURIER.

**Inputs / Outputs:**

| | Detail |
|---|---|
| Input | Renewal work item from TIMELINE (cert name, expiry date, urgency) |
| Output | Enriched renewal record (+ owner, CA, environments, SLA) published to COURIER |
| Output Format | Service Bus message to COURIER; Azure Table Storage inventory update |

**Trigger Type:** Event-based (Service Bus `cert.renewal.required`)

### Architecture (MANDATORY)

**Conceptual Diagram:**
```
TIMELINE --> Service Bus: cert.renewal.required
    |
    v
REGENT (Azure Function)
    +-- Tool: read_cert_inventory --> Azure Table Storage
    +-- AI: Enrich with owner, CA, environments
    +-- Tool: update_cert_inventory --> Azure Table Storage
    +-- Publish: cert.renewal.enriched --> Service Bus --> COURIER
```

**HLD:** See Diagrams/HLD/REGENT_HLD.png

**LLD:** See Diagrams/LLD/REGENT_LLD.png (must be completed before Production)

### AI / Agent Configuration

**Model:** claude-sonnet-4-6 (Anthropic API)

**System Prompt Summary:**
"You are REGENT, a certificate inventory manager. When you receive a renewal work item, look up the certificate in the inventory and enrich it with: owner name, owner contact, CA type (internal C&M portal / external DigiCert), CA contact details, affected environments (Dev/QA/Prod), renewal SLA (days), and last renewal date. Update the inventory record to reflect that renewal is in progress. Produce an enriched renewal record for COURIER."

**Tools / API Specifications:**

| Tool | API | Description |
|---|---|---|
| `read_cert_inventory` | Azure Table Storage SDK | Reads certificate inventory record |
| `update_cert_inventory` | Azure Table Storage SDK | Updates inventory with renewal status |
| `publish_to_service_bus` | Azure Service Bus SDK | Publishes enriched record to COURIER |

### Engineering & Access

| Field | Value |
|---|---|
| Repo Link | poc/agents/ (BlueLine monorepo) |
| Environment Mapping | Dev -> QA -> Prod |
| Credentials Required | Anthropic API key, Azure Table Storage connection string, Azure Service Bus connection string |

### Operations & Visibility

- **Monitoring & Logging:** Application Insights — inventory reads/writes, enrichment success rate, records updated per day.
- **Support / Runbook:** If a certificate is not found in the inventory, REGENT logs a warning and alerts the Operations team to add the certificate manually. Never block the renewal pipeline on a missing inventory record.
- **Catalogue:** Register under "Certificate Loop > REGENT."

### Knowledge & Training

- **Demo Recordings:** To be added.
- **KT / KM Session Links:** To be scheduled.

### Lifecycle Operations

- **Pause / Restart:** Disable Service Bus subscription. Work items queue safely; resume when re-enabled.
- **Intern ID Deactivation:** Rotate Table Storage access keys (prefer Managed Identity).

### For Completed Agents

> **Status: In Design.**

---

## Agent 11: COURIER

### Core Definition

| Field | Value |
|---|---|
| Agent Name | COURIER |
| Agent ID | BL-CERT-003 |
| Project Mapping | Project BlueLine — Certificate Loop Track |
| Status Lifecycle | Design -> Development |
| Trigger Type | Event-based (REGENT Service Bus output) |
| Human Gate | No |

### Problem & Purpose (MANDATORY)

**Agent-Level Problem Statement:**
Requesting and downloading renewed SSL/TLS certificates from Certificate Authorities (internal C&M portal or external DigiCert) is a fully manual process. Engineers must navigate CA portals, fill in request forms, wait for issuance, and download certificates — a process that can take days and is prone to human error.

**Executive Summary:**
COURIER receives an enriched renewal record from REGENT and automates the certificate issuance process: it calls the appropriate CA API (internal or DigiCert), submits the renewal request, polls for issuance completion, downloads the new certificate file, validates it, and stores it in Azure Key Vault — ready for HARBOUR to deploy.

**Business Value:** Eliminates manual CA portal interactions; accelerates issuance from days to hours; produces a validated, ready-to-deploy certificate package.

### Functional Design

**Functional Flow (Step-by-Step):**

1. COURIER picks up enriched renewal record from Service Bus `cert.renewal.enriched`.
2. COURIER determines CA type: internal (C&M portal API) or external (DigiCert API).
3. Claude calls `submit_certificate_request` with the appropriate CA API and parameters.
4. COURIER polls `check_certificate_status` until issuance is confirmed (with configurable timeout).
5. COURIER calls `download_certificate` to retrieve the certificate file (PEM/PFX).
6. COURIER validates the downloaded certificate: subject, SAN, expiry, chain.
7. COURIER stores the validated certificate in Azure Key Vault via `store_certificate_in_keyvault`.
8. COURIER publishes to Service Bus `cert.renewal.ready` for HARBOUR to deploy.

**Inputs / Outputs:**

| | Detail |
|---|---|
| Input | Enriched renewal record from REGENT (cert name, CA type, CA contact, environments, expiry) |
| Output | Validated certificate file stored in Azure Key Vault; deployment message to HARBOUR |
| Output Format | Azure Key Vault certificate + Service Bus message |

**Trigger Type:** Event-based (Service Bus `cert.renewal.enriched`)

### Architecture (MANDATORY)

**Conceptual Diagram:**
```
REGENT --> Service Bus: cert.renewal.enriched
    |
    v
COURIER (Azure Function)
    +-- Tool: submit_certificate_request --> CA API (C&M or DigiCert)
    +-- Tool: check_certificate_status --> CA API (polling)
    +-- Tool: download_certificate --> CA API
    +-- Tool: validate_certificate --> local validation
    +-- Tool: store_certificate_in_keyvault --> Azure Key Vault API
    +-- Publish: cert.renewal.ready --> Service Bus --> HARBOUR
```

**HLD:** See Diagrams/HLD/COURIER_HLD.png

**LLD:** See Diagrams/LLD/COURIER_LLD.png (must be completed before Production)

### AI / Agent Configuration

**Model:** claude-sonnet-4-6 (Anthropic API)

**System Prompt Summary:**
"You are COURIER, a certificate issuance orchestrator. Submit renewal requests to the correct CA (internal C&M portal or external DigiCert). Poll for issuance. Download the certificate. Validate it: confirm subject matches, SAN is correct, expiry is in the future, chain is complete and trusted. Store in Key Vault. If validation fails, do not proceed to HARBOUR — log the failure and alert the Operations team."

**Tools / API Specifications:**

| Tool | API | Description |
|---|---|---|
| `submit_certificate_request` | Internal C&M API / DigiCert REST API | Submits renewal request to CA |
| `check_certificate_status` | Internal C&M API / DigiCert REST API | Polls for issuance completion |
| `download_certificate` | Internal C&M API / DigiCert REST API | Downloads certificate file (PEM/PFX) |
| `validate_certificate` | Local (cryptography library) | Validates subject, SAN, expiry, chain |
| `store_certificate_in_keyvault` | Azure Key Vault SDK | Stores validated cert in Key Vault |
| `publish_to_service_bus` | Azure Service Bus SDK | Notifies HARBOUR |

### Engineering & Access

| Field | Value |
|---|---|
| Repo Link | poc/agents/ (BlueLine monorepo) |
| Environment Mapping | Dev -> QA -> Prod |
| Credentials Required | Anthropic API key, CA API credentials (C&M + DigiCert), Azure Key Vault access, Azure Service Bus connection |

### Operations & Visibility

- **Monitoring & Logging:** Application Insights — request submission count, issuance latency, validation pass/fail rate, Key Vault write success.
- **Support / Runbook:** If CA API is unavailable, COURIER retries with exponential backoff (3 attempts over 24 hours). Alert Operations team on third failure.
- **Catalogue:** Register under "Certificate Loop > COURIER."

### Knowledge & Training

- **Demo Recordings:** To be added.
- **KT / KM Session Links:** To be scheduled with InfoSec and Operations team.

### Lifecycle Operations

- **Pause / Restart:** Disable Service Bus subscription. REGENT messages accumulate safely. On resume, certificates in the queue will be processed immediately.
- **Intern ID Deactivation:** Revoke CA API credentials for intern accounts; rotate shared credentials.

### For Completed Agents

> **Status: In Design.**

---

## Agent 12: HARBOUR

### Core Definition

| Field | Value |
|---|---|
| Agent Name | HARBOUR |
| Agent ID | BL-CERT-004 |
| Project Mapping | Project BlueLine — Certificate Loop Track |
| Status Lifecycle | Design -> Development |
| Trigger Type | Event-based (COURIER Service Bus output) |
| Human Gate | Yes — Production deployment requires explicit human approval via Teams/Email |

### Problem & Purpose (MANDATORY)

**Agent-Level Problem Statement:**
Deploying renewed SSL/TLS certificates to servers and application services is a multi-step manual process repeated across Dev, QA, and Production environments. Engineers must download certificates, copy them to each server, import into IIS, bind to websites, and verify HTTPS — with the entire sequence repeated per environment.

**Executive Summary:**
HARBOUR receives a validated certificate from COURIER and automates the full deployment sequence across all environments: Dev and QA are deployed automatically; Production requires human approval via Teams notification. For each deployment, HARBOUR installs the certificate in IIS (via WinRM/PowerShell) or Azure App Service (via Azure SDK), binds it to the appropriate websites/APIs, and verifies HTTPS is working correctly post-deployment.

**Business Value:** Eliminates the most error-prone and time-consuming step in the certificate lifecycle; ensures consistent deployment across all environments; provides automated HTTPS verification; maintains production control via human gate.

### Functional Design

**Functional Flow (Step-by-Step):**

1. HARBOUR picks up ready certificate from Service Bus `cert.renewal.ready`.
2. HARBOUR deploys to Dev environment: calls `deploy_to_iis` or `deploy_to_app_service`, then `verify_https`.
3. On Dev success, HARBOUR deploys to QA using the same sequence.
4. On QA success, HARBOUR sends a Teams/Email notification requesting Production approval.
5. Human engineer approves (clicks approve link in Teams or replies to email).
6. On approval received, HARBOUR deploys to Production.
7. HARBOUR calls `verify_https` on Production — confirms HTTPS working.
8. HARBOUR updates Key Vault certificate metadata (renewal date, deployed environments).
9. HARBOUR publishes completion event to STEWARD for audit logging.

**Inputs / Outputs:**

| | Detail |
|---|---|
| Input | Validated certificate from Key Vault (via COURIER); environment list; binding configuration |
| Output | Deployed certificate across Dev/QA/Prod; HTTPS verification result; audit log event |
| Output Format | IIS certificate store / Azure App Service binding; HTTPS verification status |

**Trigger Type:** Event-based (Service Bus `cert.renewal.ready`)

### Architecture (MANDATORY)

**Conceptual Diagram:**
```
COURIER --> Service Bus: cert.renewal.ready
    |
    v
HARBOUR (Azure Function)
    +-- Deploy to DEV:
    |   +-- Tool: deploy_to_iis (WinRM/PS) or deploy_to_app_service (Azure SDK)
    |   +-- Tool: verify_https --> HTTP check on dev site
    +-- Deploy to QA (on Dev success):
    |   +-- Tool: deploy_to_iis / deploy_to_app_service
    |   +-- Tool: verify_https --> HTTP check on QA site
    +-- Send Teams/Email approval request for PROD (human gate)
    +-- On approval --> Deploy to PROD:
    |   +-- Tool: deploy_to_iis / deploy_to_app_service
    |   +-- Tool: verify_https --> HTTP check on Prod site
    +-- Update Key Vault metadata --> STEWARD audit log
```

**HLD:** See Diagrams/HLD/HARBOUR_HLD.png

**LLD:** See Diagrams/LLD/HARBOUR_LLD.png (must be completed before Production)

### AI / Agent Configuration

**Model:** claude-sonnet-4-6 (Anthropic API)

**System Prompt Summary:**
"You are HARBOUR, a certificate deployment and validation agent. Deploy the provided certificate to each environment in sequence: Dev -> QA -> Prod. For Dev and QA: deploy automatically. For Prod: request human approval first and only proceed on confirmation. After each deployment, verify HTTPS is working. If verification fails, roll back the certificate to the previous version and alert the Operations team immediately. Never proceed to the next environment if the current one fails verification."

**Tools / API Specifications:**

| Tool | API | Description |
|---|---|---|
| `deploy_to_iis` | WinRM / PowerShell Remoting | Imports cert into IIS and binds to site/API |
| `deploy_to_app_service` | Azure App Service SDK | Binds certificate to App Service custom domain |
| `verify_https` | HTTPS check (requests library) | Confirms site returns HTTP 200 with new certificate |
| `send_approval_request` | Microsoft Teams Webhook / Email API | Sends Prod approval notification to Operations team |
| `update_keyvault_metadata` | Azure Key Vault SDK | Updates renewal date and deployment status |
| `publish_to_service_bus` | Azure Service Bus SDK | Notifies STEWARD of completion |

### Engineering & Access

| Field | Value |
|---|---|
| Repo Link | poc/agents/ (BlueLine monorepo) |
| Environment Mapping | Dev -> QA -> Prod |
| Credentials Required | Anthropic API key, WinRM credentials (IIS servers), Azure App Service credentials (Managed Identity preferred), Teams webhook URL, Azure Key Vault access, Azure Service Bus connection |

### Operations & Visibility

- **Monitoring & Logging:** Application Insights — deployment success/failure per environment, HTTPS verification pass/fail, rollback events, approval wait time.
- **Support / Runbook:** If HTTPS verification fails post-deployment: (1) HARBOUR auto-rolls back to previous certificate; (2) Operations team is alerted; (3) Manual investigation required before retry. If WinRM connection fails: check server connectivity and firewall rules.
- **Catalogue:** Register under "Certificate Loop > HARBOUR."

### Knowledge & Training

- **Demo Recordings:** To be added after first end-to-end certificate renewal demo.
- **KT / KM Session Links:** To be scheduled with Operations and InfoSec teams.

### Lifecycle Operations

- **Pause / Restart:** Disable Service Bus subscription. Ready certificates queue safely. On resume, deployments proceed from the queued messages. If a certificate has expired by resume time, escalate to Operations for manual handling.
- **Intern ID Deactivation:** Revoke WinRM credentials and App Service principal access for intern accounts; rotate shared credentials immediately.

### For Completed Agents

> **Status: In Design.**

---

## Standard Documentation Folder Structure (MANDATORY)

```
Project/
+-- Project_Documentation.docx     (Word document)
+-- Project_Documentation.md       (Markdown version)
|
+-- Agents/
    +-- CLARION_Documentation.md
    +-- LUMEN_Documentation.md
    +-- VECTOR_Documentation.md
    +-- ASCENT_Documentation.md
    +-- BULWARK_Documentation.md
    +-- WATCHTOWER_Documentation.md
    +-- FORGE_Documentation.md
    +-- STEWARD_Documentation.md
    +-- TIMELINE_Documentation.md
    +-- REGENT_Documentation.md
    +-- COURIER_Documentation.md
    +-- HARBOUR_Documentation.md
    |
    +-- Diagrams/
        +-- HLD/
        |   +-- CLARION_HLD.png
        |   +-- LUMEN_HLD.png
        |   +-- VECTOR_HLD.png
        |   +-- ASCENT_HLD.png
        |   +-- BULWARK_HLD.png
        |   +-- WATCHTOWER_HLD.png
        |   +-- FORGE_HLD.png
        |   +-- STEWARD_HLD.png
        |   +-- TIMELINE_HLD.png
        |   +-- REGENT_HLD.png
        |   +-- COURIER_HLD.png
        |   +-- HARBOUR_HLD.png
        |
        +-- LLD/
        |   +-- CLARION_LLD.png
        |   +-- LUMEN_LLD.png
        |   +-- VECTOR_LLD.png
        |   +-- ASCENT_LLD.png
        |   +-- BULWARK_LLD.png
        |   +-- WATCHTOWER_LLD.png
        |   +-- FORGE_LLD.png
        |   +-- STEWARD_LLD.png
        |   +-- TIMELINE_LLD.png
        |   +-- REGENT_LLD.png
        |   +-- COURIER_LLD.png
        |   +-- HARBOUR_LLD.png
        |
        +-- Conceptual/
        |   +-- BlueLine_Conceptual_Architecture.png
        |
        +-- Recordings/
            +-- (demo recordings to be added)
```

---

*Project BlueLine — Project Documentation v1.0 | 2026-05-26*

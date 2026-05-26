# Project BlueLine — Understanding Document

**Version:** 1.0  
**Date:** 2026-04-15  
**Prepared by:** Project BlueLine Team  
**Status:** Draft for Review

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Background & Context](#2-background--context)
3. [Problem Statement](#3-problem-statement)
4. [Project Objectives](#4-project-objectives)
5. [Scope](#5-scope)
6. [Stakeholders](#6-stakeholders)
7. [Current State (As-Is)](#7-current-state-as-is)
8. [Future State (To-Be)](#8-future-state-to-be)
9. [Track Descriptions](#9-track-descriptions)
   - 9.1 [Quality Gate Track](#91-quality-gate-track)
   - 9.2 [Security Track](#92-security-track)
   - 9.3 [Certificate Loop Track](#93-certificate-loop-track)
10. [Agent Catalogue](#10-agent-catalogue)
11. [AI Approach](#11-ai-approach)
12. [Assumptions & Constraints](#12-assumptions--constraints)
13. [Dependencies](#13-dependencies)
14. [Risks](#14-risks)
15. [Phased Rollout Plan](#15-phased-rollout-plan)
16. [Glossary](#16-glossary)

---

## 1. Executive Summary

Project BlueLine is an AI-powered automation system designed to reduce manual effort across three critical engineering workflows: **code review**, **security vulnerability management**, and **SSL certificate lifecycle management**. 

The system introduces a suite of purpose-built AI agents, each responsible for a discrete step in one of three automation tracks. These agents operate on Azure infrastructure, are powered by a large language model (LLM) reasoning layer, and are designed to be **assistive** — human engineers retain final approval authority at every decision gate.

BlueLine targets teams working on .NET (C#) and Angular (TypeScript) codebases under Azure DevOps, and integrates with Fortify SSC for security scanning and Azure Key Vault for certificate management.

---

## 2. Background & Context

The Core & Main engineering team at PGE/ATCO currently operates a development workflow that is heavily reliant on manual processes. As the team grows and the codebase matures, several recurring pain points have been identified:

- Pull request reviews are inconsistent and time-consuming, depending heavily on individual reviewer availability and experience.
- Security vulnerability scanning via Fortify is triggered and analyzed manually, with no automated remediation path.
- SSL/TLS certificate renewals are tracked via spreadsheets and email notifications, leading to near-miss expiry incidents.

These issues were formally surfaced in internal communications from the engineering leads and discussed in sprint standup meetings as ongoing blockers to team velocity and system reliability.

---

## 3. Problem Statement

### 3.1 Code Review (Quality Gate)
- Reviewers manually check coding guidelines for every PR.
- Validation of .NET and Angular standards (naming conventions, structure, patterns) is done by individual engineers with no enforced standard.
- Security smells, anti-patterns, and type safety issues are identified inconsistently.
- Review decisions depend heavily on individual reviewer experience.
- No standardized or automated enforcement of guidelines across teams.
- Missed issues during initial review often lead to rework cycles.

### 3.2 Security Scanning (Security Track)
- Fortify is used for vulnerability scanning but is triggered manually or on a scheduled basis.
- Triggering scans, analyzing findings, and configuring scheduled scans are all done manually.
- Interpreting findings and identifying impacted code areas requires manual effort.
- Deciding appropriate remediation based on recommendations is manual.
- Implementing fixes manually in the codebase is time-consuming.
- Re-running scans to verify resolution adds further overhead.
- While Fortify identifies vulnerabilities at a high level, it does not provide concrete, code-level actionable fixes. The team wants to explore AI-based tools that can detect vulnerabilities and generate actionable fixes to reduce manual effort and improve remediation efficiency.

### 3.3 Certificate Renewal (Certificate Loop)
- SSL certificate management is entirely manual and involves multiple steps across multiple environments (Dev, QA, Prod).
- Checking certificate expiry dates is done across systems without centralized visibility.
- Tracking expiry dates across systems is done via email notifications or tracking sheets.
- For internal certificates: generating certificate requests and downloading certificates from the C&M portal is manual.
- For external certificates: raising requests with the InfoSec team and waiting for certificate issuance is manual.
- Downloading and validating renewed certificates to ensure correctness and compatibility is manual.
- Securely transferring certificates to target servers/environments is manual.
- Manually installing certificates in IIS (Server Certificates → Import) is manual.
- Binding certificates to websites/APIs over HTTPS is manual.
- Repeating the same process across multiple environments is manual.
- Following a similar manual process for machine/server certificates is manual.

---

## 4. Project Objectives

| # | Objective | Success Metric |
|---|---|---|
| O1 | Automate PR code review for .NET and Angular codebases | >80% of PR comments generated automatically with <10% false positive rate |
| O2 | Reduce time spent on Fortify finding triage and remediation | >60% reduction in manual triage time per sprint |
| O3 | Eliminate manual certificate expiry tracking and renewal coordination | Zero certificate expiry incidents; renewal initiated automatically ≥30 days before expiry |
| O4 | Maintain human control at all critical decision points | 100% of deployments and code merges require human approval |
| O5 | Provide a governed, auditable AI assistance layer | Full audit log for all AI decisions and actions |
| O6 | Build on shared Azure infrastructure | All agents deployed as Azure Functions on shared Azure tenant |

---

## 5. Scope

### In Scope
- Three automation tracks: Quality Gate, Security Loop, Certificate Loop.
- Integration with Azure DevOps (PR events, pipeline triggers).
- Integration with Fortify SSC REST API.
- Integration with Azure Key Vault for certificate storage and retrieval.
- Integration with IIS and Azure App Service for certificate binding.
- AI agent logic using Claude LLM (Anthropic) via API.
- Human approval gates at defined checkpoints.
- Audit logging for all agent actions.
- Deployment to Azure (Azure Functions, Azure Storage, Azure Monitor).

### Out of Scope
- Changes to existing CI/CD pipelines beyond trigger integration.
- Support for codebases other than C# (.NET) and TypeScript (Angular).
- Automated code merging without human approval.
- Support for certificate authorities not currently in use by the team.
- Mobile or native application certificate management.
- Fine-tuning or training custom ML models.

---

## 6. Stakeholders

| Role | Name / Team | Interest |
|---|---|---|
| Project Sponsor | Core & Main Leadership | Delivery of automation, cost reduction |
| Primary Contact | Pankaj Pathak | Architecture and implementation oversight |
| Engineering Team | Core & Main Developers | Reduced review burden, consistent standards |
| InfoSec Team | Security / InfoSec | Fortify integration, vulnerability visibility |
| Operations Team | DevOps / Ops | Certificate deployment, IIS management |
| AI Agents (automated) | BlueLine Agent Suite | Execution of defined automation tasks |

---

## 7. Current State (As-Is)

### Code Review Process
```
Developer opens PR
        ↓
Reviewer manually reads diff
        ↓
Reviewer checks against .NET/Angular guidelines (from memory or docs)
        ↓
Reviewer adds inline comments manually
        ↓
Developer addresses comments
        ↓
Re-review cycle (repeated as needed)
        ↓
Manual approval and merge
```
**Pain:** Inconsistent, slow, reviewer-dependent.

### Security Scanning Process
```
Developer or pipeline triggers Fortify scan (manual)
        ↓
Fortify generates findings report
        ↓
Engineer manually reviews findings list
        ↓
Engineer researches each finding to understand impact
        ↓
Engineer decides what to fix vs. suppress
        ↓
Engineer implements fix manually in code
        ↓
Engineer re-runs Fortify to verify (manual trigger again)
```
**Pain:** No automation, no AI-assisted fix generation, findings backlog grows.

### Certificate Renewal Process
```
Engineer notices expiry via email alert or spreadsheet
        ↓
Engineer raises request (internal: C&M portal; external: InfoSec team)
        ↓
Certificate issued (days to weeks)
        ↓
Engineer downloads cert, validates manually
        ↓
Engineer copies cert to each server (Dev, QA, Prod)
        ↓
Engineer installs in IIS, binds to site
        ↓
Engineer verifies HTTPS working
        ↓
Repeat for each environment
```
**Pain:** Fully manual, error-prone, risk of expiry if spreadsheet missed.

---

## 8. Future State (To-Be)

### Code Review Process
```
Developer opens PR
        ↓
PR trigger fires → CLARION + LUMEN + VECTOR run in parallel
        ↓
Agents post inline comments with explanations and suggested fixes
        ↓
ASCENT aggregates results, prioritizes high-risk findings
        ↓
Human reviewer sees pre-annotated PR, focuses on logic and context
        ↓
Human approves or requests changes
        ↓
Merge (human-controlled)
```

### Security Scanning Process
```
Pipeline runs OR WATCHTOWER scheduled scan fires
        ↓
BULWARK fetches Fortify findings, AI triages each finding
        ↓
Critical findings → FORGE generates code fix + test, creates draft PR
        ↓
False positives → suppressed with documented rationale
        ↓
STEWARD logs all decisions to audit trail
        ↓
Human reviews FORGE-generated PRs before merge
```

### Certificate Renewal Process
```
TIMELINE runs daily, queries Azure Key Vault for expiry data
        ↓
Certs expiring ≤ 30 days → REGENT flags, identifies owner
        ↓
COURIER raises renewal request with CA (automated)
        ↓
New cert downloaded, validated
        ↓
HARBOUR deploys cert to Dev → QA → Prod automatically
        ↓
HTTPS verified programmatically post-deploy
        ↓
Full audit log written; human notified of completion
```

---

## 9. Track Descriptions

### 9.1 Quality Gate Track

**Trigger:** Pull Request opened or updated in Azure DevOps / GitHub.

**Purpose:** Ensure that every PR is reviewed against established coding standards, architectural patterns, and maintainability criteria before a human reviewer sees it — reducing the cognitive load on reviewers and standardizing quality enforcement.

**Agents in this track:**

| Agent | Role | Output |
|---|---|---|
| CLARION | Coding standards and conventions checker | Inline PR comments for violations |
| LUMEN | Code smell and anti-pattern detector | Flagged smells with explanations |
| VECTOR | Risk hotspot and complexity scorer | Per-file risk score, reviewer attention flags |
| ASCENT | Continuous improvement engine | Updated rules, reviewer guidance |

**Human gate:** After ASCENT aggregates findings, a human reviewer must approve or reject the PR. Agents cannot merge code.

---

### 9.2 Security Track

**Trigger:** CI/CD pipeline run (on commit) or WATCHTOWER scheduled scan.

**Purpose:** Automate the end-to-end lifecycle of security vulnerability findings from Fortify — from initial discovery and triage, through fix generation, to audit logging — reducing manual effort and accelerating remediation.

**Agents in this track:**

| Agent | Role | Output |
|---|---|---|
| BULWARK | Fortify findings triage | Classified findings (critical / false positive / review needed) |
| WATCHTOWER | Scheduled scan monitor | Scan triggers, new finding alerts |
| FORGE | Fix generator | Draft PRs with AI-generated code fixes and tests |
| STEWARD | Audit trail manager | Structured log of all security decisions |

**Human gate:** FORGE-generated fix PRs require human review and approval before merge. STEWARD logs are reviewed by InfoSec periodically.

---

### 9.3 Certificate Loop Track

**Trigger:** Azure Timer (daily schedule).

**Purpose:** Fully automate the SSL/TLS certificate lifecycle — from expiry detection through issuance, deployment, and validation — across all environments, eliminating the manual spreadsheet-and-email process entirely.

**Agents in this track:**

| Agent | Role | Output |
|---|---|---|
| TIMELINE | Expiry threshold monitor | Renewal work items for certs expiring within threshold |
| REGENT | Certificate inventory manager | Structured inventory: name, owner, CA, environment, expiry |
| COURIER | Issuance orchestrator | Renewed certificate files from CA |
| HARBOUR | Deployment and validation agent | Deployed cert + HTTPS verification result |

**Human gate:** Deployment to Production requires explicit human approval (notification sent via email / Teams). Dev and QA deployments can be automated.

---

## 10. Agent Catalogue

| Agent | Track | Trigger Type | Consumes | Produces | Human Gate? |
|---|---|---|---|---|---|
| CLARION | Quality Gate | PR Event | PR diff, coding ruleset | Inline PR comments | No |
| LUMEN | Quality Gate | PR Event | PR diff | Smell annotations | No |
| VECTOR | Quality Gate | PR Event | PR diff, git history | Risk score per file | No |
| ASCENT | Quality Gate | PR Event | Agent outputs | Consolidated review summary | Yes (PR approval) |
| BULWARK | Security | Pipeline / Schedule | Fortify SSC findings | Classified finding list | No |
| WATCHTOWER | Security | Schedule | Fortify SSC API | Scan trigger, alert | No |
| FORGE | Security | BULWARK output | Classified findings, source code | Draft fix PR | Yes (PR approval) |
| STEWARD | Security | All security events | All agent outputs | Audit log entries | No |
| TIMELINE | Certificate | Timer (daily) | Azure Key Vault cert metadata | Renewal work items | No |
| REGENT | Certificate | TIMELINE output | Work items, existing inventory | Updated inventory record | No |
| COURIER | Certificate | REGENT output | Renewal work item | New certificate file | No |
| HARBOUR | Certificate | COURIER output | New cert file | Deployed cert, HTTPS status | Yes (Prod only) |

---

## 11. AI Approach

### Model
All agents use **Claude (claude-sonnet-4-6)** via the Anthropic API. The model is invoked with structured system prompts that encode:
- The agent's specific role and constraints.
- The relevant coding standards, security policies, or certificate policies.
- Tool definitions (for tool-use enabled agents).

### Reasoning Layer
Each agent follows a **reason → act → verify** loop:
1. **Reason:** Analyze the input (diff, finding, cert metadata) and form a judgment.
2. **Act:** Call the appropriate tool (post comment, create PR, deploy cert).
3. **Verify:** Confirm the action succeeded; log result.

### Policy Guardrails
- Agents cannot take destructive actions (delete code, revoke certs) without explicit human instruction.
- All agent actions are logged with the reasoning that produced them.
- Agents are instructed to express uncertainty rather than guess — uncertain findings are escalated to human review.

### Human Override
Any agent output can be overridden by a human at any point. Override decisions are logged and fed back into ASCENT for quality improvement.

---

## 12. Assumptions & Constraints

| # | Assumption / Constraint |
|---|---|
| A1 | The team uses Azure DevOps or GitHub as their source control and CI/CD platform. |
| A2 | Fortify SSC is accessible via its REST API from the agent runtime environment. |
| A3 | Azure Key Vault is already provisioned and contains the current certificate inventory. |
| A4 | The team has an existing CA (internal or external) with an API-accessible renewal process. |
| A5 | Engineers will provide the initial coding standards ruleset for CLARION/LUMEN to consume. |
| A6 | All environments (Dev, QA, Prod) are reachable from the agent runtime (VNet or firewall rules). |
| A7 | Human reviewers will monitor agent-generated PRs and comments within agreed SLA (e.g., 1 business day). |
| C1 | No code may be merged without human approval. |
| C2 | Production certificate deployment requires explicit human sign-off. |
| C3 | All agent actions must be auditable — no silent failures. |
| C4 | The solution must operate within the existing Azure tenant; no new tenants to be created. |

---

## 13. Dependencies

| Dependency | Owner | Required For |
|---|---|---|
| Fortify SSC API access | InfoSec / Security Team | BULWARK, WATCHTOWER |
| Azure DevOps / GitHub webhook configuration | DevOps | CLARION, LUMEN, VECTOR, ASCENT, FORGE |
| Azure Key Vault access (read/write) | Ops / Platform | TIMELINE, REGENT, COURIER, HARBOUR |
| CA API credentials (internal or DigiCert) | InfoSec | COURIER |
| IIS / App Service deployment credentials | Ops | HARBOUR |
| Anthropic API key (Claude) | BlueLine Team | All agents |
| Azure Function App provisioning | Platform / DevOps | All agents |
| Coding standards documentation | Engineering Lead | CLARION, LUMEN |

---

## 14. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| AI generates incorrect code fix (FORGE) | Medium | High | Human approval gate on all FORGE PRs; test coverage required |
| False positive rate too high in CLARION/BULWARK | Medium | Medium | Start with conservative rules; tune via ASCENT feedback loop |
| HARBOUR deploys wrong cert to wrong site | Low | High | Dry-run mode; verbose logging; Prod gate requires human approval |
| Fortify API rate limits slow BULWARK | Low | Medium | Implement retry with exponential backoff |
| Certificate CA API unavailable during renewal window | Low | High | TIMELINE alerts 30 days ahead, providing buffer for manual fallback |
| LLM hallucination in security context | Medium | High | Agent outputs are advisory only; InfoSec reviews STEWARD logs |
| Azure Function cold start delays PR feedback | Low | Low | Use Premium plan for always-warm instances on PR path |

---

## 15. Phased Rollout Plan

### Phase 1 — Quick Wins (Quality Gate + Security Loop)

**Goal:** Demonstrate value quickly with low-risk, easily reversible automation.

| Step | Action | Owner |
|---|---|---|
| 1.1 | Provision Azure Function App for Quality Gate agents | DevOps |
| 1.2 | Configure Azure DevOps PR webhook to trigger CLARION/LUMEN/VECTOR | DevOps |
| 1.3 | Load coding standards into agent system prompts | Engineering Lead |
| 1.4 | Run agents in shadow mode (log output, do not post comments) for 2 sprints | BlueLine Team |
| 1.5 | Review shadow output, tune rules | Engineering Lead + BlueLine Team |
| 1.6 | Enable comment posting in non-production repos first | BlueLine Team |
| 1.7 | Full rollout to all repos | BlueLine Team |
| 1.8 | Provision Fortify SSC API access | InfoSec |
| 1.9 | Deploy BULWARK + WATCHTOWER in triage-only mode (no FORGE yet) | BlueLine Team |
| 1.10 | Run FORGE in shadow mode; review generated fixes | Engineering Lead |
| 1.11 | Enable FORGE PR creation after fix quality validated | BlueLine Team |

### Phase 2 — Operational Maturity (Certificate Loop)

**Goal:** Automate the highest-risk manual process (certificate expiry).

| Step | Action | Owner |
|---|---|---|
| 2.1 | Audit and import all current certificates into Azure Key Vault | Ops |
| 2.2 | Build REGENT inventory from Key Vault + existing tracking sheets | BlueLine Team |
| 2.3 | Deploy TIMELINE in read-only mode; validate expiry detection accuracy | BlueLine Team |
| 2.4 | Integrate COURIER with CA API in Dev environment only | BlueLine Team + InfoSec |
| 2.5 | Test HARBOUR deployment in Dev; validate HTTPS post-deploy | BlueLine Team + Ops |
| 2.6 | Extend to QA; extend to Prod with human approval gate | BlueLine Team |
| 2.7 | Decommission manual tracking spreadsheets | Ops |

---

## 16. Glossary

| Term | Definition |
|---|---|
| Agent | An autonomous AI-powered software component that performs a discrete, well-defined task within a track. |
| Track | A named automation pipeline corresponding to one of the three problem areas (Quality Gate, Security, Certificate Loop). |
| ASCENT | AI agent responsible for continuous improvement of review rules based on feedback. |
| BULWARK | AI agent responsible for triaging Fortify security findings. |
| CLARION | AI agent responsible for checking coding standards compliance. |
| COURIER | AI agent responsible for orchestrating certificate issuance from a CA. |
| FORGE | AI agent responsible for generating code fixes for confirmed security vulnerabilities. |
| HARBOUR | AI agent responsible for deploying certificates to servers and validating HTTPS. |
| LUMEN | AI agent responsible for detecting code smells and anti-patterns. |
| REGENT | AI agent responsible for maintaining the certificate inventory. |
| STEWARD | AI agent responsible for writing audit logs for all security decisions. |
| TIMELINE | AI agent responsible for monitoring certificate expiry thresholds. |
| VECTOR | AI agent responsible for scoring code risk and complexity hotspots. |
| WATCHTOWER | AI agent responsible for scheduling and monitoring Fortify scans. |
| Fortify SSC | Micro Focus / OpenText Fortify Software Security Center — the static application security testing (SAST) tool used by the team. |
| Azure Key Vault | Microsoft Azure service for securely storing and managing certificates, secrets, and keys. |
| CA | Certificate Authority — the entity that issues SSL/TLS certificates. |
| IIS | Internet Information Services — Microsoft's web server, used for hosting .NET applications and binding certificates. |
| LLM | Large Language Model — the AI model (Claude) used as the reasoning engine for all agents. |
| Shadow Mode | An operating mode in which an agent produces output but does not take any real action — used for validation before full rollout. |
| Human Gate | A mandatory pause in an automated workflow that requires a human to review and explicitly approve before the workflow continues. |

---

*End of Understanding Document — Version 1.0*

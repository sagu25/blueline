# Project BlueLine — Low Level Design (LLD)

**Version:** 1.0  
**Date:** 2026-04-15  
**Prepared by:** Project BlueLine Team  
**Status:** Draft for Review

---

## Table of Contents

1. [System Architecture Overview](#1-system-architecture-overview)
2. [Technology Stack](#2-technology-stack)
3. [Infrastructure Design](#3-infrastructure-design)
4. [Agent Base Framework](#4-agent-base-framework)
5. [Track 1: Quality Gate — Detailed Design](#5-track-1-quality-gate--detailed-design)
   - 5.1 [CLARION Agent](#51-clarion-agent)
   - 5.2 [LUMEN Agent](#52-lumen-agent)
   - 5.3 [VECTOR Agent](#53-vector-agent)
   - 5.4 [ASCENT Agent](#54-ascent-agent)
6. [Track 2: Security Loop — Detailed Design](#6-track-2-security-loop--detailed-design)
   - 6.1 [WATCHTOWER Agent](#61-watchtower-agent)
   - 6.2 [BULWARK Agent](#62-bulwark-agent)
   - 6.3 [FORGE Agent](#63-forge-agent)
   - 6.4 [STEWARD Agent](#64-steward-agent)
7. [Track 3: Certificate Loop — Detailed Design](#7-track-3-certificate-loop--detailed-design)
   - 7.1 [TIMELINE Agent](#71-timeline-agent)
   - 7.2 [REGENT Agent](#72-regent-agent)
   - 7.3 [COURIER Agent](#73-courier-agent)
   - 7.4 [HARBOUR Agent](#74-harbour-agent)
8. [Data Models](#8-data-models)
9. [API Contracts](#9-api-contracts)
10. [Sequence Diagrams](#10-sequence-diagrams)
11. [Error Handling Strategy](#11-error-handling-strategy)
12. [Audit Logging Design](#12-audit-logging-design)
13. [Security Design](#13-security-design)
14. [Configuration & Environment Variables](#14-configuration--environment-variables)
15. [Deployment Topology](#15-deployment-topology)

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL TRIGGERS                            │
│  ┌─────────────┐  ┌─────────────────┐  ┌────────────────────────┐  │
│  │Azure DevOps │  │  Fortify SSC    │  │  Azure Timer (daily)   │  │
│  │ PR Webhook  │  │  Pipeline Hook  │  │  Certificate Scheduler │  │
│  └──────┬──────┘  └───────┬─────────┘  └───────────┬────────────┘  │
└─────────┼─────────────────┼────────────────────────┼───────────────┘
          │                 │                         │
┌─────────▼─────────────────▼─────────────────────────▼───────────────┐
│                     AZURE API MANAGEMENT (Gateway)                   │
│              (Auth, Rate Limiting, Request Routing)                  │
└─────────┬─────────────────┬─────────────────────────┬───────────────┘
          │                 │                         │
┌─────────▼──────┐  ┌───────▼────────┐  ┌────────────▼──────────────┐
│  QUALITY GATE  │  │ SECURITY LOOP  │  │    CERTIFICATE LOOP       │
│  Function App  │  │  Function App  │  │      Function App         │
│                │  │                │  │                           │
│ CLARION        │  │ WATCHTOWER     │  │ TIMELINE                  │
│ LUMEN          │  │ BULWARK        │  │ REGENT                    │
│ VECTOR         │  │ FORGE          │  │ COURIER                   │
│ ASCENT         │  │ STEWARD        │  │ HARBOUR                   │
└────────┬───────┘  └───────┬────────┘  └────────────┬──────────────┘
         │                  │                        │
┌────────▼──────────────────▼────────────────────────▼──────────────┐
│                      SHARED SERVICES LAYER                         │
│  ┌──────────────┐  ┌───────────────┐  ┌───────────────────────┐   │
│  │  Claude API  │  │ Azure Storage │  │  Azure Monitor /      │   │
│  │  (LLM Core)  │  │ (State Store) │  │  Log Analytics        │   │
│  └──────────────┘  └───────────────┘  └───────────────────────┘   │
└────────────────────────────────────────────────────────────────────┘
         │                  │                        │
┌────────▼──────┐  ┌────────▼────────┐  ┌───────────▼──────────────┐
│ Azure DevOps  │  │  Fortify SSC    │  │  Azure Key Vault /       │
│ / GitHub API  │  │  REST API       │  │  IIS / App Service       │
└───────────────┘  └─────────────────┘  └──────────────────────────┘
```

---

## 2. Technology Stack

| Layer | Technology | Justification |
|---|---|---|
| Agent Runtime | Azure Functions (Python 3.11) | Serverless, event-driven, native Azure integration |
| AI Reasoning | Anthropic Claude API (`claude-sonnet-4-6`) | Best-in-class reasoning for code analysis |
| Orchestration | Azure Durable Functions | Stateful, long-running workflows (cert renewal) |
| State Storage | Azure Table Storage | Lightweight key-value state per agent run |
| Secret Storage | Azure Key Vault | API keys, cert private keys, CA credentials |
| Message Bus | Azure Service Bus | Decoupled agent-to-agent communication |
| Logging | Azure Monitor + Log Analytics | Centralized audit trail and alerting |
| Source Control Integration | Azure DevOps REST API / GitHub API | PR comments, webhook handling |
| Security Scanning | Fortify SSC REST API | Existing team tool |
| Certificate Management | Azure Key Vault Certificates API | Centralized cert lifecycle |
| Notifications | Microsoft Teams Webhooks / Azure Email | Human approval notifications |
| IaC | Azure Bicep / Terraform | Repeatable infrastructure provisioning |

---

## 3. Infrastructure Design

### 3.1 Azure Resource Groups

```
blueline-rg-shared          ← Shared infrastructure (Key Vault, Service Bus, Storage)
blueline-rg-quality         ← Quality Gate Function App + supporting resources
blueline-rg-security        ← Security Loop Function App + supporting resources
blueline-rg-certloop        ← Certificate Loop Function App + supporting resources
```

### 3.2 Azure Function Apps

| Function App | Plan | Always-On | Triggers |
|---|---|---|---|
| `blueline-quality-fa` | Premium EP1 | Yes | HTTP (PR webhook) |
| `blueline-security-fa` | Consumption | No | HTTP (pipeline hook) + Timer |
| `blueline-certloop-fa` | Consumption | No | Timer (daily) |

### 3.3 Shared Resources

| Resource | Type | Purpose |
|---|---|---|
| `blueline-kv` | Azure Key Vault | API keys, CA credentials, cert storage |
| `blueline-sb` | Azure Service Bus | Agent-to-agent message passing |
| `blueline-storage` | Azure Storage Account | Agent state, audit log blobs |
| `blueline-law` | Log Analytics Workspace | Centralized logs |
| `blueline-apim` | Azure API Management | Webhook ingress, auth enforcement |

---

## 4. Agent Base Framework

Every agent is implemented as a Python class inheriting from a common `BaseAgent`. This enforces consistent structure, logging, and error handling.

### 4.1 BaseAgent Class

```python
# blueline/core/base_agent.py

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import anthropic
import logging

@dataclass
class AgentContext:
    run_id: str                         # Unique ID for this agent run
    trigger_type: str                   # "pr_event" | "pipeline" | "schedule"
    trigger_payload: dict               # Raw trigger payload
    agent_name: str                     # e.g., "CLARION"
    track: str                          # "quality_gate" | "security" | "cert_loop"
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class AgentResult:
    run_id: str
    agent_name: str
    status: str                         # "success" | "partial" | "failed" | "escalated"
    output: dict                        # Agent-specific structured output
    reasoning: str                      # LLM reasoning chain (for audit)
    actions_taken: list[str]            # List of external actions performed
    escalated_to_human: bool = False
    error: str | None = None
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class BaseAgent(ABC):
    def __init__(self, context: AgentContext):
        self.context = context
        self.client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY from env
        self.logger = logging.getLogger(context.agent_name)
        self._actions_taken: list[str] = []

    @abstractmethod
    def build_system_prompt(self) -> str:
        """Return the agent-specific system prompt."""
        pass

    @abstractmethod
    def build_tools(self) -> list[dict]:
        """Return the tool definitions this agent can use."""
        pass

    @abstractmethod
    async def execute(self) -> AgentResult:
        """Main agent logic. Must return AgentResult."""
        pass

    def call_llm(self, messages: list[dict], max_tokens: int = 4096) -> anthropic.types.Message:
        """Wrapper around Anthropic API with prompt caching enabled."""
        return self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=max_tokens,
            system=[
                {
                    "type": "text",
                    "text": self.build_system_prompt(),
                    "cache_control": {"type": "ephemeral"}   # prompt caching
                }
            ],
            tools=self.build_tools(),
            messages=messages
        )

    def log_action(self, action: str):
        self._actions_taken.append(action)
        self.logger.info(f"[{self.context.run_id}] ACTION: {action}")

    def escalate(self, reason: str) -> AgentResult:
        self.logger.warning(f"[{self.context.run_id}] ESCALATING: {reason}")
        return AgentResult(
            run_id=self.context.run_id,
            agent_name=self.context.agent_name,
            status="escalated",
            output={"escalation_reason": reason},
            reasoning=reason,
            actions_taken=self._actions_taken,
            escalated_to_human=True
        )
```

### 4.2 Agent Run State (Azure Table Storage Schema)

**Table: `AgentRuns`**

| Column | Type | Description |
|---|---|---|
| PartitionKey | string | `{track}#{agent_name}` e.g., `quality_gate#CLARION` |
| RowKey | string | `run_id` (UUID) |
| TriggerType | string | `pr_event` / `pipeline` / `schedule` |
| TriggerRef | string | PR ID / pipeline run ID / "daily" |
| Status | string | `success` / `partial` / `failed` / `escalated` |
| OutputJson | string | JSON-serialized AgentResult.output |
| ReasoningText | string | LLM reasoning chain |
| ActionsTaken | string | JSON array of action strings |
| EscalatedToHuman | bool | Whether human escalation was triggered |
| StartedAt | datetime | UTC start time |
| CompletedAt | datetime | UTC completion time |
| ErrorMessage | string | (nullable) error details |

---

## 5. Track 1: Quality Gate — Detailed Design

### Trigger Flow

```
Azure DevOps PR webhook (POST /api/quality-gate/trigger)
        │
        ▼
Azure API Management (validate HMAC signature)
        │
        ▼
blueline-quality-fa: QualityGateOrchestrator (Durable Function)
        │
   ┌────┼────────────┬────────────┐
   ▼    ▼            ▼            ▼
CLARION LUMEN     VECTOR      (parallel fan-out)
   │    │            │
   └────┴────────────┘
              │
              ▼
           ASCENT (aggregates, posts to PR)
              │
              ▼
       Human approval in PR
```

### Webhook Payload (Azure DevOps PR Created Event)

```json
{
  "eventType": "git.pullrequest.created",
  "resource": {
    "pullRequestId": 1234,
    "repositoryId": "repo-guid",
    "sourceRefName": "refs/heads/feature/my-branch",
    "targetRefName": "refs/heads/main",
    "title": "Add payment processing module"
  }
}
```

---

### 5.1 CLARION Agent

**Purpose:** Check PR diff against the team's .NET and Angular coding standards.

**Input:** PR diff (unified diff format), coding standards document.

**Output:** List of `Violation` objects, each with file path, line number, rule violated, severity, suggested fix.

**System Prompt (condensed):**
```
You are CLARION, a code standards enforcement agent for a .NET (C#) and Angular (TypeScript) 
codebase. Your job is to review a pull request diff and identify violations of the coding 
standards provided. For each violation:
- Cite the exact file and line number from the diff.
- State which rule is violated.
- Provide a clear, helpful explanation.
- Suggest a corrected code snippet where possible.
- Do NOT flag stylistic preferences — only objective rule violations.
- If you are uncertain, do NOT flag it. Express uncertainty explicitly.
```

**Tools:**
```python
tools = [
    {
        "name": "post_pr_comment",
        "description": "Post an inline comment on a specific line of the PR diff.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "line_number": {"type": "integer"},
                "comment_body": {"type": "string"},
                "severity": {"type": "string", "enum": ["error", "warning", "info"]},
                "rule_id": {"type": "string"}
            },
            "required": ["file_path", "line_number", "comment_body", "severity", "rule_id"]
        }
    },
    {
        "name": "fetch_pr_diff",
        "description": "Fetch the unified diff for the current PR.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    }
]
```

**Violation Data Model:**
```python
@dataclass
class Violation:
    file_path: str
    line_number: int
    rule_id: str            # e.g., "DOTNET-001", "ANG-007"
    rule_description: str
    severity: str           # "error" | "warning" | "info"
    message: str
    suggested_fix: str | None
    confidence: float       # 0.0 - 1.0 (filter out < 0.7)
```

**Coding Standards Categories (CLARION Rule Sets):**

| Category | Rule Prefix | Examples |
|---|---|---|
| .NET Naming | `DOTNET-N-` | PascalCase classes, camelCase locals, I prefix interfaces |
| .NET Structure | `DOTNET-S-` | Single responsibility, no God classes, async suffix |
| .NET Security | `DOTNET-SEC-` | No hardcoded secrets, parameterized queries only |
| Angular Naming | `ANG-N-` | kebab-case files, PascalCase components |
| Angular Patterns | `ANG-P-` | OnPush change detection, no direct DOM manipulation |
| Angular Security | `ANG-SEC-` | No innerHTML binding, DomSanitizer required |

---

### 5.2 LUMEN Agent

**Purpose:** Detect code smells and maintainability anti-patterns.

**Input:** PR diff + full file context for changed files.

**Output:** List of `Smell` objects with smell type, location, explanation, and refactor suggestion.

**System Prompt (condensed):**
```
You are LUMEN, an expert code quality analyst. Review the provided code changes and identify 
code smells and anti-patterns that reduce maintainability. Focus on:
- Long methods (>40 lines), Large classes (>300 lines)
- Deep nesting (>3 levels), Magic numbers/strings
- Duplicated logic, Feature envy, Shotgun surgery
- Dead code, Unnecessary complexity
For each smell: explain WHY it's a problem and suggest the refactoring approach.
```

**Smell Categories:**
```python
class SmellType(str, Enum):
    LONG_METHOD = "long_method"
    LARGE_CLASS = "large_class"
    DEEP_NESTING = "deep_nesting"
    MAGIC_NUMBER = "magic_number"
    MAGIC_STRING = "magic_string"
    DUPLICATE_CODE = "duplicate_code"
    FEATURE_ENVY = "feature_envy"
    DEAD_CODE = "dead_code"
    PRIMITIVE_OBSESSION = "primitive_obsession"
    GOD_CLASS = "god_class"
    LONG_PARAMETER_LIST = "long_parameter_list"

@dataclass
class Smell:
    smell_type: SmellType
    file_path: str
    start_line: int
    end_line: int
    description: str
    suggested_refactor: str
    severity: str           # "major" | "minor"
```

---

### 5.3 VECTOR Agent

**Purpose:** Score each changed file for risk and complexity, flagging hotspots for reviewer attention.

**Input:** PR diff, git history (commit frequency, churn rate per file).

**Output:** Per-file risk score with breakdown, overall PR risk level.

**Risk Scoring Formula:**
```
RiskScore(file) = 
    (CyclomaticComplexityScore × 0.35) +
    (ChurnRate30Days × 0.25) +
    (DependencyFanOut × 0.20) +
    (TestCoverage_inverse × 0.20)

Where:
  CyclomaticComplexityScore = min(complexity / 10, 1.0)
  ChurnRate30Days           = min(commits_in_30_days / 20, 1.0)
  DependencyFanOut          = min(imported_modules / 15, 1.0)
  TestCoverage_inverse      = 1.0 - (test_coverage / 100)

RiskLevel:
  0.0 - 0.3  → LOW
  0.3 - 0.6  → MEDIUM
  0.6 - 0.8  → HIGH
  0.8 - 1.0  → CRITICAL
```

**Output Model:**
```python
@dataclass
class FileRisk:
    file_path: str
    risk_score: float
    risk_level: str         # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    complexity_score: float
    churn_score: float
    dependency_score: float
    test_coverage_score: float
    reviewer_note: str      # Human-readable explanation for reviewer

@dataclass
class PRRiskSummary:
    pr_id: int
    overall_risk_level: str
    file_risks: list[FileRisk]
    critical_files: list[str]   # Files requiring mandatory human review
    total_risk_score: float
```

---

### 5.4 ASCENT Agent

**Purpose:** Aggregate all agent outputs into a consolidated PR review summary, post it, and collect feedback for continuous improvement.

**Input:** CLARION violations, LUMEN smells, VECTOR risk summary.

**Output:** Single consolidated PR comment (review summary), updated rules document (if feedback available).

**Aggregation Logic:**
```python
class PRReviewSummary:
    def build_summary(self, violations, smells, risk_summary) -> str:
        # Priority 1: CRITICAL risk files → "Must review carefully"
        # Priority 2: ERROR-severity violations → "Must fix before merge"
        # Priority 3: MAJOR smells → "Should fix before merge"
        # Priority 4: HIGH risk + MEDIUM violations → "Consider fixing"
        # Priority 5: INFO/MINOR → informational only
        
        sections = [
            self._build_risk_header(risk_summary),
            self._build_required_fixes(violations),
            self._build_smell_recommendations(smells),
            self._build_reviewer_checklist(risk_summary)
        ]
        return "\n\n".join(sections)
```

**Feedback Loop (ASCENT Learning):**
- Human reviewers can react to agent comments with 👍 (agree) or 👎 (disagree).
- ASCENT collects reactions via Azure DevOps API daily.
- False positive patterns (👎 on specific rule IDs) are logged.
- Rules with >20% false positive rate are flagged for engineering review.
- Engineering lead updates the standards doc; ASCENT reloads next run.

```python
@dataclass
class FeedbackRecord:
    run_id: str
    rule_id: str
    reaction: str       # "thumbs_up" | "thumbs_down"
    reviewer_id: str
    comment_id: str
    recorded_at: datetime
```

---

## 6. Track 2: Security Loop — Detailed Design

### Trigger Flow

```
(A) Pipeline completes → POST /api/security/pipeline-trigger
(B) Daily timer → WATCHTOWER fires independently

Both paths converge at:
        ▼
BULWARK: Fetch + Triage Fortify findings
        │
   ┌────┴────────────────────┐
   ▼                         ▼
Critical findings        False positives
   │                         │
FORGE: Generate fix       STEWARD: Log suppression
   │
Draft PR created
   │
Human approval
   │
STEWARD: Log merge
```

---

### 6.1 WATCHTOWER Agent

**Purpose:** Monitor Fortify SSC for new vulnerability findings and trigger the security loop.

**Schedule:** Runs daily at 02:00 UTC via Azure Timer Trigger.

**Fortify SSC API Calls:**
```
GET /api/v1/projects                        → list all projects
GET /api/v1/projectVersions?projectId={id} → get versions
GET /api/v1/issues?projectVersionId={id}&filter=NEW → new issues only
```

**WATCHTOWER Logic:**
```python
async def execute(self) -> AgentResult:
    projects = await self.fortify.list_projects()
    new_findings_all = []
    
    for project in projects:
        versions = await self.fortify.get_versions(project.id)
        for version in versions:
            new_findings = await self.fortify.get_new_issues(version.id)
            new_findings_all.extend(new_findings)
    
    if new_findings_all:
        # Publish to Service Bus → triggers BULWARK
        await self.service_bus.publish(
            topic="security.findings.new",
            message={"findings": [f.to_dict() for f in new_findings_all]}
        )
        self.log_action(f"Published {len(new_findings_all)} new findings to Service Bus")
    
    return AgentResult(status="success", output={"new_findings_count": len(new_findings_all)}, ...)
```

---

### 6.2 BULWARK Agent

**Purpose:** Triage Fortify findings using AI to classify each as critical, needs review, or false positive.

**Input:** List of Fortify findings (from WATCHTOWER via Service Bus or pipeline trigger).

**System Prompt (condensed):**
```
You are BULWARK, a security triage agent for a .NET and Angular enterprise application.
You will be given a list of Fortify SAST findings. For each finding:

1. Classify it as:
   - CRITICAL: Confirmed vulnerability that must be fixed immediately
   - NEEDS_REVIEW: Possible vulnerability requiring human security review
   - FALSE_POSITIVE: Not an actual vulnerability (explain why)
   - KNOWN_ACCEPTABLE: Accepted risk (if matches known suppression patterns)

2. For CRITICAL findings: identify the exact vulnerable code path.
3. Provide a confidence score (0.0-1.0) for your classification.
4. Never classify a finding as false positive if you are uncertain — prefer NEEDS_REVIEW.
```

**Fortify Finding Model:**
```python
@dataclass
class FortifyFinding:
    issue_id: str
    category: str               # e.g., "SQL Injection", "XSS", "Path Traversal"
    severity: str               # "Critical" | "High" | "Medium" | "Low"
    file_path: str
    line_number: int
    source_code_snippet: str
    rule_id: str
    project: str
    project_version: str

@dataclass  
class TriagedFinding:
    finding: FortifyFinding
    classification: str         # "CRITICAL" | "NEEDS_REVIEW" | "FALSE_POSITIVE" | "KNOWN_ACCEPTABLE"
    confidence: float
    reasoning: str
    vulnerable_code_path: str | None
    recommended_action: str
```

**Classification Routing:**
```python
async def route_findings(self, triaged: list[TriagedFinding]):
    for finding in triaged:
        if finding.classification == "CRITICAL" and finding.confidence >= 0.8:
            # Send to FORGE for fix generation
            await self.service_bus.publish("security.critical.fix-needed", finding)
        elif finding.classification in ("CRITICAL", "NEEDS_REVIEW"):
            # Send alert to InfoSec team
            await self.notifier.alert_infosec(finding)
        elif finding.classification == "FALSE_POSITIVE":
            # Suppress in Fortify + log to STEWARD
            await self.fortify.suppress_issue(finding.finding.issue_id, finding.reasoning)
        
        # Always log to STEWARD
        await self.service_bus.publish("security.audit", finding)
```

---

### 6.3 FORGE Agent

**Purpose:** Generate a code fix and test for confirmed critical vulnerabilities.

**Input:** TriagedFinding (CRITICAL classification), source file content.

**Output:** Draft PR containing the fix code + test + explanation.

**System Prompt (condensed):**
```
You are FORGE, a security remediation agent. You will be given a confirmed security 
vulnerability finding from a .NET or Angular codebase. Your job is to:

1. Understand the vulnerable code path precisely.
2. Generate a secure replacement implementation that:
   - Fixes the vulnerability without changing functionality.
   - Follows the project's existing naming and style conventions.
   - Adds a unit test that verifies the fix blocks the attack vector.
3. Provide a clear explanation of what was vulnerable and why your fix resolves it.
4. If the fix requires architectural changes beyond a single file, return a NEEDS_HUMAN 
   status with a detailed description of what must be done.

Security principles to apply:
- SQL Injection: Use parameterized queries / ORM only. Never string-concatenate SQL.
- XSS: Use DomSanitizer in Angular. Encode output in .NET.
- Path Traversal: Validate and sanitize all file paths against allowed roots.
- Secrets: Move to Azure Key Vault. Never hardcode credentials.
```

**FORGE Output Model:**
```python
@dataclass
class ForgeFixResult:
    finding_id: str
    status: str                 # "fix_generated" | "needs_human" | "cannot_fix"
    original_file: str
    original_code: str
    fixed_code: str
    test_code: str
    fix_explanation: str
    pr_title: str
    pr_description: str
    files_modified: list[str]
```

**PR Creation Flow:**
```python
async def create_fix_pr(self, fix: ForgeFixResult) -> str:
    branch_name = f"blueline/forge-fix-{fix.finding_id[:8]}"
    
    # Create branch from main
    await self.devops.create_branch(branch_name, base="main")
    
    # Commit the fix
    await self.devops.commit_files(
        branch=branch_name,
        files={
            fix.original_file: fix.fixed_code,
            self._test_file_path(fix): fix.test_code
        },
        message=f"[FORGE] Security fix: {fix.pr_title}"
    )
    
    # Open draft PR with security label
    pr_url = await self.devops.create_pr(
        source_branch=branch_name,
        target_branch="main",
        title=f"[Security Fix] {fix.pr_title}",
        description=fix.pr_description,
        labels=["security", "forge-generated"],
        is_draft=True,
        reviewers=["infosec-team"]     # mandatory InfoSec reviewer
    )
    
    return pr_url
```

---

### 6.4 STEWARD Agent

**Purpose:** Write a structured, immutable audit log for every security decision made in the loop.

**Input:** All events from the security track (finding triaged, fix created, PR merged, suppression added).

**Storage:** Azure Blob Storage (append-only, WORM policy enabled) + Log Analytics.

**Audit Log Schema:**
```python
@dataclass
class AuditEntry:
    entry_id: str               # UUID
    timestamp: datetime         # UTC
    track: str                  # "security"
    agent: str                  # "BULWARK" | "FORGE" | "WATCHTOWER"
    event_type: str             # "finding_triaged" | "fix_generated" | "suppressed" | "pr_created" | "pr_merged"
    subject_id: str             # Fortify issue ID or PR ID
    subject_type: str           # "fortify_finding" | "pull_request"
    decision: str               # Classification or action taken
    reasoning: str              # LLM reasoning (verbatim)
    human_involved: bool        # Whether a human took or approved an action
    human_actor: str | None     # User ID if human_involved
    metadata: dict              # Additional context
```

**Retention:** Audit blobs retained for minimum 2 years (compliance).

---

## 7. Track 3: Certificate Loop — Detailed Design

### Trigger Flow

```
Azure Timer (daily 01:00 UTC)
        │
        ▼
TIMELINE: Query Azure Key Vault for all certs
        │
        ├── Expiring ≤ 30 days → Add to renewal queue
        │
        ▼
REGENT: Update inventory, identify owner and CA type
        │
        ▼
COURIER: Request renewal from CA
        │
        ▼
HARBOUR: Deploy cert → Dev → QA → [Human Gate] → Prod
        │
        ▼
STEWARD: Log full certificate lifecycle event
```

---

### 7.1 TIMELINE Agent

**Purpose:** Query Azure Key Vault for all certificates and identify those requiring renewal.

**Key Vault Query:**
```python
async def scan_certificates(self) -> list[CertExpiry]:
    from azure.keyvault.certificates import CertificateClient
    from azure.identity import DefaultAzureCredential
    
    client = CertificateClient(
        vault_url=self.key_vault_url,
        credential=DefaultAzureCredential()
    )
    
    results = []
    async for cert_prop in client.list_properties_of_certificates():
        cert = await client.get_certificate(cert_prop.name)
        days_until_expiry = (cert.properties.expires_on - datetime.now(timezone.utc)).days
        
        results.append(CertExpiry(
            cert_name=cert_prop.name,
            thumbprint=cert.properties.x509_thumbprint.hex(),
            subject=cert.cer.subject if cert.cer else "unknown",
            expires_on=cert.properties.expires_on,
            days_until_expiry=days_until_expiry,
            needs_renewal=days_until_expiry <= self.renewal_threshold_days  # default: 30
        ))
    
    return results
```

**Renewal Threshold Logic:**
```
days_until_expiry ≤ 7  → URGENT (alert immediately + escalate to human)
days_until_expiry ≤ 30 → RENEWAL_NEEDED (trigger full renewal workflow)
days_until_expiry > 30 → OK (log status, no action)
```

---

### 7.2 REGENT Agent

**Purpose:** Maintain the certificate inventory — who owns each cert, which CA issued it, which environments use it.

**Inventory Store:** Azure Table Storage (`CertificateInventory` table).

**Certificate Inventory Record:**
```python
@dataclass
class CertificateRecord:
    # Azure Table Storage keys
    PartitionKey: str       # certificate domain name, e.g., "api.core-main.com"
    RowKey: str             # cert_name in Key Vault, e.g., "apicoremaincert"
    
    # Ownership
    owner_name: str
    owner_email: str
    team: str
    
    # Certificate details
    subject: str            # CN value
    sans: list[str]         # Subject Alternative Names
    cert_type: str          # "internal" | "external" | "machine"
    ca_type: str            # "internal_pki" | "digicert" | "letsencrypt"
    ca_profile: str         # CA-specific issuance profile name
    
    # Environment mapping
    environments: dict      # {"dev": "server-dev-01", "qa": "server-qa-01", "prod": "server-prod-01"}
    iis_site_bindings: dict # {"dev": ["Default Web Site"], "prod": ["api-site", "admin-site"]}
    
    # Lifecycle
    issued_on: datetime
    expires_on: datetime
    last_renewed_on: datetime | None
    last_deployed_on: datetime | None
    auto_renew: bool        # Whether COURIER should renew automatically
    auto_deploy_prod: bool  # Whether HARBOUR can deploy to Prod without human gate
```

---

### 7.3 COURIER Agent

**Purpose:** Request and retrieve a renewed certificate from the CA.

**Input:** CertificateRecord (from REGENT), expiry alert from TIMELINE.

**CA Integration Design:**

```python
class CAType(str, Enum):
    INTERNAL_PKI = "internal_pki"
    DIGICERT = "digicert"
    LETS_ENCRYPT = "letsencrypt"

class CACourierFactory:
    @staticmethod
    def get_courier(ca_type: CAType) -> "BaseCACourier":
        couriers = {
            CAType.INTERNAL_PKI:  InternalPKICourier,
            CAType.DIGICERT:      DigiCertCourier,
            CAType.LETS_ENCRYPT:  LetsEncryptCourier
        }
        return couriers[ca_type]()

class BaseCACourier(ABC):
    @abstractmethod
    async def request_certificate(self, cert_record: CertificateRecord) -> CertBundle: ...
    
    @abstractmethod
    async def download_certificate(self, request_id: str) -> CertBundle: ...

@dataclass
class CertBundle:
    certificate_pem: str        # PEM-encoded certificate
    private_key_pem: str        # PEM-encoded private key (stored in Key Vault only)
    chain_pem: str              # Intermediate CA chain
    thumbprint: str
    expires_on: datetime
    issued_by: str
```

**COURIER Validation Steps (before passing to HARBOUR):**
```python
async def validate_cert_bundle(self, bundle: CertBundle, record: CertificateRecord) -> bool:
    checks = [
        self._verify_cn_matches(bundle, record.subject),
        self._verify_sans_present(bundle, record.sans),
        self._verify_not_expired(bundle),
        self._verify_chain_valid(bundle),
        self._verify_key_matches_cert(bundle)
    ]
    return all(checks)
```

---

### 7.4 HARBOUR Agent

**Purpose:** Deploy the renewed certificate to all environments and validate HTTPS after deployment.

**Deployment Sequence:**
```
Dev deployment → HTTPS check Dev → 
QA deployment  → HTTPS check QA  → 
[Human approval notification for Prod] →
Prod deployment → HTTPS check Prod → 
Log success
```

**IIS Deployment Logic:**
```python
async def deploy_to_iis(
    self, 
    bundle: CertBundle, 
    server: str, 
    site_bindings: list[str],
    environment: str
) -> DeployResult:
    
    # Step 1: Upload cert to remote server cert store via WinRM
    await self.winrm.run_powershell(server, f"""
        $certBytes = [Convert]::FromBase64String('{bundle.certificate_pfx_b64}')
        $cert = Import-PfxCertificate `
            -FilePath (New-TempFile $certBytes) `
            -CertStoreLocation Cert:\\LocalMachine\\My `
            -Password (ConvertTo-SecureString '{bundle.pfx_password}' -AsPlainText -Force)
        Write-Output $cert.Thumbprint
    """)
    
    # Step 2: Bind cert to IIS sites
    for site in site_bindings:
        await self.winrm.run_powershell(server, f"""
            Get-WebBinding -Name '{site}' -Protocol https |
            ForEach-Object {{ $_.AddSslCertificate('{bundle.thumbprint}', 'My') }}
        """)
    
    # Step 3: Verify HTTPS
    https_ok = await self._verify_https(server, site_bindings)
    
    return DeployResult(
        environment=environment,
        server=server,
        sites=site_bindings,
        thumbprint=bundle.thumbprint,
        https_verified=https_ok
    )
```

**HTTPS Verification:**
```python
async def _verify_https(self, server: str, sites: list[str]) -> bool:
    import ssl, socket
    
    for site in sites:
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((server, 443), timeout=10) as sock:
                with ctx.wrap_socket(sock, server_hostname=server) as ssock:
                    cert = ssock.getpeercert()
                    # Verify not expired and thumbprint matches
                    expiry = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    if expiry < datetime.utcnow():
                        return False
        except Exception as e:
            self.logger.error(f"HTTPS verification failed for {server}: {e}")
            return False
    
    return True
```

**Production Human Gate:**
```python
async def request_prod_approval(self, bundle: CertBundle, record: CertificateRecord) -> bool:
    # Send Teams notification with approve/reject buttons
    approval_id = str(uuid4())
    
    await self.teams_notifier.send_approval_card(
        channel="cert-management-approvals",
        title=f"Production Certificate Deployment: {record.subject}",
        details={
            "Certificate": record.subject,
            "Expires": bundle.expires_on.strftime("%Y-%m-%d"),
            "Target Servers": record.environments["prod"],
            "IIS Sites": record.iis_site_bindings["prod"]
        },
        approval_id=approval_id,
        callback_url=f"{self.base_url}/api/certloop/approve/{approval_id}"
    )
    
    # Wait up to 24 hours for approval
    approved = await self.approval_store.wait_for_response(
        approval_id, 
        timeout_hours=24
    )
    
    if not approved:
        await self.teams_notifier.send_message(
            "cert-management-approvals",
            f"⚠️ Prod deployment for {record.subject} timed out — manual action required"
        )
    
    return approved
```

---

## 8. Data Models

### 8.1 Complete Entity Relationship

```
AgentRun ──────────── has many ──────────── AuditEntry
    │
    ├── (quality track) ──── has many ──── Violation
    │                         └────────── Smell
    │                         └────────── FileRisk
    │
    ├── (security track) ─── has many ──── TriagedFinding
    │                         └────────── ForgeFixResult
    │
    └── (cert track) ──────── has many ──── CertExpiry
                               └────────── DeployResult

CertificateRecord ─── tracked by ─── REGENT
    └── has many ──── CertBundle (historical)
    └── has many ──── DeployResult (per environment)
```

### 8.2 Service Bus Topics & Subscriptions

| Topic | Publisher | Subscriber | Message Type |
|---|---|---|---|
| `quality.pr.triggered` | API Gateway | QualityGateOrchestrator | PRWebhookPayload |
| `security.findings.new` | WATCHTOWER | BULWARK | list[FortifyFinding] |
| `security.critical.fix-needed` | BULWARK | FORGE | TriagedFinding |
| `security.audit` | BULWARK, FORGE | STEWARD | TriagedFinding / ForgeFixResult |
| `certloop.renewal-needed` | TIMELINE | REGENT | list[CertExpiry] |
| `certloop.deploy-ready` | COURIER | HARBOUR | CertBundle + CertificateRecord |
| `certloop.audit` | All cert agents | STEWARD | AuditEntry |

---

## 9. API Contracts

### 9.1 Quality Gate Trigger Endpoint

```
POST /api/quality-gate/trigger
Content-Type: application/json
X-Azure-DevOps-Signature: sha256={hmac}

Body: Azure DevOps PR webhook payload

Response 202 Accepted:
{
  "run_id": "uuid",
  "status": "accepted",
  "pr_id": 1234,
  "estimated_completion_seconds": 120
}
```

### 9.2 Security Pipeline Trigger Endpoint

```
POST /api/security/pipeline-trigger
Content-Type: application/json
X-Pipeline-Token: {token}

Body:
{
  "pipeline_run_id": "string",
  "project": "string",
  "commit_sha": "string",
  "branch": "string"
}

Response 202 Accepted:
{
  "run_id": "uuid",
  "status": "accepted"
}
```

### 9.3 Certificate Approval Callback

```
POST /api/certloop/approve/{approval_id}
Authorization: Bearer {teams_token}
Content-Type: application/json

Body:
{
  "decision": "approved" | "rejected",
  "approver_id": "user@company.com",
  "comment": "string (optional)"
}

Response 200 OK:
{
  "approval_id": "uuid",
  "decision": "approved",
  "deployment_status": "in_progress"
}
```

### 9.4 Agent Status Query

```
GET /api/runs/{run_id}
Authorization: Bearer {token}

Response 200 OK:
{
  "run_id": "uuid",
  "track": "quality_gate",
  "status": "completed",
  "agents": [
    {"name": "CLARION", "status": "success", "completed_at": "2026-04-15T09:00:00Z"},
    {"name": "LUMEN",   "status": "success", "completed_at": "2026-04-15T09:01:00Z"},
    {"name": "VECTOR",  "status": "success", "completed_at": "2026-04-15T09:01:30Z"},
    {"name": "ASCENT",  "status": "success", "completed_at": "2026-04-15T09:02:00Z"}
  ],
  "output_summary": { ... }
}
```

---

## 10. Sequence Diagrams

### 10.1 Quality Gate — PR Review Flow

```
Developer      Azure DevOps    API Gateway    Orchestrator   CLARION/LUMEN/VECTOR   ASCENT
    │               │               │               │                │                 │
    │──opens PR────►│               │               │                │                 │
    │               │──webhook─────►│               │                │                 │
    │               │               │──validate sig─┤                │                 │
    │               │               │──POST trigger►│                │                 │
    │               │               │               │──fan-out───────►│                 │
    │               │               │               │                │──fetch diff─────┤
    │               │               │               │                │◄─diff content───┤
    │               │               │               │                │──call Claude────►
    │               │               │               │                │◄─violations─────┤
    │               │               │               │◄──results──────│                 │
    │               │               │               │──send to ASCENT►──────────────────►
    │               │               │               │                │            aggregate
    │               │               │               │                │         ──►post PR comment
    │               │◄──PR comment──────────────────────────────────────────────────────│
    │◄──notified────│               │               │                │                 │
```

### 10.2 Certificate Loop — Renewal Flow

```
Timer       TIMELINE     REGENT      COURIER     CA API    HARBOUR    IIS/AppSvc  Human
  │             │            │           │           │          │          │         │
  │──fires─────►│            │           │           │          │          │         │
  │             │──query KV──►           │           │          │          │         │
  │             │◄──cert list─┤          │           │          │          │         │
  │             │──expiring?──►          │           │          │          │         │
  │             │             │──update──┤           │          │          │         │
  │             │             │  inventory           │          │          │         │
  │             │             │──publish renewal queue          │          │         │
  │             │             │──────────►│           │          │          │         │
  │             │             │           │──request──►          │          │         │
  │             │             │           │◄──new cert─┤         │          │         │
  │             │             │           │──validate cert        │          │         │
  │             │             │           │──publish deploy-ready►│          │         │
  │             │             │           │           │          │──deploy Dev──────►│ │
  │             │             │           │           │          │◄─HTTPS OK──────── │ │
  │             │             │           │           │          │──deploy QA───────►│ │
  │             │             │           │           │          │◄─HTTPS OK──────── │ │
  │             │             │           │           │          │──notify approval──────►│
  │             │             │           │           │          │◄──approved────────────│
  │             │             │           │           │          │──deploy Prod─────►│   │
  │             │             │           │           │          │◄─HTTPS OK─────────│   │
```

---

## 11. Error Handling Strategy

### 11.1 Failure Modes and Responses

| Failure | Detection | Response |
|---|---|---|
| Claude API timeout | HTTP 408 / timeout exception | Retry 3× with exponential backoff (1s, 4s, 16s). If all fail → escalate to human. |
| Claude API rate limit | HTTP 429 | Back off 60s, retry. Log to Azure Monitor. |
| Claude returns low-confidence output | confidence < 0.7 in response | Mark finding as NEEDS_REVIEW, escalate. Never act on low-confidence output. |
| Fortify API unavailable | HTTP 503 / connection error | Retry 3×, then send Teams alert to InfoSec. Skip this run, retry next schedule. |
| Key Vault access denied | HTTP 403 | Alert Ops team, halt cert loop. Do NOT proceed without cert access. |
| IIS deployment failure | WinRM error / PS exception | Rollback: rebind previous certificate. Alert Ops. Log to STEWARD. |
| HTTPS verification failure post-deploy | SSL check fails | Rollback immediately. Alert Ops and cert owner. |
| Azure DevOps API failure | HTTP 4xx/5xx | Do not post partial comments. Log error. Alert team. |
| Service Bus message poison | Delivery count > 5 | Move to dead-letter queue. Alert BlueLine team. Do not reprocess. |

### 11.2 Retry Policy

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=16),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError))
)
async def call_with_retry(func, *args, **kwargs):
    return await func(*args, **kwargs)
```

### 11.3 Dead Letter Handling

All Service Bus topics have a dead-letter queue. A monitoring Azure Function runs hourly:
- If DLQ depth > 0 → send Teams alert with message details.
- Dead-letter messages are never auto-reprocessed — require human investigation.

---

## 12. Audit Logging Design

### 12.1 Log Levels and Destinations

| Event Type | Log Level | Destination |
|---|---|---|
| Agent started / completed | INFO | Log Analytics |
| Tool call made (LLM) | INFO | Log Analytics + Table Storage |
| PR comment posted | INFO | Log Analytics |
| Security finding triaged | WARNING/INFO | Log Analytics + Blob (immutable) |
| Fix PR created | INFO | Log Analytics + Blob (immutable) |
| Certificate deployed | INFO | Log Analytics + Blob (immutable) |
| Certificate deployment failed | ERROR | Log Analytics + Blob + Teams Alert |
| Human escalation triggered | WARNING | Log Analytics + Teams Alert |
| Agent failed | ERROR | Log Analytics + Teams Alert |

### 12.2 Structured Log Format

Every log entry uses this JSON structure:
```json
{
  "timestamp": "2026-04-15T09:00:00.000Z",
  "level": "INFO",
  "track": "security",
  "agent": "BULWARK",
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "finding_triaged",
  "subject_id": "ISSUE-12345",
  "message": "Classified SQL Injection finding as CRITICAL (confidence: 0.95)",
  "reasoning_snippet": "The code concatenates user input directly into SQL query at line 47...",
  "human_involved": false,
  "metadata": {
    "fortify_rule": "SQL Injection",
    "file": "Services/PaymentService.cs",
    "line": 47
  }
}
```

---

## 13. Security Design

### 13.1 Secrets Management

All secrets stored in Azure Key Vault `blueline-kv`. No secrets in environment variables or code.

| Secret Name | Contents | Rotated |
|---|---|---|
| `anthropic-api-key` | Claude API key | Monthly |
| `devops-pat` | Azure DevOps Personal Access Token | Monthly |
| `fortify-api-token` | Fortify SSC API token | Monthly |
| `ca-digicert-apikey` | DigiCert API key | Per CA instructions |
| `ca-internal-creds` | Internal PKI service account | Quarterly |
| `teams-webhook-url` | Outgoing webhook for notifications | On rotation |
| `servicebus-connection` | Service Bus SAS connection string | Monthly |

### 13.2 Authentication

- All Function App endpoints require **Azure AD Bearer token** authentication.
- Webhooks from Azure DevOps validated via **HMAC-SHA256 signature**.
- Agent-to-agent Service Bus communication uses **Managed Identity** (no connection strings in code).
- Key Vault access via **Managed Identity** on each Function App.

### 13.3 Network Security

- Function Apps deployed in **VNet Integration** — no public internet egress except to allowed FQDNs.
- Fortify SSC and internal CA accessed via **Private Endpoint** or VPN.
- IIS servers accessible only via **WinRM over HTTPS** (port 5986) with certificate auth.

### 13.4 LLM Security Controls

- Agent system prompts include explicit instructions: **never output secrets, keys, or credentials**.
- LLM responses are parsed structurally (via tool use) — raw text responses are not executed.
- FORGE-generated code is treated as **draft only** and requires human review before merge.
- Agent inputs (PR diffs, Fortify findings) are sanitized to remove any content that could constitute prompt injection.

---

## 14. Configuration & Environment Variables

Each Function App reads configuration from Azure App Configuration + Key Vault references.

```env
# Shared across all Function Apps
ANTHROPIC_API_KEY=@Microsoft.KeyVault(SecretUri=...)
AZURE_SERVICE_BUS_NAMESPACE=blueline-sb.servicebus.windows.net
AZURE_STORAGE_ACCOUNT=bluelinestorage
LOG_ANALYTICS_WORKSPACE_ID=<workspace-id>
BLUELINE_ENV=production                     # "production" | "staging" | "shadow"

# Quality Gate Function App
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/your-org
AZURE_DEVOPS_PAT=@Microsoft.KeyVault(...)
AZURE_DEVOPS_PROJECT=CoreMain
QUALITY_GATE_WEBHOOK_SECRET=@Microsoft.KeyVault(...)
CLARION_CONFIDENCE_THRESHOLD=0.75
VECTOR_RISK_THRESHOLD_HIGH=0.6
VECTOR_RISK_THRESHOLD_CRITICAL=0.8

# Security Function App
FORTIFY_SSC_URL=https://fortify.internal/ssc
FORTIFY_API_TOKEN=@Microsoft.KeyVault(...)
BULWARK_CONFIDENCE_THRESHOLD=0.80
FORGE_AUTO_PR_ENABLED=true
INFOSEC_TEAMS_CHANNEL=<webhook-url>

# Certificate Loop Function App
AZURE_KEYVAULT_URL=https://blueline-kv.vault.azure.net
CERT_RENEWAL_THRESHOLD_DAYS=30
CERT_URGENT_THRESHOLD_DAYS=7
DIGICERT_API_KEY=@Microsoft.KeyVault(...)
DIGICERT_ORG_ID=<org-id>
HARBOUR_AUTO_DEPLOY_PROD=false              # Always false — human gate required
CERT_APPROVALS_TEAMS_CHANNEL=<webhook-url>
HARBOUR_APPROVAL_TIMEOUT_HOURS=24
```

---

## 15. Deployment Topology

### 15.1 Azure Resource Diagram

```
Azure Subscription
├── blueline-rg-shared
│   ├── blueline-kv              (Key Vault — Premium tier, soft delete enabled)
│   ├── blueline-sb              (Service Bus — Standard tier, 3 topics)
│   ├── blueline-storage         (Storage Account — LRS, WORM policy on audit container)
│   ├── blueline-law             (Log Analytics Workspace)
│   └── blueline-apim            (API Management — Consumption tier)
│
├── blueline-rg-quality
│   ├── blueline-quality-fa      (Function App — Premium EP1, Python 3.11)
│   ├── blueline-quality-asp     (App Service Plan — EP1)
│   └── blueline-quality-vnet    (VNet Integration)
│
├── blueline-rg-security
│   ├── blueline-security-fa     (Function App — Consumption, Python 3.11)
│   └── blueline-security-vnet   (VNet Integration)
│
└── blueline-rg-certloop
    ├── blueline-certloop-fa     (Function App — Consumption, Python 3.11)
    └── blueline-certloop-vnet   (VNet Integration)
```

### 15.2 CI/CD for BlueLine Itself

```
BlueLine Repo (GitHub/Azure DevOps)
        │
        ├── Push to feature/* → Unit tests + linting
        ├── PR to main        → Integration tests (against sandbox)
        └── Merge to main     → Azure Bicep deployment → Staging → Prod
```

### 15.3 Function App Project Structure

```
blueline/
├── core/
│   ├── base_agent.py           ← BaseAgent, AgentContext, AgentResult
│   ├── llm_client.py           ← Claude API wrapper with caching
│   ├── audit_logger.py         ← STEWARD integration
│   ├── service_bus.py          ← Message publishing/subscribing
│   └── notifier.py             ← Teams notifications
│
├── quality_gate/
│   ├── orchestrator.py         ← Durable Function orchestrator
│   ├── clarion.py              ← CLARION agent
│   ├── lumen.py                ← LUMEN agent
│   ├── vector.py               ← VECTOR agent
│   ├── ascent.py               ← ASCENT agent
│   └── devops_client.py        ← Azure DevOps API wrapper
│
├── security/
│   ├── watchtower.py           ← WATCHTOWER agent
│   ├── bulwark.py              ← BULWARK agent
│   ├── forge.py                ← FORGE agent
│   ├── steward.py              ← STEWARD agent
│   └── fortify_client.py       ← Fortify SSC API wrapper
│
├── cert_loop/
│   ├── timeline.py             ← TIMELINE agent
│   ├── regent.py               ← REGENT agent
│   ├── courier/
│   │   ├── base_ca_courier.py
│   │   ├── digicert_courier.py
│   │   ├── internal_pki_courier.py
│   │   └── letsencrypt_courier.py
│   ├── harbour.py              ← HARBOUR agent
│   └── keyvault_client.py      ← Azure Key Vault wrapper
│
├── function_app.py             ← Azure Functions entrypoints (all routes)
├── requirements.txt
├── host.json
└── local.settings.json         ← Local dev only (gitignored)
```

---

*End of Low Level Design Document — Version 1.0*

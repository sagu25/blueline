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
16. [Durable Functions Orchestrator Design](#16-durable-functions-orchestrator-design)
17. [ASCENT Feedback Loop — Detailed Design](#17-ascent-feedback-loop--detailed-design)
18. [VECTOR Agent — Implementation Detail](#18-vector-agent--implementation-detail)
19. [FORGE — Multi-File Fix Handling](#19-forge--multi-file-fix-handling)
20. [HARBOUR — Azure App Service Certificate Deployment](#20-harbour--azure-app-service-certificate-deployment)
21. [PR Comment Format — ASCENT Output Example](#21-pr-comment-format--ascent-output-example)
22. [Testing Strategy](#22-testing-strategy)
23. [Cost Estimation](#23-cost-estimation)
24. [Monitoring & Alerting Design](#24-monitoring--alerting-design)

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

## 16. Durable Functions Orchestrator Design

The Quality Gate and Certificate Loop use **Azure Durable Functions** for stateful, multi-step orchestration. This section shows the actual orchestrator code for both tracks.

### 16.1 Quality Gate Orchestrator

CLARION, LUMEN, and VECTOR run in **parallel** (fan-out). ASCENT waits for all three to finish before aggregating (fan-in). This is the core pattern.

```python
# quality_gate/orchestrator.py
import azure.durable_functions as df

def orchestrator_function(context: df.DurableOrchestrationContext):
    pr_payload = context.get_input()

    # Step 1: Fan-out — run CLARION, LUMEN, VECTOR in parallel
    parallel_tasks = [
        context.call_activity("run_clarion", pr_payload),
        context.call_activity("run_lumen",   pr_payload),
        context.call_activity("run_vector",  pr_payload),
    ]
    # Wait for ALL three to complete before continuing
    results = yield context.task_all(parallel_tasks)

    clarion_result = results[0]
    lumen_result   = results[1]
    vector_result  = results[2]

    # Step 2: Fan-in — ASCENT aggregates and posts to PR
    ascent_input = {
        "pr_id":          pr_payload["pr_id"],
        "clarion_result": clarion_result,
        "lumen_result":   lumen_result,
        "vector_result":  vector_result,
    }
    ascent_result = yield context.call_activity("run_ascent", ascent_input)

    return {
        "pr_id":        pr_payload["pr_id"],
        "status":       "completed",
        "comment_url":  ascent_result["comment_url"],
        "risk_level":   vector_result["overall_risk_level"],
        "violations":   len(clarion_result["violations"]),
        "smells":       len(lumen_result["smells"]),
    }

main = df.Orchestrator.create(orchestrator_function)
```

**Activity function wrappers** (each one instantiates and runs the agent):

```python
# function_app.py — activity bindings

@app.activity_trigger(input_name="payload")
async def run_clarion(payload: dict) -> dict:
    ctx = AgentContext(run_id=payload["run_id"], agent_name="CLARION", ...)
    result = await ClarionAgent(ctx).execute()
    return result.output

@app.activity_trigger(input_name="payload")
async def run_lumen(payload: dict) -> dict:
    ctx = AgentContext(run_id=payload["run_id"], agent_name="LUMEN", ...)
    result = await LumenAgent(ctx).execute()
    return result.output

@app.activity_trigger(input_name="payload")
async def run_vector(payload: dict) -> dict:
    ctx = AgentContext(run_id=payload["run_id"], agent_name="VECTOR", ...)
    result = await VectorAgent(ctx).execute()
    return result.output

@app.activity_trigger(input_name="payload")
async def run_ascent(payload: dict) -> dict:
    ctx = AgentContext(run_id=payload["run_id"], agent_name="ASCENT", ...)
    result = await AscentAgent(ctx, payload).execute()
    return result.output
```

**Execution timeline:**

```
T+0s   PR webhook arrives → Orchestrator starts
T+0s   CLARION starts ──┐
T+0s   LUMEN starts   ──┤  (all three in parallel)
T+0s   VECTOR starts  ──┘
T+45s  All three complete (slowest one determines wait)
T+45s  ASCENT starts → aggregates → posts PR comment
T+60s  Orchestrator completes
```

### 16.2 Certificate Loop Orchestrator

The Certificate Loop is **sequential** — each agent depends on the previous one's output.

```python
# cert_loop/orchestrator.py
import azure.durable_functions as df

def cert_loop_orchestrator(context: df.DurableOrchestrationContext):

    # Step 1: TIMELINE — find all expiring certs
    expiring_certs = yield context.call_activity("run_timeline", {})

    if not expiring_certs:
        return {"status": "no_renewals_needed"}

    renewal_results = []

    # Step 2: Process each expiring cert independently
    for cert in expiring_certs:

        # Step 2a: REGENT — update inventory, identify owner + CA
        cert_record = yield context.call_activity("run_regent", cert)

        # Step 2b: COURIER — request + download new cert from CA
        cert_bundle = yield context.call_activity("run_courier", cert_record)

        if cert_bundle["status"] != "issued":
            # CA issuance failed — escalate to human
            yield context.call_activity("notify_escalation", {
                "cert": cert_record,
                "reason": cert_bundle["error"]
            })
            continue

        # Step 2c: HARBOUR — deploy to Dev, then QA
        dev_result = yield context.call_activity("harbour_deploy", {
            "bundle": cert_bundle, "record": cert_record, "env": "dev"
        })
        qa_result = yield context.call_activity("harbour_deploy", {
            "bundle": cert_bundle, "record": cert_record, "env": "qa"
        })

        # Step 2d: Human approval gate for Prod
        if not cert_record.get("auto_deploy_prod"):
            approval_id = yield context.call_activity("send_prod_approval_request", {
                "bundle": cert_bundle, "record": cert_record
            })
            # Pause orchestrator — wait for human callback (up to 24 hours)
            approval_event = context.wait_for_external_event("prod_approval")
            approved = yield context.create_timer(
                context.current_utc_datetime + timedelta(hours=24)
            ) if False else (yield approval_event)

            if not approved:
                yield context.call_activity("notify_timeout", cert_record)
                continue

        # Step 2e: HARBOUR — deploy to Prod
        prod_result = yield context.call_activity("harbour_deploy", {
            "bundle": cert_bundle, "record": cert_record, "env": "prod"
        })

        renewal_results.append({
            "cert": cert_record["subject"],
            "dev": dev_result["https_verified"],
            "qa":  qa_result["https_verified"],
            "prod": prod_result["https_verified"],
        })

    return {"status": "completed", "renewals": renewal_results}

main = df.Orchestrator.create(cert_loop_orchestrator)
```

---

## 17. ASCENT Feedback Loop — Detailed Design

ASCENT is the only agent that **learns over time**. This section designs the full feedback storage, collection, analysis, and rules-update cycle.

### 17.1 Feedback Storage Schema

**Azure Table: `AscentFeedback`**

| Column | Type | Description |
|---|---|---|
| PartitionKey | string | `rule_id` — e.g., `DOTNET-SEC-001` |
| RowKey | string | `comment_id` from Azure DevOps |
| RunId | string | The AgentRun that generated this comment |
| PRId | int | PR the comment was posted on |
| ReviewerId | string | Azure DevOps user ID who reacted |
| Reaction | string | `thumbs_up` or `thumbs_down` |
| AgentName | string | `CLARION` or `LUMEN` |
| RecordedAt | datetime | UTC timestamp |

**Azure Table: `AscentRuleStats`** — aggregated false positive rates per rule

| Column | Type | Description |
|---|---|---|
| PartitionKey | string | `agent_name` — `CLARION` or `LUMEN` |
| RowKey | string | `rule_id` |
| TotalFired | int | Total times this rule produced a comment |
| ThumbsUp | int | Reviewer agreed with the comment |
| ThumbsDown | int | Reviewer disagreed (false positive signal) |
| FalsePositiveRate | float | ThumbsDown / TotalFired |
| LastUpdated | datetime | Last time stats were recalculated |
| Status | string | `active` / `flagged` / `suppressed` |

### 17.2 Feedback Collection Flow

ASCENT runs a **daily batch job** (Azure Timer, 23:00 UTC) to collect reactions:

```python
# quality_gate/ascent.py  — feedback collection

async def collect_daily_feedback(self):
    """
    Queries Azure DevOps for all reactions posted on BlueLine
    bot comments in the last 24 hours.
    """
    # Fetch all PRs updated in last 24 hours
    prs = await self.devops.get_recently_updated_prs(hours=24)

    for pr in prs:
        # Get all threads on this PR
        threads = await self.devops.get_pr_threads(pr.id)

        for thread in threads:
            # Only process threads started by the BlueLine bot account
            if not self._is_blueline_comment(thread):
                continue

            rule_id = thread.properties.get("blueline_rule_id")
            if not rule_id:
                continue

            # Get reactions on the root comment
            reactions = await self.devops.get_comment_reactions(
                pr.id, thread.id, thread.comments[0].id
            )

            for reaction in reactions:
                feedback = FeedbackRecord(
                    run_id=thread.properties["blueline_run_id"],
                    rule_id=rule_id,
                    reaction=self._map_reaction(reaction.type),  # thumbs_up / thumbs_down
                    reviewer_id=reaction.created_by.id,
                    comment_id=str(thread.id),
                    recorded_at=datetime.now(timezone.utc)
                )
                await self.storage.upsert_feedback(feedback)

    # Recalculate rule stats after collecting
    await self._recalculate_rule_stats()
```

### 17.3 False Positive Rate Calculation

```python
async def _recalculate_rule_stats(self):
    """
    Recalculates false positive rate for each rule.
    Flags rules exceeding the threshold for engineering review.
    """
    FLAGGING_THRESHOLD = 0.20   # 20% false positive rate triggers review

    all_feedback = await self.storage.get_all_feedback()

    # Group by rule_id
    by_rule = {}
    for f in all_feedback:
        by_rule.setdefault(f.rule_id, []).append(f)

    for rule_id, feedbacks in by_rule.items():
        total      = len(feedbacks)
        thumbs_up   = sum(1 for f in feedbacks if f.reaction == "thumbs_up")
        thumbs_down = sum(1 for f in feedbacks if f.reaction == "thumbs_down")
        fp_rate     = thumbs_down / total if total > 0 else 0.0

        status = "active"
        if fp_rate > FLAGGING_THRESHOLD and total >= 10:
            # Only flag if we have enough data (>=10 reactions)
            status = "flagged"
            await self.notifier.alert_engineering_lead(
                f"Rule {rule_id} has {fp_rate:.0%} false positive rate "
                f"across {total} reactions — review recommended"
            )

        await self.storage.upsert_rule_stat(RuleStat(
            rule_id=rule_id,
            total_fired=total,
            thumbs_up=thumbs_up,
            thumbs_down=thumbs_down,
            false_positive_rate=fp_rate,
            status=status,
            last_updated=datetime.now(timezone.utc)
        ))
```

### 17.4 Rule Reload Mechanism

CLARION and LUMEN reload rules at the **start of each agent run** — not on a schedule. This means:
- Engineering lead updates the standards document in Azure Blob Storage
- Next PR that is opened automatically picks up the updated rules
- No restart or redeployment needed

```python
# quality_gate/clarion.py

async def _load_standards(self) -> str:
    """
    Loads the coding standards document from Azure Blob Storage.
    Also loads current rule suppression list (rules with status='suppressed').
    """
    # Load standards document
    standards_text = await self.blob_client.download_text(
        container="blueline-config",
        blob="coding-standards.md"
    )

    # Load suppressed rules from ASCENT stats
    suppressed = await self.storage.get_rules_by_status("suppressed")
    suppressed_ids = [r.rule_id for r in suppressed]

    if suppressed_ids:
        standards_text += f"\n\nDO NOT flag these rule IDs — they are suppressed: {suppressed_ids}"

    return standards_text
```

---

## 18. VECTOR Agent — Implementation Detail

VECTOR uses two data sources: **static analysis of the diff** (for complexity) and **git history** (for churn). This section shows how both are computed.

### 18.1 Cyclomatic Complexity Calculation

VECTOR parses the diff and counts decision points (if, for, while, catch, case, &&, ||) to approximate complexity without running a full static analysis tool:

```python
# quality_gate/vector.py

import re

DECISION_KEYWORDS_CSHARP = [
    r'\bif\b', r'\belse if\b', r'\bfor\b', r'\bforeach\b',
    r'\bwhile\b', r'\bcase\b', r'\bcatch\b', r'\b&&\b', r'\b\|\|\b',
    r'\?\s*\w'  # ternary operator
]

DECISION_KEYWORDS_TYPESCRIPT = [
    r'\bif\b', r'\belse if\b', r'\bfor\b', r'\bforEach\b',
    r'\bwhile\b', r'\bcase\b', r'\bcatch\b', r'\b&&\b', r'\b\|\|\b',
    r'\?\?', r'\?\.'   # nullish coalescing, optional chaining
]

def calculate_cyclomatic_complexity(file_content: str, language: str) -> int:
    """
    Approximates cyclomatic complexity by counting decision points.
    Baseline complexity = 1, +1 per decision point found.
    """
    keywords = (DECISION_KEYWORDS_CSHARP if language == "csharp"
                else DECISION_KEYWORDS_TYPESCRIPT)
    complexity = 1  # baseline
    for pattern in keywords:
        complexity += len(re.findall(pattern, file_content))
    return complexity
```

### 18.2 Churn Rate from Git History

```python
async def get_file_churn(self, file_path: str, days: int = 30) -> int:
    """
    Queries Azure DevOps API for commit count on a file in the last N days.
    High churn = frequently changing file = higher risk.
    """
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    commits = await self.devops.get_commits_for_file(
        file_path=file_path,
        from_date=since
    )
    return len(commits)
```

### 18.3 Full Risk Score Computation

```python
async def score_file(self, file_path: str, file_content: str, language: str) -> FileRisk:
    complexity   = calculate_cyclomatic_complexity(file_content, language)
    churn        = await self.get_file_churn(file_path, days=30)
    fan_out      = self._count_imports(file_content)
    test_cov     = await self._get_test_coverage(file_path)  # 0-100, None if unknown

    c_score  = min(complexity / 10, 1.0)
    ch_score = min(churn / 20, 1.0)
    d_score  = min(fan_out / 15, 1.0)
    t_score  = 1.0 - ((test_cov or 50) / 100)   # assume 50% if unknown

    risk = (c_score * 0.35) + (ch_score * 0.25) + (d_score * 0.20) + (t_score * 0.20)
    risk = round(min(risk, 1.0), 3)

    level = (
        "CRITICAL" if risk >= 0.8 else
        "HIGH"     if risk >= 0.6 else
        "MEDIUM"   if risk >= 0.3 else
        "LOW"
    )

    return FileRisk(
        file_path=file_path,
        risk_score=risk,
        risk_level=level,
        complexity_score=c_score,
        churn_score=ch_score,
        dependency_score=d_score,
        test_coverage_score=t_score,
        reviewer_note=self._build_reviewer_note(level, complexity, churn, fan_out)
    )

def _build_reviewer_note(self, level, complexity, churn, fan_out) -> str:
    notes = []
    if complexity > 15: notes.append(f"high cyclomatic complexity ({complexity})")
    if churn > 10:      notes.append(f"changed {churn} times in 30 days")
    if fan_out > 10:    notes.append(f"{fan_out} dependencies")
    return f"{level} risk — " + ", ".join(notes) if notes else f"{level} risk"
```

---

## 19. FORGE — Multi-File Fix Handling

Real vulnerabilities often span more than one file (e.g., a vulnerable helper method called from multiple controllers). This section covers how FORGE handles that.

### 19.1 Fix Scope Classification

Before generating a fix, FORGE classifies whether the fix is **single-file** or **multi-file**:

```python
async def classify_fix_scope(self, finding: TriagedFinding) -> str:
    """
    Asks the LLM to determine if the fix requires changes to one file or multiple.
    Returns: "single_file" | "multi_file" | "architectural"
    """
    prompt = f"""
    Given this vulnerability in {finding.finding.file_path} at line {finding.finding.line_number}:
    {finding.vulnerable_code_path}

    Classify the fix scope:
    - single_file: Fix is contained entirely within {finding.finding.file_path}
    - multi_file: Fix requires changes to 2-5 files (e.g., interface + implementation)
    - architectural: Fix requires design changes across many files — cannot be auto-generated

    Respond with only one of: single_file, multi_file, architectural
    """
    scope = (await self.llm.complete(prompt)).strip()
    return scope
```

### 19.2 Multi-File Fix Strategy

```python
async def generate_multi_file_fix(self, finding: TriagedFinding) -> ForgeFixResult:
    """
    For multi-file fixes: identify all affected files, generate fix for each,
    commit all changes in a single branch.
    """
    # Step 1: Ask LLM to list all files that need changing
    affected_files = await self._identify_affected_files(finding)

    if len(affected_files) > 5:
        # Too broad — escalate to human
        return ForgeFixResult(
            finding_id=finding.finding.issue_id,
            status="needs_human",
            fix_explanation=f"Fix spans {len(affected_files)} files — requires human architect review",
            files_modified=affected_files
        )

    # Step 2: Fetch content of all affected files
    file_contents = {}
    for fp in affected_files:
        file_contents[fp] = await self.devops.get_file_content(fp)

    # Step 3: Generate fix for each file in one LLM call
    # (passing all file contents as context)
    fixes = await self._generate_fixes_for_all_files(finding, file_contents)

    # Step 4: Create single PR with all file changes
    return ForgeFixResult(
        finding_id=finding.finding.issue_id,
        status="fix_generated",
        files_modified=list(fixes.keys()),
        fixed_code=fixes,   # dict: file_path → new_content
        fix_explanation=f"Multi-file fix across {len(fixes)} files",
        pr_title=f"[Security Fix] {finding.finding.category} — {len(fixes)} files",
        pr_description=self._build_pr_description(finding, fixes)
    )
```

---

## 20. HARBOUR — Azure App Service Certificate Deployment

The existing HARBOUR design covers IIS (WinRM). This section adds the **Azure App Service** deployment path, which uses the Azure SDK — not PowerShell.

### 20.1 App Service Deployment

```python
# cert_loop/harbour.py  — App Service path

from azure.mgmt.web import WebSiteManagementClient
from azure.identity import DefaultAzureCredential

async def deploy_to_app_service(
    self,
    bundle: CertBundle,
    subscription_id: str,
    resource_group: str,
    app_name: str,
    slot: str = "production"
) -> DeployResult:

    credential = DefaultAzureCredential()
    client = WebSiteManagementClient(credential, subscription_id)

    # Step 1: Upload certificate to App Service
    cert_response = client.certificates.create_or_update(
        resource_group_name=resource_group,
        name=f"blueline-{bundle.thumbprint[:8]}",
        certificate_envelope={
            "location": self.azure_region,
            "properties": {
                "pfxBlob": bundle.certificate_pfx_b64,
                "password": bundle.pfx_password,
            }
        }
    )

    # Step 2: Bind to custom domain SSL
    app = client.web_apps.get(resource_group, app_name)
    for hostname_binding in app.host_name_ssl_states:
        if hostname_binding.ssl_state in ("SniEnabled", "IpBasedEnabled"):
            client.web_apps.create_or_update_host_name_binding(
                resource_group_name=resource_group,
                name=app_name,
                host_name=hostname_binding.name,
                host_name_binding={
                    "ssl_state": "SniEnabled",
                    "thumbprint": bundle.thumbprint
                }
            )
            self.log_action(f"Bound cert {bundle.thumbprint[:8]} to {hostname_binding.name}")

    # Step 3: Verify HTTPS
    https_ok = await self._verify_https(app_name + ".azurewebsites.net", [])

    return DeployResult(
        environment=slot,
        server=f"{app_name}.azurewebsites.net",
        sites=[app_name],
        thumbprint=bundle.thumbprint,
        https_verified=https_ok
    )
```

### 20.2 Deployment Target Router

HARBOUR automatically chooses the right deployment path based on the environment record:

```python
async def deploy(self, bundle: CertBundle, record: CertificateRecord, env: str) -> DeployResult:
    target = record.environments[env]

    if target["type"] == "iis":
        return await self.deploy_to_iis(
            bundle=bundle,
            server=target["server"],
            site_bindings=record.iis_site_bindings[env],
            environment=env
        )
    elif target["type"] == "app_service":
        return await self.deploy_to_app_service(
            bundle=bundle,
            subscription_id=target["subscription_id"],
            resource_group=target["resource_group"],
            app_name=target["app_name"],
            slot=target.get("slot", "production")
        )
    else:
        raise ValueError(f"Unknown deployment target type: {target['type']}")
```

---

## 21. PR Comment Format — ASCENT Output Example

This section shows exactly what a developer sees on their PR after ASCENT posts the consolidated review.

### 21.1 Sample ASCENT PR Comment

```markdown
## 🔵 BlueLine Code Review — PR #1234

**Risk Level:** 🔴 HIGH  
**Files Reviewed:** 6  |  **Critical Files:** 2  |  **Review Time:** 48 seconds

---

### ⛔ Must Fix Before Merge (3 issues)

| File | Line | Rule | Issue |
|---|---|---|---|
| `Services/PaymentService.cs` | 47 | DOTNET-SEC-001 | SQL string concatenation — SQL injection risk |
| `Services/PaymentService.cs` | 12 | DOTNET-SEC-003 | Hardcoded connection string with password |
| `Controllers/UserController.cs` | 89 | DOTNET-SEC-002 | User input passed to file path without sanitization |

---

### ⚠️ Should Fix (2 issues)

| File | Issue |
|---|---|
| `Services/PaymentService.cs` | Long Parameter List — `ProcessPayment` takes 8 parameters. Extract to `PaymentRequest` object. |
| `Services/PaymentService.cs` | Duplicate Code — `ProcessPayment` and `ProcessRefund` share identical DB query logic. Extract to private method. |

---

### 🔴 High-Risk Files — Review Carefully

| File | Risk Score | Reason |
|---|---|---|
| `Services/PaymentService.cs` | 0.87 — CRITICAL | High complexity (18), changed 14× in 30 days, 0% test coverage |
| `Repositories/OrderRepository.cs` | 0.71 — HIGH | 12 dependencies, changed 8× in 30 days |

---

### ✅ Reviewer Checklist

Before approving, confirm:
- [ ] SQL injection fix uses parameterized queries (not just escaping)
- [ ] Connection string moved to Key Vault reference — not just environment variable
- [ ] File path fix validates against allowed root directory
- [ ] `PaymentService` has unit test coverage added with this PR

---

<sub>🤖 BlueLine AI Review — CLARION v1.0 · LUMEN v1.0 · VECTOR v1.0 · Confidence: 91%
React 👍 if this comment is correct · React 👎 if this is a false positive</sub>
```

### 21.2 Inline Comment Format (Individual Violations)

Each violation also appears as a separate inline comment on the exact diff line:

```markdown
**[CLARION · DOTNET-SEC-001 · ERROR]**

⛔ **SQL Injection Risk** — User input is concatenated directly into a SQL query string.

**Vulnerable code:**
```csharp
string query = "SELECT * FROM Users WHERE Id = '" + userId + "'";
```

**Fix:**
```csharp
string query = "SELECT * FROM Users WHERE Id = @userId";
var cmd = new SqlCommand(query, connection);
cmd.Parameters.AddWithValue("@userId", userId);
```

**Why this matters:** An attacker can pass `' OR '1'='1` as the userId to
bypass authentication and access all user records.

<sub>Confidence: 96% · React 👍 agree · 👎 false positive</sub>
```

---

## 22. Testing Strategy

### 22.1 Testing Approach by Layer

| Layer | Test Type | Tool | What is Tested |
|---|---|---|---|
| Agent logic (no LLM) | Unit tests | pytest | Prompt construction, output parsing, routing logic |
| Agent + real LLM | Integration tests | pytest + live API | End-to-end agent response quality |
| Full track | E2E tests | pytest + Azure DevOps sandbox | Webhook → agents → PR comment posted |
| Infrastructure | IaC validation | Bicep linter + checkov | Security and config correctness |

### 22.2 Unit Testing Agents Without Calling the LLM

Agents are designed to be testable without real LLM calls by injecting a mock LLM client:

```python
# tests/test_clarion.py
import pytest
from unittest.mock import AsyncMock, patch
from quality_gate.clarion import ClarionAgent
from core.base_agent import AgentContext

SAMPLE_DIFF = """
+public class paymentservice {
+    private string conn = "Server=db;Password=Admin@123;";
+    public void Process(string userId) {
+        string q = "SELECT * FROM Users WHERE Id = '" + userId + "'";
+    }
+}
"""

MOCK_LLM_RESPONSE = """{
  "summary": "Multiple critical violations found",
  "overall_score": 2,
  "violations": [
    {
      "line": 1, "severity": "error", "rule": "DOTNET-N-001",
      "message": "Class name must be PascalCase",
      "fix": "Rename to PaymentService", "confidence": 0.98
    },
    {
      "line": 2, "severity": "error", "rule": "DOTNET-SEC-003",
      "message": "Hardcoded password in connection string",
      "fix": "Use Azure Key Vault reference", "confidence": 0.99
    }
  ]
}"""

@pytest.mark.asyncio
async def test_clarion_detects_violations():
    ctx = AgentContext(
        run_id="test-001",
        trigger_type="pr_event",
        trigger_payload={"pr_id": 1, "diff": SAMPLE_DIFF},
        agent_name="CLARION",
        track="quality_gate"
    )

    with patch.object(ClarionAgent, "call_llm", return_value=MOCK_LLM_RESPONSE):
        agent = ClarionAgent(ctx)
        result = await agent.execute()

    assert result.status == "success"
    assert len(result.output["violations"]) == 2
    assert result.output["violations"][0]["rule"] == "DOTNET-N-001"
    assert result.output["overall_score"] == 2


@pytest.mark.asyncio
async def test_clarion_clean_code_returns_no_violations():
    clean_diff = """
+public class PaymentService : IPaymentService {
+    private readonly IConfiguration _config;
+    public async Task<Result> ProcessAsync(PaymentRequest request) {
+        var connStr = _config["ConnectionStrings:Payments"];
+        return await _processor.RunAsync(request);
+    }
+}"""

    ctx = AgentContext(run_id="test-002", trigger_type="pr_event",
                       trigger_payload={"pr_id": 2, "diff": clean_diff},
                       agent_name="CLARION", track="quality_gate")

    CLEAN_RESPONSE = '{"summary": "Code follows all standards", "overall_score": 9, "violations": []}'

    with patch.object(ClarionAgent, "call_llm", return_value=CLEAN_RESPONSE):
        agent = ClarionAgent(ctx)
        result = await agent.execute()

    assert result.status == "success"
    assert result.output["violations"] == []
    assert result.output["overall_score"] >= 8
```

### 22.3 Integration Test — Full Security Loop

```python
# tests/integration/test_security_loop.py

@pytest.mark.integration   # only runs when --integration flag is passed
@pytest.mark.asyncio
async def test_bulwark_classifies_sql_injection_as_critical():
    """
    Calls the real LLM API with a known SQL injection finding.
    Asserts it is classified as CRITICAL with >= 85% confidence.
    """
    finding = FortifyFinding(
        issue_id="TEST-001",
        category="SQL Injection",
        severity="Critical",
        file_path="Services/UserService.cs",
        line_number=34,
        source_code_snippet='string q = "SELECT * FROM Users WHERE Id = \'" + userId + "\'";',
        rule_id="sql-injection",
        project="TestProject",
        project_version="1.0"
    )

    ctx = AgentContext(run_id="int-test-001", trigger_type="pipeline",
                       trigger_payload={}, agent_name="BULWARK", track="security")

    result = await BulwarkAgent(ctx).triage([finding])

    triaged = result.output["triaged_findings"][0]
    assert triaged["classification"] == "CRITICAL"
    assert triaged["confidence"] >= 0.85
    assert "sql" in triaged["owasp_category"].lower()
```

### 22.4 Test Coverage Targets

| Component | Target Coverage | Priority |
|---|---|---|
| Agent output parsers | 100% | Critical — any parsing failure breaks the track |
| Routing logic (BULWARK classification → FORGE/STEWARD) | 100% | Critical |
| Risk scoring formula (VECTOR) | 100% | High |
| ASCENT aggregation logic | 90% | High |
| HARBOUR rollback path | 90% | Critical — must verify rollback works before going live |
| COURIER CA factory | 80% | High |
| Feedback collection (ASCENT) | 80% | Medium |

### 22.5 Shadow Mode Testing (Pre-Production)

Before agents post real comments or take real actions, run in **shadow mode**:

```python
# Set in .env / App Configuration
BLUELINE_ENV=shadow   # "shadow" | "production"
```

In shadow mode:
- All agent logic runs normally
- All LLM calls are made
- **No external actions are taken** — no PR comments posted, no certs deployed, no Fortify suppressions added
- All outputs are written to `shadow-output` Azure Blob container for human review

```python
# core/base_agent.py

async def take_action(self, action_fn, action_description: str):
    """
    Wrapper for all external actions. In shadow mode, logs but does not execute.
    """
    if os.getenv("BLUELINE_ENV") == "shadow":
        self.logger.info(f"[SHADOW] Would have taken action: {action_description}")
        self.log_action(f"[SHADOW] {action_description}")
        return None
    else:
        self.log_action(action_description)
        return await action_fn()
```

---

## 23. Cost Estimation

### 23.1 Token Usage Per Operation

| Operation | Agent(s) | Input Tokens (est.) | Output Tokens (est.) | Total Tokens |
|---|---|---|---|---|
| PR review — small PR (50 lines changed) | CLARION + LUMEN | ~8,000 | ~1,500 | ~9,500 |
| PR review — medium PR (200 lines changed) | CLARION + LUMEN + VECTOR | ~20,000 | ~2,500 | ~22,500 |
| PR review — large PR (500+ lines changed) | CLARION + LUMEN + VECTOR | ~45,000 | ~3,500 | ~48,500 |
| Security triage — single finding | BULWARK | ~3,000 | ~800 | ~3,800 |
| Security fix generation | FORGE | ~8,000 | ~2,000 | ~10,000 |
| Certificate analysis — single cert | TIMELINE | ~1,000 | ~500 | ~1,500 |

> Note: Input tokens are significantly cheaper than output tokens. Prompt caching reduces input token cost by ~90% on repeated calls with the same system prompt (coding standards document).

### 23.2 Monthly Cost Estimate — Azure OpenAI (GPT-4o)

**Assumptions:**
- 30 PRs per day (team activity estimate)
- 60% small, 30% medium, 10% large PRs
- 50 new Fortify findings per week
- 5 certificates renewed per month
- GPT-4o pricing: ~$2.50 / 1M input tokens, ~$10.00 / 1M output tokens

| Track | Volume / Month | Tokens / Month | Estimated Cost |
|---|---|---|---|
| Quality Gate (PRs) | ~900 PRs | ~18M input, ~2M output | ~$65 |
| Security Loop (findings) | ~200 findings | ~0.8M input, ~0.2M output | ~$4 |
| Certificate Loop (renewals) | ~5 renewals | ~0.1M input, ~0.05M output | <$1 |
| **Total** | | **~19M input, ~2.3M output** | **~$70/month** |

> With prompt caching applied to the system prompts (coding standards + security rules), input token cost drops by ~60%, bringing the estimate to approximately **$40–50/month**.

### 23.3 Azure Infrastructure Cost Estimate

| Resource | SKU | Estimated Monthly Cost |
|---|---|---|
| Quality Gate Function App | Premium EP1 (always-on) | ~$140 |
| Security Function App | Consumption | ~$5 |
| Cert Loop Function App | Consumption | ~$2 |
| Azure Service Bus | Standard tier | ~$10 |
| Azure Storage (blobs + tables) | LRS | ~$5 |
| Azure Key Vault | Standard | ~$5 |
| Azure API Management | Consumption tier | ~$3.50 |
| Log Analytics Workspace | Pay-per-GB (~5GB/mo) | ~$12 |
| **Total Infrastructure** | | **~$183/month** |

### 23.4 Total Cost of Ownership

| Period | AI Tokens | Infrastructure | Total |
|---|---|---|---|
| Monthly | ~$45 | ~$183 | **~$228** |
| Annual | ~$540 | ~$2,196 | **~$2,736** |

**ROI context:** If the Quality Gate saves each developer 2 hours of review work per week across a 10-person team, that is 1,040 hours/year recovered. At a blended rate of $80/hour, that is **$83,200/year in recovered developer time** against a **$2,736/year operating cost**.

---

## 24. Monitoring & Alerting Design

### 24.1 Azure Monitor Alert Rules

| Alert Name | Condition | Severity | Notification |
|---|---|---|---|
| PR Review Timeout | Quality Gate Function > 5 min execution | P2 | Teams + Email |
| Agent Failure Rate | >5% of agent runs fail in 1 hour | P1 | Teams + PagerDuty |
| Dead Letter Queue Depth | Service Bus DLQ > 0 messages | P2 | Teams |
| Certificate Expiry Missed | Cert expires with no TIMELINE renewal triggered | P0 | PagerDuty |
| HTTPS Verification Failed | HARBOUR post-deploy check fails | P0 | PagerDuty + Email to Ops |
| LLM API Latency | Azure OpenAI p95 > 30s | P3 | Teams |
| High False Positive Rate | Any rule FP rate > 20% | P3 | Email to Engineering Lead |
| Fortify API Unreachable | WATCHTOWER fails 3× in a row | P2 | Teams + InfoSec |

### 24.2 Log Analytics Queries (Key Dashboards)

**PR Review SLA Dashboard — average time from PR open to ASCENT comment:**
```kusto
AgentRuns
| where AgentName == "ASCENT" and Track == "quality_gate"
| extend DurationSecs = datetime_diff('second', CompletedAt, StartedAt)
| summarize
    AvgDuration = avg(DurationSecs),
    P95Duration = percentile(DurationSecs, 95),
    TotalRuns   = count()
  by bin(StartedAt, 1d)
| render timechart
```

**Security Finding Classification Breakdown:**
```kusto
AuditLog
| where EventType == "finding_triaged"
| summarize Count = count() by Decision
| render piechart
```

**Certificate Health — days until expiry for all active certs:**
```kusto
CertificateInventory
| extend DaysUntilExpiry = datetime_diff('day', ExpiresOn, now())
| order by DaysUntilExpiry asc
| project Subject, Environment, DaysUntilExpiry, Owner
```

### 24.3 SLA Targets

| Metric | Target | Alert Threshold |
|---|---|---|
| PR review completed (webhook → comment) | < 90 seconds | > 5 minutes |
| Fortify triage per finding | < 30 seconds | > 2 minutes |
| Certificate renewal initiated before expiry | ≥ 30 days ahead | < 14 days ahead |
| Agent availability | 99.5% | < 99% in rolling 24h |
| HTTPS verification after cert deploy | 100% success | Any failure |

---

*End of Low Level Design Document — Version 1.1*  
*(Sections 16–24 added: Orchestrator code, ASCENT feedback loop, VECTOR implementation, FORGE multi-file handling, HARBOUR App Service, PR comment format, testing strategy, cost estimation, monitoring & alerting)*

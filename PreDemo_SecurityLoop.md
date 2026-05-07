# Pre-Demo Reading — Security Loop
**Read this 10 minutes before your demo. Everything below is based on the actual agent code.**

---

## What It Does in One Line

When Fortify SSC completes a scan and produces security findings, four agents automatically triage each finding, classify its severity, generate the corrected fix code, create a draft Pull Request in Azure DevOps, and write an immutable audit log entry — without a human doing any of it manually.

---

## The Problem It Solves

Today when Fortify produces a finding, an engineer has to:
1. Read the finding description
2. Look up what OWASP category it falls under
3. Decide if it is a real vulnerability or a false positive
4. Research how to fix it correctly
5. Write the fix code
6. Create a branch in git
7. Commit and push
8. Raise a Pull Request
9. Write the PR description

That is hours of work per finding, done manually, inconsistently. BlueLine's Security Loop does steps 1 through 9 automatically. The developer's job becomes: review the AI's work, verify it is correct, and click Approve.

---

## The Four Agents — What Each One Does and How It Decides

---

### Agent 1 — WATCHTOWER (Finding Discovery)

**Job:** Monitor Fortify SSC continuously for new findings and publish them to the pipeline.

**How it decides:**
WATCHTOWER polls the Fortify SSC REST API on a schedule. When new findings appear, it publishes them to Azure Service Bus — a message queue — so BULWARK can pick them up.

**In the POC:**
WATCHTOWER is simulated. You paste the finding description manually to show what happens when WATCHTOWER receives one. The agent pipeline and logic that follows is identical to what happens in production — only the input method differs.

**What to say in the demo:**
> "In production WATCHTOWER polls Fortify automatically after every CI/CD pipeline run. For today's demo we're providing the finding directly so you can see exactly what the agents do with it."

---

### Agent 2 — BULWARK (Triage and Classification)

**Job:** Read the finding and classify it — is this a real vulnerability that must be fixed, or a false positive that can be dismissed?

**How it decides:**
BULWARK is given a deep security knowledge base as its instructions. It reads the finding description and optionally the vulnerable code, then classifies it across four categories:

| Classification | Meaning | What happens next |
|---|---|---|
| `CRITICAL` | Confirmed, exploitable vulnerability — fix immediately | FORGE creates a draft fix PR |
| `HIGH` | Very likely a real vulnerability — fix before next release | FORGE creates a draft fix PR |
| `NEEDS_REVIEW` | Possible vulnerability — human security engineer must verify | Escalated to InfoSec team |
| `FALSE_POSITIVE` | Not actually vulnerable — reasoning provided | Logged to STEWARD, no action |

**What BULWARK produces for each finding:**
- **Classification** with confidence score (0.0–1.0)
- **OWASP category** — e.g. A03:2021 – Injection
- **Attack scenario** — exactly how an attacker would exploit this if left unfixed
- **Affected systems** — which data or services are at risk
- **Secure code example** — the corrected code to replace the vulnerable version
- **False positive reason** — if dismissed, why it is not actually a vulnerability

**The security knowledge BULWARK applies:**

| Vulnerability | What BULWARK knows to check |
|---|---|
| SQL Injection | Is user input concatenated into a query? Are parameterised queries used? |
| XSS | Is user data rendered in HTML without encoding? Is `innerHTML` used unsafely? |
| Path Traversal | Are file paths validated against an allowed root? Is `..` rejected? |
| Hardcoded Secrets | Is any credential, key, or token written directly in source code? |
| Insecure Deserialization | Is `BinaryFormatter` used on untrusted data? |
| Broken Auth | Is custom auth logic being used instead of ASP.NET Identity or Azure AD? |
| Sensitive Data Exposure | Are passwords, tokens, or PII being logged or returned in responses? |
| CSRF | Do state-changing endpoints have `AntiForgeryToken`? |
| IDOR | Does the code verify the current user owns the resource they are accessing? |

**Confidence threshold:**
If BULWARK's confidence is below 0.7, it automatically classifies as `NEEDS_REVIEW` and escalates to a human rather than taking action.

**What to say in the demo:**
> "BULWARK does not just say 'this looks bad'. It tells you the OWASP category, the exact attack scenario, which data is at risk, and gives you the corrected code. A junior developer can read this and understand exactly what to do — no security research required."

---

### Agent 3 — FORGE (Fix PR Generator)

**Job:** Take BULWARK's classification and secure code fix and create a complete, ready-to-review draft Pull Request in Azure DevOps.

**How it decides:**
FORGE only runs when BULWARK classifies a finding as CRITICAL or HIGH. For NEEDS_REVIEW or FALSE_POSITIVE, FORGE is skipped.

**What FORGE produces:**
- **Branch name** — always follows the convention `fix/security/<kebab-case-description>` e.g. `fix/security/sql-injection-orders-controller`
- **Commit message** — always follows conventional commits: `fix(security): <what was fixed and why>`
- **PR title** — clear description of the security fix
- **Full PR description** — structured Markdown with four sections:
  - Summary
  - Security Impact
  - Changes Made
  - Testing Required
- **Files to modify** — list of affected files
- **Reviewer note** — specific instructions for the human reviewer on what to verify before approving
- **ready_to_merge: false** — always. FORGE never creates a mergeable PR. It always creates a DRAFT that requires human review.

**The hard rule:**
FORGE is explicitly instructed that `ready_to_merge` is **always false**. This is not configurable. No finding, however obvious, results in code being merged automatically.

**What to say in the demo:**
> "FORGE does all the work of creating the fix — branch, commit, PR description, reviewer instructions. But it never touches the merge button. The developer reviews the draft, satisfies themselves the fix is correct, and approves. The AI prepares, the human decides."

---

### Agent 4 — STEWARD (Immutable Audit Logger)

**Job:** Write a permanent, tamper-proof record of every decision made in the security pipeline.

**How it decides:**
STEWARD runs after every pipeline execution — regardless of classification or outcome. It records everything.

**What every STEWARD entry contains:**

| Field | What it records |
|---|---|
| `run_id` | Unique identifier — trace any decision back to its full context |
| `timestamp_utc` | Exact time of the decision |
| `pipeline` | Which track handled this (Security Loop) |
| `agents_involved` | Full list of agents that participated |
| `finding_summary` | What the finding was |
| `classification` | BULWARK's verdict |
| `confidence` | How confident BULWARK was |
| `action_taken` | What FORGE did (or why it was skipped) |
| `human_gate_required` | Whether a human must approve before code is merged |
| `human_gate_status` | PENDING_APPROVAL or APPROVED |
| `immutable` | Always true — cannot be edited after writing |
| `retention_policy` | 7 years — meets compliance requirements |

**In production:**
STEWARD writes to Azure Blob Storage with WORM (Write Once Read Many) policy. Even an administrator cannot alter or delete an entry after it is written.

**What to say in the demo:**
> "Every finding, every classification, every action is logged permanently. If an auditor asks 'why was this SQL injection finding suppressed?', STEWARD has the answer — who made the decision, when, with what confidence, and what the reasoning was. 7-year retention, immutable storage."

---

## The Full Flow

```
Fortify SSC scan completes
         │
         ▼
WATCHTOWER detects new findings
Publishes to Azure Service Bus
         │
         ▼
BULWARK reads each finding
Classifies: CRITICAL / HIGH / NEEDS_REVIEW / FALSE_POSITIVE
         │
         ├── CRITICAL or HIGH ──────────────────────────────────────┐
         │                                                           ▼
         │                                                        FORGE
         │                                               Creates draft fix PR:
         │                                               - Branch: fix/security/...
         │                                               - Corrected code written
         │                                               - PR raised as DRAFT
         │                                               - Reviewer note added
         │                                                           │
         ├── NEEDS_REVIEW ─── Escalated to InfoSec team             │
         │                                                           │
         └── FALSE_POSITIVE ─ Logged, no action                     │
                  │                                                  │
                  └──────────────────────────────────────────────────┤
                                                                     ▼
                                                                 STEWARD
                                                     Writes immutable audit entry
                                                     (every outcome, every time)
                                                                     │
                                                                     ▼
                                                     Human developer reviews draft PR
                                                     Verifies fix is correct
                                                     Approves → code merged
                                                     (Agents cannot merge — ever)
```

---

## Key Numbers to Remember

| Metric | Value |
|---|---|
| Confidence threshold to act | 70% — below this, escalated to human |
| FORGE triggers on | CRITICAL and HIGH only |
| Audit retention | 7 years |
| Branch naming convention | `fix/security/<kebab-case>` |
| PR state when created | Always DRAFT — never ready to merge |
| SQL injection confidence in the demo | 100% — CRITICAL |

---

## If They Ask Difficult Questions

**"What if BULWARK gets the classification wrong?"**
> "Two things protect against this. First, the confidence score — if it is below 70% it automatically escalates to a human rather than acting. Second, FORGE always creates a DRAFT PR. Even if BULWARK called something CRITICAL incorrectly, a developer reviews the draft before any code is merged. The human is the final check."

**"What happens to false positives in Fortify?"**
> "BULWARK classifies them as FALSE_POSITIVE with its reasoning — for example, 'this SQL pattern looks dangerous but the input is already validated upstream at the API gateway'. STEWARD logs the reasoning. In production, InfoSec reviews the false positive log periodically to validate BULWARK's calls and decide whether to suppress the finding in Fortify."

**"How does it know what a secure fix looks like?"**
> "BULWARK is given a security knowledge base covering the most common vulnerability types — SQL injection, XSS, path traversal, hardcoded secrets, CSRF, IDOR, and more. For each type it knows the correct pattern in C# and Angular. It does not guess — it applies known secure coding patterns."

**"Is the audit log really tamper-proof?"**
> "In production yes. Azure Blob Storage with WORM policy means the entry can be read but cannot be modified or deleted. This is the same storage class used for financial records and regulated data. Even an Azure administrator cannot alter a WORM-protected blob after it is written."

---

*Project BlueLine — LTM AI-Led Engineering Team · Security Loop Pre-Demo Brief*

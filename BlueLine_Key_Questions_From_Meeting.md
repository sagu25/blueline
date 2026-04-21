# Project BlueLine — Key Questions from the Team Meeting
### Prepared Answers for the Four Strategic Questions Raised

**Version:** 1.0
**Date:** 2026-04-21

---

## Question 1 — Why Custom Agents Over Azure AI Agents?

Azure AI Foundry does offer a hosted agent framework — you can spin up agents inside Azure without writing code. The reason we built custom agents instead comes down to one thing: **Azure's generic agents don't know who you are.**

Azure AI Foundry agents are general-purpose. They have no idea what your DAS coding standards say, they have no idea how your Fortify SSC is configured, they have no concept of your certificate environment, your IIS topology, or your internal C&M portal. You would spend as much time configuring and constraining them as you would building a custom agent — except with less control and more vendor lock-in.

Here is the specific breakdown:

| What You Need | Azure AI Foundry Agent | BlueLine Custom Agent |
|---|---|---|
| Your DAS/CDAS rules enforced | ❌ No — general coding knowledge only | ✅ Yes — your exact standards document loaded |
| Fortify SSC integration | ❌ No connector exists | ✅ Built to your Fortify API |
| ADO inline PR comments | ❌ Requires custom connector anyway | ✅ Native ADO REST API client built |
| Confidence threshold + escalation | ❌ Not configurable | ✅ Built-in — 0.7 threshold, escalate() method |
| Shadow mode | ❌ Not available | ✅ Built-in toggle |
| Immutable audit log (STEWARD) | ❌ Generic logging only | ✅ Designed to your compliance requirements |
| Certificate + IIS deployment | ❌ No concept of this | ✅ HARBOUR does WinRM + App Service |
| Teams approval gate | ❌ Not built in | ✅ HARBOUR sends Teams card before Prod |
| Cost control | ❌ Per-agent pricing, fixed tiers | ✅ Pay only for tokens used — ~$30-80/month total |

**The short answer:** Azure AI Foundry gives you a framework. BlueLine gives you agents that know your environment, enforce your standards, and fit your exact workflow. The framework still runs on Azure OpenAI — we are not replacing Azure, we are using it more precisely.

---

## Question 2 — What Do We Need to Make It Production Ready?

The Quality Gate is closest — it needs 3 things. The Security and Certificate Loops each need their integration access confirmed first, then infrastructure wiring. Here is the complete list:

---

### Quality Gate — 1 to 2 weeks

| What's Needed | Detail |
|---|---|
| Azure Function App (HTTP trigger) | Receives the webhook POST from ADO when a PR is opened or updated |
| ADO webhook configured | In ADO project settings — fires on `git.pullrequest.created` and `git.pullrequest.updated` |
| Managed Identity | Replace the PAT in `.env` with an Azure Managed Identity so auth doesn't expire |
| App Settings / Key Vault | Move credentials out of `.env` into Azure Key Vault + Function App settings |

That is it for the Quality Gate. The agents, the ADO client, the PR runner, shadow mode — all already built.

---

### Security Loop — 3 to 4 weeks (after access is granted)

| What's Needed | Detail |
|---|---|
| **Fortify SSC API URL + Token** | Biggest blocker — WATCHTOWER cannot be built without this |
| WATCHTOWER fully built | Polling schedule, finding filter, Service Bus publisher |
| Azure Service Bus namespace | Topics: `security.findings.new` and `security.critical.fix-needed` |
| Azure Function Apps (3) | One each for WATCHTOWER, BULWARK+FORGE, STEWARD |
| Azure Blob Storage container | STEWARD writes immutable audit logs here |
| Managed Identity | Auth for all agents |
| ADO service account | FORGE needs permission to create branches and open PRs |

---

### Certificate Loop — 4 to 6 weeks (after access is granted)

| What's Needed | Detail |
|---|---|
| **C&M portal API access** | Biggest blocker — COURIER cannot automate requests without this |
| **Azure Key Vault access** | REGENT reads live cert metadata from here |
| **WinRM enabled on IIS servers** | HARBOUR needs remote PowerShell access to deploy certs |
| **Service account with cert permissions** | Needs rights to import PFX and update IIS bindings remotely |
| **Teams webhook URL** | HARBOUR sends approval card here before Prod deployment |
| Azure Table Storage | REGENT writes and reads the cert inventory here |
| Azure Function Apps (4) | One each for REGENT, TIMELINE+COURIER, HARBOUR, trigger scheduler |
| Azure Service Bus namespace | Topics for cert pipeline messages |

---

### Common Infrastructure (all tracks)

| Item | Purpose |
|---|---|
| Azure Function Apps (deployed) | Runtime for all agents |
| Azure Service Bus | Agent-to-agent messaging |
| Azure Key Vault | Secrets management for all credentials |
| Azure Blob Storage | STEWARD audit logs |
| Azure Monitor + Log Analytics | Alerting if any agent fails or stops running |
| Managed Identity | Auth — no PATs, no expiring keys |
| Azure DevOps pipeline | CI/CD to deploy agent updates automatically |

---

## Question 3 — Can We Link to User Stories / Work Items in ADO?

**Yes — fully possible.** Azure DevOps has a complete Work Item REST API and this is a natural extension of what FORGE already does.

Here is what linking would look like in practice:

**When BULWARK classifies a finding as CRITICAL or HIGH:**
- FORGE creates the fix PR as it does today
- FORGE also calls the ADO Work Items API to create a Bug work item with the finding details, OWASP category, attack scenario, and the fix branch
- The Bug is automatically linked to the fix PR
- The Bug is assigned to the developer who introduced the vulnerability (git blame)
- The Bug status moves from New → Active when FORGE creates it, → Resolved when the PR is merged

**When CLARION finds a blocking violation on a PR:**
- ASCENT posts the PR comment as it does today
- ASCENT can also create a Task work item linked to the PR for each Tier 1 (Must Fix) finding
- The Task closes automatically when the developer pushes the fix

**What this gives you:**
- Your ADO board shows security debt and code quality debt as real work items
- Sprint planning can include agent-generated bugs alongside manually created ones
- Velocity tracking includes the remediation work the agents are finding
- Audit trail: every vulnerability has a work item, a fix PR, and a STEWARD log entry — three levels of traceability

**What we need from you to build this:**
- Confirmation of the work item type to use — Bug? Task? Custom type?
- Which ADO Area Path the agent-created items should go into
- Who should be the default assignee if git blame returns no clear owner

---

## Question 4 — GitHub Copilot / Spec Kit vs BlueLine — Why Use Our Agents?

This is an important question. GitHub Copilot and BlueLine are solving different problems. They are not alternatives — but if the question is why BlueLine instead of just using Copilot, here is the honest answer:

---

### The Fundamental Difference

**GitHub Copilot is reactive.** A developer has to open it, ask a question, and decide whether to accept the suggestion. It helps one developer at a time, when they choose to use it.

**BlueLine agents are proactive.** They act automatically the moment a PR is opened, without anyone asking. Every PR gets reviewed, every Fortify finding gets triaged, every certificate gets monitored — regardless of whether the developer remembered to check.

---

### Side by Side

| Capability | GitHub Copilot | BlueLine |
|---|---|---|
| Reviews every PR automatically | ❌ Developer must ask | ✅ Fires on webhook, no action needed |
| Enforces YOUR DAS standards | ❌ Knows general best practices | ✅ Loaded with your exact DAS/CDAS rules |
| Posts inline ADO PR comments | ❌ GitHub-first, limited ADO support | ✅ Native ADO integration |
| Fortify finding triage | ❌ No integration | ✅ WATCHTOWER + BULWARK |
| Generates actual fix PR | ❌ Suggests code in editor only | ✅ FORGE creates the branch and PR |
| Certificate management | ❌ No concept | ✅ Full REGENT → TIMELINE → COURIER → HARBOUR pipeline |
| Immutable audit log for InfoSec | ❌ No audit capability | ✅ STEWARD — every action logged |
| Human approval gate before Prod | ❌ No workflow | ✅ Hard gate — Teams card, human clicks approve |
| Confidence scoring + escalation | ❌ No | ✅ Built-in — low confidence goes to human |
| Shadow mode for safe rollout | ❌ No | ✅ Built-in toggle |
| Works on Azure DevOps | ⚠️ Limited | ✅ Built specifically for ADO |
| Cost model | Per seat (~$19-39/developer/month) | Token-based (~$30-80/month total for whole team) |
| Your data stays in Azure tenant | ⚠️ GitHub servers | ✅ Azure OpenAI — your own tenant |

---

### On GitHub Spec Kit — What It Actually Is

GitHub Spec Kit is an open-source toolkit (released by GitHub in late 2025, 80,000+ stars) that promotes **Spec-Driven Development** — the idea of writing a detailed specification before writing any code, then using AI agents to implement it against that spec.

**How Spec Kit works — 4 phases:**
1. **Specify** — You describe what you want to build. AI drafts a detailed spec document
2. **Plan** — You declare architecture and constraints. AI proposes a technical plan
3. **Tasks** — AI breaks the plan into small, reviewable implementation units
4. **Implement** — AI agents (Copilot, Claude Code, Gemini) implement each task

It creates `.github` and `.specify` folders in your project with templates, prompts, and a CLI called `Specify`. It works with 24+ AI coding agents.

**The key difference from BlueLine:**

Spec Kit and BlueLine are solving completely different problems and are not alternatives to each other.

| | GitHub Spec Kit | BlueLine |
|---|---|---|
| **What it does** | Helps you build new features and projects with AI | Automatically reviews, secures, and manages existing code and infrastructure |
| **When it runs** | Developer triggers it manually when starting new work | Runs automatically in the background on everything the team builds |
| **Who uses it** | Individual developer building something new | Entire engineering pipeline — no one needs to trigger it |
| **Scope** | Greenfield development workflow | PR reviews, security triage, certificate management — ongoing operations |
| **ADO integration** | None | Native — posts comments, creates branches, opens PRs |
| **Fortify / Security** | None | WATCHTOWER + BULWARK + FORGE full pipeline |
| **Certificate management** | None | Full REGENT → TIMELINE → COURIER → HARBOUR pipeline |
| **Audit trail** | None | STEWARD — immutable log for every agent action |

**The one-line answer if they ask:**

> *"GitHub Spec Kit helps a developer plan and build something new using AI. BlueLine runs automatically on everything your team builds — it does not need a developer to ask it anything. They solve different problems and can coexist."*

---

### On GitHub Copilot PR Summaries

If the question is about GitHub Copilot for Pull Requests — Copilot PR summaries describe what changed. BlueLine's ASCENT tells you whether to approve, block, or request changes, what the biggest risk is, and exactly what the reviewer must manually verify. Copilot gives you a description. ASCENT gives you a decision.

### On GitHub Advanced Security (GHAS)

GHAS is closer to Fortify — it scans code for vulnerabilities but leaves triage, investigation, and fix to a human. BULWARK and FORGE automate that entire middle layer — classify, assess impact, generate fix, create PR.

---

### The One-Line Answer for the Whole Question

> *"Copilot and Spec Kit make individual developers faster when they choose to use them. BlueLine makes the entire engineering process more consistent, more secure, and more automated — without any developer having to remember to use it."*

---

*End of Key Questions Document — Version 1.1*

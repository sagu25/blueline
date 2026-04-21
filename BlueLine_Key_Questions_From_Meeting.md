# Project BlueLine — Key Questions from the Team Meeting
### Prepared Answers for Strategic Questions Raised + Anticipated Follow-Ups

**Version:** 1.2
**Date:** 2026-04-22

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

---

---

# Part 2 — Anticipated Follow-Up Questions
### Based on What the Team Shared in the Meeting

---

## On Their Tech Stack

---

**Q: You mentioned .NET 4.8 and .NET 8. We are migrating to .NET 10. Can the agent help with that migration?**

> *"Yes — this is actually a strong use case for CLARION. During a migration, developers often carry forward patterns that were acceptable in .NET 4.8 but are anti-patterns in .NET 8 and .NET 10 — things like synchronous blocking calls that deadlock in modern ASP.NET, or HttpClient instantiation patterns that cause socket exhaustion. CLARION already has rules for both framework versions in its standards document. We can add migration-specific rules — for example, flagging any code that is valid .NET 4.8 but should be updated before it reaches .NET 10. The migration becomes a rolling quality gate rather than a big-bang audit at the end."*

---

**Q: We have some legacy applications in Ember. Can the agent review those?**

> *"Ember is not in the current scope — CLARION and LUMEN are built for C# and Angular TypeScript. For the Ember applications, the honest answer is they would be excluded from agent review for now. However, since you mentioned they are legacy and you have a migration plan, the priority is to cover the new Angular TypeScript code first. Ember support can be added later by updating the system prompt — no infrastructure change needed."*

---

**Q: We use .NET MAUI for mobile. Can BlueLine cover that?**

> *"MAUI is C# under the hood, so CLARION's .NET rules — async patterns, dependency injection, exception handling, secrets management — all apply directly. What MAUI introduces that is different from ASP.NET is UI lifecycle patterns and platform-specific code. We would need to add MAUI-specific rules to CLARION's standards document, which is a configuration update not a code change. This is a Phase 2 addition — Phase 1 focuses on the web stack first."*

---

## On Security and Scanning

---

**Q: Fortify is a static scanner. You mentioned you also want dynamic scanning (DAST). Can BlueLine do that?**

> *"BlueLine currently covers SAST — static analysis of source code. Dynamic scanning (DAST) tests a running application, not the source code — it sends requests to a live endpoint and looks for vulnerabilities in the response. That is a different category of tool — examples are OWASP ZAP, Burp Suite, or Microsoft Defender for APIs. BlueLine does not do DAST today. What we can do is integrate DAST findings the same way we integrate Fortify findings — if you run OWASP ZAP and it produces findings, BULWARK can triage those findings exactly the way it triages Fortify findings. So the triage and fix automation applies to any scanner output, not just Fortify."*

---

**Q: We use SonarQube as well. Can BlueLine work alongside it?**

> *"Yes — they work at different layers. SonarQube does static analysis on the full codebase on a schedule. CLARION does AI-powered review on the specific code diff in each PR. They are complementary. SonarQube catches issues across the whole codebase; CLARION catches issues in the exact change a developer just made, in real time, before it merges. You do not need to choose one over the other."*

---

**Q: What if a vulnerability has already been accepted as a known risk — can we suppress it?**

> *"Yes. BULWARK has a suppression mechanism — if a finding is marked as accepted risk or intentionally false positive, it is logged by STEWARD and excluded from future triage runs for that specific finding. In production this mirrors how Fortify SSC handles suppressions — the suppression is recorded with a reason and an approver, not silently skipped."*

---

## On the System Itself

---

**Q: What if Azure OpenAI goes down? Does our PR pipeline stop?**

> *"If Azure OpenAI is unavailable, the agents fail gracefully — they do not block the PR. The PR remains open and reviewable by humans normally. The agent simply does not post its comment for that run. STEWARD logs the failure. An alert fires to the configured Teams channel so the team knows the agents are not running. The pipeline degrades to manual review, it does not break."*

---

**Q: Can we run different rules for different repositories or teams?**

> *"Yes. Each agent has its own system prompt configuration. You can have CLARION load a different standards document per repository — for example, stricter rules for the Payments API than for an internal tooling repo, or different Angular rules for the new codebase versus the legacy Ember migration. In production this is controlled through environment variables per Function App deployment."*

---

**Q: What if the false positive rate is too high and developers start ignoring the comments?**

> *"This is exactly what shadow mode is designed to prevent. We run in shadow mode for the first 2 to 3 sprints — agents review every PR but post nothing. We review the logs, tune the rules, and only go live once the false positive rate is below 20%. Even after go live, ASCENT tracks every finding a developer marks as false positive. If any rule crosses 20% false positive rate, ASCENT flags it for engineering review automatically. The goal is for developers to trust the comments because they are consistently right — if they are not, we fix the rules before developers start tuning out."*

---

**Q: Can it handle very large PRs — hundreds of files?**

> *"The current design reviews each changed `.cs` and `.ts` file individually and then aggregates. Very large PRs — say 50 or more files — would increase cost and run time linearly. In production we would add a file limit threshold — for PRs above a certain size, VECTOR's risk scoring prioritises which files to review first and the others are flagged for manual review. A PR with 200 files is usually a sign of a branch that was open too long, not a normal review scenario."*

---

**Q: How long does it take to onboard the team to this? Is there a learning curve?**

> *"For developers — almost none. They open a PR and comments appear. The only thing they need to understand is how to respond to a comment — agree, dismiss, or mark as false positive. That takes five minutes to explain. For the team member who owns the rules — the person who maintains the DAS standards document — the learning curve is updating a Markdown file when rules change. No code, no deployment."*

---

## On Commercial and Ownership

---

**Q: Who maintains BlueLine after it goes live? Do we need your team permanently?**

> *"The system is designed for your team to own after handover. The agents are Python files on Azure Function Apps — any developer who can write Python can maintain them. The rules live in a Markdown document — any tech lead can update them. We would do a handover sprint at the end of the project including documentation, a runbook, and a session with your team. Ongoing support is an optional arrangement — it is not a dependency."*

---

**Q: What is the commercial model — is this a licensed product or a build-once engagement?**

> *"BlueLine is a build-once engagement — we build it for you, it runs on your Azure infrastructure, you own the code completely. There is no per-seat licence, no ongoing subscription to us, no vendor dependency. Your only running cost is Azure OpenAI token consumption — approximately $30 to $80 per month for a team doing 20 to 30 PRs per day. Everything else is standard Azure services you are likely already paying for."*

---

**Q: Can HARBOUR integrate with our change management process — ServiceNow or similar?**

> *"Yes — if you have a formal change management process for Production deployments, HARBOUR can be extended to create a Change Request in ServiceNow (or equivalent) before the Prod deployment, wait for approval there instead of (or in addition to) the Teams card, and then mark the Change as implemented after deployment completes. This is an integration point we would scope in the discovery questions — question 5.3 in the discovery document covers your change management process."*

---

**Q: How do we measure the ROI from this? How do we know it is working?**

> *"Three metrics we recommend tracking from day one: First — PR review cycle time, the time from PR opened to first human reviewer comment. ASCENT handles the mechanical review in under a minute, so reviewers spend less time on the checklist and more time on the logic. Second — security finding resolution time, from Fortify finding created to fix merged. Third — certificate expiry incidents — the target is zero. We define the baseline before we go live, measure after, and review with you at the end of each sprint. We suggest setting the success criteria before Phase 1 starts so the result is objective."*

---

*End of Key Questions Document — Version 1.2*

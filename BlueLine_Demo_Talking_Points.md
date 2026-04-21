# Project BlueLine — Demo Talking Points
### How to Present the POC to the Stakeholder Team

**Version:** 2.0
**Updated:** 2026-04-21

---

## Before You Start

- Have the app running at `http://localhost:8501` **before** the meeting starts
- Tab 1: click **Load Sample Code** (C#) — do not run yet
- Tab 2: click **Load Sample Finding** — do not run yet
- Tab 3: select **payments.external.com** from the inventory — do not run yet
- Keep this document open on your second screen as a reference

---

## Opening Statement (30 seconds)

> *"So based on the pain points you shared — the manual PR reviews, the Fortify triage work, and the certificate management overhead — we did some research and built a working proof of concept.*
>
> *This is not a mockup. Every time I click a button here it is making a real call to an AI model and returning real analysis. What I want to show you today is the actual intelligence that would run inside the production system."*

---

## Slide 1 — The Problem (1 minute)

> *"Three specific problems. Let me re-state them so we're aligned:*
>
> *First — code reviews. Your reviewers are manually checking every PR for .NET and Angular standards. It's time-consuming, inconsistent, and depends on who's reviewing that day.*
>
> *Second — Fortify. You trigger scans manually, read findings manually, investigate manually. Fortify tells you there's a problem but doesn't tell you what to do about it.*
>
> *Third — certificates. Everything lives in spreadsheets and emails, renewals happen manually across Dev, QA, and Prod — and a certificate expiry takes down a service immediately.*
>
> *What we're proposing is an AI agent system that automates all three. And today I'm going to show you the full pipeline for each one — not just one agent, but the entire chain from detection to action."*

---

## Tab 1 — Quality Gate (3–4 minutes)
### CLARION → LUMEN → VECTOR → ASCENT

### What to say when you open the tab:

> *"This is the Quality Gate. The moment a developer opens a pull request in Azure DevOps, four AI agents kick in automatically — in parallel.*
>
> *CLARION checks coding standards. LUMEN detects code smells. VECTOR scores risk and complexity. ASCENT takes all three outputs and produces one consolidated recommendation: Approve, Request Changes, or Block.*
>
> *In this demo I'm pasting code manually. In production, Azure DevOps fires a webhook and all four agents run before the human reviewer even opens the PR."*

### Click "Load Sample Code" → Select C# → Click "Run Full Review"

While it's loading, watch the agent status panel:
> *"You can see all four agents running in sequence — CLARION, LUMEN, VECTOR, then ASCENT aggregating. Total time is 20 to 45 seconds."*

### When results appear — point out:

1. **ASCENT recommendation at the top** — *"ASCENT gives one clear verdict — BLOCK, REQUEST CHANGES, or APPROVE — so the reviewer doesn't have to read through individual findings to understand the overall picture."*
2. **Tier 1 — Must Fix** — *"These are blocking issues. The hardcoded database password and the SQL injection — ASCENT says do not merge until these are resolved."*
3. **The Fix shown inline** — *"Every finding comes with the corrected code. Not just 'this is wrong' — here is what it should look like. That's what makes it actionable for the developer."*
4. **VECTOR metrics** — *"VECTOR computed cyclomatic complexity, nesting depth, and method count before even calling the AI. It flagged this code as HIGH risk before CLARION looked at a single line."*
5. **Reviewer Checklist** — *"ASCENT also gives the human reviewer a specific checklist — things the AI cannot verify, like business logic correctness. The AI handles the mechanical review, the human focuses on the parts that need human judgment."*

> *"So instead of a reviewer spending 30 minutes going through a file line by line, they open the PR and the annotations are already there. Tier 1, Tier 2, Tier 3 — they know exactly where to focus."*

---

## Tab 2 — Security Loop (4–5 minutes)
### WATCHTOWER → BULWARK → FORGE → STEWARD

### What to say when you open the tab:

> *"This is the full Security Loop — all four agents. Let me walk you through what each one does.*
>
> *WATCHTOWER monitors Fortify SSC on a schedule and publishes new findings to a message queue. In this demo I'm providing the finding manually — that's the only difference.*
>
> *BULWARK receives the finding, triages it, and classifies it. FORGE takes BULWARK's output and creates a draft fix PR in Azure DevOps — branch, commit, PR description, everything. STEWARD writes an immutable audit log entry for InfoSec.*
>
> *The whole chain runs automatically. Right now your team does all of this manually."*

### Click "Load Sample Finding" → Click "Run Security Pipeline"

Watch the pipeline status indicators as each agent completes.

### When results appear — point out:

1. **WATCHTOWER message** — *"WATCHTOWER confirmed it received the finding from Fortify and passed it to BULWARK via Service Bus."*
2. **BULWARK classification** — *"CRITICAL, 95% confidence. It's mapped it to OWASP A03 — Injection. Your InfoSec team immediately has the compliance context without reading the full finding."*
3. **Attack scenario** — *"This is the most valuable part for the developer — it explains what an attacker can actually do with this. Not just 'SQL injection found', but the real impact. That's what motivates the fix."*
4. **FORGE draft PR** — *"Now watch what FORGE did. It generated the branch name, the conventional commit message, and a full PR description with Summary, Security Impact, Changes Made, and Testing Required sections. In production, this PR is already open in Azure DevOps before anyone on the team has looked at the finding."*
5. **Click to expand PR Description** — *"This is what the developer sees when they open the PR — a professional, complete description. They review the fix, they approve, they merge. That's it."*
6. **STEWARD audit entry** — *"And STEWARD has written an immutable log entry — which agents ran, what the classification was, what action was taken, run ID, timestamp. This is what InfoSec reviews. In production this goes to Azure Blob Storage with a 7-year retention policy."*

> *"So the workflow becomes: Fortify finds it → WATCHTOWER picks it up → BULWARK triages it → FORGE creates the fix PR → developer reviews and merges → STEWARD logs everything. The manual investigation step is gone."*

---

## Tab 3 — Certificate Loop (4–5 minutes)
### REGENT → TIMELINE → COURIER → HARBOUR

### What to say when you open the tab:

> *"This is the full Certificate Loop. Four agents, completely automated.*
>
> *REGENT is the inventory manager — it knows every certificate you have, where it's deployed, who owns it, and how many days are left. In production this reads from Azure Key Vault.*
>
> *Look at the inventory table at the top."*

### Point out the inventory table first:

> *"This is what REGENT maintains. You can see straight away — payments.external.com is CRITICAL, 4 days left. api.core-main.internal is URGENT, about 10 days. These are the two that need action right now.*
>
> *In your current process, someone has to maintain a spreadsheet to know this. REGENT knows automatically because it reads directly from Key Vault daily."*

### Select "payments.external.com" → Click "Run Certificate Pipeline"

Watch the pipeline status indicators.

### When results appear — point out:

1. **REGENT confirmation** — *"REGENT retrieved the cert from inventory and published it to the pipeline."*
2. **TIMELINE urgency badge** — *"CRITICAL — 4 days remaining. TIMELINE has identified the renewal path as DigiCert external CA and assessed whether automation is possible."*
3. **COURIER CA request** — *"COURIER has already called the DigiCert API — simulated here, real in production. It has an order ID, it knows the validation method, it knows the delivery timeline. The new certificate is ready to download."*
4. **HARBOUR deployment plan** — *"Now expand the commands for Dev and QA. These are the actual PowerShell commands that HARBOUR would run via WinRM on each IIS server — Import-PfxCertificate, update the IIS binding, verify HTTPS. Dev and QA are already marked as deployed."*
5. **Teams approval card** — *"And this is what appears in your Teams channel. The certificate subject, the environments already deployed, the production target — and two buttons: Approve or Hold. A human clicks Approve, HARBOUR deploys to Production. That is the only manual step in the entire process."*

> *"The goal is zero certificate expiry incidents. The system handles it before it becomes a problem. No spreadsheet, no email chain, no emergency Friday afternoon IIS work."*

---

## Closing Statement (1 minute)

> *"So what you've just seen across all three tabs is the complete agent pipeline for each track — not just the AI reasoning, but the full chain from detection to action.*
>
> *The POC runs on Azure OpenAI — your own Azure tenant. No code, no findings, no certificate metadata went anywhere external.*
>
> *What's left to go to production is wiring these agents into your actual environment — Azure DevOps webhooks for the Quality Gate, Fortify SSC API for the Security Loop, and Azure Key Vault for the Certificate Loop. The intelligence is already built.*
>
> *We only need answers to five questions to scope Phase 1: do you have a written coding standards document, can we get Fortify SSC API access, does the C&M portal have an API, is Azure OpenAI approved, and which track do you want live first.*
>
> *We're recommending the Quality Gate — lowest risk, most visible, value from the first sprint."*

---

## Handling Likely Questions

**"Is this the full system or just a demo?"**
> *"The AI reasoning is the full system — the same agents, the same prompts, the same logic that would run in production. What the POC doesn't have is the live integrations — the Fortify API connection, the real IIS deployment, the real Key Vault. Those are the Phase 1, 2, and 3 build items. The brain is done."*

**"Is the AI always right?"**
> *"No — and that's why every agent has a confidence score and a human gate. BULWARK won't classify as False Positive if it's uncertain — it escalates to NEEDS_REVIEW. FORGE never merges code. HARBOUR never deploys to Production without a human clicking approve. The AI is assistive, not autonomous."*

**"What happens if FORGE generates a wrong fix?"**
> *"FORGE creates a draft PR — it never merges. The developer reviews the fix, edits it if needed, and approves it. The AI does the investigation and drafts the solution, the engineer validates it before anything goes anywhere."*

**"What about our code and data going to an AI model?"**
> *"It's Azure OpenAI — Microsoft's hosted version running inside your own Azure subscription. Your code diffs, Fortify findings, and certificate metadata never leave your Azure tenant. Same governance as any other Azure service you already use."*

**"How long to build the full thing?"**
> *"We're not giving a timeline today — we need the five discovery answers first. Once we have those we'll come back with a proper implementation plan. What we can say is Phase 1 — the Quality Gate — has the shortest path because Azure DevOps access is the only new integration needed."*

**"What if Fortify API access is restricted?"**
> *"Phase 1 is Quality Gate only — no Fortify needed. We can start immediately and sort Fortify access in parallel for Phase 2."*

**"What if the C&M portal has no API?"**
> *"Then COURIER uses a workaround — either browser automation or a manual download step with HARBOUR handling the deployment automatically. The deployment and verification parts still save most of the manual work even if the request step needs a human."*

**"Can it handle languages other than C# and Angular?"**
> *"Yes. The AI model understands most languages. Adapting to Java or Python means updating the system prompts and rules — not rebuilding any infrastructure."*

---

## What NOT to Say

- Don't say "it will take X weeks" — you don't have the discovery answers yet
- Don't promise 100% accuracy — say "high confidence with human gates"
- Don't call it "ChatGPT" — it's Azure OpenAI / GPT-4o on their own Azure tenant
- Don't say "the POC is the final system" — say "the AI reasoning is done, the integrations are Phase 1, 2, and 3"
- Don't say FORGE "creates PRs automatically" without adding "draft PRs — human approves before anything merges"

---

*End of Demo Talking Points — Version 2.0*

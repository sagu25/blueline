# Project BlueLine — Demo Talking Points
### How to Present the POC to the Stakeholder Team

---

## Before You Start

- Have the app running at `http://localhost:8501` **before** the meeting starts
- Have all three tabs pre-loaded with sample data (click "Load Sample" on each tab)
- Keep this document open on your second screen as a reference

---

## Opening Statement (30 seconds)

> *"So based on the pain points you shared in your email — the manual PR reviews, the Fortify triage work, and the certificate management overhead — we did some research and built a quick proof of concept to show you what an AI-powered approach could look like.*
>
> *This is a working demo — it's actually calling an AI model right now and giving you real analysis. What I want to show you today is not a mockup — it's the actual intelligence that would run inside the system we're proposing."*

---

## Slide 1 — The Problem (1 minute)

Refer back to their own email. Say:

> *"In your email you highlighted three specific problems. Let me just quickly re-state them so we're aligned:*
>
> *First — code reviews. Your reviewers are manually checking every PR for .NET and Angular standards. It's time-consuming, inconsistent, and depends on who's reviewing that day.*
>
> *Second — Fortify. You're triggering scans manually, reading through findings manually, and deciding what to fix manually. Fortify tells you there's a problem but doesn't tell you how to fix it.*
>
> *Third — certificates. Everything is tracked in spreadsheets and emails, and renewals happen manually across Dev, QA, and Prod — which means the risk of something expiring and taking down a service is real.*
>
> *What we're proposing is an AI agent system that automates all three of these. Let me show you what that looks like."*

---

## Tab 1 — Quality Gate: CLARION + LUMEN (3–4 minutes)

### What to say when you open the tab:

> *"This is the Quality Gate track. The idea is — the moment a developer opens a pull request in Azure DevOps, two AI agents automatically kick in.*
>
> *CLARION checks coding standards — things like naming conventions, SQL injection risks, hardcoded secrets, async patterns.*
>
> *LUMEN looks at code quality — code smells like deep nesting, magic numbers, duplicate logic, methods that are doing too much.*
>
> *In this demo I'm pasting code manually, but in production this happens automatically — Azure DevOps fires a webhook, the agents fetch the PR diff, and the comments appear on the PR before the human reviewer even opens it."*

### Click "Load Sample Code" → Select C# → Click "Run Review"

While it's loading:
> *"The sample I've loaded has a few deliberate violations — hardcoded database password, SQL string concatenation which is a SQL injection risk, five levels of nesting, and some duplicate code. Let's see what the agents catch."*

### When results appear — point out:

1. **Overall score** — *"It's giving us an overall quality score for the PR."*
2. **Error: hardcoded password** — *"This is a security violation — it caught a database password hardcoded in the connection string. This is the kind of thing that slips through human review when people are in a rush."*
3. **Error: SQL injection** — *"SQL string concatenation — this is an OWASP Top 10 vulnerability. The agent not only flags it but shows the correct parameterized query fix right there."*
4. **The Fix column** — *"Every violation comes with a specific fix — not just 'this is wrong' but 'here is the corrected code'. That's what makes this actionable for the developer."*
5. **LUMEN smells** — *"LUMEN caught the deep nesting and duplicate code as separate concerns from standards — these are about maintainability, not just rules."*

> *"So instead of a reviewer spending 30 minutes going through this file, they open the PR and the annotations are already there. They focus on the logic and the architecture — the AI handles the checklist."*

---

## Tab 2 — Security Loop: BULWARK (3–4 minutes)

### What to say when you open the tab:

> *"This is the Security track. BULWARK is the agent that replaces the manual Fortify triage process.*
>
> *Right now, when Fortify produces a finding, someone from the team has to read it, understand the vulnerable code path, decide if it's real or a false positive, and then figure out how to fix it. That whole process is manual.*
>
> *BULWARK does the triage automatically. It classifies each finding — Critical, High, Needs Review, or False Positive — and it generates the actual code fix."*

### Click "Load Sample Finding" → Click "Run Triage"

While loading:
> *"The sample is a SQL injection finding from Fortify — Category SQL Injection, from an Orders API service."*

### When results appear — point out:

1. **Classification badge** — *"BULWARK has classified this as CRITICAL with 95% confidence."*
2. **OWASP category** — *"It maps it to OWASP A03 — Injection — so your InfoSec team immediately has the compliance context."*
3. **Attack scenario** — *"This is what I think is the most valuable part — it explains the actual attack scenario. Not just 'SQL injection found', but what an attacker can actually do with this, what data is at risk."*
4. **Secure code fix** — *"And then it generates the fix — the parameterized query that resolves the vulnerability. FORGE, the next agent in the chain, would take this fix and automatically create a draft pull request for the developer to review and merge."*

> *"So the workflow becomes: Fortify finds it → BULWARK triages it → FORGE creates the fix PR → developer reviews and merges. The manual investigation step in the middle is eliminated."*

---

## Tab 3 — Certificate Loop: TIMELINE (2–3 minutes)

### What to say when you open the tab:

> *"The third track is certificate management. This one is actually the highest risk of the three because a certificate expiry takes down a service immediately — it's not a gradual degradation.*
>
> *Right now the process is entirely manual — spreadsheets, email reminders, then a multi-step IIS deployment process repeated across Dev, QA, and Prod.*
>
> *TIMELINE is the agent that monitors Azure Key Vault daily, spots certificates approaching expiry, and kicks off the renewal workflow automatically."*

### Click "Load Sample Certificate" → Click "Analyse Certificate"

While loading:
> *"This sample is an internal certificate for an API endpoint expiring in about 16 days — which puts it in the urgent zone."*

### When results appear — point out:

1. **Urgency badge** — *"URGENT — 16 days remaining. In the real system this would have already triggered the workflow 14 days ago."*
2. **Renewal path** — *"It identifies the renewal path — in this case internal PKI via your C&M portal."*
3. **Action plan** — *"This is what COURIER and HARBOUR do — they execute these steps automatically. Request from the CA, download, validate, deploy to Dev, then QA, then a notification is sent to a Teams channel asking for production approval. Human only needs to click approve."*

> *"The goal is zero certificate expiry incidents — the system handles it before it becomes a problem."*

---

## Closing Statement (1 minute)

> *"So what you've just seen is the actual AI reasoning — the same models and logic that would run in the production system. The POC is running on Azure OpenAI so all of this stayed within your Azure tenant — no data went anywhere external.*
>
> *What we're proposing is to take this intelligence and wire it into your actual environment — Azure DevOps webhooks for the quality gate, Fortify SSC API for the security loop, and Azure Key Vault for the certificate loop.*
>
> *We've already done the research, the architecture design, and the low-level design. The discovery questions document I'll share with you has about 40 questions — we only really need answers to five of them to start Phase 1.*
>
> *The five key ones are: do you have a written coding standards document, can we get Fortify SSC API access, does the C&M certificate portal have an API, is Azure OpenAI approved for this use case, and which of the three tracks do you want to go live first?*
>
> *We're suggesting starting with the Quality Gate — lowest risk, most visible, and you'll see value from the first sprint."*

---

## Handling Likely Questions

**"Is the AI always right?"**
> *"No — and that's why every agent has a confidence score and a human gate. Agents with low confidence escalate to a human automatically. No code gets merged, no cert gets deployed to production without a human approving it. The AI is assistive, not autonomous."*

**"What happens if the AI gives wrong advice on a security fix?"**
> *"FORGE creates a draft PR — it never merges code. A developer reviews the fix before it goes anywhere. The AI does the investigation and drafts the solution, the engineer validates it."*

**"What about our data going to an AI model?"**
> *"It's running on Azure OpenAI — your company's own Azure subscription. The code diff, the Fortify findings, the cert metadata — none of it leaves your Azure tenant. It's the same governance model as any other Azure service you use."*

**"How long to build the full thing?"**
> *"Don't give a timeline estimate in this meeting — say you want to get answers to the discovery questions first, then you'll come back with a proper implementation plan and timeline."*

**"What if Fortify API access is restricted?"**
> *"Phase 1 doesn't need Fortify — the Quality Gate only needs Azure DevOps access. We can start there and get Fortify access sorted in parallel for Phase 2."*

**"Can we use this for languages other than C# and Angular?"**
> *"The AI model understands most languages — adapting to Java or Python would just mean updating the system prompts and rule sets, not rebuilding the agents."*

---

## What NOT to Say

- Don't say "it will take X weeks" — you don't have enough information yet
- Don't promise 100% accuracy — say "high confidence with human gates"
- Don't call it "ChatGPT" — it's Azure OpenAI / GPT-4o running on their own Azure
- Don't say the POC "is the final system" — it's a proof of concept showing the AI intelligence

---

*End of Demo Talking Points*

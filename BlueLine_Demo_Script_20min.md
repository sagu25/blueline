# BlueLine Demo Script — 20 Minutes
**Memorise the bold lines. The rest is guidance.**

---

## BEFORE YOU START — Setup Checklist

- [ ] Browser open, `BlueLine_Agenda_Slide.html` ready in one tab
- [ ] `BlueLine_Overview_Slide.html` ready in another tab
- [ ] Streamlit app running at `localhost:8501`
- [ ] PR #13 visible in Azure DevOps (or ready to load)
- [ ] Shadow Mode **OFF** if you want to post real comments, **ON** for safe demo
- [ ] Security Loop sample finding loaded
- [ ] Certificate Loop — `api.core-main.internal` selected
- [ ] Font size bumped up in browser (Ctrl + twice) so back row can read

---

## MINUTE 0:00 — Opening (Don't touch the screen yet)

*Stand, make eye contact, no slides yet.*

> **"Before I show you anything, let me ask — how many Pull Requests does your team raise in a week?"**

*Wait for their answer. Nod.*

> **"And how long does a typical review take a human reviewer?"**

*Wait.*

> **"So if you have [their number] PRs a week, and each takes [their time] — that is [multiply] hours of your engineers' time, every week, just on mechanical checking. Checking naming conventions, async patterns, SQL queries. Things a machine can do. That is the problem BlueLine solves."**

*Now open the Agenda slide. F11 fullscreen.*

---

## MINUTE 1:00 — Agenda (30 seconds)

*Show `BlueLine_Agenda_Slide.html`*

> **"Twenty minutes. Five things. We will look at what we built, I will show it working live on real code, and we will leave time for your questions at the end."**

*Do not read every agenda item. Just gesture at it and move on.*

---

## MINUTE 1:30 — Context (90 seconds)

*Switch to `BlueLine_Overview_Slide.html`*

> **"We automated three things. Quality Gate — every Pull Request reviewed automatically in 45 seconds. Security Loop — Fortify findings triaged and fixed without manual research. Certificate Loop — SSL certificates monitored, renewed, and deployed across your environments."**

*Point to each card as you name it.*

> **"One principle runs through all three — agents do the work, humans keep the control. Nothing merges without a developer approving it. Nothing touches Production without a human clicking Approve. The AI handles the routine. The engineer handles the judgment."**

*Pause. Let that land. Then —*

> **"Let me show you what this actually looks like."**

*Switch to the Streamlit app.*

---

## MINUTE 3:00 — Quality Gate (8 minutes)

### Setting up — 30 seconds

*App is open on the Quality Gate tab. ADO is configured.*

> **"This is connected live to your Azure DevOps repository. These are real open Pull Requests."**

*Click Load PRs. Let it populate.*

> **"I'm going to pick PR #13 — a developer added inventory and user management features. Four files changed."**

*Select PR #13. Point at the branch name.*

> **"Branch is feature/blueline-demo going into main. Created by Sagar. This PR was raised two minutes ago — in a normal day, it would sit in a reviewer's queue for hours before anyone looked at it."**

*Shadow Mode — make sure it is set appropriately. Then —*

> **"I'm going to run the Quality Gate now. Watch what happens."**

*Click Run Quality Gate.*

---

### While it runs — 45 seconds

*Do not go silent. Narrate.*

> **"Four agents are running right now. CLARION is reading every line of C# and TypeScript and checking it against your DAS/CDAS coding standards. LUMEN is looking for code smells — things that are not rule violations but will cause problems in three months. VECTOR is calculating a risk score and finding the hotspots. ASCENT is waiting for all three to finish."**

*Watch the progress. When ASCENT fires —*

> **"And ASCENT is aggregating everything into one verdict."**

---

### The BLOCK verdict lands — 2 minutes

*BLOCK appears on screen with 2/10. Pause. Say nothing for 3 seconds. Let them read it.*

> **"BLOCK. Score 2 out of 10."**

*Pause again.*

> **"This PR has critical issues that must be fixed before it can be merged. Let me show you what it found."**

*Scroll to Must Fix Before Merge.*

> **"Five blockers. These are not suggestions — these are things that will cause production failures or security incidents if this code goes live."**

*Click on the first finding — hardcoded connection string.*

> **"First one — hardcoded connection string. The developer typed the database password directly into the source code file. That password is now visible to every engineer who has access to this repository. BlueLine tells them exactly what to do — move it to Azure Key Vault."**

*Click the SQL injection finding.*

> **"This one is more serious. The SearchStock method builds a SQL query by pasting user input directly into the string. An attacker who can reach this endpoint can type a single quote and run arbitrary commands against your database. This is OWASP A03 — Injection. One of the most common ways applications get breached."**

*Click the .Result finding.*

> **"And this — using .Result on an async method. This looks harmless. It passes all unit tests. But under real production load, this causes a deadlock. The thread that called .Result holds a lock waiting for the async task to finish, while the async task waits for that thread. The application freezes. This is the kind of thing that shows up on a Monday morning as a P1 incident."**

*Scroll down briefly to show Should Fix and Consider sections.*

> **"Beyond the blockers, five more issues that should be fixed, and three informational findings. All of this — 13 findings, tiered by priority — in 45 seconds, automatically, without a human opening the file."**

---

### The human's role — 30 seconds

*Pause. Step back from the screen.*

> **"Now — and this is important — BlueLine cannot merge this PR. The developer fixes these issues, pushes again, and BlueLine reviews the new version automatically. The human reviewer then looks at the ASCENT summary, applies their judgment on the business logic and design, and clicks Approve in Azure DevOps. The AI handles the mechanical checks. The engineer handles the thinking."**

---

## MINUTE 11:00 — Security Loop (5 minutes)

*Click the Security Loop tab.*

> **"Same idea — but for Fortify security findings."**

*Click Load Sample Finding.*

> **"In production, WATCHTOWER polls Fortify SSC after every CI/CD run and picks up new findings automatically. For today I'm providing the finding directly."**

*Show the finding in the text area — it's the SQL injection one.*

> **"SQL injection in GetOrdersByCustomer — user input concatenated directly into the query string. Let me run the pipeline."**

*Click Run Security Pipeline.*

---

### While BULWARK runs — 20 seconds

> **"BULWARK is now reading this finding, cross-referencing it against its security knowledge base — SQL injection, XSS, path traversal, hardcoded secrets, broken auth — and deciding what classification it deserves."**

---

### BULWARK result — 90 seconds

*CRITICAL appears with 100% confidence.*

> **"CRITICAL. 100% confidence."**

*Point to the OWASP category.*

> **"OWASP A03:2021 — Injection. BULWARK has mapped this to the global security standard so there is no ambiguity about what category of risk this is."**

*Point to the attack scenario.*

> **"And this — the attack scenario. It tells you exactly what an attacker can do. Not in abstract terms. Specific — an attacker can execute arbitrary SQL commands and potentially gain unauthorised access to sensitive data. That is the conversation you have with your security team."**

*Point to the Secure Code Fix.*

> **"And the fix is already written. Parameterised query — exactly what the developer needs to implement. No research, no Stack Overflow, no guessing."**

---

### FORGE and STEWARD — 60 seconds

*Scroll to FORGE result.*

> **"FORGE has created a draft Pull Request. Branch name follows your convention — fix/security/sql-injection. Commit message is conventional commits format. PR description is structured — summary, security impact, changes made, testing required. And a reviewer note telling the developer exactly what to verify before they approve."**

*Point to the DRAFT banner.*

> **"Always a draft. FORGE never merges. The developer reviews this, satisfies themselves the fix is correct, and approves."**

*Scroll to STEWARD.*

> **"And STEWARD has written an immutable audit log entry. Every field — run ID, timestamp, classification, confidence, what action was taken, who needs to approve. In production this goes to Azure Blob Storage with a WORM policy. Seven-year retention. Your InfoSec and compliance teams will love this conversation."**

---

## MINUTE 16:00 — Certificate Loop (4 minutes)

*Click the Certificate Loop tab.*

> **"Last one. This one tends to surprise people."**

*Let them see the inventory table.*

> **"This is your certificate inventory. REGENT reads this from Azure Key Vault every morning. Look at the first two rows."**

*Point to the EXPIRED certs.*

> **"payments.external.com — expired 13 days ago. api.core-main.internal — expired yesterday. Two certificates that right now are potentially causing HTTPS errors for your users."**

*Pause.*

> **"In your current process — how would you know these are expired?"**

*Wait for their answer. Then —*

> **"With BlueLine — you know at 6:00 AM, before anyone in the business has started their day. Let me show you what happens."**

*Select api.core-main.internal. Click Run Pipeline.*

---

### Pipeline runs — 90 seconds

> **"TIMELINE has assessed it — EXPIRED, -1 days. The renewal path is Internal PKI, your C&M portal. COURIER is now contacting the CA via API."**

*COURIER result appears.*

> **"Renewal submitted. Order ID assigned. Internal PKI auto-approves — the certificate comes back immediately. New thumbprint generated."**

*HARBOUR result appears.*

> **"HARBOUR has deployed the renewed certificate to Dev — imports it, binds it to IIS, verifies HTTPS. QA — same. Both done automatically. No RDP session. No manual import."**

*Scroll to the Teams approval card.*

> **"And then it stops. Production — HARBOUR sends this card to a Teams channel."**

*Point to the Approve and Hold buttons.*

> **"The approver sees the domain, the new expiry date, which servers are already done. They click Approve. HARBOUR deploys to Production. The whole thing — from EXPIRED to Production deployed — without a single person logging into a server."**

*Pause.*

> **"And the only reason a human was involved at all is because we decided Production should always require human approval. Dev and QA — automated. Production — human gate. That is a design choice, not a technical limitation."**

---

## MINUTE 20:00 — Close (30 seconds)

*Step away from the screen. Look at them directly.*

> **"What you just saw — the PR review, the security fix, the certificate renewal — in your current world that is multiple engineers, multiple tools, and multiple hours every time it happens. BlueLine does it in under two minutes, consistently, on every event, with a full audit trail."**

*Beat.*

> **"The engineers do not disappear. They stop doing the mechanical work and start doing the work that actually needs their brain."**

*Smile.*

> **"What questions do you have?"**

---

## HANDLING INTERRUPTIONS

If they stop you mid-demo to ask something — answer it in two sentences max, then say:

> **"Let me show you that in a moment — I want you to see it in context."**

Then finish what you were showing and come back to their question.

---

## IF SOMETHING BREAKS

If the app crashes or an API call fails, do not panic. Say:

> **"This is a live demo environment — let me pull that up again."**

Restart the relevant section. If it fails twice, move to the slides and talk through what the output looks like using the demo screenshots from the walkthrough document.

---

## THE THREE LINES THAT MUST LAND

Write these on your hand if you need to. These are the moments that stick:

1. **When BLOCK appears with 2/10:**
   > *"This PR has critical issues that must be fixed before it can be merged."*
   Then silence for 3 seconds.

2. **When FORGE draft PR appears:**
   > *"The fix is already written. The developer reviews and approves. That is it."*

3. **When the Teams approval card appears:**
   > *"Dev and QA — automated. Production — human gate. Agents do the work. Humans keep the control."*

---

## TIME MAP

| Time | Section |
|---|---|
| 0:00 – 1:00 | Opening question + context |
| 1:00 – 1:30 | Agenda slide |
| 1:30 – 3:00 | Overview slide + three tracks |
| 3:00 – 11:00 | Quality Gate demo |
| 11:00 – 16:00 | Security Loop demo |
| 16:00 – 20:00 | Certificate Loop demo + close |

---

*Project BlueLine — LTM AI-Led Engineering Team · 20-Minute Demo Script*

# Project BlueLine — Team Q&A Preparation
### Questions the Team May Ask During the Demo & How to Answer Them

**Version:** 1.0
**Date:** 2026-04-21
**Purpose:** Pre-prepare confident answers for every question the team might raise — technical, process, data security, cost, and risk.

---

## Category 1 — "Does it actually work / Is this real?"

---

**Q: Is this a mockup or is it actually calling AI?**

> *"This is live. Every time you click Run Review or Run Triage, it is making a real API call to Azure OpenAI and returning real analysis. There is no hardcoded response anywhere in this demo."*

---

**Q: How accurate is it? What is the error rate?**

> *"In our internal testing on the sample code, the agents correctly identified every planted violation. For production accuracy, the honest answer is: we will validate in shadow mode first — agents run and log their output without taking any action, and we review the results for 2–3 sprints before going live. That is how we establish a real accuracy baseline for your specific codebase — not a lab number."*

---

**Q: Has this been tested on real code, or just the samples?**

> *"The POC is tested on the sample code we built specifically with known violations. The next step — Phase 1 — is to run it on your actual repositories in shadow mode, which gives us real-world accuracy numbers before anything goes live."*

---

**Q: What if the AI gives the wrong fix for a security vulnerability?**

> *"FORGE only creates a draft pull request — it never merges code. The developer receives the draft PR, reviews the suggested fix, and either accepts it, edits it, or rejects it. The AI does the investigation and drafts the solution — the engineer has the final say. No code reaches any environment without a human approving it."*

---

**Q: What if the AI misses a real vulnerability?**

> *"The agents are a first pass — they are designed to catch the common, repeatable issues that currently slow down reviewers. They do not replace a security-focused human review for complex business logic. Think of it as an automated pre-check that handles 80% of the mechanical work so your reviewers can focus on the 20% that needs human judgment."*

---

## Category 2 — "What does it actually do to our workflow?"

---

**Q: Will this replace our human code reviewers?**

> *"No. The agents handle the mechanical checklist — naming conventions, SQL injection patterns, hardcoded secrets, async mistakes. Reviewers still own the logic review, the architecture decisions, and the business context. What changes is that by the time a reviewer opens the PR, the annotations are already there. They are not starting from scratch."*

---

**Q: Will developers find the AI comments annoying or intrusive?**

> *"That is a fair concern, and the design accounts for it. First, every comment includes a confidence score — low-confidence findings are either suppressed or marked as advisory. Second, you can configure which rules are blocking versus advisory. Third, we start in shadow mode, so developers do not even see the comments until the team has reviewed and validated them. The goal is for developers to find the comments useful, not noisy."*

---

**Q: How does it post comments on a PR — does it use someone's account?**

> *"It uses a dedicated service account or bot account — for example, 'BlueLine Bot' in Azure DevOps. It does not post under any individual's name. The comment will clearly identify itself as an automated agent review."*

---

**Q: Can we turn it off for a specific PR or repo?**

> *"Yes. You can exclude specific repositories, folders, or file types entirely. You can also add a label or flag to a PR to skip agent review for that specific PR — for example, if it is a hotfix and you just need it merged fast."*

---

**Q: What happens if a developer disagrees with the AI comment?**

> *"They dismiss it or mark it as resolved — the same way they would dismiss any PR comment they disagree with. The agents are advisory by default. If you want specific rules to be blocking, we configure that explicitly and only for rules you are confident about."*

---

**Q: Will it slow down our PR pipeline?**

> *"The Quality Gate agents run in parallel — CLARION, LUMEN, and VECTOR all start at the same time. Total time from PR open to comments appearing is 20 to 45 seconds. That is faster than a human reviewer opening their email and finding the notification."*

---

## Category 3 — "What about our data and security?"

---

**Q: Where does our code go? Is it sent to OpenAI externally?**

> *"In this POC, it is running on Azure OpenAI — that is Microsoft's hosted version of GPT-4o, running inside a specific Azure subscription. Your code diff never leaves Azure. It is the same governance model as any other Azure service your team already uses. We are not using the public OpenAI API."*

---

**Q: What about IP protection? Our code is proprietary.**

> *"Azure OpenAI has explicit contractual terms that Microsoft does not use your prompts or completions to train their models. Your code is processed in memory for the duration of the call and not retained. If you need this confirmed in writing for your legal team, that is in the Microsoft Azure OpenAI service terms — we can pull the exact clause."*

---

**Q: What data does the certificate agent access?**

> *"TIMELINE only reads certificate metadata from Azure Key Vault — the certificate name, expiry date, and subject. It does not read the private key. The private key never leaves Key Vault. HARBOUR handles deployment using Azure SDK calls that also do not expose the private key."*

---

**Q: Is there an audit trail of what the agents did?**

> *"Yes — STEWARD is the dedicated audit agent. Every action taken by every agent is written to an immutable log before the action happens. The log records: which agent, what action, what input, what output, what confidence score, and the timestamp. This is designed to satisfy InfoSec and compliance review requirements."*

---

**Q: What if someone tries to inject malicious code into a PR to manipulate the AI?**

> *"Good question — this is called prompt injection. The agents are designed to only analyse code against rules and produce structured output. They cannot take actions based on code content — they cannot call external URLs, they cannot modify their own instructions. The tools available to each agent are locked at design time. A malicious comment inside the code diff cannot instruct the agent to do something outside its defined tool set."*

---

## Category 4 — "Cost and infrastructure"

---

**Q: How much will this cost to run?**

> *"The main running cost is Azure OpenAI token consumption. The system uses prompt caching — the coding standards document is sent once and cached for subsequent calls, so you only pay for the new code diff each time. Our estimate for a team doing 20–30 PRs per day is in the range of $30–80 per month in token costs. We can provide a more precise estimate once we know your actual PR volume and average diff size."*

---

**Q: What Azure infrastructure does this require?**

> *"Four Azure Function Apps (one per track), Azure Service Bus for agent-to-agent messaging, Azure Table Storage for the certificate inventory, Azure Key Vault for secrets management, and Azure OpenAI. All of these are standard Azure services — nothing exotic. Most teams at this scale have most of this already provisioned."*

---

**Q: Who manages and maintains this after it goes live?**

> *"The system is designed to be low-maintenance. CLARION's rules are updated via a document — no code change required. The main ongoing task is reviewing the shadow mode logs and approving or rejecting new rules each sprint. We estimate 1–2 hours per sprint from one team member. We will also set up alerting if any agent fails or stops running."*

---

**Q: How long would Phase 1 take to build?**

> *"We are intentionally not giving a timeline today — we need answers to five key discovery questions before we can estimate accurately. The questions are: do you have a written coding standards document, can we get Azure DevOps webhook access, is Azure OpenAI approved, which track goes first, and what does a successful pilot look like for you. Once we have those answers, we will come back with a proper plan."*

---

## Category 5 — "Technical / how does it work?"

---

**Q: What AI model is it using?**

> *"GPT-4o, running via Azure OpenAI. It is the same model behind Microsoft Copilot. The choice of GPT-4o specifically is because it has strong code reasoning, supports tool use (which is how agents take actions), and supports prompt caching (which reduces cost significantly)."*

---

**Q: Can it support languages other than C# and Angular?**

> *"Yes. The AI model understands most modern programming languages. Adapting to Java, Python, or Go means updating the system prompts and rule sets — not rebuilding any infrastructure. The agent architecture is language-agnostic by design."*

---

**Q: How does the agent know our coding standards?**

> *"CLARION's system prompt includes your coding standards document. When we go live, we load your actual standards document into the prompt — the same document your reviewers reference today. The agent enforces exactly what that document says, no more and no less. If the document changes, we update the prompt."*

---

**Q: What is the difference between CLARION and LUMEN?**

> *"CLARION enforces rules — it checks against a defined standard. Did you name this variable correctly? Did you use parameterized queries? Is there a hardcoded secret? Pass or fail against a rule.*
>
> *LUMEN identifies smells — it uses AI judgment to spot things that are technically valid but will cause problems: methods that are doing too much, deep nesting that is hard to maintain, duplicate logic that will lead to bugs when one copy gets updated and the other doesn't. Smells are not rule violations — they are code health issues."*

---

**Q: How do agents talk to each other?**

> *"Through Azure Service Bus — a message queue. One agent publishes a message, the next agent picks it up. They are completely independent — if one agent is slow or fails, it does not block the others. Every message is persisted, so if an agent crashes mid-process, the message is not lost and the work can resume."*

---

**Q: Can an agent take action on its own — like auto-merging code or auto-deploying a certificate?**

> *"No. There are hard-coded human gates in three places: code can never be merged without a human approving the PR, certificates can never be deployed to Production without a human clicking approve in Teams, and any agent with a confidence score below 0.7 stops and escalates to a human instead of acting. The agents are assistive — they do the investigation and preparation, humans make the final call on anything consequential."*

---

## Category 6 — "Risk and what could go wrong?"

---

**Q: What if the Service Bus goes down or an agent crashes?**

> *"Azure Service Bus has built-in message persistence and retry logic. If an agent crashes after picking up a message but before completing, the message is returned to the queue and retried. Azure Function Apps restart automatically on failure. There is also a dead-letter queue — messages that fail after multiple retries land there and trigger an alert so a human can investigate."*

---

**Q: What is the worst case scenario if something goes wrong?**

> *"In the Quality Gate — a PR that should have been flagged gets missed. A human reviewer catches it. No production impact.*
>
> *In the Security Loop — a FORGE-generated fix PR contains a mistake. A developer reviews and rejects it. No production impact.*
>
> *In the Certificate Loop — HARBOUR deploys a certificate to Dev or QA incorrectly. This is a non-production environment and can be rolled back. Production deployments always require a human approval — no automated production deployment is possible."*

---

**Q: What if we configure a rule incorrectly and CLARION starts blocking all PRs?**

> *"That is why we start in shadow mode. In shadow mode, agents log their output but do not post comments and do not block anything. You review the log, tune the rules, and only go live when you are confident. Even in live mode, you can switch any rule from blocking to advisory instantly — it is a configuration change, not a code change."*

---

**Q: Have you considered what happens when developers start gaming the AI — writing code just to pass the checks?**

> *"This is a healthy outcome, actually — if developers start writing cleaner code because an AI is reviewing it, that is the goal. For gaming in a malicious sense — like obfuscating code to hide violations — the agent still analyses the code structure and AST patterns, not just surface-level text. But more importantly, the AI review supplements human review, not replaces it. A developer who is actively trying to hide bad code from the AI will not also hide it from their team lead."*

---

## Category 7 — "What's next / how do we proceed?"

---

**Q: What do you need from us to start?**

> *"Five things: a written coding standards document for CLARION, Azure DevOps webhook permission so agents can listen for PR events, Azure OpenAI approval from your IT/Cloud team, a sandbox repository we can test against, and a decision on which track to start with. We only need these five to begin Phase 1."*

---

**Q: Can we start with just one track?**

> *"Absolutely — that is actually what we recommend. Start with the Quality Gate. It has the lowest risk, the most visible output (PR comments), and the fastest feedback loop. You will see the value within the first week. The Security Loop and Certificate Loop can follow in Phase 2 and Phase 3 once the team has confidence in the system."*

---

**Q: How do we measure if it is working?**

> *"We suggest three metrics for the pilot: PR review cycle time (time from PR open to first human reviewer comment), number of violations found by agents vs. missed by agents (tracked during shadow mode), and developer satisfaction — a quick survey after 4 weeks. We define what 'success' looks like with you before the pilot starts, not after."*

---

**Q: What is the rollback plan if it is not working?**

> *"The Quality Gate is additive — it adds comments to PRs. Turning it off means no more automatic comments. No code is changed, no process is broken, no data is deleted. You just stop the Azure Function App. Rollback is a one-click operation and has zero impact on your existing pipeline."*

---

## Quick Reference — One-Line Answers for Fast Questions

| Question | One-line Answer |
|---|---|
| Is this a demo or is it live? | Live — real AI calls, real analysis |
| Does our code leave Azure? | No — Azure OpenAI only, within your subscription |
| Can it auto-merge code? | No — only creates draft PRs, human approves merge |
| Can it auto-deploy to Prod? | No — hard human gate before every Prod action |
| What if the AI is wrong? | Human reviews every output before any consequential action |
| How long to set up? | 15 minutes for the POC; Phase 1 scoped after discovery questions |
| What does it cost? | Roughly $30–80/month in Azure OpenAI tokens for a 20–30 PR/day team |
| Does it replace reviewers? | No — handles the checklist, reviewers focus on logic and architecture |
| What languages does it support? | C# and Angular now; any language with a prompt update |
| Where do we start? | Quality Gate first — lowest risk, most visible value |

---

*End of Q&A Preparation Document — Version 1.0*

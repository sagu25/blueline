# Project BlueLine — How Each Agent Is Built
### One Paragraph Per Agent — For Team Explanation

**Version:** 1.0
**Date:** 2026-04-21
**Purpose:** If the team asks "how is this agent actually built?" — use this document to give a confident, complete answer for each agent that leaves no follow-up questions.

---

> **Before you use this document — one sentence that covers all agents:**
>
> *"Every agent is built the same way — we give the AI a detailed identity and ruleset through a system prompt, we give it tools to take actions, and Azure OpenAI does the reasoning in between. The only difference between agents is what rules they know and what actions they can take."*

---

## Quality Gate Agents

---

### CLARION — Coding Standards Agent

CLARION is built around a system prompt that contains your complete DAS and CDAS coding standards — all 13 rule categories including async patterns, HttpClient usage, dependency injection, secrets management, exception handling, input validation, CORS, EF patterns, logging, and resilience. When a PR is opened, CLARION receives the code diff and reasons against those rules line by line. Every violation it returns includes the exact line number, the rule that was broken, why it is dangerous, the corrected code, and a confidence score between 0 and 1. We only surface violations where confidence is 0.7 or above — anything below that gets filtered out so developers are not flooded with uncertain findings. The standards document is prompt-cached, which means if 30 PRs come in on the same day, the rules are only sent to the AI once — every PR after that only sends the new code diff, cutting the cost by around 60%.

---

### LUMEN — Code Smell Detector

LUMEN is built with a system prompt that teaches it to recognise ten categories of code smells — long methods, large classes, deep nesting, magic numbers, duplicate code, dead code, long parameter lists, feature envy, god classes, and primitive obsession — plus four .NET-specific structural issues like DbContext held as a singleton, TransactionScope without async flow, N+1 query patterns, and blocking async calls. Unlike CLARION which checks against fixed rules, LUMEN uses AI judgment to assess maintainability — these are issues that are technically valid code but will cause problems over time. LUMEN returns each smell with the specific method or class it is in, why it is a problem, a practical refactoring suggestion, and an effort estimate so the developer knows whether it is a quick fix or a larger piece of work.

---

### VECTOR — Risk Scorer

VECTOR is unique because it works in two layers. First, it computes static metrics directly in Python code — cyclomatic complexity by counting decision branches, maximum nesting depth by measuring indentation, method count, dependency count, and specific high-risk pattern hits like `.Result`, `new HttpClient()`, and wildcard CORS. It does this locally without even calling the AI. Then it passes those computed metrics plus the code to Azure OpenAI, which uses both the numbers and its own reading of the code to produce a risk score between 0 and 1, identify the specific hotspot methods, and write a reviewer note explaining exactly what the human reviewer should focus on. This two-layer approach means the risk score is grounded in real measurements, not just AI guesswork.

---

### ASCENT — Aggregator and Final Decision

ASCENT does not look at code directly — it receives the structured JSON outputs from CLARION, LUMEN, and VECTOR and synthesises them into one consolidated review. Its system prompt defines a strict prioritisation logic: any CLARION error-severity violation or security issue automatically forces a BLOCK or REQUEST CHANGES recommendation, while lower-severity findings are sorted into Tier 2 and Tier 3. ASCENT then writes a one-paragraph plain-English summary, a three-tier prioritised finding list, and a reviewer checklist of things the AI cannot verify — like whether the business logic is correct. The result is one card at the top of the PR that tells the reviewer everything they need to know before reading a single line of code.

---

## Security Loop Agents

---

### WATCHTOWER — Fortify Monitor

WATCHTOWER is built as a scheduled polling agent that connects to the Fortify SSC REST API on a defined interval — daily or per-commit depending on configuration. It authenticates using an API token, retrieves the list of new or unreviewed findings across all configured repositories, and publishes each finding as a structured message to an Azure Service Bus topic. WATCHTOWER does not do any AI reasoning itself — its job is purely discovery and routing. In the POC, this polling step is replaced by manual input since we do not yet have the Fortify SSC API credentials. In production, the moment Fortify completes a scan, WATCHTOWER picks up the findings and the rest of the pipeline runs automatically without anyone touching it.

---

### BULWARK — Security Triage Agent

BULWARK is built with a system prompt that contains the OWASP Top 10 knowledge base and detailed triage logic for the most common vulnerability classes — SQL injection, XSS, path traversal, hardcoded secrets, insecure deserialization, broken auth, sensitive data exposure, CSRF, and insecure direct object references. It receives a Fortify finding and the vulnerable code snippet, and returns four things: a classification of CRITICAL, HIGH, NEEDS_REVIEW, or FALSE_POSITIVE with a confidence score; the specific OWASP category so InfoSec has immediate compliance context; the actual attack scenario explaining what an attacker can do with this vulnerability; and the corrected secure code with the exact fix applied. BULWARK is intentionally conservative — if it is uncertain whether something is a false positive, it always defaults to NEEDS_REVIEW rather than dismissing it, because the cost of missing a real vulnerability is higher than the cost of a human reviewing an extra finding.

---

### FORGE — Fix PR Creator

FORGE is built with a system prompt that knows secure coding patterns for each major vulnerability class — it understands what a correct parameterized query looks like, what a properly sanitized output looks like, what a correctly validated file upload looks like. It receives BULWARK's triage output including the secure code fix, and generates a complete draft pull request: a branch name following the `fix/security/` convention, a conventional commit message, a PR title, and a full PR description with Summary, Security Impact, Changes Made, and Testing Required sections. In production FORGE uses the Azure DevOps REST API to create the branch, commit the fixed file, and open the draft PR — the same API we already use in the Quality Gate. The key design decision is that `ready_to_merge` is always false — FORGE creates draft PRs only, and no code reaches any environment without a developer reviewing and approving the fix first.

---

### STEWARD — Audit Log Agent

STEWARD requires no AI reasoning — it is a structured logging agent that creates an immutable audit record for every action taken by every other agent in the Security Loop. For each pipeline run it records the run ID, timestamp in UTC, which agents were involved, a summary of the finding, the classification, the confidence score, what action was taken, whether a human gate is required, and the current gate status. In production this record is written to Azure Blob Storage in an append-only container — once written it cannot be modified or deleted. The design is intentional: if someone questions whether an agent acted correctly on a finding, the audit trail shows exactly what the AI decided, with what confidence, and what happened next. This is also what InfoSec reviews periodically to validate the system is behaving correctly.

---

## Certificate Loop Agents

---

### REGENT — Certificate Inventory Manager

REGENT is built as a data management agent with no AI reasoning — it is the single source of truth for every certificate the team manages. It reads certificate metadata from Azure Key Vault — subject, expiry date, environments deployed to, CA type, owner, and deployment targets — and maintains a structured inventory in Azure Table Storage. Every time it runs it computes the days remaining for each certificate and assigns a status: OK, MONITOR, RENEWAL_NEEDED, URGENT, CRITICAL, or EXPIRED. The inventory is sorted by days remaining so the most urgent certificates are always at the top. In the POC, this is an in-memory sample inventory that mirrors exactly what Key Vault and Table Storage would hold in production. REGENT is also the agent that triggers the rest of the pipeline — when a certificate crosses the RENEWAL_NEEDED threshold of 30 days, REGENT publishes it to Azure Service Bus and the TIMELINE, COURIER, and HARBOUR chain begins.

---

### TIMELINE — Expiry Analyser

TIMELINE is built with a system prompt that knows certificate lifecycle management — urgency thresholds, renewal paths for different CA types, common risks and complications, and what automation is possible versus what requires manual steps. It receives the certificate details from REGENT and returns a structured analysis: the urgency level, a plain-English summary of the situation, the renewal path — internal PKI, external CA like DigiCert, or Let's Encrypt — whether full automation is possible, a step-by-step action plan, and any risks or complications to be aware of. TIMELINE does the thinking that previously sat in someone's head — it knows that an internal PKI renewal is faster than a DigiCert OV certificate, it knows that a wildcard certificate covers multiple services and carries higher deployment risk, and it flags these things proactively so nothing is missed.

---

### COURIER — CA Renewal Requester

COURIER is built to communicate with Certificate Authority APIs — either the internal C&M portal API or external CAs like DigiCert. It takes TIMELINE's analysis and constructs the appropriate API call for the CA type: for internal PKI it submits a certificate signing request to the C&M portal; for DigiCert it calls the CertCentral REST API with the order details. It returns the CA's order ID, the validation method required, the estimated delivery timeline, and the certificate once it is ready to download. In the POC, this CA communication is simulated by AI — it generates a realistic order ID, delivery estimate, and certificate thumbprint to show exactly what the real flow would look like. In production, COURIER needs the C&M portal API endpoint and credentials, or the DigiCert API key, both of which are in our discovery questions.

---

### HARBOUR — Deployment Agent

HARBOUR is the most complex agent in the system — it handles the physical deployment of the renewed certificate to every environment. For IIS servers it connects via WinRM, which is Windows Remote Management, and runs PowerShell commands: it imports the PFX certificate into the Windows certificate store, updates the IIS site binding to use the new certificate thumbprint, and then runs an HTTPS verification check to confirm the site is serving the new certificate correctly. For Azure App Service deployments it uses the Azure SDK to upload the certificate and bind it to the app. Dev and QA environments are deployed automatically without any human involvement. Before touching Production, HARBOUR sends a Teams approval card to the configured channel — it shows the certificate subject, the new expiry date, which environments are already deployed, and the production target — with Approve and Hold buttons. A human must click Approve before HARBOUR touches Production. This hard gate is non-negotiable by design and cannot be bypassed by configuration.

---

*End of Agent Build Explanations — Version 1.0*

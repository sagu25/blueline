# Project BlueLine — Discovery Questions
### For the Stakeholder / Requesting Team Meeting

**Version:** 1.0  
**Date:** 2026-04-15  
**Purpose:** To gather the information needed to finalize the implementation design, avoid incorrect assumptions, and align on priorities and constraints before development begins.

---

> **How to use this document:**  
> Go through these questions in the meeting with the team (Pankaj / Ravi / Manjunath). Not all questions need formal answers — even a "we haven't thought about that yet" is useful. Mark each with the answer so the BlueLine team can update the LLD accordingly.

---

## Section 1 — Current Environment & Tools

These questions confirm our technical assumptions about what already exists.

**1.1** Are you currently using **Azure DevOps** or **GitHub** as your source control and CI/CD platform? Or both?

**1.2** What version of Azure DevOps are you on — cloud (dev.azure.com) or on-premises (Azure DevOps Server)?

**1.3** How many active repositories does the Core & Main team maintain? Roughly how many PRs are opened per day/week?

**1.4** What is the current branching strategy — GitFlow, trunk-based, feature branches? Which branch do PRs target?

**1.5** Is **Fortify SSC** hosted on-premises or in the cloud? Do you have the REST API endpoint URL and does the team already have an API token we can use?

**1.6** Is Azure Key Vault already provisioned for the team? Does it currently store any certificates, or would we be setting it up from scratch?

**1.7** What types of certificates does the team manage?
- Internal (issued by your own PKI / C&M portal)?
- External (DigiCert, GlobalSign, or other commercial CA)?
- Machine/server certificates?
- All of the above?

**1.8** Where are certificates currently deployed — IIS only, or also Azure App Service, Azure API Management, or other targets?

**1.9** Is there an existing **certificate inventory** somewhere — a spreadsheet, a wiki, a ticket system? Can we get access to it to seed the REGENT inventory?

---

## Section 2 — Coding Standards & Code Review

These questions define what CLARION and LUMEN will enforce.

**2.1** Does the team have a written coding standards document for C# (.NET) and/or Angular (TypeScript)? If yes, can you share it? This is the single most important input for CLARION.

**2.2** Are you using `.editorconfig` files in your repositories? If yes, can we access them?

**2.3** Are you currently using any static analysis tools — Roslyn analyzers, StyleCop, SonarQube? If yes, what rules are enabled and what are the known high false-positive rules we should skip?

**2.4** What are the top 3–5 issues your reviewers most commonly catch that they wish were automated? (e.g., "people always forget to use async/await properly", "hardcoded connection strings keep showing up")

**2.5** Are there any rules that are team-specific and not in any public standard? For example, naming conventions for your service classes, or a rule about how you structure your controller methods?

**2.6** What is your current PR approval process — how many reviewers are required, and are there mandatory reviewers (e.g., a senior engineer or tech lead must always approve)?

**2.7** How do you want BlueLine agent comments to appear on PRs?
- As comments from a bot account (e.g., "BlueLine Bot")?
- As a single summary comment, or individual inline comments per violation?
- Should agent comments be blocking (PR cannot merge until resolved) or advisory only?

**2.8** Are there any files or folders in the repos that should be **excluded** from AI review — e.g., auto-generated code, migration files, vendor code?

---

## Section 3 — Security Process & Fortify

These questions define the BULWARK, FORGE, and WATCHTOWER behavior.

**3.1** Who currently triages Fortify findings — is it developers, a dedicated security engineer, or the InfoSec team? Who would be notified when BULWARK escalates a finding?

**3.2** What is the current SLA or expectation for how quickly a Critical Fortify finding should be addressed? (e.g., "within 5 business days")

**3.3** Are there categories of Fortify findings that the team already knows are typically false positives for your codebase? If yes, listing them will let us pre-configure BULWARK to suppress them automatically.

**3.4** When FORGE generates a fix PR, who should be assigned as the mandatory reviewer — the developer who introduced the vulnerability, the InfoSec team, or a specific security champion?

**3.5** Are there any Fortify projects or repositories that should be **excluded** from automated triage — for example, archived projects or third-party integrations?

**3.6** How often does the team currently run Fortify scans — on every commit, daily, or ad hoc? What scan schedule would you like WATCHTOWER to enforce?

**3.7** The STEWARD audit log is intended to be reviewed periodically by InfoSec. How often would InfoSec want to review it — weekly, monthly? Should there be an automated summary report sent to them?

---

## Section 4 — Certificate Management

These questions define TIMELINE, REGENT, COURIER, and HARBOUR behavior.

**4.1** What is the internal CA portal you mentioned (the "C&M portal")? Does it have an API, or is it a web UI only? If UI only, can someone provide access credentials for COURIER to automate requests?

**4.2** For external certificates, which CA do you use — DigiCert, Sectigo, GlobalSign, or other? Do you have an API key for them?

**4.3** How many certificates does the team currently manage in total? Ballpark is fine (e.g., 10–20, 50–100, 100+).

**4.4** How many environments do certificates need to be deployed to — Dev, QA, Prod only? Or also staging, DR, UAT?

**4.5** On the IIS servers, is WinRM (remote PowerShell) enabled? Does the team have service accounts with permission to install certificates and update IIS bindings remotely?

**4.6** Are any certificates deployed to Azure App Service or Azure API Management (not just IIS)?

**4.7** What is the current expiry notice period — at what point does the team typically start the renewal process? We are proposing 30 days — is that acceptable, or should it be longer given how long the internal CA process takes?

**4.8** For production certificate deployments, who should receive the approval notification — a specific person, a distribution list, or a Teams channel? What is an acceptable response window (e.g., 24 hours, 48 hours)?

**4.9** Has the team ever had a certificate expiry incident (site went down or showed a cert error)? If yes, what happened and how long did it take to recover? This will help us size the urgency threshold.

---

## Section 5 — Azure Infrastructure & Access

These questions confirm what infrastructure exists and what needs to be provisioned.

**5.1** Is there an existing Azure subscription the BlueLine Function Apps should be deployed to, or should we provision a new one?

**5.2** Does the team have an existing Azure DevOps service account or managed identity that pipeline automation typically runs under? Should BlueLine use that, or create its own identity?

**5.3** Are there any network restrictions we need to be aware of — firewall rules, VPN requirements, private endpoints — between Azure and the Fortify SSC server, internal CA, or IIS servers?

**5.4** Is there a preferred Azure region for deployment (e.g., Australia East, East US)?

**5.5** Does the team use Azure Monitor / Log Analytics already, or will this be new? Is there a preference for where logs land?

**5.6** Does the team use Microsoft Teams? If yes, which channel should BlueLine notifications (approvals, alerts, escalations) go to?

---

## Section 6 — Priorities, Constraints & Success

These questions align on what done looks like and what constraints we need to respect.

**6.1** Between the three tracks — Quality Gate, Security Loop, Certificate Loop — which one is causing the most pain right now? Which would you like to see working first?

**6.2** Is there a deadline or event driving this project — a release, a compliance audit, a leadership review?

**6.3** Are there any compliance requirements (ISO 27001, SOC 2, internal audit) that BlueLine must satisfy — for example, around data handling, audit trail retention, or AI decision logging?

**6.4** The system sends PR diff content and Fortify finding details to the Claude API (Anthropic). Is your organization comfortable with this, or is there a data residency / IP protection policy that requires all data to stay on-premises? If the latter, we would evaluate Azure OpenAI (hosted on Azure in your chosen region) as the LLM instead.

**6.5** What does a successful pilot look like for you — what would you need to see in the first 4 weeks to say "this is working"?

**6.6** Are there any approaches or tools that have already been tried and failed that we should know about? We want to avoid repeating something that didn't work.

**6.7** Who on the Core & Main team will be the primary point of contact for ongoing tuning of CLARION's rules and ASCENT's feedback? This person should plan to spend ~1–2 hours per sprint reviewing and approving rule updates.

**6.8** Is the team open to starting in **shadow mode** for the first 2–3 sprints (agents run and log output but don't post comments or take actions)? This is the safest way to validate accuracy before going live.

---

## Section 7 — Quick Clarifiers (Yes/No)

These are fast yes/no questions to confirm or challenge key assumptions.

| # | Question | Expected Answer | Your Answer |
|---|---|---|---|
| 7.1 | Is C# (.NET) the primary backend language? | Yes | |
| 7.2 | Is Angular (TypeScript) the primary frontend framework? | Yes | |
| 7.3 | Are all target environments hosted on Azure (not on-premises VMs)? | Mostly yes | |
| 7.4 | Should agents be blocked from any action if confidence is below a threshold? | Yes | |
| 7.5 | Can FORGE open PRs automatically without asking a human first? | Yes (draft PR) | |
| 7.6 | Should HARBOUR deploy to Prod automatically (no human gate)? | No | |
| 7.7 | Is there a sandbox/test environment we can use during development? | Yes | |
| 7.8 | Is Microsoft Teams used for team communication? | Yes | |
| 7.9 | Has the team previously used any AI tooling in the pipeline? | Unknown | |
| 7.10 | Is there a formal change management process for Prod deployments that HARBOUR needs to integrate with? | Unknown | |

---

## Priority Questions (If Time is Limited)

If the meeting is short, focus on these five first:

1. **Do you have a written coding standards document?** (most critical for CLARION)
2. **What is the Fortify SSC API URL and does the team have an API token?** (blocks BULWARK/WATCHTOWER)
3. **What is the internal CA portal — does it have an API?** (blocks COURIER)
4. **Is sending code diffs to the Anthropic Claude API acceptable from a data policy perspective?**
5. **Which track do you want to go live first?**

---

*End of Discovery Questions Document — Version 1.0*

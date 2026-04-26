# AI-Led Engineering: Code Review & Security Tools Overview
**Prepared for: PGE, Core & Main, ATCO Accounts**
**Date: April 2026 | LTM AI-Led Engineering Team**

---

## Executive Summary

This document outlines the AI-based tools available in the market for **Code Review** and **Security Checks**, along with LTM's custom agent approach and recommendations based on experience across multiple customer engagements.

The goal is to position LTM not as a vendor of isolated tools, but as a partner delivering a **holistic, AI-led engineering offering** that combines best-in-class market tools with custom agents tailored to the customer's environment (C#, .NET, Angular, Azure DevOps).

---

## 1. Code Review — AI Tools Landscape & Recommendations

### 1.1 The Problem (Current State)

The current PR review process at PGE/Core & Main is manual and inconsistent:
- Reviewers manually check .NET and Angular standards (C#, TypeScript, naming conventions, structure)
- Security and vulnerability checks are done partially via tools but mostly by hand
- Code smells, anti-patterns, and type safety issues are identified inconsistently
- No standardized enforcement of guidelines across teams
- Review quality depends heavily on individual reviewer experience
- Missed issues during initial review lead to costly rework cycles

### 1.2 AI-Based Code Review Tools — Market Overview

| Tool | Type | Key Capabilities | Best For | Pricing Model |
|---|---|---|---|---|
| **GitHub Copilot for PRs** | Cloud SaaS | AI-generated PR summaries, inline code suggestions, vulnerability detection | Teams already on GitHub | Per-seat subscription |
| **CodeRabbit** | Cloud SaaS | Line-by-line AI review, multi-language support, GitHub/GitLab/Azure DevOps integration, customizable review rules | Teams wanting deep PR feedback | Per-seat / usage-based |
| **Qodo Merge (CodiumAI)** | Open Source + SaaS | AI PR review agent, supports GPT-4/Claude, configurable review checklist | Teams wanting open-source flexibility | Free OSS / paid cloud |
| **Bito AI** | Cloud SaaS | AI code review in IDE and PR workflow, context-aware suggestions, security checks | Developer-first review in IDE | Per-seat subscription |
| **Amazon CodeGuru Reviewer** | Cloud (AWS) | ML-based code review, Java/Python focus, security detectors, cost and performance recommendations | AWS-native environments | Pay-per-line-of-code |
| **SonarQube / SonarCloud** | On-Prem / Cloud | Static analysis, code smells, security hotspots, quality gates, C#/.NET and TypeScript support | Enterprise with existing CI/CD pipelines | Community (free) / Commercial |
| **Snyk Code** | Cloud SaaS | Real-time SAST in IDE and CI/CD, AI-powered fix suggestions, integrates with Azure DevOps | Security-first code review | Free tier / Enterprise |
| **DeepSource** | Cloud SaaS | Automated code review, anti-pattern detection, auto-fix PRs, supports C#, TypeScript | Teams wanting auto-fix capability | Per-seat subscription |
| **Sourcegraph Cody** | Cloud / Self-hosted | AI coding assistant, codebase-aware review, context from entire repo | Large codebases with complex context | Enterprise licensing |

### 1.3 Capability Comparison

| Capability | GitHub Copilot | CodeRabbit | SonarQube | Qodo Merge | LTM Custom Agent |
|---|---|---|---|---|---|
| C# / .NET Standards | Partial | Yes | Yes | Yes | **Fully Customizable** |
| Angular / TypeScript | Yes | Yes | Yes | Yes | **Fully Customizable** |
| Custom Coding Guidelines | Limited | Yes (config) | Yes (rules) | Yes (config) | **Native — built around your standards** |
| Azure DevOps Integration | Yes | Yes | Yes | Yes | **Yes** |
| Auto-comment on PR | Yes | Yes | No | Yes | **Yes** |
| Contextual Fix Suggestions | Partial | Partial | No | Partial | **Yes — with codebase context** |
| Learning from your patterns | No | No | No | No | **Yes — fine-tuned on your repos** |
| Works on-prem / air-gapped | No | No | Yes | Partial | **Yes** |
| Cost for 50+ devs | High | Medium | Medium | Low | **Predictable / Included in engagement** |

### 1.4 LTM Custom Code Review Agent — Our Approach

Rather than replacing market tools, our custom agent **sits on top of** the existing DevOps pipeline and adds a layer that off-the-shelf tools cannot provide:

**What the custom agent does:**
- Pulls each PR from Azure DevOps automatically
- Validates code against the customer's **specific .NET and Angular coding standards** (not generic rules)
- Identifies security issues, code smells, and anti-patterns with **contextual fix suggestions** pulled from the customer's own codebase
- Posts structured, actionable review comments directly on the PR
- Enforces **consistent guidelines across all teams** — removing reviewer dependency
- Generates a **PR Review Score** (0–10) so leads can prioritize which PRs need human attention
- Learns from accepted/rejected suggestions over time

**What makes it different from market tools:**
- Customer-specific rules — not just generic language standards
- Awareness of the full application estate (multiple repos, shared libraries, patterns)
- Integrated into the existing workflow — no developer behavior change required
- Can be extended to new use cases (certificate, security) with the same agent framework

### 1.5 Recommendations

1. **Short-term**: Deploy LTM's Custom Code Review Agent as the primary reviewer for all PRs — it is MVP-ready and can be demoed immediately.
2. **Complement with SonarQube**: If the customer already has SonarQube, integrate it as a quality gate signal fed into the custom agent rather than replacing it.
3. **Avoid per-seat SaaS tools** for large teams — cost scales poorly; a custom agent on an LLM API is more cost-effective at scale.
4. **Long-term**: Expand the agent to cover all repositories across the customer application estate, not just one codebase.

---

## 2. Security Checks — AI Tools Landscape & Recommendations

### 2.1 The Problem (Current State)

The customer currently uses **Fortify** for vulnerability scanning. The process is heavily manual:
- Fortify scans are triggered manually or on a schedule — no event-driven automation
- Vulnerability reports are reviewed and analyzed manually by engineers
- Findings are interpreted manually — no consistent prioritization framework
- Remediation approach is decided case-by-case — no AI-assisted guidance
- Fixes are implemented manually, then re-scanned to verify — slow feedback loop
- **Fortify identifies vulnerabilities but does not provide contextual fixes** — the gap our agent fills

### 2.2 AI-Enabled Security Tools — Market Overview

| Tool | Category | Key Capabilities | Fortify Relationship | Best For |
|---|---|---|---|---|
| **Snyk** | SAST + SCA + IaC | Real-time vulnerability detection, AI-powered fix PRs, integrates with DevOps pipelines | Complementary — developer-facing, Fortify is enterprise-wide | Developer-first security, fast remediation |
| **Checkmarx One** | SAST + DAST + SCA | AI-enhanced scanning, correlation engine, risk-based prioritization, Azure DevOps native | Competing / Complementary | Enterprise SAST replacement or complement |
| **Veracode** | SAST + DAST + SCA | AI-assisted triage, Fix Agent (auto-generates fixes), IDE integration | Competing — similar scope to Fortify | Teams wanting auto-fix suggestions |
| **GitHub Advanced Security (CodeQL)** | SAST | Semantic code analysis, variant analysis, can scan C# and TypeScript | Complementary — open-source findings | Teams on GitHub |
| **Semgrep** | SAST + Supply Chain | Fast OSS scanning engine, custom rule writing, AI assistant for rule creation | Complementary — lightweight, fast | Teams wanting custom security rules |
| **Cycode** | ASPM | AI-powered Application Security Posture Management, correlates findings across all tools including Fortify | **Fortify-native integration** — aggregates Fortify + other tools | Teams wanting unified view across multiple scanners |
| **Mend.io** | SCA | AI-powered dependency scanning, license compliance, auto-remediation PRs | Complementary — focuses on third-party libraries | Teams with heavy OSS dependency risk |
| **Aikido Security** | All-in-one | Cloud-native, AI triage engine, SAST + SCA + IaC + container scanning | Complementary — lightweight alternative | Startups / mid-market teams |
| **Endor Labs** | Next-gen SCA | AI reachability analysis — tells you if a vulnerable function is actually called | Complementary | Teams drowning in SCA alert noise |
| **Orca Security** | Cloud Security | Cloud posture + workload scanning, AI risk prioritization | Complementary — cloud-layer | Teams with cloud infrastructure exposure |

### 2.3 The Core Gap Fortify Leaves Open

Fortify is a **detection engine** — it finds vulnerabilities accurately. But it does not:
- Explain WHY a specific finding is critical in **your codebase context**
- Tell a developer **exactly what to change** in their specific file and function
- Prioritize findings based on **business impact** (what's customer-facing vs. internal)
- Automatically open a fix PR or suggest a code patch
- Track the remediation lifecycle end-to-end

**This is exactly where the LTM Custom Security Agent adds value.**

### 2.4 LTM Custom Security Agent — Our Approach (Complementing Fortify)

```
Fortify Scan Output
       |
       v
LTM Security Agent
       |
       |-- Reads Fortify SAST report (XML/JSON)
       |-- Maps findings to exact file + line in the codebase
       |-- Ranks findings by: severity + exploitability + business context
       |-- Generates contextual fix suggestion (specific code patch, not generic advice)
       |-- Posts actionable comment on the relevant PR / work item in Azure DevOps
       |-- Tracks status: Open → Fix Suggested → Fix Applied → Re-scan Verified
       |-- Escalates unresolved critical findings after SLA breach
       v
Developer gets an actionable fix — not just a vulnerability report
```

**Key differentiators over raw Fortify:**
- **Contextual fixes**: "In `PaymentController.cs` line 142, replace `string.Format` with parameterized query — here is the exact replacement code"
- **Prioritization engine**: Ranks which of the 200 Fortify findings to fix first based on exploitability and blast radius
- **Workflow integration**: Creates Azure DevOps work items automatically for each finding above a severity threshold
- **Remediation tracking**: Closes work items automatically when re-scan confirms the fix
- **Trend reporting**: Shows MTTR (Mean Time to Remediate) per team, per finding type, over time

### 2.5 AI Tool Recommendations for Security

| Priority | Tool | Rationale |
|---|---|---|
| **1 — Use Now** | LTM Custom Security Agent (on top of Fortify) | Fills Fortify's remediation gap; no new tool licensing required |
| **2 — Add** | Snyk Code | Developer-facing, real-time in IDE; catches issues before Fortify scan even runs |
| **3 — Evaluate** | Cycode | Aggregates findings across Fortify + Snyk + other tools into one risk view |
| **4 — Consider** | Endor Labs | If OSS dependency alerts are generating noise — filters to actually reachable vulnerabilities |
| **Avoid for now** | Checkmarx / Veracode | Overlap with Fortify at high cost; replace only if Fortify licensing becomes uneconomical |

### 2.6 Recommendations

1. **Keep Fortify** as the detection engine — it is enterprise-grade and already trusted by the customer.
2. **Deploy LTM Custom Security Agent** immediately as the remediation and prioritization layer on top of Fortify output.
3. **Add Snyk Code** at the developer IDE level for shift-left — catch issues before they ever reach Fortify.
4. **Build a unified security dashboard** that aggregates Fortify + Snyk findings with priority scoring — gives leadership a single pane of glass.
5. **Do not buy another full SAST tool** (Checkmarx, Veracode) — it duplicates Fortify and increases cost without adding the contextual intelligence our agent provides.

---

## 3. Certificate Renewal — Alignment Note

The customer and LTM teams are aligned on the Certificate Renewal automation approach. Key points:

- Automated expiry tracking across all environments (Dev, QA, Prod) — no more spreadsheet-based monitoring
- Event-driven renewal workflows: detect → generate CSR → request/renew → validate → deploy to IIS → bind → verify
- Agent handles both internal (C&M portal) and external (InfoSec team coordination) certificate flows
- Positioned as a fast-value, operations-focused capability that can be delivered as MVP alongside Code Review

---

## 4. Why Custom Agents Over Off-The-Shelf Tools

| Dimension | Off-The-Shelf Tools | LTM Custom Agents |
|---|---|---|
| **Fit to standards** | Generic rules — require extensive configuration | Built around your exact standards from day one |
| **Cost at scale** | Per-seat SaaS — expensive for 50+ developers | API-based — cost scales with usage, not headcount |
| **Workflow integration** | Requires adapting to the tool's workflow | Adapts to your existing Azure DevOps workflow |
| **Customization** | Limited to vendor's configuration options | Fully extensible — add new rules, new use cases |
| **Data privacy** | Code sent to vendor's cloud | Can run on-prem or in customer's Azure tenant |
| **Cross-use-case expansion** | Separate tools for each problem | One agent framework — Code Review + Security + Certificates + more |
| **LTM value lock-in** | Customer buys tool directly from vendor | LTM delivers, maintains, and evolves the agent |

---

## 5. Proposed Next Steps

1. **Demo** — Showcase the Code Review Agent MVP with a live PR from the customer's codebase (C#/.NET repo)
2. **Security Agent PoC** — Run Fortify output through the custom agent and show contextual fix suggestions vs. raw Fortify report
3. **Market Tool Comparison Walkthrough** — Walk the customer through the tool landscape table in a 30-minute session
4. **Expand Scope** — Once Code Review Agent is live, extend to cover all repos in the customer application estate
5. **Holistic Roadmap** — Present a 6-month roadmap: Code Review (Month 1) → Security Agent (Month 2-3) → Certificate Renewal (Month 3-4) → Unified Dashboard (Month 5-6)

---

*Prepared by: LTM AI-Led Engineering Team*
*Contact: Pankaj Pathak | Manjunath Singh Riekwar*

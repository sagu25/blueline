# How BlueLine Agents Are Built
### A Brief Overview of Agent Design & Capabilities

---

## The Core Idea

Every BlueLine agent is essentially **three things combined:**

```
System Prompt          +       Tools          +       Claude (LLM)
(gives it identity         (gives it hands —          (does the
 and rules)                 what it can do)             thinking)
```

The agent knows *who it is* and *what rules it follows* from the system prompt.
It knows *what actions it can take* from the tools.
Claude does the actual reasoning in between.

---

## How Every Agent Is Built — The Base

All 12 agents inherit from a single `BaseAgent` class. This means every agent automatically gets:

- A unique `run_id` for tracking
- A logger
- A connection to the LLM (Claude / Azure OpenAI)
- An `escalate()` method — if confidence is low, it stops and asks a human
- An action log — every external action is recorded before it happens

```
BaseAgent
    │
    ├── ClarionAgent      (Quality Gate)
    ├── LumenAgent        (Quality Gate)
    ├── VectorAgent       (Quality Gate)
    ├── AscentAgent       (Quality Gate)
    ├── WatchtowerAgent   (Security)
    ├── BulwarkAgent      (Security)
    ├── ForgeAgent        (Security)
    ├── StewardAgent      (Security)
    ├── TimelineAgent     (Certificate)
    ├── RegentAgent       (Certificate)
    ├── CourierAgent      (Certificate)
    └── HarbourAgent      (Certificate)
```

Every agent must implement exactly three things:
1. `build_system_prompt()` — its identity and rules
2. `build_tools()` — what actions it can take
3. `execute()` — its main logic

---

## How Agents Get Their Capabilities

There are exactly **two mechanisms** that give an agent its capability:

---

### Mechanism 1 — The System Prompt (gives it knowledge)

The system prompt is a text instruction sent to Claude before every call.
It tells the agent:
- What it is and what its job is
- What rules or standards to apply
- How to format its output
- What it should never do

**Example — CLARION's identity:**
> *"You are CLARION, a coding standards enforcement agent for a .NET and Angular codebase.
> Check the code for naming violations, security issues, and structure problems.
> Only flag violations you are confident about. Always provide a fix."*

**Example — BULWARK's identity:**
> *"You are BULWARK, a security triage agent. Classify each Fortify finding as
> CRITICAL / HIGH / NEEDS_REVIEW / FALSE_POSITIVE. Never classify as false positive
> if uncertain — prefer NEEDS_REVIEW."*

The system prompt is **cached** after the first call (prompt caching). This means
if 30 PRs are reviewed in a day, the coding standards document is only billed once —
subsequent calls only pay for the new code diff. This reduces cost by ~60%.

---

### Mechanism 2 — Tools (gives it hands)

Tools are functions the agent can call during its reasoning.
Without tools, Claude can only produce text.
With tools, it can take real actions.

Each tool has:
- A **name** — what Claude calls it
- A **description** — when to use it
- A **schema** — what parameters it takes

**Example — CLARION's tools:**

| Tool | What it does |
|---|---|
| `fetch_pr_diff` | Fetches the actual code diff from Azure DevOps |
| `post_pr_comment` | Posts an inline comment on a specific line of the PR |

**Example — FORGE's tools:**

| Tool | What it does |
|---|---|
| `get_file_content` | Reads the vulnerable source file |
| `create_branch` | Creates a new git branch |
| `commit_files` | Commits the fixed code to the branch |
| `create_pull_request` | Opens a draft PR with the fix |

**Example — HARBOUR's tools:**

| Tool | What it does |
|---|---|
| `deploy_to_iis` | Runs PowerShell on a remote IIS server via WinRM |
| `deploy_to_app_service` | Calls Azure SDK to bind cert to App Service |
| `verify_https` | Checks HTTPS is working after deployment |

The agent decides **which tools to call and in what order** based on its reasoning —
it is not hardcoded. Claude reads the situation and picks the right tool.

---

## How a Single Agent Run Works — Step by Step

Using CLARION as an example:

```
1. PR opened in Azure DevOps
         │
2. Webhook fires → CLARION receives PR ID
         │
3. CLARION calls Claude with:
   - System prompt  (who it is + .NET/Angular rules)
   - User message   ("review this PR diff: ...")
         │
4. Claude reasons about the diff
   → decides to call tool: fetch_pr_diff
         │
5. fetch_pr_diff runs → returns actual code changes
         │
6. Claude analyses the code against the rules
   → finds 3 violations
   → calls tool: post_pr_comment  (3 times, once per violation)
         │
7. Each comment is posted to the PR with:
   - The exact file and line number
   - What rule was violated
   - Why it matters
   - The corrected code
   - A confidence score
         │
8. CLARION logs all actions to the audit trail
   → returns AgentResult (status, violations, reasoning)
```

Total time: ~20–45 seconds from PR open to comments appearing.

---

## How Agents Talk to Each Other

Agents do not call each other directly. They communicate through **Azure Service Bus** — a message queue. One agent publishes a message, the next agent picks it up.

```
WATCHTOWER finds new Fortify findings
    │
    └── publishes to Service Bus topic: "security.findings.new"
                │
                ▼
        BULWARK picks up the message
        → triages each finding
        → CRITICAL findings published to: "security.critical.fix-needed"
                │
                ▼
        FORGE picks up the message
        → generates fix
        → creates draft PR
                │
                ▼
        STEWARD picks up ALL messages
        → writes immutable audit log entry
```

This design means:
- Agents are **independent** — if FORGE is slow, BULWARK is not affected
- Agents are **replaceable** — swap out FORGE without touching BULWARK
- Every message is **persisted** — if an agent crashes, the message is not lost

---

## How the Quality Gate Runs All Agents in Parallel

The Quality Gate uses **Azure Durable Functions** to run CLARION, LUMEN, and VECTOR
at the same time — then waits for all three before ASCENT posts the summary.

```
PR arrives
    │
    ├── CLARION starts ──┐
    ├── LUMEN starts     ├── all three run at the same time (~30–45 seconds)
    └── VECTOR starts ───┘
                │
                ▼  (all three done)
             ASCENT
         aggregates results
         posts one consolidated
         comment to the PR
```

Without parallelism this would take 3× longer. With it, the total time
is determined by the slowest of the three — not the sum of all three.

---

## How Agents Stay Safe — The Guardrails

Four mechanisms prevent agents from doing the wrong thing:

**1. Confidence threshold**
Every agent output includes a confidence score (0.0–1.0).
If confidence is below 0.7, the agent does not act — it escalates to a human.

**2. Shadow mode**
Before going live, all agents run in shadow mode — they reason and generate
output but take no real actions. Output is logged for human review.
This is how the team validates accuracy before agents touch real systems.

**3. Human approval gates**
- No code is ever merged without a human approving the PR
- No certificate is deployed to Production without a human clicking approve in Teams
- FORGE only creates *draft* PRs — they cannot be merged automatically

**4. The escalate() method**
Every agent has a built-in escape hatch. If it encounters something unexpected
or uncertain, it stops, logs the reason, and sends a notification to a human.
It never guesses when unsure.

---

## Summary — One Line Per Agent

| Agent | Capability given by system prompt | Capability given by tools |
|---|---|---|
| CLARION | Knows .NET + Angular coding rules | Can fetch PR diff, post inline comments |
| LUMEN | Knows code smell patterns | Can fetch PR diff, post smell annotations |
| VECTOR | Knows risk scoring formula | Can query git history, read file complexity |
| ASCENT | Knows how to aggregate and prioritise | Can post PR summary, read ADO reactions |
| WATCHTOWER | Knows Fortify API structure | Can list projects, fetch new findings |
| BULWARK | Knows OWASP Top 10, triage logic | Can suppress Fortify issues, publish to Service Bus |
| FORGE | Knows secure coding patterns per vulnerability class | Can read files, create branches, commit code, open PRs |
| STEWARD | Knows audit log schema | Can write to immutable blob storage |
| TIMELINE | Knows cert expiry urgency thresholds | Can query Azure Key Vault cert metadata |
| REGENT | Knows cert inventory structure | Can read/write Azure Table Storage inventory |
| COURIER | Knows CA API patterns (DigiCert, internal PKI) | Can call CA API to request and download certs |
| HARBOUR | Knows deployment sequence and verification steps | Can deploy to IIS via WinRM, App Service via Azure SDK, verify HTTPS |

---

*Project BlueLine — Agent Architecture Overview v1.0*

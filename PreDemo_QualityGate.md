# Pre-Demo Reading — Quality Gate
**Read this 10 minutes before your demo. Everything below is based on the actual agent code.**

---

## What It Does in One Line

Every time a developer opens or updates a Pull Request in Azure DevOps, four AI agents automatically review the code and post a verdict — BLOCK, REQUEST CHANGES, or APPROVE — within 45 seconds.

---

## The Four Agents — What Each One Does and How It Decides

---

### Agent 1 — CLARION (Coding Standards Checker)

**Job:** Read the code and check it against the team's DAS/CDAS coding standards.

**How it decides:**
CLARION is given the full list of your team's coding rules as its instructions. It reads the code and looks for violations. Every finding it produces has:
- A **severity** — error, warning, or info
- A **rule** — the specific standard that was broken
- A **line number** — exactly where in the file
- A **fix** — the corrected code to use instead
- A **confidence score** — CLARION only reports findings it is at least 70% confident about

**The rules CLARION enforces — C# / .NET:**

| Category | Key Rules |
|---|---|
| Naming | PascalCase for classes/methods, camelCase for variables, `I` prefix for interfaces, `Async` suffix on async methods |
| Async (CRITICAL) | Never `.Result` or `.Wait()` — causes deadlocks. Never `async void`. Always pass `CancellationToken`. Use `ConfigureAwait(false)` in library code |
| HttpClient (CRITICAL) | Never `new HttpClient()` inside a method — socket exhaustion. Use `IHttpClientFactory` instead |
| Secrets (CRITICAL) | Never hardcode connection strings, API keys, passwords, GUIDs. Must come from Azure Key Vault |
| SQL (CRITICAL) | Never concatenate strings into SQL queries — SQL injection risk. Always use parameterised queries |
| Exceptions | Never return `ex.Message` to API callers — information disclosure. Never empty catch blocks |
| Input Validation | Never accept `JObject` without converting to typed model. Always check `ModelState.IsValid` |
| File Uploads | Always validate file size and extension before reading |
| DI | Never `new ClassName()` inside controllers — use constructor injection |
| EF | Use `.AsNoTracking()` on read-only queries. No queries inside loops |
| Logging | Use `ILogger<T>` only. Structured templates. Never log passwords or tokens |
| CORS | No wildcard origin with credentials |

**The rules CLARION enforces — Angular / TypeScript:**

| Rule | Why |
|---|---|
| Never use `any` type | Bypasses TypeScript's safety — bugs hide at runtime |
| Never bind to `innerHTML` directly | XSS vulnerability — attacker injects scripts |
| Always unsubscribe from Observables | Memory leak — component keeps running after it is destroyed |
| No direct DOM manipulation | Use Angular template bindings instead |
| Prefer `OnPush` change detection | Performance — component only re-renders when inputs change |

**What to say in the demo:**
> "CLARION is given the team's actual coding rulebook as its instructions — not a generic set of rules, your specific DAS/CDAS standards. It only flags violations it is confident about. Every finding includes the exact line, what is wrong, and the corrected code."

---

### Agent 2 — LUMEN (Code Smell Detector)

**Job:** Find code quality and maintainability problems — things that are not hard rule violations but will cause real problems as the codebase grows.

**How it decides:**
LUMEN reads the code looking for patterns that experienced engineers would flag in a review. It names the exact method or class where the smell is, explains why it is a problem, and suggests how to refactor it.

**What LUMEN looks for:**

| Smell | Threshold | Why It Matters |
|---|---|---|
| Long Method | Over ~40 lines | Hard to understand, hard to test, easy to break |
| Large Class | Over ~300 lines | Too many responsibilities — violates Single Responsibility |
| Deep Nesting | More than 3 levels of `if`/`for`/`while` | Impossible to read, hard to debug |
| Magic Numbers | Unexplained numeric literals | Nobody knows what `999999` means in 6 months |
| Duplicate Code | Same logic in multiple places | Change in one place, forget the other — bugs |
| Dead Code | Unused variables, unreachable blocks | Confuses future readers, adds noise |
| Long Parameter List | More than 4–5 parameters | Method is doing too much |
| DbContext as Instance Field | `private AppDbContext _db = new AppDbContext()` | Causes stale data and threading issues — must be scoped per request |
| TransactionScope without AsyncFlowOption | Transaction silently lost across `await` | Data corruption — transaction doesn't roll back correctly |
| N+1 Query | Query inside a `foreach` loop | 100 records = 100 database round trips |

**What to say in the demo:**
> "LUMEN finds the things that pass a linting check but will cause problems in 3 months. Things like a 70-line method that should be split, or a DbContext held as an instance field that will cause data corruption under load."

---

### Agent 3 — VECTOR (Risk Scorer)

**Job:** Calculate a risk score for the code and tell the human reviewer exactly where to focus their attention.

**How it decides:**
VECTOR runs in two stages:

**Stage 1 — Static analysis (no AI, instant, deterministic):**
Python code scans the file and counts:
- Cyclomatic complexity (number of decision branches — `if`, `for`, `while`, `&&`, `||`)
- Maximum nesting depth
- Method count
- Dependency/import count
- Security-sensitive patterns (SQL, HTTP calls, auth, crypto, file operations)
- Blocking async calls (`.Result`, `.Wait()`)
- High-risk patterns (`new HttpClient()`, file upload without validation, wildcard CORS)
- Empty catch blocks
- Whether any test indicators exist (`Assert`, `expect`, `Mock`, `[Test]`, `describe`)

**Stage 2 — AI analysis:**
VECTOR gives Claude the static metrics plus the actual code and asks it to:
- Produce a risk score between 0.0 and 1.0
- Identify the specific hotspots (which methods are most dangerous)
- Write a reviewer note telling the human exactly what to check

**Risk levels:**

| Score | Level | Meaning |
|---|---|---|
| 0.0 – 0.3 | LOW | Safe to review quickly |
| 0.3 – 0.6 | MEDIUM | Needs careful review |
| 0.6 – 0.8 | HIGH | Reviewer must pay close attention |
| 0.8 – 1.0 | CRITICAL | Must not be approved without thorough review |

**What to say in the demo:**
> "VECTOR scores the risk before the AI even reads the code — it counts branches, measures complexity, detects SQL patterns. Then the AI reads the actual code on top of that. You cannot write bad code in a clever way to fool it."

---

### Agent 4 — ASCENT (Aggregator and Final Verdict)

**Job:** Read the reports from CLARION, LUMEN, and VECTOR and produce one consolidated PR review comment with a clear recommendation.

**How it decides:**

| Condition | Recommendation |
|---|---|
| Any `error`-severity CLARION violation | REQUEST CHANGES or BLOCK |
| Any security violation confirmed | BLOCK |
| Only warnings and minor smells | REQUEST CHANGES |
| Minor issues only, no blockers | APPROVE |

**What ASCENT produces:**
- Overall score out of 10 (1 = worst, 10 = best)
- Three tiers of findings:
  - **Tier 1 — Must Fix Before Merge:** Errors, security issues, CRITICAL risk findings
  - **Tier 2 — Should Fix:** Warnings, major smells, HIGH risk areas
  - **Tier 3 — Consider Fixing:** Info-level, minor smells, MEDIUM risk
- A reviewer checklist — specific things the human must manually verify
- A biggest risk statement — the single most important concern in one sentence

**What to say in the demo:**
> "ASCENT reads all three reports and synthesises them into one verdict. The human reviewer does not have to read three separate reports — they get one comment, one score, one recommendation, and a checklist of what to verify themselves."

---

## The Full Flow

```
Developer opens PR in Azure DevOps
         │
         ▼
Webhook fires → BlueLine receives PR ID and diff
         │
         ├── CLARION runs → checks every .cs and .ts file against DAS/CDAS standards
         ├── LUMEN runs   → detects smells and structural problems
         └── VECTOR runs  → scores complexity and identifies hotspots
                  │
                  ▼ (all three complete)
               ASCENT
          reads all three outputs
          produces one score + recommendation
          posts summary comment to the PR in Azure DevOps
                  │
                  ▼
         Human reviewer reads the findings
         Fixes the Must Fix items
         Applies their own judgement on design and business logic
         Approves or rejects the PR
         (Agents cannot merge — ever)
```

---

## Where the Human Comes In

- **Developer:** Receives findings on their PR. Fixes the violations. Pushes again — BlueLine re-reviews automatically.
- **Reviewer:** Reads the ASCENT summary. Focuses on logic and design rather than mechanical checks. Clicks Approve or Request Changes in Azure DevOps.
- **Override:** If the reviewer disagrees with a finding, they can still approve. BlueLine's recommendation is advisory — the human has the final say.

---

## Key Numbers to Remember

| Metric | Value |
|---|---|
| Time from PR open to verdict | ~45 seconds |
| Minimum confidence to flag a violation | 70% |
| Score range | 1 (worst) to 10 (best) |
| PR #13 score in the demo | 2/10 — BLOCK |
| Must Fix findings in PR #13 | 5 |
| Should Fix findings in PR #13 | 5 |

---

## If They Ask Difficult Questions

**"Can it be wrong?"**
> "Yes — it can produce false positives, especially on complex patterns. That is why the human reviewer still approves the merge. If a finding is wrong, the reviewer overrides it. Over time we track false positive rates — if CLARION flags something that is wrong more than 20% of the time, we tune the rule."

**"What if a developer disagrees with a finding?"**
> "They discuss it in the PR comment thread, exactly as they would with a human reviewer. They can also mark it as a false positive and the reviewer decides."

**"Does it replace the human reviewer?"**
> "No. It handles the mechanical checks — standards, smells, complexity. The human reviewer handles logic, design, architecture, business correctness. Things the AI genuinely cannot assess. The reviewer's time goes from 30 minutes of mechanical checking to 5 minutes of focused judgment."

---

*Project BlueLine — LTM AI-Led Engineering Team · Quality Gate Pre-Demo Brief*

# Project BlueLine — Live Demo Walkthrough
**Document Type:** Customer Explanation Guide
**Date:** May 2026
**PR Reviewed:** PR #13 — "Added 4 files to / ADD inventory and user management features"
**Branch:** feature/blueline-demo → main

---

## What This Document Covers

This document walks through what happened when Project BlueLine reviewed a real Pull Request from the Azure DevOps repository. Every finding shown is real — the agents read the actual code submitted in the PR and produced these results automatically, with no human involvement.

---

## Screen 1 — The Overall Verdict

**What the screen shows:**
BlueLine connected to Azure DevOps, picked up PR #13, ran all four AI agents across the changed files, and delivered its verdict in under 45 seconds.

**The result:**

| Field | Value |
|---|---|
| ASCENT Recommendation | **BLOCK** |
| Overall Code Quality Score | **2 / 10** |

**What this means for the customer:**

The AI determined this Pull Request **must not be merged** in its current state. A score of 2/10 means the code has critical problems — not minor style issues, but genuine security vulnerabilities and patterns that will cause production failures.

**Why this matters:**
Without BlueLine, this PR would go into a human reviewer's queue. Depending on the reviewer's experience and how busy they are that day, these issues may or may not get caught. BlueLine catches them every single time, on every PR, in under a minute — before any reviewer has even opened the file.

---

## Screen 2 & 3 — Must Fix Before Merge (5 Issues)

These are the issues ASCENT classified as **blockers** — the PR cannot be safely merged until every one of these is resolved.

---

### Issue 1 — Hardcoded Connection String
**Agent:** CLARION
**Severity:** ERROR

**What was found:**
The developer typed a database connection string (including the server address, database name, username and password) directly into the source code file.

**Why it is a blocker:**
That source code is stored in Azure DevOps, which means the database credentials are now visible to every developer who has access to the repository. If the repository is ever accidentally made public, or if any developer's machine is compromised, the attacker has direct database access.

**What needs to happen:**
The connection string must be moved to Azure Key Vault and referenced by name from code — not stored in the file itself.

---

### Issue 2 — DbContext Held as Instance Field
**Agent:** CLARION
**Severity:** ERROR

**What was found:**
The database context object (`AppDbContext`) is being stored as a permanent field on the class, rather than being injected fresh per request.

**Why it is a blocker:**
In a web application handling multiple users simultaneously, this causes one user's database session to bleed into another user's request. This leads to data corruption, stale reads, and hard-to-reproduce bugs in production under load.

**What needs to happen:**
Inject `AppDbContext` through the class constructor so the framework creates a fresh instance per request and disposes it correctly.

---

### Issue 3 — Blocking Async Call (.Result)
**Agent:** CLARION + VECTOR (both flagged this)
**Severity:** ERROR / CRITICAL

**What was found:**
The `GetServiceToken` method uses `.Result` to wait for an async operation instead of using `await`.

**Why it is a blocker:**
This is a known cause of **deadlocks** in ASP.NET applications. Under certain conditions, the thread that called `.Result` holds a lock waiting for the async task to finish, while the async task is waiting for that same thread to be free. The application freezes. This typically only shows up in production under real load — it passes all local testing.

**What needs to happen:**
Change `GetServiceToken` to be an `async` method that returns `Task<string>` and use `await` properly throughout the call chain.

---

### Issue 4 — SQL Injection Vulnerability
**Agent:** VECTOR
**Severity:** ERROR

**What was found:**
The `SearchStock` method builds a SQL query by concatenating user input directly into the query string:
```
string query = "SELECT * FROM Orders WHERE CustomerId = '" + customerId + "'";
```

**Why it is a blocker:**
This is one of the most well-known and dangerous security vulnerabilities in software — OWASP A03:2021 (Injection). An attacker who can control the `customerId` input can break out of the query and run arbitrary SQL commands against the database. They can read all data, delete records, or in some configurations execute commands on the server.

**What needs to happen:**
Replace string concatenation with parameterized queries:
```csharp
string query = "SELECT * FROM Orders WHERE CustomerId = @customerId";
cmd.Parameters.AddWithValue("@customerId", customerId);
```

---

## Screen 4 — Should Fix (5 Issues)

These are serious issues that do not block the merge on their own but should be fixed in this PR or the next one. Left unaddressed, they accumulate into technical debt and production risk.

| # | Agent | Issue | Impact |
|---|---|---|---|
| 1 | CLARION | Direct binding to innerHTML without sanitization | XSS vulnerability — attacker can inject scripts into the browser |
| 2 | LUMEN | AppDbContext held as instance field | Same as Issue 2 above — data integrity risk |
| 3 | LUMEN | TransactionScope used in async method without AsyncFlowOption | Transactions silently do not roll back correctly in async code |
| 4 | VECTOR | CallWarehouseApi creates `new HttpClient()` inside a method | Socket exhaustion — under load, the application runs out of network connections |
| 5 | VECTOR | ImportStockFromFile lacks file size and type validation | A user can upload a very large file and crash the server (Denial of Service) |

---

## Consider Fixing (3 Issues)

Lower priority — informational findings the team should be aware of.

| # | Agent | Issue |
|---|---|---|
| 1 | CLARION | Magic number `999999` used without explanation — should be a named constant |
| 2 | LUMEN | Raw exception message returned to the API caller — leaks internal system details |
| 3 | VECTOR | GetAllUsers method makes a blocking database call from a synchronous controller action |

---

## Screen 5 — Security Loop: SQL Injection Confirmed

This screen shows the **Security Loop** running on the same SQL injection finding.

**What happened:**
1. **WATCHTOWER** received the finding description (in production this comes directly from Fortify SSC)
2. **BULWARK** analysed it and classified it as **CRITICAL** with **100% confidence**
3. BULWARK identified the OWASP category as **A03:2021 — Injection**
4. BULWARK described the attack scenario: *"An attacker could execute arbitrary SQL commands, potentially gaining unauthorised access to sensitive data or manipulating the database"*
5. BULWARK generated the **secure code fix** showing exactly how to rewrite the vulnerable method using parameterised queries
6. **FORGE** (next step) would create a draft Pull Request with this fix ready for a developer to review and approve

**Why this is significant:**
Normally, a Fortify finding goes into a backlog. A developer has to read the finding, understand the vulnerability, research the correct fix, write the code, and submit a PR. This takes hours to days per finding. BlueLine's Security Loop does the research and writes the fix automatically — the developer just reviews and approves.

---

## Summary — What BlueLine Did on This PR

| What happened | Time taken |
|---|---|
| PR opened in Azure DevOps | T=0 |
| BlueLine webhook triggered automatically | T=0 |
| All four agents ran across all changed files | ~45 seconds |
| ASCENT posted BLOCK recommendation with full findings | T=45s |
| Human reviewer received structured, prioritised findings | T=45s |

**Without BlueLine:**
- Reviewer opens the PR manually (minutes to hours later)
- Reviewer may or may not catch the SQL injection depending on experience
- Reviewer may or may not catch the async deadlock — this one is subtle
- Hardcoded credentials may be missed entirely — they do not look dangerous at a glance

**With BlueLine:**
- Every issue surfaced within 45 seconds, every time, on every PR
- Reviewer's time is spent on logic, design, and business correctness — not mechanical checks
- Security vulnerabilities are caught before merge, not after deployment

---

## Is the Output Correct?

Yes. Every finding shown is a genuine, real problem in the submitted code:

- The hardcoded connection string is a real credential exposure risk
- The `.Result` pattern genuinely causes deadlocks in ASP.NET under load
- The SQL concatenation is a textbook SQL injection vulnerability
- The `new HttpClient()` pattern genuinely causes socket exhaustion in production
- The missing file validation genuinely enables a DoS attack

These are not false positives. They are real issues in real code, caught automatically.

---

*Project BlueLine — LTM AI-Led Engineering Team · May 2026*

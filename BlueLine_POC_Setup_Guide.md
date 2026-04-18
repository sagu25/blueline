# Project BlueLine POC — Setup Guide

**Version:** 1.2
**Date:** 2026-04-18
**Time to set up:** ~15 minutes

---

## What You Need Before Starting

| Requirement | Where to get it |
|---|---|
| Windows laptop with internet access | You have this |
| Python 3.9 or later | Already installed — confirmed Python 3.11.9 |
| Azure OpenAI access | Ask your Azure admin (see Section 2) |
| Azure DevOps PAT | Generate yourself — 2 minutes (see Section 3) |
| The `poc` folder from the BlueLine project | Clone from `https://github.com/sagu25/blueline.git` |

---

## Section 1 — Folder Structure

After setup, your project should look like this:

```
blueline/
│
├── docs/
│   └── das_review_standards.md     ← DAS/CDAS rule reference (agents use this)
│
├── poc/
│   ├── app.py                      ← Main application (do not edit)
│   ├── requirements.txt            ← Python dependencies
│   ├── .env                        ← YOUR credentials (you create this — never share)
│   ├── .env.example                ← Template (copy this to create .env)
│   ├── run.bat                     ← Double-click to start the app
│   │
│   ├── agents/
│   │   ├── clarion.py              ← Quality Gate: DAS-aligned coding standards
│   │   ├── lumen.py                ← Quality Gate: code smell detector
│   │   ├── vector.py               ← Quality Gate: risk scorer and hotspot analyser
│   │   ├── ascent.py               ← Quality Gate: aggregator and final recommendation
│   │   ├── bulwark.py              ← Security: vulnerability triage agent
│   │   └── timeline.py             ← Certificate: expiry analysis agent
│   │
│   ├── utils/
│   │   ├── llm_client.py           ← AI provider connector (Azure OpenAI)
│   │   ├── azure_devops.py         ← Azure DevOps REST API client
│   │   └── pr_runner.py            ← PR orchestrator — runs agents on real PRs
│   │
│   └── samples/
│       ├── bad_csharp.cs           ← Sample C# with violations (manual demo)
│       ├── bad_typescript.ts       ← Sample Angular with violations (manual demo)
│       ├── fortify_finding.txt     ← Sample Fortify finding (security demo)
│       └── ado_test_files/         ← 4 realistic files to push as a demo PR
│           ├── InventoryService.cs         (BLOCK — critical violations)
│           ├── UserController.cs           (REQUEST_CHANGES — medium violations)
│           ├── stock-upload.component.ts   (BLOCK — Angular security violations)
│           ├── order-list.component.ts     (APPROVE — mostly clean)
│           └── HOW_TO_USE.md              (instructions for demo PR)
```

---

## Section 2 — Getting Azure OpenAI Credentials

> **Recommended for company laptops.**
> All AI calls stay within your company's Azure subscription.

### Ask your Azure Admin for:

1. **Azure OpenAI Endpoint URL**
   - Looks like: `https://YOUR-RESOURCE-NAME.openai.azure.com/`
   - Found in: Azure Portal → Your OpenAI resource → Keys and Endpoint

2. **API Key**
   - Either Key 1 or Key 2 from the same page

3. **Deployment Name**
   - The name of the deployed model (usually `gpt-4o`)
   - Found in: Azure OpenAI Studio → Deployments

---

## Section 3 — Getting Azure DevOps Credentials

> Required for the **Live PR Review** tab (Tab 4).
> Allows BlueLine to fetch real PR diffs and post findings as PR comments.

### Step 1 — Find your Org URL, Project, and Repo

Open Azure DevOps in your browser. Your values are in the URL:

```
https://dev.azure.com/your-org/YourProject/_git/YourRepo
                     ^^^^^^^^  ^^^^^^^^^^^       ^^^^^^^^
                     ORG_URL   PROJECT           REPO
```

### Step 2 — Generate a Personal Access Token (PAT)

1. In Azure DevOps — click your **profile picture** (top right)
2. Click **"Personal access tokens"**
3. Click **"+ New Token"**
4. Fill in:
   - **Name:** `BlueLine`
   - **Expiry:** 90 days
   - **Scopes:** tick exactly these two:
     - ✅ **Code** → Read
     - ✅ **Pull Request Threads** → Read & Write
5. Click **Create**
6. **Copy the token immediately** — it is shown only once

---

## Section 4 — One-Time Setup Steps

### Step 1 — Clone the repository (if not already done)

```bat
git clone https://github.com/sagu25/blueline.git
cd blueline
```

### Step 2 — Open a Command Prompt in the poc folder

- Open File Explorer → navigate to `blueline\poc`
- Click the address bar, type `cmd`, press Enter

### Step 3 — Install Python dependencies

```bat
pip install -r requirements.txt
```

Expected output: packages installing, no red error lines.

> If you see `ERROR: Could not install packages` — run Command Prompt as Administrator.

### Step 4 — Create your `.env` file

Copy the template:

```bat
copy .env.example .env
```

Open in Notepad:

```bat
notepad .env
```

Fill in all credentials:

```
# Azure OpenAI — required for all AI agents
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE-NAME.openai.azure.com/
AZURE_OPENAI_API_KEY=your-actual-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Azure DevOps — required for Live PR Review tab
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/your-org-name
AZURE_DEVOPS_PAT=your-personal-access-token-here
AZURE_DEVOPS_PROJECT=YourProjectName
AZURE_DEVOPS_REPO=YourRepoName
```

Save and close Notepad.

> **Important:** Never commit or share the `.env` file. It is in `.gitignore` and will not be pushed to GitHub.

---

## Section 5 — Running the App

### Option A — Double-click (easiest)

Double-click `run.bat` in the `poc` folder.

### Option B — Command line

```bat
cd blueline\poc
streamlit run app.py
```

### Open in browser

Go to: **http://localhost:8501**

### To stop the app

Press `Ctrl + C` in the command prompt window.

---

## Section 6 — Using the App

### Sidebar — Connection Status

When the app opens, check the **left sidebar**. You should see:

```
🟢 Connected: Azure OpenAI
🟢 ADO Connected — Live PR Review enabled
```

- If Azure OpenAI shows 🔴 — check your 4 OpenAI lines in `.env`
- If ADO shows 🟡 — check your 4 Azure DevOps lines in `.env`

You can also enter credentials directly in the sidebar without editing `.env`.

---

### Tab 1 — Quality Gate (Manual — paste code)

Runs all four agents on code you paste manually. Good for quick demos without needing a real PR.

| Agent | What it does |
|---|---|
| CLARION | Checks DAS/CDAS coding standards — async patterns, HttpClient, DI, secrets, CORS, logging |
| LUMEN | Detects code smells — DbContext lifetime, N+1 queries, TransactionScope, deep nesting |
| VECTOR | Scores risk — detects blocking async calls, file upload risks, empty catch blocks |
| ASCENT | Aggregates all three into one verdict: APPROVE / REQUEST_CHANGES / BLOCK |

**Demo steps:**

1. Select language: **csharp**
2. Click **"📂 Load Sample Code"** — loads a C# file with deliberate DAS violations
3. Click **"🔍 Run Full Review"**
4. Watch each agent run (30–60 seconds total)
5. Review: ASCENT verdict → Tier 1 Must Fix → Tier 2 Should Fix → Tier 3 Consider
6. Complete the **Human Review Gate** — mark findings as Agree or False Positive

**Strongest demo contrast:**

- Load `ado_test_files/InventoryService.cs` → expect **BLOCK**
- Load `ado_test_files/order-list.component.ts` → expect **APPROVE**

This shows the agents are calibrated — not just flagging everything.

---

### Tab 2 — Security Loop (BULWARK)

Triages a Fortify finding or any vulnerability description.

**Demo steps:**

1. Click **"📂 Load Sample Finding"** — loads a SQL injection finding
2. Click **"🔒 Run Triage"**
3. Results show: classification (CRITICAL/HIGH/NEEDS_REVIEW/FALSE_POSITIVE), attack scenario, and a secure code fix

**To test with a real Fortify finding:**

1. Copy any finding description from Fortify SSC
2. Paste into the finding box
3. Optionally paste the vulnerable code for a more precise fix
4. Click Run Triage

---

### Tab 3 — Certificate Loop (TIMELINE)

Analyses a certificate and produces a renewal action plan.

**Demo steps:**

1. Click **"📂 Load Sample Certificate"** — pre-fills a certificate expiring soon
2. Click **"📜 Analyse Certificate"**
3. Results show: urgency level, days until expiry, renewal path, step-by-step action plan

**To test with a real certificate:**

1. Fill in the Subject/Domain
2. Enter the expiry date (YYYY-MM-DD format)
3. Select the CA type
4. Click Analyse Certificate

---

### Tab 4 — Live PR Review (Azure DevOps)

**This is the full integration.** BlueLine connects to your real Azure DevOps repo,
fetches changed files from a real PR, runs all 4 agents, and posts findings back
as inline comments directly on the PR.

**Before using this tab:** ADO must show 🟢 in the sidebar.

**Demo steps:**

**Step 1 — Prepare a demo PR in Azure DevOps**

Push the 4 test files from `poc/samples/ado_test_files/` as a PR:

```bat
git checkout -b feature/blueline-demo-review
```

Copy the files to your repo structure and push:

```bat
git add .
git commit -m "Add inventory and user management features"
git push origin feature/blueline-demo-review
```

Open a Pull Request in Azure DevOps. Note the PR ID from the URL.

**Step 2 — Run the review**

1. Go to Tab 4 — Live PR Review
2. Keep **Shadow Mode ON** (read only — nothing posted to ADO yet)
3. Click **"🔄 Refresh PRs"** — your demo PR appears in the dropdown
4. Select the PR
5. Click **"🔍 Run Quality Gate on this PR"**
6. Watch the live log as agents fetch and review each file (~60–90 seconds for 4 files)

**Step 3 — Review results**

Results appear on screen:
- ASCENT verdict with overall score
- Tier 1 Must Fix / Tier 2 Should Fix / Tier 3 Consider
- Per-file breakdown (InventoryService.cs, UserController.cs, etc.)
- Preview of what the PR comment will look like

**Step 4 — Post real comments (when ready)**

1. Toggle **Shadow Mode OFF**
2. Click Run again
3. BlueLine posts inline comments directly on the PR in Azure DevOps
4. Open the PR in Azure DevOps — findings appear as reviewer comments on each file

---

## Section 7 — Troubleshooting

### "🔴 Not configured" (Azure OpenAI)

**Fix:** Check your `.env` has all 4 Azure OpenAI lines filled in. Restart the app.

---

### "🟡 ADO not configured"

**Fix:** Check your `.env` has all 4 Azure DevOps lines:
```
AZURE_DEVOPS_ORG_URL
AZURE_DEVOPS_PAT
AZURE_DEVOPS_PROJECT
AZURE_DEVOPS_REPO
```

---

### "Could not connect to Azure DevOps" in Tab 4

**Causes and fixes:**
- PAT expired → generate a new one (Section 3)
- PAT missing scopes → ensure Code (Read) + Pull Request Threads (Read & Write)
- Wrong project or repo name → check spelling matches exactly what's in your ADO URL
- VPN required → connect to company VPN and retry

---

### No PRs showing in dropdown

**Cause:** No active PRs in the configured repo.
**Fix:** Push a branch and open a PR first. Click Refresh PRs after.

---

### App opens but clicking Run shows spinner forever

**Cause:** Network issue — Azure OpenAI endpoint not reachable.
**Fix:**
- Check company VPN is connected
- Verify endpoint URL ends with `/`

---

### `pip install` fails with "access denied"

**Fix:** Right-click Command Prompt → Run as Administrator, then retry.

---

### "JSONDecodeError" in results

**Cause:** AI returned unexpected format.
**Fix:** Click Run again — it will work on retry.

---

### Port 8501 already in use

```bat
streamlit run app.py --server.port 8502
```
Then open `http://localhost:8502`

---

## Section 8 — What This POC Does and Does Not Do

| Capability | This POC |
|---|---|
| Review code pasted manually | ✅ Yes — Tab 1 |
| Connect to real Azure DevOps PRs | ✅ Yes — Tab 4 |
| Fetch real PR diffs automatically | ✅ Yes — Tab 4 |
| Post inline comments on real PRs | ✅ Yes — Tab 4 (shadow mode OFF) |
| Triage Fortify findings | ✅ Yes — Tab 2 |
| Analyse certificate expiry | ✅ Yes — Tab 3 |
| Auto-trigger on PR open (webhook) | ❌ Phase 3 — needs Azure hosting |
| Connect to Fortify SSC API | ❌ Phase 3 — needs Fortify credentials |
| Connect to Azure Key Vault (certs) | ❌ Phase 3 — needs Key Vault access |
| Deploy certificates to IIS | ❌ Phase 3 — HARBOUR agent |
| Auto-generate fix PRs (FORGE) | ❌ Phase 3 — FORGE agent |

---

## Section 9 — Quick Reference

| Action | Command / Location |
|---|---|
| Start the app | Double-click `run.bat` OR `streamlit run app.py` |
| Open in browser | http://localhost:8501 |
| Stop the app | Ctrl + C in the command window |
| Edit credentials | `poc\.env` in Notepad |
| Sample C# (manual demo) | `poc\samples\bad_csharp.cs` |
| Sample Angular (manual demo) | `poc\samples\bad_typescript.ts` |
| Sample Fortify finding | `poc\samples\fortify_finding.txt` |
| Demo PR test files | `poc\samples\ado_test_files\` |
| DAS rule reference | `docs\das_review_standards.md` |
| GitHub repo | https://github.com/sagu25/blueline.git |

---

*End of Setup Guide — Project BlueLine POC v1.2*

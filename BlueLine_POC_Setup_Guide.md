# Project BlueLine POC — Setup Guide

**Version:** 1.1  
**Date:** 2026-04-17  
**Time to set up:** ~10 minutes

---

## What You Need Before Starting

| Requirement | Where to get it |
|---|---|
| Windows laptop with internet access | You have this |
| Python 3.9 or later | Already installed — confirmed Python 3.11.9 |
| Azure OpenAI access | Ask your Azure admin (see Section 2) |
| The `poc` folder from the BlueLine project | `C:\Users\Admin\Desktop\blu\poc\` |

---

## Section 1 — Folder Structure

After setup, your `poc` folder should look like this:

```
poc/
├── app.py                  ← Main application (do not edit)
├── requirements.txt        ← Python dependencies
├── .env                    ← YOUR credentials (you create this — never share it)
├── .env.example            ← Template (copy this to create .env)
├── run.bat                 ← Double-click to start the app
│
├── agents/
│   ├── clarion.py          ← Quality Gate: coding standards agent
│   ├── lumen.py            ← Quality Gate: code smell detector
│   ├── vector.py           ← Quality Gate: risk scorer and hotspot analyser
│   ├── ascent.py           ← Quality Gate: aggregator and final recommendation
│   ├── bulwark.py          ← Security: vulnerability triage agent
│   └── timeline.py         ← Certificate: expiry analysis agent
│
├── utils/
│   └── llm_client.py       ← AI provider connector (Azure OpenAI / Anthropic)
│
└── samples/
    ├── bad_csharp.cs        ← Sample C# code with violations (for demo)
    ├── bad_typescript.ts    ← Sample Angular code with violations (for demo)
    └── fortify_finding.txt  ← Sample Fortify finding (for demo)
```

---

## Section 2 — Getting Azure OpenAI Credentials

> **This is the recommended option for company laptops.**  
> All AI calls stay within your company's Azure subscription.

### Ask your Azure Admin for:

1. **Azure OpenAI Endpoint URL**
   - Looks like: `https://YOUR-RESOURCE-NAME.openai.azure.com/`
   - Found in: Azure Portal → Your OpenAI resource → Keys and Endpoint

2. **API Key**
   - Either Key 1 or Key 2 from the same page
   - Looks like: `abc123def456...` (32+ characters)

3. **Deployment Name**
   - The name of the deployed model (usually `gpt-4o` or `gpt-4`)
   - Found in: Azure OpenAI Studio → Deployments

---

## Section 3 — One-Time Setup Steps

### Step 1 — Open a Command Prompt in the poc folder

- Open File Explorer
- Navigate to `C:\Users\Admin\Desktop\blu\poc`
- Click the address bar, type `cmd`, press Enter

### Step 2 — Install Python dependencies

```bat
pip install -r requirements.txt
```

Expected output: packages installing, no red error lines.

> If you see a warning about `grpcio-status` — that is fine, ignore it.  
> If you see `ERROR: Could not install packages` — run as Administrator.

### Step 3 — Create your `.env` file

In the `poc` folder, copy `.env.example` to `.env`:

```bat
copy .env.example .env
```

Then open `.env` in Notepad:

```bat
notepad .env
```

Fill in your Azure OpenAI credentials:

```
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE-NAME.openai.azure.com/
AZURE_OPENAI_API_KEY=your-actual-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

Save and close Notepad.

> **Important:** Never commit or share the `.env` file. It contains your API key.

---

## Section 4 — Running the App

### Option A — Double-click (easiest)

Double-click `run.bat` in the `poc` folder.

A command prompt window will open and after a few seconds you will see:

```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

### Option B — Command line

```bat
cd C:\Users\Admin\Desktop\blu\poc
streamlit run app.py
```

### Open in browser

Go to: **http://localhost:8501**

The app will open automatically in your default browser.

### To stop the app

Press `Ctrl + C` in the command prompt window.

---

## Section 5 — Using the App

### Sidebar — AI Provider Setup

When the app opens, look at the **left sidebar**:

1. Select **"Azure OpenAI (Company)"** — recommended
2. The endpoint, key, and deployment name from your `.env` file will be pre-filled
3. You should see **"🟢 Connected: Azure OpenAI"** at the bottom of the sidebar

If you see **"🔴 Not configured"**, your `.env` file credentials are missing or incorrect. All four Azure OpenAI lines must be filled in.

---

### Tab 1 — Quality Gate (Full 4-Agent Pipeline)

The Quality Gate runs all four agents in sequence and produces a single consolidated review:

| Agent | What it does |
|---|---|
| CLARION | Checks naming conventions, security patterns, coding standards |
| LUMEN | Detects code smells (long methods, deep nesting, magic numbers, etc.) |
| VECTOR | Scores risk level using static complexity analysis + hotspot identification |
| ASCENT | Aggregates all three outputs into one prioritised recommendation |

**For the demo:**

1. Select language: **csharp**
2. Click **"📂 Load Sample Code"** — loads a C# file with deliberate violations
3. Click **"🔍 Run Full Review"**
4. Watch the pipeline status — each agent shows a live status indicator as it runs
5. Wait 30–60 seconds for all four agents to complete
6. The right panel shows:
   - **ASCENT Summary** — overall recommendation (APPROVE / REQUEST\_CHANGES / BLOCK), score out of 10, and the single biggest risk
   - **Tier 1 — Must Fix** — critical issues that must be resolved before merge (expanded by default)
   - **Tier 2 — Should Fix** — important but not blocking
   - **Tier 3 — Consider** — informational improvements
   - **Reviewer Checklist** — things a human must manually verify
   - **Individual agent reports** — CLARION, LUMEN, and VECTOR results collapsed below (expand to see raw findings)

**Human Review Gate (appears after results load):**

After the AI review completes, a reviewer form appears. This simulates the human-in-the-loop step:

1. **Step 1** — React to each finding: mark it as *Agree* or *False Positive*
2. **Step 2** — Override the ASCENT recommendation if needed (or keep the AI decision)
3. **Step 3** — Add a free-text comment for the developer
4. Click **"Submit Review Decision"**
5. The final decision card shows: agreed vs false positive counts, false positive rate, and a warning if FP rate exceeds 20% (indicating ASCENT's rules may need tuning)

**To test with your own code:**

1. Open any C# or TypeScript file from your project
2. Copy the content
3. Paste it into the text area
4. Click Run Full Review

---

### Tab 2 — Security Loop (BULWARK)

**For the demo:**

1. Click **"📂 Load Sample Finding"** — loads a SQL injection finding
2. Click **"🔒 Run Triage"**
3. Wait 10–20 seconds
4. Results show classification (CRITICAL/HIGH/etc.), attack scenario, and a secure code fix

**To test with a real finding:**

1. Copy the description of any Fortify finding
2. Paste it into the "Vulnerability / Fortify Finding Description" box
3. Optionally paste the vulnerable code snippet for a more precise fix
4. Click Run Triage

---

### Tab 3 — Certificate Loop (TIMELINE)

**For the demo:**

1. Click **"📂 Load Sample Certificate"** — pre-fills a certificate expiring in ~16 days
2. Click **"📜 Analyse Certificate"**
3. Wait 10–20 seconds
4. Results show urgency level, renewal path, and step-by-step action plan

**To test with a real certificate:**

1. Fill in the Subject/Domain (e.g., `api.yourcompany.com`)
2. Enter the expiry date in YYYY-MM-DD format
3. Select the CA type
4. Click Analyse Certificate

---

## Section 6 — Troubleshooting

### "🔴 Not configured" in sidebar

**Cause:** Credentials not set.  
**Fix:** Check your `.env` file has all four Azure OpenAI lines filled in. Restart the app after editing `.env`.

---

### App opens but clicking Run does nothing / shows spinner forever

**Cause:** Usually a network issue — the Azure OpenAI endpoint is not reachable.  
**Fix:**
- Check you are on the company VPN if required
- Verify the endpoint URL in `.env` ends with `/`
- Test the endpoint in a browser — you should get a JSON response, not a "site not found"

---

### `pip install` fails with "access denied"

**Fix:** Right-click Command Prompt → Run as Administrator, then retry.

---

### "ModuleNotFoundError: No module named 'openai'"

**Fix:** Dependencies not installed. Run:
```bat
pip install -r requirements.txt
```

---

### "JSONDecodeError" in results

**Cause:** The AI returned an unexpected response format.  
**Fix:** This is rare. Simply click Run again — it will work on retry.

---

### Port 8501 already in use

**Fix:**
```bat
streamlit run app.py --server.port 8502
```
Then open `http://localhost:8502`

---

## Section 7 — What This POC Does NOT Do

This is important to be clear about during the demo:

| This POC does NOT... | Production will... |
|---|---|
| Connect to Azure DevOps | Receive PR diffs automatically via webhook |
| Post comments on actual PRs | Post inline comments directly on the PR |
| Connect to Fortify SSC | Fetch findings automatically from Fortify SSC API |
| Access Azure Key Vault | Monitor all certificates in Key Vault daily |
| Deploy certificates to IIS | Automate cert deployment to Dev/QA/Prod |

**The POC proves the AI intelligence works.**  
The Azure DevOps / Fortify / Key Vault connections are integration plumbing — straightforward to add once the approach is approved.

---

## Section 8 — Quick Reference

| Action | Command / Location |
|---|---|
| Start the app | Double-click `run.bat` OR `streamlit run app.py` |
| Open in browser | http://localhost:8501 |
| Stop the app | Ctrl + C in the command window |
| Edit credentials | Open `poc\.env` in Notepad |
| View sample C# code | `poc\samples\bad_csharp.cs` |
| View sample Angular code | `poc\samples\bad_typescript.ts` |
| View sample Fortify finding | `poc\samples\fortify_finding.txt` |

---

*End of Setup Guide — Project BlueLine POC v1.1*

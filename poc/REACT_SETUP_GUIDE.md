# BlueLine React UI — Setup & Run Guide

**Stack:** FastAPI (Python backend) + React 18 + Vite + Tailwind CSS  
**Replaces:** Streamlit (`app.py`) — the old app still works, both can coexist

---

## Prerequisites

| Requirement | Version | Check |
|---|---|---|
| Python | 3.9+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |

---

## One-time Setup

### Step 1 — Install Python dependencies

```bash
cd poc
pip install -r requirements.txt
```

New packages added: `fastapi`, `uvicorn`, `python-multipart`

### Step 2 — Install Node dependencies

```bash
cd poc/frontend
npm install
```

This installs React, Vite, Tailwind, and Lucide icons (~30 seconds).

### Step 3 — Make sure your `.env` is configured

The React UI reads credentials from the same `.env` file as the Streamlit app.

```bash
cd poc
cp .env.example .env    # if you haven't already
```

Fill in your values in `poc/.env`:

```env
# AI Provider (required for all agent tabs)
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Azure DevOps (required for Live PR Review tab only)
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/your-org
AZURE_DEVOPS_PAT=your-pat
AZURE_DEVOPS_PROJECT=YourProject
AZURE_DEVOPS_REPO=YourRepo
```

---

## Running the App

You need **two terminals open at the same time**.

### Terminal 1 — Start the API backend

```bash
cd poc
uvicorn api:app --reload --port 8000
```

**Windows shortcut:** double-click `poc/start_api.bat`

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Verify it's working: open `http://localhost:8000/docs` in your browser — you'll see the interactive API explorer.

### Terminal 2 — Start the React frontend

```bash
cd poc/frontend
npm run dev
```

You should see:
```
  VITE v5.x  ready in 300ms
  ➜  Local:   http://localhost:5173/
```

### Open the app

Go to **`http://localhost:5173`** in your browser.

---

## Using the App

### Sidebar (left panel)

- **AI Provider** — select Azure OpenAI (recommended, data stays in your tenant) or Anthropic
- Enter credentials and click **Apply Config**
- Green pills at the top confirm AI and ADO are connected

### Tab 1 — Quality Gate

1. Select language (C# or TypeScript)
2. Click **Sample** to load a pre-built bad code file, or paste your own
3. Click **Run Full Review**
4. Watch the pipeline bar: CLARION → LUMEN → VECTOR → ASCENT light up in sequence
5. Results appear: ASCENT recommendation card, tiered findings, individual agent reports

### Tab 2 — Security Loop

1. Click **Sample** next to the finding input to load a Fortify finding
2. Optionally paste the vulnerable code snippet
3. Click **Run Security Pipeline**
4. See: BULWARK triage result → FORGE draft PR → STEWARD audit log

### Tab 3 — Certificate Loop

1. The REGENT inventory table loads automatically on page open
2. Click a row to select a certificate
3. Click **Run Pipeline**
4. See: TIMELINE expiry analysis → COURIER renewal request → HARBOUR deployment plan + Teams approval card preview

### Tab 4 — Live PR Review

1. Configure Azure DevOps credentials in the sidebar
2. Click **Load PRs** to fetch open pull requests from your repo
3. Select a PR from the list
4. Toggle **Shadow Mode** (ON = read-only, OFF = posts real comments to ADO)
5. Click **Run Quality Gate**

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `npm install` fails | Make sure Node 18+ is installed: `node --version` |
| `uvicorn: command not found` | Run `pip install uvicorn` or use `python -m uvicorn api:app --reload --port 8000` |
| Port 8000 already in use | Change port: `uvicorn api:app --port 8001` and update `vite.config.ts` proxy target |
| "No AI provider configured" red banner | Enter credentials in sidebar and click Apply Config |
| "Azure DevOps not configured" on Live PR tab | Add ADO credentials in sidebar and click Apply Config |
| Agents time out | AI calls can take 30–60 seconds — this is normal for GPT-4o |
| CORS error in browser console | Make sure the API is running on port 8000 and Vite is on 5173 |

---

## File Reference

```
poc/
├── api.py              ← FastAPI backend — all agent endpoints
├── start_api.bat       ← Windows shortcut to start the API
├── requirements.txt    ← Python deps (now includes fastapi + uvicorn)
├── app.py              ← Original Streamlit app (still works)
│
└── frontend/
    ├── package.json        ← Node deps
    ├── vite.config.ts      ← Dev server + /api proxy to port 8000
    ├── tailwind.config.js  ← BlueLine colour theme
    └── src/
        ├── App.tsx                        ← Root layout + tab navigation
        ├── api.ts                         ← All fetch calls to FastAPI
        ├── types.ts                       ← TypeScript interfaces
        ├── components/
        │   ├── Sidebar.tsx                ← Config panel (AI + ADO)
        │   ├── AgentPipeline.tsx          ← Animated pipeline status bar
        │   └── Badge.tsx                  ← Severity / status badges
        └── tabs/
            ├── QualityGate.tsx            ← Tab 1
            ├── SecurityLoop.tsx           ← Tab 2
            ├── CertificateLoop.tsx        ← Tab 3
            └── LivePRReview.tsx           ← Tab 4
```

---

## Notes

- The React UI and Streamlit app are completely independent. Both read the same `.env` and call the same Python agents. You can run either or both.
- The `poc/frontend/node_modules/` folder is git-ignored — always run `npm install` after cloning.
- Credentials entered in the sidebar are stored **in memory only** for the current API server session. They are not written to disk. Restart the API server and re-enter them, or keep them in `.env`.

---

*Project BlueLine POC · React UI v1.0 · May 2026*

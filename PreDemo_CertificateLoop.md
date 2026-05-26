# Pre-Demo Reading — Certificate Loop
**Read this 10 minutes before your demo. Everything below is based on the actual agent code.**

---

## What It Does in One Line

Every morning at 6:00 AM, four agents automatically check every SSL/TLS certificate in the estate, flag anything expiring within 90 days, contact the Certificate Authority to renew it, install the new certificate on Dev and QA servers, verify HTTPS is working, and send a Teams approval card before touching Production.

---

## The Problem It Solves

Today, certificate management works like this:
- A spreadsheet (or someone's memory) tracks when each cert expires
- Someone has to remember to check it
- When it is close to expiry, someone manually logs into the CA portal and requests a renewal
- Someone downloads the new certificate
- Someone RDPs into each server and imports it into IIS
- Someone rebinds the IIS site to the new thumbprint
- Someone checks that HTTPS still works
- Someone sends an email to confirm it is done

If that someone is on leave, or the spreadsheet is out of date, or the reminder is missed — the certificate expires. The service goes down. Users see a security error. On a Friday night this becomes an incident.

BlueLine replaces the entire manual chain with one automated pipeline that runs every single morning without anyone having to remember.

---

## The Four Agents — What Each One Does and How It Decides

---

### Agent 1 — REGENT (Certificate Inventory Manager)

**Job:** Maintain a structured, up-to-date inventory of every SSL/TLS certificate across all environments.

**How it decides:**
REGENT does not make decisions — it is the data layer. Every other agent reads from REGENT and writes back to it. REGENT holds the following for each certificate:

| Field | What it stores |
|---|---|
| Domain / Subject | e.g. `api.core-main.internal` |
| Expiry date | The exact date the certificate expires |
| Days remaining | Calculated daily — can be negative if already expired |
| Status | See urgency levels below |
| CA type | Internal PKI, DigiCert, Let's Encrypt |
| Owner | Which team is responsible |
| Environments | Dev, QA, Production |
| Deployment targets | Which specific servers or App Services |

**In production:** REGENT reads from Azure Key Vault (which stores the actual certificates) and Azure Table Storage (which stores the metadata and inventory).

**In the POC:** Four sample certificates are loaded in memory to demonstrate the pipeline.

**What to say in the demo:**
> "REGENT is the single source of truth for every certificate in the estate. In production it reads directly from Azure Key Vault so the inventory is always accurate — no spreadsheet, no manual updates."

---

### Agent 2 — TIMELINE (Expiry Analyser)

**Job:** Assess the urgency of each certificate's situation and produce an action plan.

**How it decides:**
TIMELINE calculates the number of days remaining until expiry and assigns an urgency level:

| Urgency | Condition | What it means |
|---|---|---|
| `EXPIRED` | Already past expiry date | Certificate is already causing HTTPS errors |
| `CRITICAL` | Less than 7 days remaining | Renewal must happen today |
| `URGENT` | Less than 14 days remaining | Renewal must happen this week |
| `RENEWAL_NEEDED` | Less than 30 days remaining | Renewal should be scheduled now |
| `MONITOR` | 30 – 90 days remaining | No action yet — watching |
| `OK` | More than 90 days remaining | Healthy — no action needed |

**What TIMELINE produces:**
- Urgency classification
- Days until expiry (or days since expiry if negative)
- Risk level (critical, high, medium, low)
- One-sentence summary of the situation
- Renewal path — which CA and process to use:
  - `internal_pki` — C&M Portal API (automatic)
  - `external_ca` — DigiCert API (automatic)
  - `letsencrypt` — ACME protocol (automatic)
- Step-by-step action plan
- Risk flags — any complications (e.g. IIS binding needs manual update if thumbprint changes)
- Whether full automation is possible

**What triggers COURIER:**
Only `EXPIRED`, `CRITICAL`, `URGENT`, and `RENEWAL_NEEDED` trigger the next agents. `MONITOR` and `OK` certificates are logged and left alone.

**What to say in the demo:**
> "TIMELINE does not just say a certificate is expiring — it tells you how urgent it is, what the renewal path is, what the risks are, and gives you a step-by-step plan. In the demo you will see `api.core-main.internal` — it expired yesterday, so TIMELINE flags it as EXPIRED immediately."

---

### Agent 3 — COURIER (Certificate Authority Renewal Requester)

**Job:** Contact the Certificate Authority via API, submit the renewal request, and retrieve the new certificate.

**How it decides:**
COURIER looks at the CA type recorded in REGENT and calls the appropriate API:

| CA Type | How COURIER contacts it | Validation method | Delivery |
|---|---|---|---|
| Internal PKI (C&M Portal) | C&M Portal REST API | Internal auto-approval | Immediate |
| DigiCert (External) | DigiCert REST API | DNS or email validation | 2–4 hours for OV |
| Let's Encrypt | ACME protocol | HTTP or DNS challenge | Immediate after challenge |

**What COURIER produces:**
- Confirmation the renewal request was submitted
- CA order ID (for tracking)
- Validation method used
- Estimated delivery time
- New certificate in the requested format (PFX or PEM)
- New thumbprint of the renewed certificate
- Instructions for HARBOUR on what to do next

**What to say in the demo:**
> "COURIER talks to whichever CA issued the original certificate. Internal PKI is instant — it auto-approves and the certificate comes back immediately. DigiCert takes a few hours because it needs domain validation. COURIER handles all of this — the engineer never has to log into the CA portal."

---

### Agent 4 — HARBOUR (Certificate Deployment Agent)

**Job:** Install the renewed certificate on every target server, verify HTTPS is working after each install, and gate Production deployment on human approval.

**How it decides:**
HARBOUR has different rules for each environment:

**Dev and QA — automatic:**
- Generate the exact PowerShell commands to run via WinRM (Windows Remote Management)
- Import the PFX into the IIS certificate store
- Rebind the IIS site to the new thumbprint
- Run HTTPS verification (`Invoke-WebRequest https://...`)
- Mark as deployed

**Production — human gate:**
- Do NOT deploy automatically
- Send a Teams adaptive card to the designated approval channel
- The card shows: domain, new certificate expiry date, servers already deployed to, the specific Production server
- Two buttons: **Approve — Deploy to Production** and **Hold — Do Not Deploy**
- HARBOUR waits. It will not proceed until a human clicks Approve.
- If Approve is clicked: HARBOUR runs the same PowerShell commands on the Production server
- If Hold is clicked: deployment is paused and logged to STEWARD

**The PowerShell commands HARBOUR generates for IIS:**
```powershell
# Import the certificate
Import-PfxCertificate -FilePath "cert.pfx" -CertStoreLocation Cert:\LocalMachine\My -Password $securePassword

# Bind the certificate to the IIS site
Set-WebBinding -Name "DefaultWebSite" -BindingInformation "*:443:" -CertificateThumbprint "3A9F..." -CertificateStoreName "My"

# Verify HTTPS is working
Invoke-WebRequest https://api.core-main.internal -UseBasicParsing
```

**For Azure App Service:**
```bash
az webapp config ssl upload --certificate-file cert.pfx --certificate-password <pw> --name api-prod --resource-group rg-prod
az webapp config ssl bind --certificate-thumbprint 3A9F... --ssl-type SNI --name api-prod --resource-group rg-prod
```

**What to say in the demo:**
> "Dev and QA are deployed automatically — no approval needed. HARBOUR installs, verifies HTTPS, moves on. But for Production, it stops completely. A Teams card is sent to the team. A human has to click Approve. HARBOUR waits until they do. This is the core safety design — automate the routine, gate the risk."

---

## The Full Flow

```
Every morning — 6:00 AM Azure Timer fires
         │
         ▼
REGENT retrieves full certificate inventory from Azure Key Vault
         │
         ▼
TIMELINE analyses each certificate
Assigns urgency: EXPIRED / CRITICAL / URGENT / RENEWAL_NEEDED / MONITOR / OK
         │
         ├── MONITOR or OK ──── Logged, no action, check again tomorrow
         │
         └── EXPIRED / CRITICAL / URGENT / RENEWAL_NEEDED
                  │
                  ▼
               COURIER
         Contacts the CA via API
         Submits renewal request
         Retrieves new certificate + thumbprint
                  │
                  ▼
               HARBOUR
         ┌─── Dev environment ────────────────────────────────────┐
         │    Import cert → rebind IIS → verify HTTPS ✅ Done     │
         └─────────────────────────────────────────────────────────┘
         ┌─── QA environment ─────────────────────────────────────┐
         │    Import cert → rebind IIS → verify HTTPS ✅ Done     │
         └─────────────────────────────────────────────────────────┘
         ┌─── Production ─────────────────────────────────────────┐
         │    STOP — send Teams approval card                     │
         │    Wait for human to click Approve                     │
         │    Human clicks Approve → deploy → verify HTTPS        │
         └─────────────────────────────────────────────────────────┘
         │
         ▼
STEWARD logs the full deployment record
```

---

## The Certificate Inventory in the Demo

| Certificate | Status | Days | Owner |
|---|---|---|---|
| payments.external.com | EXPIRED | -13 | Manjunath Rao |
| api.core-main.internal | EXPIRED | -1 | Pankaj Pathak |
| adein.core-main.internal | MONITOR | 73 | Ravi Kumar |
| *.internal.local | OK | 160 | Pankaj Pathak |

You select `api.core-main.internal` for the demo — it expired yesterday, so TIMELINE immediately flags it EXPIRED and the full pipeline runs.

---

## Key Numbers to Remember

| Metric | Value |
|---|---|
| How often TIMELINE runs | Daily at 6:00 AM UTC |
| Advance warning window | Flags certs up to 90 days before expiry |
| Critical threshold | Less than 7 days |
| Renewal triggered at | Less than 30 days (RENEWAL_NEEDED or higher) |
| Dev and QA | Deployed automatically — no approval |
| Production | Always requires human approval via Teams |

---

## If They Ask Difficult Questions

**"What if someone clicks Approve by mistake?"**
> "STEWARD logs the approval — who clicked it, when, on which certificate. The deployment is traceable. For future iterations, we can add a two-person approval requirement or a confirmation dialog."

**"What if the CA is slow and the certificate doesn't come back immediately?"**
> "For internal PKI it is always immediate. For DigiCert it can take hours — COURIER records the order ID and in production HARBOUR polls for the certificate to arrive before proceeding. The pipeline is designed to handle async delivery."

**"What if HTTPS verification fails after install?"**
> "HARBOUR detects the failure, logs it to STEWARD, and sends a Teams alert. The failed environment is marked as needing manual intervention. It does not proceed to the next environment if one fails."

**"Does it handle wildcard certificates?"**
> "Yes — REGENT tracks wildcard certs like `*.internal.local` exactly the same way. The domain is stored as-is. TIMELINE analyses the expiry date regardless of whether it is a single domain or wildcard. COURIER and HARBOUR handle them identically."

**"What about certificates that are not in Azure Key Vault yet?"**
> "That is a valid gap for the initial rollout. The first step in going live would be a one-time migration — inventory every certificate and register it in Key Vault. REGENT then takes over from there. We can run REGENT in read-only mode first to validate the inventory before any automation is enabled."

---

*Project BlueLine — LTM AI-Led Engineering Team · Certificate Loop Pre-Demo Brief*

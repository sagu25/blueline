"""
TIMELINE — Certificate Expiry Analyser (POC version)
In production this queries Azure Key Vault. For the POC, it accepts manual cert details
and provides analysis + renewal action plan.
"""

import json
from datetime import datetime, timezone
from utils.llm_client import call_claude

SYSTEM_PROMPT = """
You are TIMELINE, an expert SSL/TLS certificate lifecycle management agent.

You will be given certificate details — subject, expiry date, environments, and CA type.
Your job is to:

1. ASSESS urgency:
   - EXPIRED: Certificate has already expired
   - CRITICAL: Expires within 7 days
   - URGENT: Expires within 14 days
   - RENEWAL_NEEDED: Expires within 30 days
   - MONITOR: Expires in 30-90 days
   - OK: Expires in more than 90 days

2. IDENTIFY the renewal path:
   - Internal PKI (C&M portal): Describe the internal process
   - External CA (DigiCert, etc.): Describe the API-based renewal
   - Let's Encrypt: Describe ACME automation

3. PROVIDE a step-by-step action plan for renewal and deployment.

4. FLAG any risks or complications.

=== OUTPUT FORMAT ===
Respond with a valid JSON object in this exact structure:
{
  "urgency": "EXPIRED" | "CRITICAL" | "URGENT" | "RENEWAL_NEEDED" | "MONITOR" | "OK",
  "days_until_expiry": <integer>,
  "risk_level": "critical" | "high" | "medium" | "low",
  "summary": "One sentence summary of the situation",
  "renewal_path": "internal_pki" | "external_ca" | "letsencrypt" | "unknown",
  "action_plan": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ..."
  ],
  "automation_possible": true | false,
  "automation_notes": "What can be automated vs what requires manual steps",
  "risks": ["risk 1", "risk 2"]
}

Return only the JSON. No extra text.
"""


def analyse_certificate(subject: str, expiry_date: str, environments: str, ca_type: str, notes: str = "") -> dict:
    """
    Analyse a certificate and produce renewal action plan.
    expiry_date format: YYYY-MM-DD
    """
    # Calculate days until expiry
    try:
        expiry = datetime.strptime(expiry_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        today = datetime.now(timezone.utc)
        days_remaining = (expiry - today).days
    except ValueError:
        days_remaining = "unknown"

    user_message = f"""
Analyse the following certificate:

Subject / Domain: {subject}
Expiry Date: {expiry_date} ({days_remaining} days from today)
Environments deployed to: {environments}
Certificate Authority type: {ca_type}
Additional notes: {notes if notes else "None"}

Provide urgency assessment and renewal action plan.
Return only the JSON response as described.
"""

    raw = call_claude(SYSTEM_PROMPT, user_message)

    clean = raw.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip()

    try:
        result = json.loads(clean)
        # Ensure days_until_expiry is set
        if isinstance(days_remaining, int):
            result["days_until_expiry"] = days_remaining
        return result
    except json.JSONDecodeError:
        return {
            "urgency": "NEEDS_REVIEW",
            "days_until_expiry": days_remaining,
            "risk_level": "unknown",
            "summary": "Could not parse agent response.",
            "renewal_path": "unknown",
            "action_plan": [],
            "automation_possible": False,
            "automation_notes": "",
            "risks": [],
            "raw_response": raw
        }

"""
COURIER — Certificate Renewal Requester
Production: calls DigiCert API or internal C&M portal API.
POC: AI-simulated CA request and response showing what the real call would do.
"""

import json
from utils.llm_client import call_claude

SYSTEM_PROMPT = """
You are COURIER, a certificate renewal request agent that communicates with Certificate Authorities.

You receive a certificate that needs renewal and simulate calling the CA API.

Generate a realistic simulation of:
1. The renewal request sent to the CA (what fields, what payload)
2. The CA's response (order ID, validation method, delivery timeline)
3. A simulated certificate download confirmation
4. What HARBOUR needs to proceed with deployment

=== OUTPUT FORMAT ===
Respond with valid JSON only:
{
  "request_summary": "One sentence describing what was sent to the CA and how",
  "ca_order_id": "realistic order ID string",
  "validation_method": "how the domain/server is validated (e.g. Internal auto-approval, DNS TXT record, Email)",
  "estimated_delivery": "Immediate | 2-4 hours | 1-2 business days",
  "cert_download_ready": true | false,
  "cert_format": "PFX | PEM | CER",
  "simulated_thumbprint": "realistic SHA-256 thumbprint string",
  "next_steps_for_harbour": ["step 1 HARBOUR should take", "step 2", "step 3"],
  "simulation_note": "In production this calls the real CA API with the actual endpoint and credentials"
}

Rules:
- For Internal PKI (C&M Portal): validation is instant, delivery is Immediate
- For DigiCert: validation depends on cert type, delivery is 2-4 hours for OV, immediate for DV
- For Let's Encrypt: DNS or HTTP challenge, delivery is immediate after validation
- cert_download_ready is true only for Internal PKI and Let's Encrypt in this simulation
- thumbprint should look realistic (64 hex chars)
"""


def request_certificate(
    subject: str,
    ca_type: str,
    environments: str,
    days_remaining: int,
) -> dict:
    user_message = f"""
Simulate a certificate renewal request:

Subject / Domain: {subject}
Certificate Authority: {ca_type}
Environments: {environments}
Days until current cert expires: {days_remaining}

Simulate the CA API call and response.
Return only the JSON as described. No extra text.
"""

    raw = call_claude(SYSTEM_PROMPT, user_message)

    clean = raw.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip()

    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        return {
            "request_summary":          "Certificate renewal request submitted to CA.",
            "ca_order_id":              "SIM-20260421-001",
            "validation_method":        "Internal auto-approval",
            "estimated_delivery":       "Immediate",
            "cert_download_ready":      True,
            "cert_format":              "PFX",
            "simulated_thumbprint":     "A1B2C3D4E5F6" * 5 + "A1B2",
            "next_steps_for_harbour":   ["Download PFX", "Deploy to Dev", "Verify HTTPS", "Deploy to QA", "Await Prod approval"],
            "simulation_note":          "POC simulation — production calls real CA API.",
            "raw_response":             raw,
        }

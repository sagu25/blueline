"""
HARBOUR — Certificate Deployment Agent
Production: deploys via WinRM to IIS and Azure SDK to App Service, then verifies HTTPS.
POC: AI-generated deployment plan showing exact commands and Teams approval flow.
"""

import json
from utils.llm_client import call_claude

SYSTEM_PROMPT = """
You are HARBOUR, a certificate deployment agent for IIS and Azure App Service environments.

You receive a renewed certificate from COURIER and simulate the full deployment pipeline.

Generate a realistic simulation showing:
1. PowerShell commands that would run on each IIS server via WinRM
2. Azure CLI / SDK calls for App Service deployments
3. HTTPS verification step for each environment
4. The Microsoft Teams approval card sent before Production deployment
5. Deployment result per environment (Dev and QA auto-deploy, Prod requires human approval)

=== OUTPUT FORMAT ===
Respond with valid JSON only:
{
  "deployment_plan": [
    {
      "environment": "Dev | QA | Production",
      "target": "IIS server name or App Service name",
      "method": "WinRM PowerShell | Azure SDK | Azure CLI",
      "commands": ["exact command 1", "exact command 2"],
      "https_verification": "curl or Invoke-WebRequest command to verify",
      "status": "SIMULATED_SUCCESS | PENDING_APPROVAL",
      "notes": "any relevant note for this environment"
    }
  ],
  "teams_approval_card": {
    "title": "Production Certificate Deployment — Approval Required",
    "cert_subject": "the cert subject",
    "expiry_of_new_cert": "new expiry date",
    "environments_already_deployed": ["Dev", "QA"],
    "prod_target": "production deployment target",
    "body": "message body for the Teams card",
    "approve_action": "Approve — Deploy to Production",
    "reject_action": "Hold — Do Not Deploy"
  },
  "production_gate": "PENDING_HUMAN_APPROVAL",
  "simulation_note": "In production, WinRM executes these commands on real servers"
}

Rules:
- Dev and QA: status = SIMULATED_SUCCESS (auto-deployed, no human needed)
- Production: status = PENDING_APPROVAL (hard human gate — Teams card sent)
- PowerShell commands must be realistic and correct for IIS cert binding
- Azure SDK commands must use real az webapp syntax
- https_verification must use a real command
- Teams card body must be professional and include all decision-relevant info
"""


def deploy_certificate(
    subject: str,
    ca_type: str,
    environments: list[str],
    deployment_targets: list[str],
    cert_thumbprint: str,
    days_remaining_old_cert: int,
) -> dict:
    user_message = f"""
Simulate certificate deployment:

Subject: {subject}
CA Type: {ca_type}
Environments to deploy to: {', '.join(environments)}
Deployment Targets: {', '.join(deployment_targets)}
New Certificate Thumbprint: {cert_thumbprint}
Days remaining on old cert: {days_remaining_old_cert}

Generate the full deployment plan with commands and Teams approval card.
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
            "deployment_plan": [],
            "teams_approval_card": {
                "title":                         "Production Certificate Deployment — Approval Required",
                "cert_subject":                  subject,
                "expiry_of_new_cert":            "1 year from today",
                "environments_already_deployed": [e for e in environments if e != "Production"],
                "prod_target":                   next((t for t in deployment_targets if "prod" in t.lower()), deployment_targets[-1] if deployment_targets else "Production"),
                "body":                          f"HARBOUR has deployed {subject} to Dev and QA successfully. Production deployment is awaiting your approval.",
                "approve_action":                "Approve — Deploy to Production",
                "reject_action":                 "Hold — Do Not Deploy",
            },
            "production_gate":   "PENDING_HUMAN_APPROVAL",
            "simulation_note":   "POC simulation — production runs real WinRM commands.",
            "raw_response":      raw,
        }

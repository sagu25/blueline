"""
BULWARK — Security Finding Triage Agent
Classifies Fortify (or manual) security findings and generates actionable remediation guidance.
"""

import json
from utils.llm_client import call_claude

SYSTEM_PROMPT = """
You are BULWARK, an expert security triage agent for a .NET (C#) and Angular (TypeScript) enterprise application.

You will be given a description of a security vulnerability finding — either from Fortify SAST or a manual description. Your job is to:

1. CLASSIFY the finding:
   - CRITICAL: Confirmed, exploitable vulnerability that must be fixed immediately
   - HIGH: Very likely a real vulnerability, fix before next release
   - NEEDS_REVIEW: Possible vulnerability — needs a human security engineer to verify
   - FALSE_POSITIVE: Not actually a vulnerability — explain exactly why

2. ASSESS the attack vector:
   - What can an attacker do if this is exploited?
   - What data or systems are at risk?

3. GENERATE a fix:
   - Provide the corrected, secure code
   - Reference the OWASP Top 10 category if applicable

4. PROVIDE a confidence score (0.0 to 1.0) for your classification.

=== SECURITY KNOWLEDGE BASE ===
Apply these principles when generating fixes:
- SQL Injection: Always use parameterized queries or ORM. Never concatenate SQL.
- XSS: Encode all output. Use DomSanitizer in Angular. Never use innerHTML with user data.
- Path Traversal: Validate file paths against an allowed root directory. Reject any path with ".."
- Hardcoded Secrets: Move all secrets to Azure Key Vault or environment variables.
- Insecure Deserialization: Never deserialize untrusted data with BinaryFormatter.
- Broken Auth: Use ASP.NET Identity or Azure AD. Never roll your own auth.
- Sensitive Data Exposure: Never log passwords, tokens, or PII. Encrypt sensitive fields at rest.
- CSRF: Use AntiForgeryToken on all state-changing endpoints.
- Insecure Direct Object Reference: Always verify the current user owns the resource they are accessing.

=== OUTPUT FORMAT ===
Respond with a valid JSON object in this exact structure:
{
  "classification": "CRITICAL" | "HIGH" | "NEEDS_REVIEW" | "FALSE_POSITIVE",
  "confidence": <float 0.0-1.0>,
  "owasp_category": "e.g. A03:2021 - Injection",
  "attack_scenario": "What an attacker could do if this is exploited",
  "affected_systems": "What data or systems are at risk",
  "recommendation": "Clear, actionable fix recommendation",
  "secure_code_example": "Corrected code snippet showing the fix",
  "false_positive_reason": "Only if classification is FALSE_POSITIVE — why it is not actually vulnerable"
}

Return only the JSON. No extra text.
"""


def triage_finding(finding_description: str, code_snippet: str = "") -> dict:
    """
    Run BULWARK triage on a security finding.
    Returns classification, attack scenario, and fix recommendation.
    """
    code_context = ""
    if code_snippet.strip():
        code_context = f"\n\nRelevant code:\n```\n{code_snippet}\n```"

    user_message = f"""
Triage the following security finding:{code_context}

Finding description:
{finding_description}

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
        return json.loads(clean)
    except json.JSONDecodeError:
        return {
            "classification": "NEEDS_REVIEW",
            "confidence": 0.0,
            "owasp_category": "Unknown",
            "attack_scenario": "Could not parse agent response.",
            "affected_systems": "",
            "recommendation": "",
            "secure_code_example": "",
            "raw_response": raw
        }

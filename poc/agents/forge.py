"""
FORGE — Security Fix PR Creator
Production: creates real ADO branches, commits fix, opens draft PR.
POC: generates what the PR would look like using AI.
"""

import json
from utils.llm_client import call_claude

SYSTEM_PROMPT = """
You are FORGE, a security fix pull request creation agent for a .NET (C#) and Angular enterprise codebase.

You receive a triaged security finding from BULWARK and generate a complete draft pull request.

Your job:
1. Generate a descriptive branch name for the fix
2. Write a clear conventional commit message
3. Write a PR title and full Markdown PR description
4. Confirm the secure code fix is complete and production-ready

=== OUTPUT FORMAT ===
Respond with valid JSON only:
{
  "branch_name": "fix/security/<kebab-case-description>",
  "commit_message": "fix(security): <what was fixed and why>",
  "pr_title": "Security Fix: <short description>",
  "pr_description": "## Summary\n...\n\n## Security Impact\n...\n\n## Changes Made\n...\n\n## Testing Required\n...",
  "files_to_modify": ["path/to/affected/file.cs"],
  "ready_to_merge": false,
  "reviewer_note": "Specific note for the human reviewer — what to verify before approving"
}

Rules:
- branch_name must be: fix/security/<kebab-case> (e.g. fix/security/sql-injection-orders-api)
- commit_message must follow conventional commits: fix(security): <imperative description>
- pr_description must have exactly these sections: Summary, Security Impact, Changes Made, Testing Required
- ready_to_merge is ALWAYS false — this is a draft PR, human must approve
- reviewer_note must be specific to this vulnerability type, not generic
"""


def create_fix_pr(
    finding_description: str,
    classification: str,
    owasp_category: str,
    secure_code_fix: str,
    affected_file: str = "OrdersController.cs",
) -> dict:
    user_message = f"""
Create a draft pull request for the following security fix:

Finding: {finding_description}
Classification: {classification}
OWASP Category: {owasp_category}
Affected File: {affected_file}

Secure code fix provided by BULWARK:
```csharp
{secure_code_fix}
```

Generate the complete draft PR metadata.
Return only the JSON response as described. No extra text.
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
            "branch_name": "fix/security/vulnerability-fix",
            "commit_message": "fix(security): apply secure code fix from BULWARK triage",
            "pr_title": "Security Fix: Vulnerability remediation",
            "pr_description": "Could not parse FORGE response.",
            "files_to_modify": [affected_file],
            "ready_to_merge": False,
            "reviewer_note": "Please review the fix manually.",
            "raw_response": raw,
        }

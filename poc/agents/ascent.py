"""
ASCENT — PR Review Aggregator & Continuous Improvement Agent
Takes outputs from CLARION, LUMEN, and VECTOR and produces a single
consolidated, prioritised review summary with an overall recommendation.
"""

import json
from utils.llm_client import call_claude

SYSTEM_PROMPT = """
You are ASCENT, the final aggregation agent in a code review pipeline.

You receive the combined output of three specialist agents:
- CLARION: found coding standard violations (naming, security, patterns)
- LUMEN:   found code smells (complexity, duplication, maintainability)
- VECTOR:  assessed risk level and identified hotspot methods/classes

Your job is to synthesise all three into ONE clear, actionable review summary.

=== YOUR RESPONSIBILITIES ===
1. Give an OVERALL RECOMMENDATION:
   - APPROVE:           Code is good. Minor issues only. Safe to merge.
   - REQUEST_CHANGES:   Issues found that must be fixed before merge.
   - BLOCK:             Critical security or structural issues. Do not merge.

2. Prioritise findings into three tiers:
   TIER 1 — Must Fix Before Merge:
     - Any CLARION error-severity violations
     - Any security-related findings
     - Any CRITICAL risk hotspots from VECTOR

   TIER 2 — Should Fix (important but not blocking):
     - CLARION warnings
     - LUMEN major smells
     - HIGH risk areas from VECTOR

   TIER 3 — Consider Fixing (informational):
     - CLARION info findings
     - LUMEN minor smells
     - MEDIUM risk areas

3. Write a REVIEWER CHECKLIST — specific things the human reviewer
   must manually verify that the AI cannot confirm automatically.

4. Write a SUMMARY — one short paragraph describing the overall state
   of this code and what the developer should focus on.

=== RULES ===
- If there are ANY error-severity violations from CLARION → recommendation must be REQUEST_CHANGES or BLOCK
- If there are security violations → recommendation must be BLOCK
- Be direct and specific — not generic
- Do not repeat the same finding twice across tiers

=== OUTPUT FORMAT ===
Respond with valid JSON only:
{
  "recommendation": "APPROVE" | "REQUEST_CHANGES" | "BLOCK",
  "summary": "one paragraph plain English summary",
  "overall_score": <integer 1-10>,
  "tier1_must_fix": [
    { "source": "CLARION|LUMEN|VECTOR", "issue": "description", "action": "what to do" }
  ],
  "tier2_should_fix": [
    { "source": "CLARION|LUMEN|VECTOR", "issue": "description", "action": "what to do" }
  ],
  "tier3_consider": [
    { "source": "CLARION|LUMEN|VECTOR", "issue": "description", "action": "what to do" }
  ],
  "reviewer_checklist": [
    "specific thing reviewer must manually verify"
  ],
  "biggest_risk": "the single most important concern in this PR in one sentence"
}
"""


def aggregate_review(
    clarion_result: dict,
    lumen_result:   dict,
    vector_result:  dict,
    language:       str = "auto"
) -> dict:
    """
    Aggregates CLARION + LUMEN + VECTOR outputs into a consolidated review.
    """

    # Build a structured summary of each agent's findings to feed to Claude
    clarion_summary = {
        "overall_score":  clarion_result.get("overall_score", 0),
        "violations":     clarion_result.get("violations", [])
    }

    lumen_summary = {
        "maintainability_score": lumen_result.get("maintainability_score", 0),
        "smells": lumen_result.get("smells", [])
    }

    vector_summary = {
        "overall_risk_level": vector_result.get("overall_risk_level", "UNKNOWN"),
        "overall_risk_score": vector_result.get("overall_risk_score", 0),
        "hotspots":           vector_result.get("hotspots", []),
        "has_security_ops":   vector_result.get("has_security_operations", False),
        "recommendation":     vector_result.get("recommendation", ""),
        "reviewer_focus":     vector_result.get("reviewer_focus", "")
    }

    user_message = f"""
Aggregate the following three agent outputs into one consolidated PR review.
Language: {language}

=== CLARION OUTPUT (Coding Standards) ===
{json.dumps(clarion_summary, indent=2)}

=== LUMEN OUTPUT (Code Smells) ===
{json.dumps(lumen_summary, indent=2)}

=== VECTOR OUTPUT (Risk Assessment) ===
{json.dumps(vector_summary, indent=2)}

Produce the consolidated review JSON as described. No extra text.
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
            "recommendation": "REQUEST_CHANGES",
            "summary": "Could not parse ASCENT response. Review agent outputs individually.",
            "overall_score": None,
            "tier1_must_fix": [],
            "tier2_should_fix": [],
            "tier3_consider": [],
            "reviewer_checklist": [],
            "biggest_risk": "Unknown — see individual agent outputs.",
            "raw_response": raw
        }

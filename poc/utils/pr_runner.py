"""
PR Runner — orchestrates the 4-agent Quality Gate pipeline on a real ADO pull request.
Fetches changed files, runs CLARION + LUMEN + VECTOR + ASCENT per file,
and optionally posts findings back to the PR as inline comments.
"""

from utils.azure_devops import (
    get_pr_details,
    get_pr_changed_files,
    get_file_content,
    post_inline_comment,
    post_pr_summary,
)
from agents.clarion import review_code
from agents.lumen   import detect_smells
from agents.vector  import score_risk
from agents.ascent  import aggregate_review


def _detect_language(file_path: str) -> str:
    if file_path.endswith(".cs"):
        return "csharp"
    if file_path.endswith(".ts"):
        return "typescript"
    return "auto"


def _format_summary_comment(pr_title: str, ascent_result: dict, file_results: list[dict]) -> str:
    """Formats the ASCENT summary as a Markdown comment for ADO."""
    rec   = ascent_result.get("recommendation", "REQUEST_CHANGES")
    score = ascent_result.get("overall_score", 0)
    risk  = ascent_result.get("biggest_risk", "")

    rec_icons = {
        "APPROVE":         "✅",
        "REQUEST_CHANGES": "⚠️",
        "BLOCK":           "🚫",
    }
    icon = rec_icons.get(rec, "⚠️")

    lines = [
        f"## {icon} BlueLine Quality Gate — {rec}",
        f"",
        f"**Overall Score:** {score}/10 &nbsp;&nbsp; **Files Reviewed:** {len(file_results)}",
        f"",
    ]

    if risk:
        lines += [f"> **Biggest Risk:** {risk}", ""]

    t1 = ascent_result.get("tier1_must_fix", [])
    if t1:
        lines += [f"### ⛔ Must Fix Before Merge ({len(t1)})"]
        for item in t1:
            lines.append(f"- **[{item.get('source','?')}]** {item.get('issue','')}  \n  *Fix: {item.get('action','')}*")
        lines.append("")

    t2 = ascent_result.get("tier2_should_fix", [])
    if t2:
        lines += [f"### ⚠️ Should Fix ({len(t2)})"]
        for item in t2:
            lines.append(f"- **[{item.get('source','?')}]** {item.get('issue','')}  \n  *Fix: {item.get('action','')}*")
        lines.append("")

    t3 = ascent_result.get("tier3_consider", [])
    if t3:
        lines += [f"### 💡 Consider ({len(t3)})"]
        for item in t3:
            lines.append(f"- **[{item.get('source','?')}]** {item.get('issue','')}")
        lines.append("")

    checklist = ascent_result.get("reviewer_checklist", [])
    if checklist:
        lines += ["### Reviewer Checklist"]
        for item in checklist:
            lines.append(f"- [ ] {item}")
        lines.append("")

    lines += [
        "---",
        "*Posted by **BlueLine** — AI-powered Quality Gate · Review findings and use your judgement before merging.*"
    ]

    return "\n".join(lines)


def _format_inline_comment(violation: dict, agent: str) -> str:
    """Formats a single finding as a short inline comment."""
    severity = violation.get("severity", "").upper()
    rule     = violation.get("rule", violation.get("type", ""))
    message  = violation.get("message", violation.get("description", ""))
    fix      = violation.get("fix", violation.get("refactor", ""))

    lines = [f"**{agent} [{severity}] — {rule}**", "", message]
    if fix:
        lines += ["", f"**Fix:** `{fix}`" if len(fix) < 100 else f"**Fix:** {fix}"]
    lines += ["", "*BlueLine Quality Gate*"]
    return "\n".join(lines)


# ── Main entry point ───────────────────────────────────────────────────────────

def run_pr_review(pr_id: int, shadow_mode: bool = True, progress_callback=None) -> dict:
    """
    Runs the full Quality Gate pipeline on a real ADO pull request.

    Args:
        pr_id:             Azure DevOps Pull Request ID
        shadow_mode:       If True, generates findings but does NOT post to ADO
        progress_callback: Optional callable(message: str) for status updates in UI

    Returns:
        {
            "pr":           PR details dict,
            "files":        list of per-file results,
            "ascent":       aggregated ASCENT result,
            "summary_comment": formatted markdown for the PR summary,
            "posted":       True if comments were posted (shadow_mode=False only),
            "errors":       list of error strings,
        }
    """
    def log(msg):
        if progress_callback:
            progress_callback(msg)

    errors      = []
    file_results = []

    # ── 1. PR details ──────────────────────────────────────────────────────
    log("Fetching PR details from Azure DevOps...")
    pr = get_pr_details(pr_id)
    source_branch = pr["source_branch"]
    log(f"PR #{pr_id}: \"{pr['title']}\" — branch: {source_branch}")

    # ── 2. Changed files ───────────────────────────────────────────────────
    log("Fetching changed files...")
    changed_files = get_pr_changed_files(pr_id)
    supported = [f for f in changed_files if f["path"].endswith((".cs", ".ts"))]
    log(f"Found {len(changed_files)} changed file(s) — {len(supported)} reviewable (.cs / .ts)")

    if not supported:
        return {
            "pr":              pr,
            "files":           [],
            "ascent":          {},
            "summary_comment": "",
            "posted":          False,
            "errors":          ["No reviewable .cs or .ts files found in this PR."],
        }

    # ── 3. Run agents on each file ─────────────────────────────────────────
    all_clarion_violations = []
    all_lumen_smells       = []
    all_vector_hotspots    = []

    combined_clarion = {"overall_score": 0, "violations": []}
    combined_lumen   = {"maintainability_score": 0, "smells": []}
    combined_vector  = {"overall_risk_score": 0.0, "overall_risk_level": "LOW",
                        "hotspots": [], "reviewer_focus": "", "has_security_operations": False,
                        "has_test_indicators": True, "recommendation": "QUICK_REVIEW_OK"}

    for file in supported:
        path = file["path"]
        lang = _detect_language(path)
        filename = path.split("/")[-1]

        log(f"Reviewing {filename}...")

        # Fetch file content
        try:
            content = get_file_content(path, source_branch)
        except Exception as ex:
            errors.append(f"Could not fetch {path}: {ex}")
            continue

        # Run agents
        try:
            log(f"  CLARION → {filename}")
            clarion = review_code(content, lang)

            log(f"  LUMEN   → {filename}")
            lumen   = detect_smells(content, lang)

            log(f"  VECTOR  → {filename}")
            vector  = score_risk(content, lang)
        except Exception as ex:
            errors.append(f"Agent error on {path}: {ex}")
            continue

        file_results.append({
            "path":    path,
            "lang":    lang,
            "clarion": clarion,
            "lumen":   lumen,
            "vector":  vector,
        })

        # Accumulate for ASCENT
        combined_clarion["violations"].extend(clarion.get("violations", []))
        clarion_score = clarion.get("overall_score") or None
        if clarion_score:
            combined_clarion["overall_score"] = min(
                combined_clarion["overall_score"] or clarion_score,
                clarion_score
            )

        combined_lumen["smells"].extend(lumen.get("smells", []))
        lumen_score = lumen.get("maintainability_score") or None
        if lumen_score:
            combined_lumen["maintainability_score"] = min(
                combined_lumen["maintainability_score"] or lumen_score,
                lumen_score
            )
        # Escalate risk level to worst seen
        v_risk = vector.get("overall_risk_score", 0.0)
        if v_risk > combined_vector["overall_risk_score"]:
            combined_vector["overall_risk_score"] = v_risk
            combined_vector["overall_risk_level"]  = vector.get("overall_risk_level", "LOW")
            combined_vector["reviewer_focus"]       = vector.get("reviewer_focus", "")
            combined_vector["recommendation"]       = vector.get("recommendation", "")
        combined_vector["hotspots"].extend(vector.get("hotspots", []))
        if vector.get("has_security_operations"):
            combined_vector["has_security_operations"] = True
        if not vector.get("has_test_indicators", True):
            combined_vector["has_test_indicators"] = False

    if not file_results:
        return {
            "pr":              pr,
            "files":           [],
            "ascent":          {},
            "summary_comment": "",
            "posted":          False,
            "errors":          errors or ["No files could be reviewed."],
        }

    # ── 4. ASCENT aggregation ──────────────────────────────────────────────
    log("ASCENT aggregating all findings...")
    ascent = aggregate_review(combined_clarion, combined_lumen, combined_vector)
    summary_comment = _format_summary_comment(pr["title"], ascent, file_results)

    # ── 5. Post to ADO (if not shadow mode) ───────────────────────────────
    posted = False
    if not shadow_mode:
        log("Posting summary comment to PR...")
        post_pr_summary(pr_id, summary_comment)

        log("Posting inline comments...")
        for file_r in file_results:
            path = file_r["path"]
            for v in file_r["clarion"].get("violations", []):
                line = v.get("line") or 1
                comment = _format_inline_comment(v, "CLARION")
                post_inline_comment(pr_id, path, line, comment)

            for s in file_r["lumen"].get("smells", []):
                comment = _format_inline_comment(s, "LUMEN")
                post_inline_comment(pr_id, path, 1, comment)

        posted = True
        log("All comments posted.")

    return {
        "pr":              pr,
        "files":           file_results,
        "ascent":          ascent,
        "summary_comment": summary_comment,
        "posted":          posted,
        "errors":          errors,
    }

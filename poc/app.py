"""
Project BlueLine — POC Demo
A Streamlit app demonstrating the three AI agent tracks:
  1. Quality Gate  (CLARION + LUMEN)
  2. Security Loop (BULWARK)
  3. Certificate Loop (TIMELINE)
"""

import os
import sys
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Project BlueLine — POC",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── helpers ────────────────────────────────────────────────────────────────────
SAMPLES_DIR = Path(__file__).parent / "samples"

def load_sample(filename: str) -> str:
    path = SAMPLES_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""

def severity_badge(severity: str) -> str:
    colours = {
        "error":    "#FF4B4B",
        "warning":  "#FFA500",
        "info":     "#1E90FF",
        "major":    "#FF4B4B",
        "minor":    "#FFA500",
    }
    col = colours.get(severity.lower(), "#888888")
    return f'<span style="background:{col};color:white;padding:2px 8px;border-radius:4px;font-size:0.8rem;font-weight:bold">{severity.upper()}</span>'

def classification_badge(classification: str) -> str:
    colours = {
        "CRITICAL":       "#FF0000",
        "HIGH":           "#FF4B4B",
        "NEEDS_REVIEW":   "#FFA500",
        "FALSE_POSITIVE": "#28A745",
    }
    col = colours.get(classification, "#888888")
    return f'<span style="background:{col};color:white;padding:4px 12px;border-radius:6px;font-size:1rem;font-weight:bold">{classification}</span>'

def urgency_badge(urgency: str) -> str:
    colours = {
        "EXPIRED":        "#FF0000",
        "CRITICAL":       "#FF4B4B",
        "URGENT":         "#FF8C00",
        "RENEWAL_NEEDED": "#FFA500",
        "MONITOR":        "#1E90FF",
        "OK":             "#28A745",
    }
    col = colours.get(urgency, "#888888")
    return f'<span style="background:{col};color:white;padding:4px 12px;border-radius:6px;font-size:1rem;font-weight:bold">{urgency}</span>'

def score_colour(score: int) -> str:
    if score >= 8:   return "#28A745"
    if score >= 5:   return "#FFA500"
    return "#FF4B4B"

def confidence_bar(confidence: float) -> str:
    pct = int(confidence * 100)
    col = "#28A745" if pct >= 80 else "#FFA500" if pct >= 60 else "#FF4B4B"
    return f"""
    <div style="background:#333;border-radius:4px;height:10px;width:100%">
      <div style="background:{col};border-radius:4px;height:10px;width:{pct}%"></div>
    </div>
    <small style="color:#aaa">{pct}% confidence</small>
    """

# ── sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔵 Project BlueLine")
    st.markdown("**AI-Powered Engineering Automation**")
    st.divider()
    st.markdown("""
**Three Tracks:**
- 🧑‍💻 Quality Gate
- 🔒 Security Loop
- 📜 Certificate Loop
    """)
    st.divider()

    # ── AI Provider Configuration ──
    st.markdown("#### AI Provider")

    provider_choice = st.radio(
        "Select Provider",
        ["Azure OpenAI (Company)", "Anthropic Claude (External)"],
        index=0,
        help="Use Azure OpenAI on company laptops — data stays in your Azure tenant."
    )

    if provider_choice == "Azure OpenAI (Company)":
        st.caption("✅ Data stays in your Azure tenant")
        az_endpoint = st.text_input(
            "Azure OpenAI Endpoint",
            value=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            placeholder="https://YOUR-RESOURCE.openai.azure.com/"
        )
        az_key = st.text_input(
            "Azure OpenAI API Key",
            type="password",
            value=os.getenv("AZURE_OPENAI_API_KEY", "")
        )
        az_deployment = st.text_input(
            "Deployment Name",
            value=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
            placeholder="gpt-4o"
        )
        if az_endpoint: os.environ["AZURE_OPENAI_ENDPOINT"]    = az_endpoint
        if az_key:      os.environ["AZURE_OPENAI_API_KEY"]     = az_key
        if az_deployment: os.environ["AZURE_OPENAI_DEPLOYMENT"] = az_deployment
        # clear anthropic key so it doesn't take over
        os.environ.pop("ANTHROPIC_API_KEY", None)

    else:
        st.caption("⚠️ Data sent to Anthropic servers (external)")
        ant_key = st.text_input(
            "Anthropic API Key",
            type="password",
            value=os.getenv("ANTHROPIC_API_KEY", "")
        )
        if ant_key:
            os.environ["ANTHROPIC_API_KEY"] = ant_key
        # clear azure keys so they don't take over
        os.environ.pop("AZURE_OPENAI_ENDPOINT", None)
        os.environ.pop("AZURE_OPENAI_API_KEY", None)

    # ── Show active provider status ──
    from utils.llm_client import get_active_provider
    active = get_active_provider()
    if active == "azure_openai":
        st.success("🟢 Connected: Azure OpenAI")
    elif active == "anthropic":
        st.warning("🟡 Connected: Anthropic (external)")
    else:
        st.error("🔴 Not configured — enter credentials above")

    st.divider()

    # ── Azure DevOps connection ──
    st.markdown("#### Azure DevOps")
    from utils.azure_devops import is_configured
    if is_configured():
        st.success("🟢 ADO Connected — Live PR Review enabled")
    else:
        st.warning("🟡 ADO not configured — add credentials to .env")
        st.caption("Required: ORG_URL, PAT, PROJECT, REPO — see .env.example")

    ado_org     = st.text_input("ADO Org URL",     value=os.getenv("AZURE_DEVOPS_ORG_URL",""),  placeholder="https://dev.azure.com/your-org", key="ado_org")
    ado_pat     = st.text_input("Personal Access Token", value=os.getenv("AZURE_DEVOPS_PAT",""), type="password", key="ado_pat")
    ado_project = st.text_input("Project",         value=os.getenv("AZURE_DEVOPS_PROJECT",""), placeholder="YourProjectName", key="ado_project")
    ado_repo    = st.text_input("Repository",      value=os.getenv("AZURE_DEVOPS_REPO",""),    placeholder="YourRepoName",    key="ado_repo")

    if ado_org:     os.environ["AZURE_DEVOPS_ORG_URL"]  = ado_org
    if ado_pat:     os.environ["AZURE_DEVOPS_PAT"]      = ado_pat
    if ado_project: os.environ["AZURE_DEVOPS_PROJECT"]  = ado_project
    if ado_repo:    os.environ["AZURE_DEVOPS_REPO"]     = ado_repo

    st.divider()
    st.caption("POC v1.0 — BlueLine Team")

# ── header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='color:#4A9EFF'>🔵 Project BlueLine</h1>
<p style='color:#aaa;font-size:1.1rem'>AI Agent POC — Quality Gate · Security Loop · Certificate Loop</p>
""", unsafe_allow_html=True)
st.divider()

# ── tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🧑‍💻  Quality Gate  (CLARION + LUMEN + VECTOR + ASCENT)",
    "🔒  Security Loop  (WATCHTOWER → BULWARK → FORGE → STEWARD)",
    "📜  Certificate Loop  (REGENT → TIMELINE → COURIER → HARBOUR)",
    "🔗  Live PR Review  (Azure DevOps)",
])


# ══════════════════════════════════════════════════════════════════════
# TAB 1 — QUALITY GATE
# ══════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Quality Gate — Full Code Review Pipeline")
    st.markdown(
        "All four agents run in sequence: **CLARION** checks standards → "
        "**LUMEN** detects smells → **VECTOR** scores risk → "
        "**ASCENT** consolidates into one final review."
    )

    col_left, col_right = st.columns([4, 6])

    with col_left:
        lang = st.selectbox("Language", ["csharp", "typescript"], key="lang")
        sample_map = {"csharp": "bad_csharp.cs", "typescript": "bad_typescript.ts"}

        if st.button("📂 Load Sample Code", key="load_sample"):
            st.session_state["code_input"] = load_sample(sample_map[lang])

        code_input = st.text_area(
            "Code to Review",
            value=st.session_state.get("code_input", ""),
            height=420,
            key="code_area",
            placeholder="Paste your C# or TypeScript code here..."
        )

        run_review = st.button("🔍 Run Full Review", type="primary", key="run_review")

        # Agent pipeline status indicators
        st.markdown("#### Agent Pipeline")
        status_clarion  = st.empty()
        status_lumen    = st.empty()
        status_vector   = st.empty()
        status_ascent   = st.empty()

        status_clarion.markdown("⬜ CLARION — waiting")
        status_lumen.markdown("⬜ LUMEN — waiting")
        status_vector.markdown("⬜ VECTOR — waiting")
        status_ascent.markdown("⬜ ASCENT — waiting")

    with col_right:
        if run_review:
            from utils.llm_client import get_active_provider
            if get_active_provider() == "none":
                st.error("No AI provider configured. Enter credentials in the sidebar.")
            elif not code_input.strip():
                st.warning("Please paste some code first.")
            else:
                from agents.clarion import review_code
                from agents.lumen   import detect_smells
                from agents.vector  import score_risk
                from agents.ascent  import aggregate_review

                # ── Run all 4 agents ──────────────────────────────
                status_clarion.markdown("🔄 CLARION — running...")
                clarion_result = review_code(code_input, lang)
                status_clarion.markdown("✅ CLARION — done")

                status_lumen.markdown("🔄 LUMEN — running...")
                lumen_result = detect_smells(code_input, lang)
                status_lumen.markdown("✅ LUMEN — done")

                status_vector.markdown("🔄 VECTOR — running...")
                vector_result = score_risk(code_input, lang)
                status_vector.markdown("✅ VECTOR — done")

                status_ascent.markdown("🔄 ASCENT — aggregating...")
                ascent_result = aggregate_review(clarion_result, lumen_result, vector_result, lang)
                status_ascent.markdown("✅ ASCENT — done")

                # ════════════════════════════════════════════════
                # ASCENT — Consolidated Summary (shown first)
                # ════════════════════════════════════════════════
                rec = ascent_result.get("recommendation", "REQUEST_CHANGES")
                rec_colours = {
                    "APPROVE":         ("#28A745", "APPROVE"),
                    "REQUEST_CHANGES": ("#FFA500", "REQUEST CHANGES"),
                    "BLOCK":           ("#FF0000", "BLOCK"),
                }
                rec_col, rec_label = rec_colours.get(rec, ("#888", rec))

                overall = ascent_result.get("overall_score", 0)
                oc = score_colour(overall)

                st.markdown(
                    f"""
                    <div style='background:#1a1a2e;border-radius:10px;padding:16px 20px;margin-bottom:16px'>
                      <div style='display:flex;align-items:center;gap:16px'>
                        <div>
                          <div style='color:#aaa;font-size:0.8rem;text-transform:uppercase'>ASCENT Recommendation</div>
                          <div style='color:{rec_col};font-size:1.6rem;font-weight:bold'>{rec_label}</div>
                        </div>
                        <div style='margin-left:auto;text-align:right'>
                          <div style='color:#aaa;font-size:0.8rem'>Overall Score</div>
                          <div style='color:{oc};font-size:1.6rem;font-weight:bold'>{overall}/10</div>
                        </div>
                      </div>
                      <div style='color:#ccc;margin-top:10px;font-size:0.95rem;line-height:1.5'>
                        {ascent_result.get("summary", "")}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Biggest risk callout
                if ascent_result.get("biggest_risk"):
                    st.markdown(
                        f"<div style='background:#3d1c1c;border-left:4px solid #FF4B4B;"
                        f"padding:10px 14px;border-radius:4px;color:#ffcccc;margin-bottom:12px'>"
                        f"<strong>Biggest Risk:</strong> {ascent_result['biggest_risk']}</div>",
                        unsafe_allow_html=True
                    )

                # ── Tier 1 — Must Fix ────────────────────────────
                t1 = ascent_result.get("tier1_must_fix", [])
                if t1:
                    st.markdown(f"#### ⛔ Must Fix Before Merge ({len(t1)})")
                    for item in t1:
                        with st.expander(
                            f"[{item.get('source','?')}] {item.get('issue','')[:80]}",
                            expanded=True
                        ):
                            st.markdown(
                                severity_badge("error"), unsafe_allow_html=True
                            )
                            st.markdown(f"**Issue:** {item.get('issue','')}")
                            st.markdown(f"**Action:** {item.get('action','')}")

                # ── Tier 2 — Should Fix ──────────────────────────
                t2 = ascent_result.get("tier2_should_fix", [])
                if t2:
                    st.markdown(f"#### ⚠️ Should Fix ({len(t2)})")
                    for item in t2:
                        with st.expander(
                            f"[{item.get('source','?')}] {item.get('issue','')[:80]}"
                        ):
                            st.markdown(
                                severity_badge("warning"), unsafe_allow_html=True
                            )
                            st.markdown(f"**Issue:** {item.get('issue','')}")
                            st.markdown(f"**Action:** {item.get('action','')}")

                # ── Tier 3 — Consider ────────────────────────────
                t3 = ascent_result.get("tier3_consider", [])
                if t3:
                    st.markdown(f"#### 💡 Consider Fixing ({len(t3)})")
                    for item in t3:
                        with st.expander(
                            f"[{item.get('source','?')}] {item.get('issue','')[:80]}"
                        ):
                            st.markdown(
                                severity_badge("info"), unsafe_allow_html=True
                            )
                            st.markdown(f"**Issue:** {item.get('issue','')}")
                            st.markdown(f"**Action:** {item.get('action','')}")

                # ── Reviewer Checklist ───────────────────────────
                checklist = ascent_result.get("reviewer_checklist", [])
                if checklist:
                    st.markdown("#### Reviewer Checklist")
                    for item in checklist:
                        st.markdown(f"- [ ] {item}")

                st.divider()

                # ════════════════════════════════════════════════
                # Individual Agent Results (collapsed by default)
                # ════════════════════════════════════════════════
                st.markdown("#### Individual Agent Reports")

                # ── CLARION detail ───────────────────────────────
                with st.expander(
                    f"CLARION — {len(clarion_result.get('violations',[]))} violation(s)  |  "
                    f"Score {clarion_result.get('overall_score',0)}/10"
                ):
                    violations = clarion_result.get("violations", [])
                    if violations:
                        for v in violations:
                            st.markdown(
                                f"{severity_badge(v.get('severity','info'))} "
                                f"**{v.get('rule','')}**"
                                + (f" — Line {v['line']}" if v.get('line') else ""),
                                unsafe_allow_html=True
                            )
                            st.caption(v.get("message", ""))
                            if v.get("fix"):
                                st.code(v["fix"], language=lang)
                            st.markdown(
                                confidence_bar(v.get("confidence", 0)),
                                unsafe_allow_html=True
                            )
                            st.markdown("---")
                    else:
                        st.success("No violations found.")

                # ── LUMEN detail ─────────────────────────────────
                with st.expander(
                    f"LUMEN — {len(lumen_result.get('smells',[]))} smell(s)  |  "
                    f"Maintainability {lumen_result.get('maintainability_score',0)}/10"
                ):
                    smells = lumen_result.get("smells", [])
                    if smells:
                        for s in smells:
                            effort_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(
                                s.get("effort", ""), "⚪"
                            )
                            st.markdown(
                                f"{severity_badge(s.get('severity','minor'))} "
                                f"**{s.get('type','')}** — {s.get('location','')}",
                                unsafe_allow_html=True
                            )
                            st.caption(s.get("description", ""))
                            st.markdown(f"**Refactor:** {s.get('refactor','')}  {effort_icon}")
                            st.markdown("---")
                    else:
                        st.success("No smells detected.")

                # ── VECTOR detail ────────────────────────────────
                with st.expander(
                    f"VECTOR — Risk: {vector_result.get('overall_risk_level','?')}  |  "
                    f"Score {vector_result.get('overall_risk_score', 0):.2f}"
                ):
                    metrics = vector_result.get("static_metrics", {})
                    if metrics:
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Cyclomatic Complexity", metrics.get("cyclomatic_complexity", "?"))
                        m2.metric("Max Nesting Depth",     metrics.get("max_nesting_depth", "?"))
                        m3.metric("Lines of Code",         metrics.get("lines_of_code", "?"))
                        m4, m5, m6 = st.columns(3)
                        m4.metric("Methods",               metrics.get("method_count", "?"))
                        m5.metric("Dependencies",          metrics.get("dependency_count", "?"))
                        m6.metric("Has Security Ops",
                                  "Yes" if metrics.get("has_security_ops") else "No")

                    hotspots = vector_result.get("hotspots", [])
                    if hotspots:
                        st.markdown("**Hotspots:**")
                        for h in hotspots:
                            rl = h.get("risk_level", "LOW")
                            col = {"CRITICAL":"#FF0000","HIGH":"#FF4B4B",
                                   "MEDIUM":"#FFA500","LOW":"#28A745"}.get(rl, "#888")
                            st.markdown(
                                f"<span style='color:{col};font-weight:bold'>{rl}</span> "
                                f"— **{h.get('name','')}**: {h.get('reason','')}",
                                unsafe_allow_html=True
                            )

                    if vector_result.get("reviewer_focus"):
                        st.info(vector_result["reviewer_focus"])

                # ════════════════════════════════════════════════
                # HUMAN LOOP — Reviewer Feedback Gate
                # ════════════════════════════════════════════════
                st.divider()
                st.markdown("#### Human Review Gate")
                st.caption(
                    "In production this happens on the Azure DevOps PR — "
                    "reviewer reacts to each comment and posts their decision. "
                    "In this POC you submit feedback here. "
                    "ASCENT uses this to track false positive rates per rule."
                )

                # Store results in session so feedback form persists
                st.session_state["last_ascent"]  = ascent_result
                st.session_state["last_clarion"] = clarion_result
                st.session_state["last_lumen"]   = lumen_result
                st.session_state["review_done"]  = True

        # ── Human feedback form (shown after any completed review) ──
        if st.session_state.get("review_done"):
            ascent_r  = st.session_state.get("last_ascent", {})
            clarion_r = st.session_state.get("last_clarion", {})
            lumen_r   = st.session_state.get("last_lumen", {})

            all_findings = []
            for item in ascent_r.get("tier1_must_fix", []):
                all_findings.append({"tier": "Must Fix",    "item": item})
            for item in ascent_r.get("tier2_should_fix", []):
                all_findings.append({"tier": "Should Fix",  "item": item})
            for item in ascent_r.get("tier3_consider", []):
                all_findings.append({"tier": "Consider",    "item": item})

            with st.form("human_review_form"):
                st.markdown("**Step 1 — React to each finding**")
                st.caption("Mark each finding as Agree (AI was correct) or False Positive (AI was wrong)")

                reactions = {}
                for idx, finding in enumerate(all_findings):
                    item  = finding["item"]
                    tier  = finding["tier"]
                    label = f"[{item.get('source','?')}] {item.get('issue','')[:70]}"

                    col_label, col_react = st.columns([5, 2])
                    with col_label:
                        tier_col = {
                            "Must Fix":   "#FF4B4B",
                            "Should Fix": "#FFA500",
                            "Consider":   "#1E90FF"
                        }.get(tier, "#888")
                        st.markdown(
                            f"<small style='color:{tier_col};font-weight:bold'>{tier}</small><br>{label}",
                            unsafe_allow_html=True
                        )
                    with col_react:
                        reaction = st.radio(
                            f"reaction_{idx}",
                            ["Agree", "False Positive"],
                            horizontal=True,
                            label_visibility="collapsed",
                            key=f"react_{idx}"
                        )
                        reactions[idx] = {
                            "source":   item.get("source", ""),
                            "issue":    item.get("issue", ""),
                            "reaction": reaction
                        }

                st.markdown("**Step 2 — Override ASCENT recommendation (optional)**")
                ai_rec = ascent_r.get("recommendation", "REQUEST_CHANGES")
                human_decision = st.radio(
                    "Your final decision",
                    ["Keep AI recommendation", "APPROVE", "REQUEST_CHANGES", "BLOCK"],
                    horizontal=True,
                    key="human_decision"
                )

                st.markdown("**Step 3 — Add reviewer comment (optional)**")
                reviewer_comment = st.text_area(
                    "Comment for the developer",
                    placeholder="e.g. The SQL injection fix is critical — please also check OrderRepository.cs which has the same pattern.",
                    height=80,
                    key="reviewer_comment"
                )

                submitted = st.form_submit_button(
                    "Submit Human Review",
                    type="primary",
                    use_container_width=True
                )

            if submitted:
                # ── Calculate feedback stats ──────────────────
                agreed        = [r for r in reactions.values() if r["reaction"] == "Agree"]
                false_pos     = [r for r in reactions.values() if r["reaction"] == "False Positive"]
                fp_rate       = len(false_pos) / len(reactions) if reactions else 0

                final_decision = (
                    ai_rec if human_decision == "Keep AI recommendation"
                    else human_decision
                )

                # ── Show submitted summary ────────────────────
                decision_colours = {
                    "APPROVE":         "#28A745",
                    "REQUEST_CHANGES": "#FFA500",
                    "BLOCK":           "#FF0000"
                }
                dc = decision_colours.get(final_decision, "#888")

                st.markdown(
                    f"""
                    <div style='background:#0d1f0d;border:1px solid #28A745;
                    border-radius:10px;padding:16px 20px;margin-top:12px'>
                      <div style='color:#28A745;font-size:1.1rem;font-weight:bold;
                      margin-bottom:8px'>Human Review Submitted</div>
                      <div style='display:flex;gap:32px;flex-wrap:wrap'>
                        <div>
                          <div style='color:#aaa;font-size:0.8rem'>Final Decision</div>
                          <div style='color:{dc};font-size:1.3rem;font-weight:bold'>
                          {final_decision}</div>
                        </div>
                        <div>
                          <div style='color:#aaa;font-size:0.8rem'>Findings Agreed</div>
                          <div style='color:#28A745;font-size:1.3rem;font-weight:bold'>
                          {len(agreed)} / {len(reactions)}</div>
                        </div>
                        <div>
                          <div style='color:#aaa;font-size:0.8rem'>False Positives</div>
                          <div style='color:{"#FF4B4B" if false_pos else "#28A745"};
                          font-size:1.3rem;font-weight:bold'>
                          {len(false_pos)} ({fp_rate:.0%})</div>
                        </div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if reviewer_comment.strip():
                    st.info(f"Reviewer comment: *{reviewer_comment.strip()}*")

                # ── False positive feedback to ASCENT ─────────
                if false_pos:
                    st.markdown("**ASCENT would log the following false positives:**")
                    for fp in false_pos:
                        st.markdown(
                            f"- `{fp['source']}` flagged **\"{fp['issue'][:60]}\"** "
                            f"as false positive — rule confidence will be reduced"
                        )
                    if fp_rate > 0.20:
                        st.warning(
                            f"False positive rate is {fp_rate:.0%} — above the 20% threshold. "
                            f"In production, ASCENT would flag these rules for engineering review "
                            f"and notify the Engineering Lead."
                        )

                # ── Decision mismatch note ────────────────────
                if final_decision != ai_rec:
                    st.markdown(
                        f"> Human overrode ASCENT's **{ai_rec}** to **{final_decision}**. "
                        f"In production this override is logged to the audit trail "
                        f"and feeds back into ASCENT's confidence calibration."
                    )
                else:
                    st.success("Human decision matches ASCENT recommendation — no override needed.")

        else:
            st.info("👈 Load sample code or paste your own, then click **Run Full Review**.")


# ══════════════════════════════════════════════════════════════════════
# TAB 2 — SECURITY LOOP  (WATCHTOWER → BULWARK → FORGE → STEWARD)
# ══════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Security Loop — Full 4-Agent Pipeline")
    st.markdown(
        "**WATCHTOWER** discovers the finding → **BULWARK** triages it → "
        "**FORGE** creates a draft fix PR → **STEWARD** writes the audit log entry."
    )

    col_l, col_r = st.columns([1, 1])

    with col_l:
        # ── WATCHTOWER (simulated input) ─────────────────────────────
        st.markdown("#### WATCHTOWER — Finding Input")
        st.caption(
            "In production WATCHTOWER polls Fortify SSC on a schedule and publishes "
            "findings to Azure Service Bus. Here you provide the finding manually."
        )

        if st.button("📂 Load Sample Finding", key="load_finding"):
            st.session_state["finding_input"] = load_sample("fortify_finding.txt")
            st.session_state["code_input_sec"] = ""

        finding_input = st.text_area(
            "Fortify Finding Description",
            value=st.session_state.get("finding_input", ""),
            height=180,
            key="finding_area",
            placeholder="Paste the Fortify finding description or describe the vulnerability..."
        )

        code_sec = st.text_area(
            "Vulnerable Code Snippet (optional)",
            value=st.session_state.get("code_input_sec", ""),
            height=150,
            key="code_sec_area",
            placeholder="Paste the vulnerable code here for a more precise fix..."
        )

        affected_file = st.text_input(
            "Affected File (optional)",
            value="OrdersController.cs",
            key="affected_file",
            placeholder="e.g. OrdersController.cs"
        )

        # ── Agent pipeline status ────────────────────────────────────
        st.markdown("#### Agent Pipeline")
        st_watchtower = st.empty()
        st_bulwark    = st.empty()
        st_forge      = st.empty()
        st_steward    = st.empty()

        st_watchtower.markdown("⬜ WATCHTOWER — waiting")
        st_bulwark.markdown("⬜ BULWARK — waiting")
        st_forge.markdown("⬜ FORGE — waiting")
        st_steward.markdown("⬜ STEWARD — waiting")

        run_triage = st.button("🔒 Run Security Pipeline", type="primary", key="run_triage")

    with col_r:
        if run_triage:
            from utils.llm_client import get_active_provider
            if get_active_provider() == "none":
                st.error("No AI provider configured. Enter credentials in the sidebar.")
            elif not finding_input.strip():
                st.warning("Please describe the finding first.")
            else:
                from agents.bulwark import triage_finding
                from agents.forge   import create_fix_pr
                from agents.steward import create_audit_entry

                # ── WATCHTOWER ───────────────────────────────────────
                st_watchtower.markdown("✅ WATCHTOWER — finding received from Fortify")
                st.markdown(
                    "<div style='background:#1a2a1a;border-left:3px solid #28A745;"
                    "padding:8px 14px;border-radius:4px;margin-bottom:12px'>"
                    "<small style='color:#28A745;font-weight:bold'>WATCHTOWER</small><br>"
                    "<span style='color:#ccc'>1 new finding published to Service Bus → BULWARK picked up</span>"
                    "</div>",
                    unsafe_allow_html=True
                )

                # ── BULWARK ──────────────────────────────────────────
                st_bulwark.markdown("🔄 BULWARK — triaging...")
                bulwark_result = triage_finding(finding_input, code_sec)
                st_bulwark.markdown("✅ BULWARK — triage complete")

                classification = bulwark_result.get("classification", "NEEDS_REVIEW")
                confidence     = bulwark_result.get("confidence", 0.0)
                owasp          = bulwark_result.get("owasp_category", "")

                st.markdown("#### BULWARK — Triage Result")
                st.markdown(
                    f"**Classification:** {classification_badge(classification)}",
                    unsafe_allow_html=True
                )
                st.markdown(confidence_bar(confidence), unsafe_allow_html=True)
                st.divider()

                if owasp:
                    st.markdown(f"**OWASP Category:** `{owasp}`")
                if bulwark_result.get("attack_scenario"):
                    st.markdown("**Attack Scenario:**")
                    st.warning(bulwark_result["attack_scenario"])
                if bulwark_result.get("affected_systems"):
                    st.markdown(f"**At Risk:** {bulwark_result['affected_systems']}")
                if classification == "FALSE_POSITIVE" and bulwark_result.get("false_positive_reason"):
                    st.success(f"**Why False Positive:** {bulwark_result['false_positive_reason']}")
                if bulwark_result.get("recommendation"):
                    st.info(bulwark_result["recommendation"])

                secure_fix = bulwark_result.get("secure_code_example", "")
                if secure_fix:
                    st.markdown("**Secure Code Fix:**")
                    st.code(secure_fix, language="csharp")

                st.divider()

                # ── FORGE — only for CRITICAL or HIGH ────────────────
                if classification in ("CRITICAL", "HIGH"):
                    st_forge.markdown("🔄 FORGE — creating draft PR...")
                    forge_result = create_fix_pr(
                        finding_description=finding_input,
                        classification=classification,
                        owasp_category=owasp,
                        secure_code_fix=secure_fix,
                        affected_file=affected_file,
                    )
                    st_forge.markdown("✅ FORGE — draft PR ready")

                    st.markdown("#### FORGE — Draft Pull Request")
                    st.markdown(
                        f"<div style='background:#1a1a2e;border-radius:8px;padding:14px 18px'>"
                        f"<div style='color:#aaa;font-size:0.8rem'>Branch</div>"
                        f"<div style='color:#4A9EFF;font-family:monospace'>{forge_result.get('branch_name','')}</div>"
                        f"<div style='color:#aaa;font-size:0.8rem;margin-top:8px'>Commit Message</div>"
                        f"<div style='color:#ccc;font-family:monospace;font-size:0.9rem'>{forge_result.get('commit_message','')}</div>"
                        f"<div style='color:#aaa;font-size:0.8rem;margin-top:8px'>PR Title</div>"
                        f"<div style='color:#fff;font-weight:bold'>{forge_result.get('pr_title','')}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                    if forge_result.get("pr_description"):
                        with st.expander("PR Description (Markdown preview)"):
                            st.markdown(forge_result["pr_description"])

                    if forge_result.get("files_to_modify"):
                        st.markdown(f"**Files to modify:** `{'`, `'.join(forge_result['files_to_modify'])}`")

                    if forge_result.get("reviewer_note"):
                        st.info(f"**Reviewer Note:** {forge_result['reviewer_note']}")

                    st.markdown(
                        "<div style='background:#2a1a1a;border-left:3px solid #FFA500;"
                        "padding:8px 14px;border-radius:4px'>"
                        "<small style='color:#FFA500;font-weight:bold'>DRAFT PR — Human Approval Required</small><br>"
                        "<span style='color:#ccc'>FORGE never merges code. The developer reviews and approves this draft before anything is merged.</span>"
                        "</div>",
                        unsafe_allow_html=True
                    )

                    st.divider()
                else:
                    st_forge.markdown(
                        f"⏭️ FORGE — skipped (classification is {classification}, not CRITICAL/HIGH)"
                    )

                # ── STEWARD ──────────────────────────────────────────
                st_steward.markdown("🔄 STEWARD — writing audit log...")
                action = (
                    f"FORGE created draft PR: {forge_result.get('branch_name','N/A')}"
                    if classification in ("CRITICAL", "HIGH") and "forge_result" in dir()
                    else f"BULWARK classified as {classification} — no FORGE action required"
                )
                audit_entry = create_audit_entry(
                    pipeline          = "Security Loop",
                    finding_summary   = finding_input,
                    classification    = classification,
                    confidence        = confidence,
                    action_taken      = action,
                    agents_involved   = ["WATCHTOWER", "BULWARK", "FORGE", "STEWARD"]
                    if classification in ("CRITICAL", "HIGH")
                    else ["WATCHTOWER", "BULWARK", "STEWARD"],
                    human_gate_required = classification in ("CRITICAL", "HIGH"),
                )
                st_steward.markdown("✅ STEWARD — audit entry written")

                st.markdown("#### STEWARD — Audit Log Entry")
                st.markdown(
                    "<div style='background:#111;border:1px solid #333;border-radius:8px;"
                    "padding:14px 18px;font-family:monospace;font-size:0.82rem'>"
                    + "<br>".join(
                        f"<span style='color:#555'>{k}:</span> "
                        f"<span style='color:#a8d8a8'>{v}</span>"
                        for k, v in audit_entry.items()
                    )
                    + "</div>",
                    unsafe_allow_html=True
                )
                st.caption("In production this entry is written to Azure Blob Storage (immutable, 7-year retention).")

        else:
            st.info("👈 Load a sample finding or describe the vulnerability, then click **Run Security Pipeline**.")


# ══════════════════════════════════════════════════════════════════════
# TAB 3 — CERTIFICATE LOOP  (REGENT → TIMELINE → COURIER → HARBOUR)
# ══════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### Certificate Loop — Full 4-Agent Pipeline")
    st.markdown(
        "**REGENT** manages the inventory → **TIMELINE** analyses expiry → "
        "**COURIER** requests renewal from the CA → **HARBOUR** deploys and awaits Prod approval."
    )

    # ── REGENT — Inventory ───────────────────────────────────────────
    from agents.regent import get_inventory, get_cert_by_name

    st.markdown("#### REGENT — Certificate Inventory")
    st.caption("In production REGENT reads from Azure Key Vault + Azure Table Storage. POC uses a sample inventory.")

    inventory = get_inventory()

    status_colours = {
        "EXPIRED":        "#FF0000",
        "CRITICAL":       "#FF4B4B",
        "URGENT":         "#FF8C00",
        "RENEWAL_NEEDED": "#FFA500",
        "MONITOR":        "#1E90FF",
        "OK":             "#28A745",
    }

    inv_cols = st.columns([3, 2, 1, 2, 2])
    inv_cols[0].markdown("**Certificate**")
    inv_cols[1].markdown("**Expiry**")
    inv_cols[2].markdown("**Days**")
    inv_cols[3].markdown("**Status**")
    inv_cols[4].markdown("**Owner**")

    for cert in inventory:
        c = st.columns([3, 2, 1, 2, 2])
        c[0].markdown(f"`{cert['name']}`")
        c[1].markdown(cert["expiry_date"])
        days_val = cert["days_remaining"]
        days_col = status_colours.get(cert["status"], "#888")
        c[2].markdown(
            f"<span style='color:{days_col};font-weight:bold'>{days_val}</span>",
            unsafe_allow_html=True
        )
        c[3].markdown(
            f"<span style='background:{days_col};color:white;padding:2px 8px;"
            f"border-radius:4px;font-size:0.78rem;font-weight:bold'>{cert['status']}</span>",
            unsafe_allow_html=True
        )
        c[4].markdown(cert["owner"])

    st.divider()

    # ── Select cert to run pipeline on ──────────────────────────────
    col_a, col_b = st.columns([1, 1])

    with col_a:
        cert_names = [c["name"] for c in inventory]
        selected_cert_name = st.selectbox(
            "Select Certificate to Analyse",
            cert_names,
            key="selected_cert"
        )
        selected_cert = get_cert_by_name(selected_cert_name)

        if selected_cert:
            st.markdown(
                f"**CA:** {selected_cert['ca_type']}  \n"
                f"**Environments:** {', '.join(selected_cert['environments'])}  \n"
                f"**Targets:** {', '.join(selected_cert['deployment_targets'])}"
            )

        # ── Agent pipeline status ────────────────────────────────────
        st.markdown("#### Agent Pipeline")
        st_regent   = st.empty()
        st_timeline = st.empty()
        st_courier  = st.empty()
        st_harbour  = st.empty()

        st_regent.markdown("⬜ REGENT — waiting")
        st_timeline.markdown("⬜ TIMELINE — waiting")
        st_courier.markdown("⬜ COURIER — waiting")
        st_harbour.markdown("⬜ HARBOUR — waiting")

        run_cert = st.button("📜 Run Certificate Pipeline", type="primary", key="run_cert")

    with col_b:
        if run_cert and selected_cert:
            from utils.llm_client import get_active_provider
            if get_active_provider() == "none":
                st.error("No AI provider configured. Enter credentials in the sidebar.")
            else:
                from agents.timeline import analyse_certificate
                from agents.courier  import request_certificate
                from agents.harbour  import deploy_certificate

                # ── REGENT ───────────────────────────────────────────
                st_regent.markdown("✅ REGENT — certificate retrieved from inventory")
                st.markdown(
                    f"<div style='background:#1a2a1a;border-left:3px solid #28A745;"
                    f"padding:8px 14px;border-radius:4px;margin-bottom:12px'>"
                    f"<small style='color:#28A745;font-weight:bold'>REGENT</small><br>"
                    f"<span style='color:#ccc'>Retrieved <code>{selected_cert['name']}</code> — "
                    f"{selected_cert['days_remaining']} days remaining — published to pipeline</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

                # ── TIMELINE ─────────────────────────────────────────
                st_timeline.markdown("🔄 TIMELINE — analysing...")
                timeline_result = analyse_certificate(
                    subject      = selected_cert["subject"],
                    expiry_date  = selected_cert["expiry_date"],
                    environments = ", ".join(selected_cert["environments"]),
                    ca_type      = selected_cert["ca_type"],
                )
                st_timeline.markdown("✅ TIMELINE — analysis complete")

                urgency = timeline_result.get("urgency", "MONITOR")
                days    = timeline_result.get("days_until_expiry", "?")

                st.markdown("#### TIMELINE — Expiry Analysis")
                st.markdown(
                    f"**Urgency:** {urgency_badge(urgency)}  &nbsp;&nbsp; "
                    f"**Days Remaining:** <span style='font-size:1.3rem;font-weight:bold'>{days}</span>",
                    unsafe_allow_html=True
                )
                if timeline_result.get("summary"):
                    st.markdown(f"*{timeline_result['summary']}*")

                renewal_path = timeline_result.get("renewal_path", "unknown")
                path_icons   = {"internal_pki": "🏢", "external_ca": "🌐", "letsencrypt": "🔒", "unknown": "❓"}
                st.markdown(f"**Renewal Path:** {path_icons.get(renewal_path,'❓')} `{renewal_path.replace('_',' ').title()}`")

                steps = timeline_result.get("action_plan", [])
                if steps:
                    with st.expander("TIMELINE Action Plan"):
                        for i, step in enumerate(steps, 1):
                            st.markdown(f"{i}. {step}")

                risks = timeline_result.get("risks", [])
                for r in risks:
                    st.warning(r)

                st.divider()

                # ── COURIER — only for actionable urgency ────────────
                trigger_statuses = {"EXPIRED", "CRITICAL", "URGENT", "RENEWAL_NEEDED"}
                if urgency in trigger_statuses:
                    st_courier.markdown("🔄 COURIER — requesting renewal from CA...")
                    courier_result = request_certificate(
                        subject        = selected_cert["subject"],
                        ca_type        = selected_cert["ca_type"],
                        environments   = ", ".join(selected_cert["environments"]),
                        days_remaining = selected_cert["days_remaining"],
                    )
                    st_courier.markdown("✅ COURIER — certificate renewal requested")

                    st.markdown("#### COURIER — CA Renewal Request")
                    st.markdown(
                        f"<div style='background:#1a1a2e;border-radius:8px;padding:14px 18px'>"
                        f"<div style='color:#aaa;font-size:0.8rem'>Request</div>"
                        f"<div style='color:#ccc'>{courier_result.get('request_summary','')}</div>"
                        f"<div style='display:flex;gap:24px;margin-top:10px;flex-wrap:wrap'>"
                        f"<div><div style='color:#aaa;font-size:0.75rem'>Order ID</div>"
                        f"<div style='color:#4A9EFF;font-family:monospace'>{courier_result.get('ca_order_id','')}</div></div>"
                        f"<div><div style='color:#aaa;font-size:0.75rem'>Validation</div>"
                        f"<div style='color:#ccc'>{courier_result.get('validation_method','')}</div></div>"
                        f"<div><div style='color:#aaa;font-size:0.75rem'>Delivery</div>"
                        f"<div style='color:#ccc'>{courier_result.get('estimated_delivery','')}</div></div>"
                        f"<div><div style='color:#aaa;font-size:0.75rem'>Format</div>"
                        f"<div style='color:#ccc'>{courier_result.get('cert_format','PFX')}</div></div>"
                        f"</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                    if courier_result.get("simulated_thumbprint"):
                        st.markdown(
                            f"**New Cert Thumbprint:** "
                            f"`{courier_result['simulated_thumbprint'][:32]}...`"
                        )

                    st.caption(courier_result.get("simulation_note", ""))
                    st.divider()

                    # ── HARBOUR ──────────────────────────────────────
                    st_harbour.markdown("🔄 HARBOUR — generating deployment plan...")
                    harbour_result = deploy_certificate(
                        subject                 = selected_cert["subject"],
                        ca_type                 = selected_cert["ca_type"],
                        environments            = selected_cert["environments"],
                        deployment_targets      = selected_cert["deployment_targets"],
                        cert_thumbprint         = courier_result.get("simulated_thumbprint", "SIMULATED"),
                        days_remaining_old_cert = selected_cert["days_remaining"],
                    )
                    st_harbour.markdown("✅ HARBOUR — Dev & QA deployed · Prod awaiting approval")

                    st.markdown("#### HARBOUR — Deployment Plan")

                    for env_plan in harbour_result.get("deployment_plan", []):
                        env_name = env_plan.get("environment", "")
                        status   = env_plan.get("status", "")
                        is_prod  = env_name == "Production"
                        bg       = "#2a1a1a" if is_prod else "#1a2a1a"
                        border   = "#FFA500" if is_prod else "#28A745"
                        status_label = "⏳ Awaiting Approval" if is_prod else "✅ Simulated Success"

                        st.markdown(
                            f"<div style='background:{bg};border-left:3px solid {border};"
                            f"padding:10px 14px;border-radius:4px;margin-bottom:8px'>"
                            f"<strong style='color:#fff'>{env_name}</strong> — "
                            f"<span style='color:#aaa'>{env_plan.get('target','')}</span> "
                            f"<span style='float:right'>{status_label}</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

                        cmds = env_plan.get("commands", [])
                        if cmds:
                            with st.expander(f"Commands — {env_name}"):
                                st.code("\n".join(cmds), language="powershell")

                        if env_plan.get("https_verification"):
                            st.caption(f"Verify: `{env_plan['https_verification']}`")

                    # ── Teams approval card ───────────────────────────
                    teams_card = harbour_result.get("teams_approval_card", {})
                    if teams_card:
                        st.divider()
                        st.markdown("#### Teams Approval Card — Sent to Channel")
                        st.markdown(
                            f"<div style='background:#1f1f3a;border:1px solid #4A9EFF;"
                            f"border-radius:10px;padding:18px 20px'>"
                            f"<div style='color:#4A9EFF;font-size:1.1rem;font-weight:bold;margin-bottom:8px'>"
                            f"{teams_card.get('title','')}</div>"
                            f"<div style='color:#ccc;margin-bottom:12px'>{teams_card.get('body','')}</div>"
                            f"<div style='display:flex;gap:10px'>"
                            f"<div style='background:#28A745;color:white;padding:6px 16px;"
                            f"border-radius:6px;font-weight:bold'>{teams_card.get('approve_action','Approve')}</div>"
                            f"<div style='background:#555;color:white;padding:6px 16px;"
                            f"border-radius:6px'>{teams_card.get('reject_action','Hold')}</div>"
                            f"</div></div>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            "<div style='background:#2a1a1a;border-left:3px solid #FFA500;"
                            "padding:8px 14px;border-radius:4px;margin-top:8px'>"
                            "<small style='color:#FFA500;font-weight:bold'>PRODUCTION GATE — Human Approval Required</small><br>"
                            "<span style='color:#ccc'>HARBOUR will not deploy to Production until a human clicks Approve in Teams.</span>"
                            "</div>",
                            unsafe_allow_html=True
                        )
                        st.caption(harbour_result.get("simulation_note", ""))

                else:
                    st_courier.markdown(f"⏭️ COURIER — skipped (urgency is {urgency}, no renewal needed yet)")
                    st_harbour.markdown("⏭️ HARBOUR — skipped (no new certificate to deploy)")
                    st.info(f"Certificate urgency is **{urgency}** — no renewal action required at this time. TIMELINE will monitor and trigger COURIER when it reaches RENEWAL_NEEDED.")

        elif run_cert and not selected_cert:
            st.warning("Could not load selected certificate from inventory.")
        else:
            st.info("👈 Select a certificate from the inventory above, then click **Run Certificate Pipeline**.")

# ══════════════════════════════════════════════════════════════════════
# TAB 4 — LIVE PR REVIEW (Azure DevOps)
# ══════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### Live PR Review — Azure DevOps Integration")
    st.markdown(
        "Connect to your Azure DevOps repo, pick an open PR, and BlueLine will "
        "fetch the real code, run all 4 agents, and post findings back as PR comments."
    )

    from utils.azure_devops import is_configured, list_pull_requests

    if not is_configured():
        st.error(
            "Azure DevOps not configured. "
            "Enter your Org URL, PAT, Project, and Repo in the sidebar, "
            "or add them to your .env file."
        )
        st.code("""
# .env — fill in these 4 values
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/your-org
AZURE_DEVOPS_PAT=your-pat-here
AZURE_DEVOPS_PROJECT=YourProject
AZURE_DEVOPS_REPO=YourRepo
        """)
        st.stop()

    # ── Shadow mode toggle ──────────────────────────────────────────
    col_sh1, col_sh2 = st.columns([3, 1])
    with col_sh1:
        st.markdown("**Shadow Mode**")
        st.caption(
            "ON = agents review the PR and show results here, but nothing is posted to Azure DevOps.  \n"
            "OFF = findings are posted as real comments on the PR."
        )
    with col_sh2:
        shadow_mode = st.toggle("Shadow Mode", value=True, key="shadow_toggle")
        if shadow_mode:
            st.markdown("<span style='color:#FFA500;font-weight:bold'>ON — read only</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:#FF4B4B;font-weight:bold'>OFF — will POST</span>", unsafe_allow_html=True)

    st.divider()

    # ── Load PR list ────────────────────────────────────────────────
    col_pr1, col_pr2 = st.columns([4, 1])
    with col_pr2:
        refresh = st.button("🔄 Refresh PRs", key="refresh_prs")

    if "pr_list" not in st.session_state or refresh:
        with st.spinner("Fetching open PRs from Azure DevOps..."):
            try:
                st.session_state["pr_list"] = list_pull_requests(status="active", top=30)
            except Exception as ex:
                st.error(f"Could not connect to Azure DevOps: {ex}")
                st.session_state["pr_list"] = []

    prs = st.session_state.get("pr_list", [])

    if not prs:
        st.info("No active pull requests found in this repo.")
    else:
        with col_pr1:
            pr_options = {
                f"PR #{p['id']} — {p['title']} ({p['created_by']})" : p["id"]
                for p in prs
            }
            selected_label = st.selectbox("Select a Pull Request", list(pr_options.keys()), key="pr_select")
            selected_pr_id = pr_options[selected_label]

        selected_pr = next(p for p in prs if p["id"] == selected_pr_id)
        st.markdown(
            f"**Branch:** `{selected_pr['source_branch']}` → `{selected_pr['target_branch']}`  "
            f"&nbsp;|&nbsp; **Created by:** {selected_pr['created_by']}"
        )

        run_live = st.button("🔍 Run Quality Gate on this PR", type="primary", key="run_live")

        if run_live:
            if get_active_provider() == "none":
                st.error("No AI provider configured. Enter Azure OpenAI credentials in the sidebar.")
            else:
                from utils.pr_runner import run_pr_review

                status_log = st.empty()
                log_lines  = []

                def progress(msg):
                    log_lines.append(msg)
                    status_log.markdown(
                        "<div style='background:#111;padding:10px;border-radius:6px;font-family:monospace;font-size:0.85rem'>"
                        + "<br>".join(f"▸ {l}" for l in log_lines[-8:])
                        + "</div>",
                        unsafe_allow_html=True
                    )

                with st.spinner("Running Quality Gate..."):
                    try:
                        result = run_pr_review(
                            pr_id=selected_pr_id,
                            shadow_mode=shadow_mode,
                            progress_callback=progress,
                        )
                        st.session_state["live_review_result"] = result
                    except Exception as ex:
                        st.error(f"Review failed: {ex}")
                        result = None

                if result:
                    status_log.empty()

                    # ── Errors ───────────────────────────────────────
                    for err in result.get("errors", []):
                        st.warning(err)

                    ascent  = result.get("ascent", {})
                    files   = result.get("files", [])
                    posted  = result.get("posted", False)

                    if not ascent:
                        st.error("No results returned — check errors above.")
                    else:
                        # ── ASCENT header ─────────────────────────────
                        rec = ascent.get("recommendation", "REQUEST_CHANGES")
                        rec_colours = {
                            "APPROVE":         ("#28A745", "APPROVE"),
                            "REQUEST_CHANGES": ("#FFA500", "REQUEST CHANGES"),
                            "BLOCK":           ("#FF0000", "BLOCK"),
                        }
                        rec_col, rec_label = rec_colours.get(rec, ("#888", rec))
                        overall = ascent.get("overall_score", 0)
                        oc = score_colour(overall)

                        st.markdown(
                            f"""
                            <div style='background:#1a1a2e;border-radius:10px;padding:16px 20px;margin-bottom:16px'>
                              <div style='display:flex;align-items:center;gap:16px'>
                                <div>
                                  <div style='color:#aaa;font-size:0.8rem'>ASCENT Recommendation</div>
                                  <div style='color:{rec_col};font-size:1.6rem;font-weight:bold'>{rec_label}</div>
                                </div>
                                <div style='margin-left:auto;text-align:right'>
                                  <div style='color:#aaa;font-size:0.8rem'>Overall Score</div>
                                  <div style='color:{oc};font-size:1.6rem;font-weight:bold'>{overall}/10</div>
                                </div>
                              </div>
                              <div style='color:#ccc;margin-top:10px;font-size:0.95rem'>
                                {ascent.get("summary","")}
                              </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if ascent.get("biggest_risk"):
                            st.markdown(
                                f"<div style='background:#3d1c1c;border-left:4px solid #FF4B4B;"
                                f"padding:10px 14px;border-radius:4px;color:#ffcccc;margin-bottom:12px'>"
                                f"<strong>Biggest Risk:</strong> {ascent['biggest_risk']}</div>",
                                unsafe_allow_html=True
                            )

                        # ── Tiers ─────────────────────────────────────
                        t1 = ascent.get("tier1_must_fix", [])
                        if t1:
                            st.markdown(f"#### ⛔ Must Fix Before Merge ({len(t1)})")
                            for item in t1:
                                with st.expander(f"[{item.get('source','?')}] {item.get('issue','')[:80]}", expanded=True):
                                    st.markdown(severity_badge("error"), unsafe_allow_html=True)
                                    st.markdown(f"**Issue:** {item.get('issue','')}")
                                    st.markdown(f"**Action:** {item.get('action','')}")

                        t2 = ascent.get("tier2_should_fix", [])
                        if t2:
                            st.markdown(f"#### ⚠️ Should Fix ({len(t2)})")
                            for item in t2:
                                with st.expander(f"[{item.get('source','?')}] {item.get('issue','')[:80]}"):
                                    st.markdown(severity_badge("warning"), unsafe_allow_html=True)
                                    st.markdown(f"**Issue:** {item.get('issue','')}")
                                    st.markdown(f"**Action:** {item.get('action','')}")

                        t3 = ascent.get("tier3_consider", [])
                        if t3:
                            st.markdown(f"#### 💡 Consider ({len(t3)})")
                            for item in t3:
                                with st.expander(f"[{item.get('source','?')}] {item.get('issue','')[:80]}"):
                                    st.markdown(f"**Issue:** {item.get('issue','')}")
                                    st.markdown(f"**Action:** {item.get('action','')}")

                        checklist = ascent.get("reviewer_checklist", [])
                        if checklist:
                            st.markdown("#### Reviewer Checklist")
                            for item in checklist:
                                st.markdown(f"- [ ] {item}")

                        st.divider()

                        # ── Per-file breakdown ────────────────────────
                        st.markdown(f"#### Files Reviewed ({len(files)})")
                        for file_r in files:
                            fname  = file_r["path"].split("/")[-1]
                            v_count = len(file_r["clarion"].get("violations", []))
                            s_count = len(file_r["lumen"].get("smells", []))
                            risk    = file_r["vector"].get("overall_risk_level", "?")
                            risk_col = {"CRITICAL":"#FF0000","HIGH":"#FF4B4B","MEDIUM":"#FFA500","LOW":"#28A745"}.get(risk,"#888")

                            with st.expander(
                                f"{fname}  |  "
                                f"{v_count} violation(s)  |  "
                                f"{s_count} smell(s)  |  "
                                f"Risk: {risk}"
                            ):
                                st.markdown(f"**Full path:** `{file_r['path']}`")
                                st.markdown(
                                    f"**Risk Level:** <span style='color:{risk_col};font-weight:bold'>{risk}</span>",
                                    unsafe_allow_html=True
                                )

                                if file_r["clarion"].get("violations"):
                                    st.markdown("**CLARION Violations:**")
                                    for v in file_r["clarion"]["violations"]:
                                        st.markdown(
                                            f"{severity_badge(v.get('severity','info'))} "
                                            f"**{v.get('rule','')}**"
                                            + (f" — Line {v['line']}" if v.get("line") else ""),
                                            unsafe_allow_html=True
                                        )
                                        st.caption(v.get("message",""))
                                        if v.get("fix"):
                                            st.code(v["fix"], language=file_r["lang"])

                                if file_r["lumen"].get("smells"):
                                    st.markdown("**LUMEN Smells:**")
                                    for s in file_r["lumen"]["smells"]:
                                        st.markdown(
                                            f"{severity_badge(s.get('severity','minor'))} "
                                            f"**{s.get('type','')}** — {s.get('location','')}",
                                            unsafe_allow_html=True
                                        )
                                        st.caption(s.get("description",""))

                        st.divider()

                        # ── Summary comment preview ───────────────────
                        with st.expander("Preview — what gets posted to the PR"):
                            st.markdown(result.get("summary_comment",""))

                        # ── Post status ───────────────────────────────
                        if shadow_mode:
                            st.info(
                                "**Shadow Mode ON** — findings shown above but NOT posted to Azure DevOps.  \n"
                                "Toggle Shadow Mode OFF in the sidebar and re-run to post real comments."
                            )
                        else:
                            if posted:
                                st.success(
                                    f"Comments posted to PR #{selected_pr_id} in Azure DevOps. "
                                    "Go to your PR to see the inline findings and summary."
                                )
                            else:
                                st.warning("Shadow mode was off but posting did not complete — check errors above.")


# ── footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<center><small style='color:#555'>Project BlueLine POC · Built on Claude (claude-sonnet-4-6) · Azure-ready</small></center>",
    unsafe_allow_html=True
)

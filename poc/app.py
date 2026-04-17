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

    # ── Azure DevOps note ──
    st.markdown("#### Azure DevOps")
    st.caption(
        "In production, BlueLine connects to Azure DevOps via webhook — "
        "it auto-fetches PR diffs and posts comments directly on the PR. "
        "In this POC, you paste code manually to demonstrate the AI agents."
    )
    with st.expander("What ADO integration looks like"):
        st.markdown("""
**Production flow:**
1. Developer opens PR in Azure DevOps
2. ADO fires a webhook → BlueLine receives the PR diff automatically
3. CLARION + LUMEN analyse the diff
4. Agents post inline comments directly on the PR
5. Developer sees AI review alongside human reviewer comments

**POC simplification:**
- You paste code → same AI agents run → same output
- No webhook needed to demonstrate the intelligence
        """)

    st.divider()
    st.caption("POC v1.0 — BlueLine Team")

# ── header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='color:#4A9EFF'>🔵 Project BlueLine</h1>
<p style='color:#aaa;font-size:1.1rem'>AI Agent POC — Quality Gate · Security Loop · Certificate Loop</p>
""", unsafe_allow_html=True)
st.divider()

# ── tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🧑‍💻  Quality Gate  (CLARION + LUMEN)",
    "🔒  Security Loop  (BULWARK)",
    "📜  Certificate Loop  (TIMELINE)"
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
# TAB 2 — SECURITY LOOP
# ══════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### BULWARK — Security Finding Triage Agent")
    st.markdown(
        "Describe a Fortify finding or paste a vulnerability description below. "
        "BULWARK will classify it, assess the attack scenario, and generate a secure fix."
    )

    col_l, col_r = st.columns([1, 1])

    with col_l:
        if st.button("📂 Load Sample Finding", key="load_finding"):
            st.session_state["finding_input"] = load_sample("fortify_finding.txt")
            st.session_state["code_input_sec"] = ""

        finding_input = st.text_area(
            "Vulnerability / Fortify Finding Description",
            value=st.session_state.get("finding_input", ""),
            height=200,
            key="finding_area",
            placeholder="Paste the Fortify finding description or describe the vulnerability..."
        )

        code_sec = st.text_area(
            "Vulnerable Code Snippet (optional)",
            value=st.session_state.get("code_input_sec", ""),
            height=180,
            key="code_sec_area",
            placeholder="Paste the vulnerable code here for a more precise fix..."
        )

        run_triage = st.button("🔒 Run Triage", type="primary", key="run_triage")

    with col_r:
        if run_triage:
            if not os.getenv("ANTHROPIC_API_KEY"):
                st.error("Please enter your Anthropic API key in the sidebar.")
            elif not finding_input.strip():
                st.warning("Please describe the finding first.")
            else:
                from agents.bulwark import triage_finding

                with st.spinner("🤖 BULWARK is triaging the finding..."):
                    result = triage_finding(finding_input, code_sec)

                classification = result.get("classification", "NEEDS_REVIEW")
                confidence = result.get("confidence", 0.0)

                # ── Classification header ────────────────────────────
                st.markdown("#### BULWARK Triage Result")
                st.markdown(
                    f"**Classification:** {classification_badge(classification)}",
                    unsafe_allow_html=True
                )
                st.markdown(
                    confidence_bar(confidence),
                    unsafe_allow_html=True
                )

                st.divider()

                # ── OWASP ────────────────────────────────────────────
                if result.get("owasp_category"):
                    st.markdown(f"**OWASP Category:** `{result['owasp_category']}`")

                # ── Attack scenario ──────────────────────────────────
                if result.get("attack_scenario"):
                    st.markdown("**⚠️ Attack Scenario:**")
                    st.warning(result["attack_scenario"])

                if result.get("affected_systems"):
                    st.markdown(f"**🎯 At Risk:** {result['affected_systems']}")

                # ── False positive ───────────────────────────────────
                if classification == "FALSE_POSITIVE" and result.get("false_positive_reason"):
                    st.success(f"**Why this is a False Positive:** {result['false_positive_reason']}")

                st.divider()

                # ── Recommendation & fix ─────────────────────────────
                if result.get("recommendation"):
                    st.markdown("**✅ Recommendation:**")
                    st.info(result["recommendation"])

                if result.get("secure_code_example"):
                    st.markdown("**🔧 Secure Code Fix (FORGE preview):**")
                    st.code(result["secure_code_example"], language="csharp")

        else:
            st.info("👈 Load a sample finding or describe the vulnerability, then click **Run Triage**.")


# ══════════════════════════════════════════════════════════════════════
# TAB 3 — CERTIFICATE LOOP
# ══════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### TIMELINE — Certificate Expiry & Renewal Analyser")
    st.markdown(
        "Enter certificate details below. TIMELINE will assess urgency, "
        "identify the renewal path, and generate a step-by-step action plan."
    )

    col_a, col_b = st.columns([1, 1])

    with col_a:
        if st.button("📂 Load Sample Certificate", key="load_cert"):
            st.session_state["cert_subject"]  = "api.core-main.internal"
            st.session_state["cert_expiry"]   = "2026-05-01"
            st.session_state["cert_envs"]     = "Dev, QA, Production (IIS)"
            st.session_state["cert_ca"]       = "Internal PKI (C&M Portal)"
            st.session_state["cert_notes"]    = "Used by the Payments API and Admin Portal. Wildcard cert covers *.core-main.internal"

        cert_subject = st.text_input(
            "Subject / Domain",
            value=st.session_state.get("cert_subject", ""),
            placeholder="e.g. api.core-main.internal or *.example.com"
        )
        cert_expiry = st.text_input(
            "Expiry Date (YYYY-MM-DD)",
            value=st.session_state.get("cert_expiry", ""),
            placeholder="e.g. 2026-05-15"
        )
        cert_envs = st.text_input(
            "Deployed Environments",
            value=st.session_state.get("cert_envs", ""),
            placeholder="e.g. Dev, QA, Production (IIS + App Service)"
        )
        cert_ca = st.selectbox(
            "Certificate Authority Type",
            ["Internal PKI (C&M Portal)", "DigiCert", "GlobalSign", "Let's Encrypt", "Other"],
            index=0
        )
        cert_notes = st.text_area(
            "Additional Notes (optional)",
            value=st.session_state.get("cert_notes", ""),
            height=100,
            placeholder="e.g. Wildcard cert, used by 3 IIS sites, owner is Pankaj Pathak"
        )

        run_cert = st.button("📜 Analyse Certificate", type="primary", key="run_cert")

    with col_b:
        if run_cert:
            if not os.getenv("ANTHROPIC_API_KEY"):
                st.error("Please enter your Anthropic API key in the sidebar.")
            elif not cert_subject.strip() or not cert_expiry.strip():
                st.warning("Please fill in Subject and Expiry Date.")
            else:
                from agents.timeline import analyse_certificate

                with st.spinner("🤖 TIMELINE is analysing the certificate..."):
                    result = analyse_certificate(
                        subject=cert_subject,
                        expiry_date=cert_expiry,
                        environments=cert_envs,
                        ca_type=cert_ca,
                        notes=cert_notes
                    )

                urgency = result.get("urgency", "MONITOR")
                days    = result.get("days_until_expiry", "?")

                # ── Urgency header ───────────────────────────────────
                st.markdown("#### TIMELINE Analysis")
                st.markdown(
                    f"**Urgency:** {urgency_badge(urgency)}  &nbsp;&nbsp; "
                    f"**Days Until Expiry:** <span style='font-size:1.3rem;font-weight:bold'>{days}</span>",
                    unsafe_allow_html=True
                )

                if result.get("summary"):
                    st.markdown(f"*{result['summary']}*")

                st.divider()

                # ── Renewal path ─────────────────────────────────────
                renewal_path = result.get("renewal_path", "unknown")
                path_icons = {
                    "internal_pki":  "🏢",
                    "external_ca":   "🌐",
                    "letsencrypt":   "🔒",
                    "unknown":       "❓"
                }
                st.markdown(f"**Renewal Path:** {path_icons.get(renewal_path, '❓')} `{renewal_path.replace('_',' ').title()}`")

                auto = result.get("automation_possible", False)
                st.markdown(f"**Automation Possible:** {'✅ Yes' if auto else '⚠️ Partial / Manual steps required'}")
                if result.get("automation_notes"):
                    st.caption(result["automation_notes"])

                st.divider()

                # ── Action plan ──────────────────────────────────────
                steps = result.get("action_plan", [])
                if steps:
                    st.markdown("**📋 Action Plan:**")
                    for i, step in enumerate(steps, 1):
                        st.markdown(f"{i}. {step}")

                # ── Risks ────────────────────────────────────────────
                risks = result.get("risks", [])
                if risks:
                    st.divider()
                    st.markdown("**⚠️ Risks to be aware of:**")
                    for r in risks:
                        st.warning(r)

        else:
            st.info("👈 Load a sample certificate or fill in the details, then click **Analyse Certificate**.")

# ── footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<center><small style='color:#555'>Project BlueLine POC · Built on Claude (claude-sonnet-4-6) · Azure-ready</small></center>",
    unsafe_allow_html=True
)

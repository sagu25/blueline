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
    st.markdown("### CLARION + LUMEN — Code Review Agents")
    st.markdown(
        "Paste a C# or TypeScript code snippet below (or load a sample), "
        "then click **Run Review**. "
        "CLARION checks coding standards; LUMEN detects code smells."
    )

    col_left, col_right = st.columns([1, 1])

    with col_left:
        lang = st.selectbox("Language", ["csharp", "typescript"], key="lang")
        sample_map = {"csharp": "bad_csharp.cs", "typescript": "bad_typescript.ts"}

        if st.button("📂 Load Sample Code", key="load_sample"):
            st.session_state["code_input"] = load_sample(sample_map[lang])

        code_input = st.text_area(
            "Code to Review",
            value=st.session_state.get("code_input", ""),
            height=400,
            key="code_area",
            placeholder="Paste your C# or TypeScript code here..."
        )

        run_review = st.button("🔍 Run Review", type="primary", key="run_review")

    with col_right:
        if run_review:
            if not os.getenv("ANTHROPIC_API_KEY"):
                st.error("Please enter your Anthropic API key in the sidebar.")
            elif not code_input.strip():
                st.warning("Please paste some code first.")
            else:
                from agents.clarion import review_code
                from agents.lumen import detect_smells

                with st.spinner("🤖 CLARION is checking coding standards..."):
                    clarion_result = review_code(code_input, lang)

                with st.spinner("🤖 LUMEN is detecting code smells..."):
                    lumen_result = detect_smells(code_input, lang)

                # ── CLARION results ──────────────────────────────────
                st.markdown("#### CLARION — Coding Standards Report")

                score = clarion_result.get("overall_score", 0)
                sc = score_colour(score)
                st.markdown(
                    f"**Overall Score:** <span style='color:{sc};font-size:1.5rem;font-weight:bold'>{score}/10</span>  "
                    f"<br><em>{clarion_result.get('summary','')}</em>",
                    unsafe_allow_html=True
                )

                violations = clarion_result.get("violations", [])
                if violations:
                    st.markdown(f"**{len(violations)} violation(s) found:**")
                    for v in violations:
                        with st.expander(
                            f"{v.get('severity','').upper()} — {v.get('rule','')}  "
                            f"{'(Line ' + str(v['line']) + ')' if v.get('line') else ''}",
                            expanded=v.get("severity") == "error"
                        ):
                            st.markdown(
                                severity_badge(v.get("severity", "info")),
                                unsafe_allow_html=True
                            )
                            st.markdown(f"**Issue:** {v.get('message','')}")
                            if v.get("fix"):
                                st.markdown(f"**Fix:**")
                                st.code(v["fix"], language=lang)
                            st.markdown(
                                confidence_bar(v.get("confidence", 0)),
                                unsafe_allow_html=True
                            )
                else:
                    st.success("✅ No coding standard violations found!")

                st.divider()

                # ── LUMEN results ────────────────────────────────────
                st.markdown("#### LUMEN — Code Smell Report")

                m_score = lumen_result.get("maintainability_score", 0)
                mc = score_colour(m_score)
                st.markdown(
                    f"**Maintainability Score:** <span style='color:{mc};font-size:1.5rem;font-weight:bold'>{m_score}/10</span>",
                    unsafe_allow_html=True
                )

                smells = lumen_result.get("smells", [])
                if smells:
                    st.markdown(f"**{len(smells)} smell(s) detected:**")
                    for s in smells:
                        effort = s.get("effort", "")
                        effort_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(effort, "⚪")
                        with st.expander(
                            f"{s.get('severity','').upper()} — {s.get('type','')}  |  {s.get('location','')}",
                            expanded=s.get("severity") == "major"
                        ):
                            st.markdown(
                                severity_badge(s.get("severity", "minor")),
                                unsafe_allow_html=True
                            )
                            st.markdown(f"**Problem:** {s.get('description','')}")
                            st.markdown(f"**Refactor:** {s.get('refactor','')}")
                            st.markdown(f"**Effort:** {effort_icon} {effort.capitalize()}")
                else:
                    st.success("✅ No code smells detected!")
        else:
            st.info("👈 Load sample code or paste your own, then click **Run Review**.")


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

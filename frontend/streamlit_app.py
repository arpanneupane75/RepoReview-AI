import asyncio
import sys
from pathlib import Path

import streamlit as st

# =========================================================
# Project Path Configuration
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.pipeline import run_full_review
from app.report import generate_markdown_report

# =========================================================
# Page Configuration & Custom CSS
# =========================================================

st.set_page_config(
    page_title="RepoReview AI — Code Review Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Metric styling */
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700;
    }
    
    /* Code snippet block polish */
    code {
        border-radius: 4px;
    }

    /* Download button highlight */
    div.stDownloadButton > button {
        width: 100%;
        background-color: #0E1117;
        color: #FFFFFF;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    div.stDownloadButton > button:hover {
        border-color: #58A6FF;
        color: #58A6FF;
    }

    /* Custom badge layout */
    .severity-badge-high {
        color: #FF7B72;
        background-color: rgba(248, 81, 73, 0.15);
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# Header Section
# =========================================================

st.title("⚡ RepoReview AI")
st.caption("Autonomous Multi-Agent Code Review & Security Audit Pipeline")

st.markdown(
    """
Automated repository evaluation powered by four specialized **Pydantic AI** agents working in synthesis.
"""
)

# =========================================================
# Sidebar Setup
# =========================================================

st.sidebar.image("https://img.icons8.com/fluent/96/github.png", width=50)
st.sidebar.title("Target Repository")

repo_url = st.sidebar.text_input(
    "GitHub Repository URL",
    placeholder="https://github.com/owner/repository.git",
    help="Enter a public GitHub repository HTTPS URL.",
)

run_review = st.sidebar.button(
    "🚀 Run Analysis Pipeline",
    use_container_width=True,
    type="primary",
)

st.sidebar.divider()
st.sidebar.markdown(
    """
    **Agents in Pipeline:**
    1. 🔎 **Repository Analyst**
    2. 🧹 **Code Quality Reviewer**
    3. 🛡️ **Security & Bug Reviewer**
    4. 👨‍💻 **Senior Synthesis Reviewer**
    """
)

# =========================================================
# Execution Logic
# =========================================================

if run_review:
    if not repo_url.strip():
        st.error("Please enter a valid GitHub repository URL before starting.")
        st.stop()

    st.session_state.pop("review_results", None)

    progress_bar = st.progress(0)
    status_container = st.empty()

    try:
        status_container.info("⏳ Initializing repository clone and agent contexts...")
        progress_bar.progress(15)

        status_container.info("🔄 Running multi-agent review pipeline...")
        results = asyncio.run(run_full_review(repo_url.strip()))

        progress_bar.progress(100)
        status_container.success("✅ Multi-agent review successfully executed!")

        st.session_state["review_results"] = results

    except Exception as error:
        progress_bar.empty()
        status_container.empty()
        st.error(f"Review pipeline failed: {error}")
        st.info("Check if the repository URL is public and correctly formatted.")
        st.stop()

# =========================================================
# Empty State View (Before Execution)
# =========================================================

if "review_results" not in st.session_state:
    st.info("👈 Enter a public GitHub repository URL in the sidebar to run the multi-agent analysis.")
    st.divider()

    st.subheader("Multi-Agent Review Architecture")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("#### 🔎 Agent 1")
        st.markdown("**Repository Analyst**")
        st.caption("Maps structure, dependency tree, framework stack, and repository metadata.")

    with col2:
        st.markdown("#### 🧹 Agent 2")
        st.markdown("**Quality Reviewer**")
        st.caption("Evaluates maintainability, complexity, modularity, and testing coverage.")

    with col3:
        st.markdown("#### 🛡️ Agent 3")
        st.markdown("**Security Reviewer**")
        st.caption("Scans for vulnerabilities, credential exposure, and memory/logic bugs.")

    with col4:
        st.markdown("#### 👨‍💻 Agent 4")
        st.markdown("**Senior Reviewer**")
        st.caption("Synthesizes reports, strips speculative findings, and outputs recommendations.")

    st.stop()

# =========================================================
# Extract Structured Results
# =========================================================

results = st.session_state["review_results"]

repository_analysis = results["repository_analysis"]
quality_review = results["quality_review"]
security_review = results["security_review"]
final_review = results["final_review"]

# =========================================================
# Overview Dashboard
# =========================================================

st.divider()
st.subheader(" Pipeline Execution Summary")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Agent 1: Repository", "Completed", delta="Structure Mapped")
m2.metric("Agent 2: Quality", f"{len(quality_review.findings)} Issues", delta="Quality Analysis")
m3.metric("Agent 3: Security", f"{len(security_review.findings)} Threats", delta="Security Audit")
m4.metric("Agent 4: Synthesis", f"{len(final_review.recommendations)} Recs", delta="Final Review Ready")

st.divider()

# =========================================================
# Structured Results Tabs
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🔎 Agent 1: Repository Architecture",
        "🧹 Agent 2: Code Quality Findings",
        "🛡️ Agent 3: Security & Bug Audit",
        "👨‍💻 Agent 4: Senior Synthesis Review",
    ]
)

# ---------------------------------------------------------
# TAB 1: Repository Analyst
# ---------------------------------------------------------
with tab1:
    st.header("🔎 Agent 1 — Repository Architecture")
    st.caption("Structural overview, stack analysis, and project layout identification.")

    st.markdown("### Summary")
    st.write(repository_analysis.summary)

    col_lang, col_fw = st.columns(2)
    with col_lang:
        st.subheader("Primary Stack")
        st.info(f"**Primary Language:** {repository_analysis.primary_language}")

    with col_fw:
        st.subheader("Frameworks & Tools")
        if repository_analysis.frameworks:
            st.write(", ".join([f"`{fw}`" for fw in repository_analysis.frameworks]))
        else:
            st.write("No major frameworks detected.")

    col_files, col_arch = st.columns(2)

    with col_files:
        st.subheader("Key Repository Files")
        if repository_analysis.key_files:
            for file in repository_analysis.key_files:
                st.code(file, language="text")
        else:
            st.write("No key files flagged.")

    with col_arch:
        st.subheader("Architectural Patterns & Notes")
        if repository_analysis.architecture_notes:
            for note in repository_analysis.architecture_notes:
                st.markdown(f"- {note}")
        else:
            st.write("No specific architecture patterns identified.")

    st.subheader("Repository Strengths (Structural)")
    if repository_analysis.strengths:
        for strength in repository_analysis.strengths:
            st.success(f"✓ {strength}")
    else:
        st.write("No notable strengths recorded.")

# ---------------------------------------------------------
# TAB 2: Code Quality Reviewer
# ---------------------------------------------------------
with tab2:
    st.header("🧹 Agent 2 — Code Quality Reviewer")
    st.caption("Evaluation of maintainability, refactoring needs, and testing gaps.")

    st.markdown("### Quality Overview")
    st.write(quality_review.summary)

    st.divider()

    if quality_review.findings:
        st.subheader(f"Quality Findings ({len(quality_review.findings)})")

        for idx, finding in enumerate(quality_review.findings, start=1):
            severity = finding.severity.upper()
            with st.expander(f"{idx}. [{severity}] {finding.title}"):
                st.markdown("**Description**")
                st.write(finding.description)

                if finding.file:
                    loc = finding.file + (f":{finding.line}" if finding.line else "")
                    st.caption(f"📍 Location: `{loc}`")

                st.info(f"💡 **Suggested Refactoring:** {finding.recommendation}")
    else:
        st.success("No code quality issues identified by Agent 2.")

# ---------------------------------------------------------
# TAB 3: Security & Bug Reviewer
# ---------------------------------------------------------
with tab3:
    st.header("🛡️ Agent 3 — Security & Bug Reviewer")
    st.caption("Audit of vulnerabilities, unsafe logic, and edge-case execution errors.")

    st.markdown("### Security Summary")
    st.write(security_review.summary)

    st.divider()

    if security_review.findings:
        st.subheader(f"Identified Security Risks ({len(security_review.findings)})")

        for idx, finding in enumerate(security_review.findings, start=1):
            severity = finding.severity.upper()
            with st.expander(f"{idx}. [{severity}] {finding.title}"):
                st.markdown("**Threat Details**")
                st.write(finding.description)

                if finding.file:
                    loc = finding.file + (f":{finding.line}" if finding.line else "")
                    st.caption(f"📍 Location: `{loc}`")

                st.warning(f"🛠️ **Remediation Step:** {finding.recommendation}")
    else:
        st.success("No security vulnerabilities or major bugs flagged by Agent 3.")

# ---------------------------------------------------------
# TAB 4: Senior Reviewer (Final Synthesis)
# ---------------------------------------------------------
with tab4:
    st.header("👨‍💻 Agent 4 — Senior Reviewer Synthesis")
    st.caption("Deduplicated findings, validated threats, and prioritized engineering recommendations.")

    st.subheader("Context Pipeline View")
    with st.expander("📥 Inspect Specialist Data Passed into Agent 4 Context"):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.caption("Agent 1 Raw Analysis")
            st.json(repository_analysis.model_dump(), expanded=False)
        with c2:
            st.caption("Agent 2 Quality Review")
            st.json(quality_review.model_dump(), expanded=False)
        with c3:
            st.caption("Agent 3 Security Review")
            st.json(security_review.model_dump(), expanded=False)

    st.divider()

    st.subheader("🎯 Final Review Overview")
    st.write(final_review.summary)

    st.markdown("### Consolidated Strengths")
    if final_review.strengths:
        for str_item in final_review.strengths:
            st.success(f"✓ {str_item}")
    else:
        st.write("No strengths noted.")

    st.divider()

    col_q_acc, col_s_acc = st.columns(2)

    with col_q_acc:
        st.markdown("### 🧹 Accepted Quality Findings")
        if final_review.quality_findings:
            for idx, f in enumerate(final_review.quality_findings, start=1):
                with st.expander(f"{idx}. {f.title} ({f.severity})"):
                    st.write(f.description)
                    if f.file:
                        loc = f.file + (f":{f.line}" if f.line else "")
                        st.caption(f"📍 Location: `{loc}`")
                    st.info(f"Action: {f.recommendation}")
        else:
            st.success("No quality findings accepted into final report.")

    with col_s_acc:
        st.markdown("### 🛡️ Accepted Security Findings")
        if final_review.security_findings:
            for idx, f in enumerate(final_review.security_findings, start=1):
                with st.expander(f"{idx}. {f.title} ({f.severity})"):
                    st.write(f.description)
                    if f.file:
                        loc = f.file + (f":{f.line}" if f.line else "")
                        st.caption(f"📍 Location: `{loc}`")
                    st.warning(f"Action: {f.recommendation}")
        else:
            st.success("No security findings accepted into final report.")

    st.divider()

    st.markdown("### 🎯 Prioritized Actionable Recommendations")
    st.caption("Mandatory actionable steps synthesized directly from validated findings.")

    if final_review.recommendations:
        for idx, rec in enumerate(final_review.recommendations, start=1):
            st.markdown(f"**{idx}.** {rec}")
    else:
        st.info("Zero actionable recommendations required for this repository.")

    # -----------------------------------------------------
    # Export Section
    # -----------------------------------------------------
    st.divider()
    st.subheader("📄 Export Final Report")

    markdown_report = generate_markdown_report(final_review)

    st.download_button(
        label="⬇️ Download Markdown Report (.md)",
        data=markdown_report,
        file_name="reporeview_final_report.md",
        mime="text/markdown",
    )
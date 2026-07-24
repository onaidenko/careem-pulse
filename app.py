import json
from typing import Literal

import altair as alt
import pandas as pd
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


class Risk(BaseModel):
    title: str
    severity: Literal["Critical", "High", "Medium", "Low"]
    market: str
    services: list[str]
    teams: list[str]
    stakeholders: list[str]
    evidence: list[str]
    dependency_chain: list[str]
    likelihood: int = Field(ge=1, le=5)
    impact: int = Field(ge=1, le=5)
    urgency: int = Field(ge=1, le=5)
    dependency_breadth: int = Field(ge=1, le=5)
    owner_role: str
    immediate_action: str
    escalate_by: str
    missing_information: list[str]
    confidence: int = Field(ge=0, le=100)


class RiskRadar(BaseModel):
    project_health: int = Field(ge=0, le=100)
    overall_status: Literal["Red", "Amber", "Green"]
    executive_summary: str
    decisions_required: list[str]
    risks: list[Risk]


def calculated_score(risk: Risk) -> int:
    weighted = (
        risk.impact * 0.35
        + risk.urgency * 0.25
        + risk.likelihood * 0.20
        + risk.dependency_breadth * 0.20
    )
    return round(weighted * 20)


def analyze_with_gemini(df: pd.DataFrame, api_key: str) -> RiskRadar:
    client = genai.Client(api_key=api_key)
    prompt = f"""
You are Careem Pulse, an AI Risk Radar supporting a cross-functional launch
at a fictional multi-service regional technology platform.

Analyze the project updates below. Do not invent facts, people, dates, or metrics.
For every material risk:
- quote exact evidence from the supplied updates;
- identify affected markets, services, teams, and stakeholders;
- detect explicit and hidden dependencies;
- score likelihood, impact, urgency, and dependency breadth from 1 to 5;
- recommend one accountable owner by role, not by invented name;
- recommend one immediate action and an escalation deadline;
- state missing information and confidence.

Use only these severity values: Critical, High, Medium, Low.
Use only these overall status values: Red, Amber, Green.
All data is fictional and prepared for a hiring exercise.

PROJECT UPDATES CSV:
{df.to_csv(index=False)}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=RiskRadar,
        ),
    )
    return RiskRadar.model_validate_json(response.text)


DEMO_RESULT = RiskRadar.model_validate(
    {
        "project_health": 58,
        "overall_status": "Red",
        "executive_summary": "The launch is exposed to three connected risks across Pay, Food, Rides, Customer Care, and KSA compliance. The most urgent decision is whether to delay or decouple the cashback campaign before customer communications are released.",
        "decisions_required": [
            "Delay the Food cashback campaign or remove cashback from the initial launch.",
            "Pause KSA promotional communication until legal approval is confirmed.",
        ],
        "risks": [
            {
                "title": "Cashback may launch before payment certification",
                "severity": "Critical",
                "market": "UAE",
                "services": ["Pay", "Food"],
                "teams": ["Payments", "Growth", "Customer Care"],
                "stakeholders": ["Customers", "Customer Care", "Operations"],
                "evidence": [
                    "Payment certification moved from Monday to Thursday.",
                    "Cashback campaign remains scheduled for Wednesday.",
                ],
                "dependency_chain": [
                    "Payment certification",
                    "Food cashback campaign",
                    "Customer complaints",
                    "Customer Care workload",
                ],
                "likelihood": 5,
                "impact": 5,
                "urgency": 5,
                "dependency_breadth": 4,
                "owner_role": "Payments Program Manager",
                "immediate_action": "Move the campaign date or decouple cashback from the initial launch.",
                "escalate_by": "Today, 14:00",
                "missing_information": ["Confirmed certification completion time", "Rollback plan"],
                "confidence": 95,
            },
            {
                "title": "KSA promotion may proceed without final legal approval",
                "severity": "High",
                "market": "KSA",
                "services": ["Food", "Super App"],
                "teams": ["Legal", "Marketing"],
                "stakeholders": ["Customers", "Compliance", "Marketing"],
                "evidence": [
                    "Saudi promotion terms are awaiting final approval.",
                    "Push notifications are already scheduled for both markets.",
                ],
                "dependency_chain": [
                    "Legal approval",
                    "Promotion terms",
                    "Scheduled push notifications",
                    "Customer communication",
                ],
                "likelihood": 4,
                "impact": 5,
                "urgency": 5,
                "dependency_breadth": 3,
                "owner_role": "KSA Launch Manager",
                "immediate_action": "Place a release hold on KSA push notifications until approval is recorded.",
                "escalate_by": "Before the next campaign send window",
                "missing_information": ["Notification cancellation cutoff", "Final legal approver"],
                "confidence": 92,
            },
            {
                "title": "Iftar ride demand may exceed captain supply",
                "severity": "High",
                "market": "UAE",
                "services": ["Rides"],
                "teams": ["Operations", "Marketplace"],
                "stakeholders": ["Customers", "Captains", "Customer Care"],
                "evidence": [
                    "Captain supply forecast is 12% below target between 17:30 and 19:30.",
                ],
                "dependency_chain": [
                    "Captain supply gap",
                    "Longer ETAs",
                    "Cancellations",
                    "Customer Care contacts",
                ],
                "likelihood": 4,
                "impact": 4,
                "urgency": 4,
                "dependency_breadth": 3,
                "owner_role": "Marketplace Operations Lead",
                "immediate_action": "Activate a targeted supply incentive and monitor ETA thresholds during the peak window.",
                "escalate_by": "Before 16:00 today",
                "missing_information": ["Current incentive budget", "Market-level ETA threshold"],
                "confidence": 89,
            },
        ],
    }
)


st.set_page_config(page_title="Careem Pulse", page_icon="⚡", layout="wide")

st.markdown(
    """
<style>
.block-container {padding-top: 4rem; padding-bottom: 3rem;}
[data-testid="stMetricValue"] {font-size: 2rem;}
.small-note {color: #6b7280; font-size: 0.9rem;}
</style>
""",
    unsafe_allow_html=True,
)

st.caption("RISK RADAR · CAREEM HIRING CHALLENGE")

st.title("⚡ Careem Pulse")
st.subheader("AI Risk Radar for Cross-Vertical Launches")

st.markdown(
    '<span style="color:#00E784;font-size:17px;font-weight:600;">'
    'Spot the ripple before it reaches the customer.'
    '</span>',
    unsafe_allow_html=True,
)

st.caption(
    "Demo scenario: Ramadan Peak Readiness · UAE + KSA · "
    "Fictional hiring-exercise data only"
)

with st.sidebar:
    st.header("Controls")
    mode = st.radio(
        "Analysis mode",
        ["Prepared demo", "Live AI"],
        help="Prepared demo guarantees a stable walkthrough. Live AI runs a fresh Gemini analysis.",
    )

    if mode == "Prepared demo":
        st.caption("Stable pre-generated analysis for the default scenario.")
    else:
        st.caption("Fresh AI analysis of the currently loaded CSV.")

    uploaded_file = st.file_uploader("Upload another CSV", type="csv")
    st.markdown("---")
    st.caption("Risk Score = 35% impact + 25% urgency + 20% likelihood + 20% dependency breadth")

try:
    df = pd.read_csv(uploaded_file if uploaded_file else "dummy_updates.csv")
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

st.markdown("### Source updates")
st.dataframe(df, width="stretch", hide_index=True)

if st.button("Run Risk Radar", type="primary", width="stretch"):
    if mode == "Prepared demo":
        st.session_state["radar"] = DEMO_RESULT
    else:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            st.error("GEMINI_API_KEY is not configured in Streamlit secrets.")
        else:
            try:
                with st.spinner("Analyzing cross-team dependencies..."):
                    st.session_state["radar"] = analyze_with_gemini(df, api_key)
            except Exception as exc:
                st.error(f"Live AI analysis failed: {exc}")

radar = st.session_state.get("radar")
if radar:
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Project health", f"{radar.project_health}/100")
    col2.metric("Overall status", radar.overall_status)
    col3.metric("Material risks", len(radar.risks))
    col4.metric("Decisions required", len(radar.decisions_required))

    status_color = {
        "Red": "#FF4D4F",
        "Amber": "#FFB020",
        "Green": "#00E784",
    }[radar.overall_status]

    st.markdown(
        f"""
        <div style="
            width: 100%;
            height: 7px;
            background: #20262B;
            border-radius: 999px;
            overflow: hidden;
            margin: 8px 0 16px 0;
        ">
            <div style="
                width: {radar.project_health}%;
                height: 100%;
                background: {status_color};
                border-radius: 999px;
            "></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(radar.executive_summary)

    if radar.decisions_required:
        with st.container(border=True):
            st.caption("WHAT NEEDS ATTENTION NOW")
            st.markdown(
                f"**Decision needed today:** {radar.decisions_required[0]}"
            )

    overview_tab, risks_tab, decisions_tab = st.tabs(
        ["Executive view", "Risk register", "Decisions"]
    )

    with overview_tab:
        severity_order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
        rows = []
        for risk in radar.risks:
            rows.append(
                {
                    "Risk": risk.title,
                    "Severity": risk.severity,
                    "Market": risk.market,
                    "Services": ", ".join(risk.services),
                    "Owner": risk.owner_role,
                    "Risk score": calculated_score(risk),
                    "Confidence": risk.confidence,
                    "Severity order": severity_order[risk.severity],
                }
            )
        risk_df = pd.DataFrame(
            rows,
            columns=[
                "Risk",
                "Severity",
                "Market",
                "Services",
                "Owner",
                "Risk score",
                "Confidence",
                "Severity order",
            ],
        ).sort_values(["Severity order", "Risk score"], ascending=False)
        if risk_df.empty:
            st.success("No material risks detected in the current updates.")
        else:
            st.dataframe(
                risk_df.drop(columns=["Severity order"]),
                width="stretch",
                hide_index=True,
            )
            service_counts = (
                risk_df.assign(Services=risk_df["Services"].str.split(", "))
                .explode("Services")
                .groupby("Services")["Risk score"]
                .mean()
                .sort_values(ascending=False)
            )
            st.markdown("#### Average risk exposure by service")

            service_chart_df = (
                service_counts.rename("Risk score")
                .reset_index()
                .rename(columns={"Services": "Service"})
            )

            service_chart = (
                alt.Chart(service_chart_df)
                .mark_bar(color="#00E784", cornerRadiusEnd=5)
                .encode(
                    x=alt.X(
                        "Risk score:Q",
                        title="Risk score",
                        scale=alt.Scale(domain=[0, 100]),
                    ),
                    y=alt.Y(
                        "Service:N",
                        title=None,
                        sort="-x",
                    ),
                    tooltip=[
                        alt.Tooltip("Service:N"),
                        alt.Tooltip("Risk score:Q", format=".0f"),
                    ],
                )
                .properties(height=220)
            )

            st.altair_chart(service_chart, width="stretch")

    with risks_tab:
        if not radar.risks:
            st.success("No material risks detected. No escalation is currently required.")

        for risk in sorted(radar.risks, key=calculated_score, reverse=True):
            score = calculated_score(risk)
            with st.expander(
                f"{risk.severity} · {score}/100 · {risk.title}", expanded=risk.severity == "Critical"
            ):
                left, right = st.columns([2, 1])
                with left:
                    st.markdown(f"**Market:** {risk.market}")
                    st.markdown(f"**Services:** {', '.join(risk.services)}")
                    st.markdown(f"**Teams:** {', '.join(risk.teams)}")
                    st.markdown(f"**Dependency chain:** {' → '.join(risk.dependency_chain)}")
                    st.markdown("**Evidence**")
                    for quote in risk.evidence:
                        st.markdown(f"> {quote}")
                with right:
                    st.metric("Confidence", f"{risk.confidence}%")
                    st.markdown(f"**Owner:** {risk.owner_role}")
                    st.markdown(f"**Escalate by:** {risk.escalate_by}")
                    st.markdown(f"**Action:** {risk.immediate_action}")
                    if risk.missing_information:
                        st.markdown("**Missing information:**")
                        for item in risk.missing_information:
                            st.markdown(f"- {item}")

    with decisions_tab:
        if not radar.decisions_required:
            st.success("No immediate management decisions are required.")

        for index, decision in enumerate(radar.decisions_required, start=1):
            st.markdown(f"**{index}. {decision}**")
        st.markdown("---")
        st.caption("AI recommends. The project manager validates ownership, priority, and escalation.")

import streamlit as st
import pandas as pd
import numpy as np
import os
from utils import (
    load_data,
    compute_kpis,
    apply_filters,
    generate_rebalance_recommendations,
    drift_color,
    get_risk_label,
    generate_csv_report,
    generate_analytics_report,
)
from charts import (
    allocation_pie_chart,
    drift_status_bar,
    monthly_return_trend,
    risk_score_distribution,
    volatility_by_asset,
    market_sentiment_donut,
    sentiment_by_asset,
    risk_heatmap,
    allocation_trend,
    risk_trend,
    rebalance_action_bar,
)

st.set_page_config(
    page_title="Portfolio Rebalancing System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_PATH = os.path.join(
    BASE_DIR,
    "synthetic_portfolio_management_dataset.csv"
)
@st.cache_data
def get_data():
    return load_data(DATA_PATH)


df_full = get_data()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Portfolio Dashboard")
    st.caption("Made by **Ritesh Sharma**")
    st.caption("Internship Prototype — Symon's Management & Analytics")
    st.divider()

    st.subheader("Dashboard")
    section = st.radio(
        "Go to",
        [
            "Executive Summary",
            "Portfolio Monitoring",
            "Rebalancing Intelligence",
            "Risk Analytics",
            "Historical Trends",
            "Institutional Insights",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.subheader("Week 3: Problem Definition")
    week3_section = st.radio(
        "Week 3",
        [
            "— Select a Task —",
            "1. Target Users & Needs",
            "2. Use Cases & Success Criteria",
            "3. In-Scope & Out-of-Scope",
            "4. Assumptions & Constraints",
            "5. Measurable Goals",
        ],
        label_visibility="collapsed",
    )
    if week3_section != "— Select a Task —":
        section = week3_section

    st.divider()
    st.subheader("Filters")

    all_portfolios = sorted(df_full["Portfolio_ID"].unique().tolist())
    selected_portfolios = st.multiselect("Portfolio ID", all_portfolios)

    all_assets = sorted(df_full["Asset_Class"].unique().tolist())
    selected_assets = st.multiselect("Asset Class", all_assets)

    all_sentiments = sorted(df_full["Market_Sentiment"].unique().tolist())
    selected_sentiments = st.multiselect("Market Sentiment", all_sentiments)

    all_drifts = sorted(df_full["Drift_Status"].unique().tolist())
    selected_drifts = st.multiselect("Drift Status", all_drifts)

    all_users = sorted(df_full["Target_User"].unique().tolist())
    selected_users = st.multiselect("Target User", all_users)

    st.divider()

df = apply_filters(
    df_full,
    selected_portfolios,
    selected_assets,
    selected_sentiments,
    selected_drifts,
    selected_users,
)

kpis = compute_kpis(df)

# ── Executive Summary ─────────────────────────────────────────────────────────
if section == "Executive Summary":
    st.title("Executive Summary")
    st.caption("Strategic overview of portfolio health, risk, and rebalancing requirements.")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Portfolios", kpis["total_portfolios"])
    c2.metric("Avg Monthly Return", f"{kpis['avg_return']}%")
    c3.metric("Avg Risk Score", f"{kpis['avg_risk_score']}")
    c4.metric("Assets Outside Range", kpis["assets_outside_range"])
    c5.metric("Rebalance Alerts", kpis["total_rebalance_alerts"])
    c6.metric("Portfolio Health Score", f"{kpis['portfolio_health_score']}")

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Target Allocation by Asset Class")
        st.plotly_chart(allocation_pie_chart(df, "Target_Allocation"), width="stretch")

    with col_b:
        st.subheader("Current Allocation by Asset Class")
        st.plotly_chart(allocation_pie_chart(df, "Current_Allocation"), width="stretch")

    st.subheader("Allocation Drift Status")
    st.plotly_chart(drift_status_bar(df), width="stretch")

    st.divider()
    st.subheader("Download Reports")
    dl1, dl2 = st.columns(2)
    with dl1:
        st.download_button(
            label="⬇ Download Filtered Data (CSV)",
            data=generate_csv_report(df),
            file_name="portfolio_filtered_data.csv",
            mime="text/csv",
        )
    with dl2:
        st.download_button(
            label="⬇ Download Analytics Report (TXT)",
            data=generate_analytics_report(df, kpis),
            file_name="portfolio_analytics_report.txt",
            mime="text/plain",
        )


# ── Portfolio Monitoring ──────────────────────────────────────────────────────
elif section == "Portfolio Monitoring":
    st.title("Portfolio Monitoring")
    st.caption("Allocation visibility and drift detection across all asset classes.")

    st.subheader("Drift Detection Status")

    display_df = df[
        [
            "Portfolio_ID",
            "Date",
            "Asset_Class",
            "Target_Allocation",
            "Current_Allocation",
            "Min_Range",
            "Max_Range",
            "Drift_Status",
            "Recommended_Action",
            "Allocation_Deviation",
            "Allocation_Deviation_Pct",
        ]
    ].copy()

    display_df["Status"] = display_df["Drift_Status"].apply(drift_color)
    display_df = display_df.rename(
        columns={
            "Allocation_Deviation": "Deviation (%pt)",
            "Allocation_Deviation_Pct": "Deviation (%)",
        }
    )

    above = display_df[display_df["Drift_Status"] == "Above Range"]
    below = display_df[display_df["Drift_Status"] == "Below Range"]
    within = display_df[display_df["Drift_Status"] == "Within Range"]

    tab_all, tab_above, tab_below, tab_within = st.tabs(
        [
            f"All ({len(display_df)})",
            f"🔴 Above Range ({len(above)})",
            f"🟠 Below Range ({len(below)})",
            f"🟢 Within Range ({len(within)})",
        ]
    )

    cols_to_show = [
        "Status", "Portfolio_ID", "Date", "Asset_Class",
        "Target_Allocation", "Current_Allocation", "Min_Range", "Max_Range",
        "Drift_Status", "Recommended_Action", "Deviation (%pt)", "Deviation (%)",
    ]

    with tab_all:
        st.dataframe(display_df[cols_to_show], width="stretch", height=420)
    with tab_above:
        st.dataframe(above[cols_to_show], width="stretch", height=420)
    with tab_below:
        st.dataframe(below[cols_to_show], width="stretch", height=420)
    with tab_within:
        st.dataframe(within[cols_to_show], width="stretch", height=420)

    st.divider()
    st.subheader("Asset Class Allocation Trend")

    asset_options = sorted(df["Asset_Class"].unique().tolist())
    if asset_options:
        chosen_asset = st.selectbox("Select Asset Class", asset_options)
        st.plotly_chart(allocation_trend(df, chosen_asset), width="stretch")
    else:
        st.info("No data available for the current filter selection.")


# ── Rebalancing Intelligence ──────────────────────────────────────────────────
elif section == "Rebalancing Intelligence":
    st.title("Rebalancing Intelligence")
    st.caption("AI-driven rebalance recommendations based on Strategic Asset Allocation (SAA) thresholds.")

    rec_df = generate_rebalance_recommendations(df)

    st.subheader("Rebalance Action Summary")
    st.plotly_chart(rebalance_action_bar(rec_df), width="stretch")

    st.subheader("Detailed Rebalancing Recommendations")

    action_filter = st.selectbox("Filter by AI Action", ["All", "BUY", "SELL", "HOLD"])
    if action_filter != "All":
        rec_df = rec_df[rec_df["AI_Action"] == action_filter]

    display_rec = rec_df[
        [
            "Portfolio_ID",
            "Date",
            "Asset_Class",
            "Target_Allocation",
            "Current_Allocation",
            "Min_Range",
            "Max_Range",
            "Recommended_Action",
            "AI_Action",
            "Allocation_Gap",
            "Risk_Score",
            "Market_Sentiment",
        ]
    ].copy()

    display_rec["Status"] = display_rec["Drift_Status"] if "Drift_Status" in display_rec.columns else ""

    def highlight_action(val):
        if val == "SELL":
            return "background-color: #fecaca; color: #991b1b"
        elif val == "BUY":
            return "background-color: #bbf7d0; color: #166534"
        return ""

    st.dataframe(
        display_rec.style.map(highlight_action, subset=["AI_Action"]),
        width="stretch",
        height=420,
    )

    st.divider()
    st.subheader("Allocation Deviation Analysis")

    col1, col2, col3 = st.columns(3)
    buy_count = (rec_df["AI_Action"] == "BUY").sum()
    sell_count = (rec_df["AI_Action"] == "SELL").sum()
    hold_count = (rec_df["AI_Action"] == "HOLD").sum()
    col1.metric("BUY Signals", buy_count, delta="Under-allocated")
    col2.metric("SELL Signals", sell_count, delta="Over-allocated")
    col3.metric("HOLD", hold_count, delta="Within range")

    with st.expander("About AI Rebalancing Logic"):
        st.markdown(
            """
**AI Rebalancing Rule Engine (Informed Rebalancing)**

| Condition | Action |
|-----------|--------|
| `Current_Allocation > Max_Range` | **SELL** — Reduce exposure to restore SAA |
| `Current_Allocation < Min_Range` | **BUY** — Increase exposure to restore SAA |
| `Min_Range ≤ Current_Allocation ≤ Max_Range` | **HOLD** — Portfolio within tolerance band |

*Allocation Gap = Current − Target. Positive = over-weight, negative = under-weight.*
"""
        )


# ── Risk Analytics ────────────────────────────────────────────────────────────
elif section == "Risk Analytics":
    st.title("Risk Analytics")
    st.caption("Portfolio exposure, volatility distribution, and risk-adjusted insights.")

    r1, r2, r3, r4 = st.columns(4)
    high_risk = df[df["Risk_Score"] >= 8].shape[0]
    avg_vol_score = df["Volatility"].map(
        {"Very Low": 1, "Low": 2, "Medium": 3, "High": 4}
    ).mean()
    r1.metric("High Risk Records (≥8)", high_risk)
    r2.metric("Avg Risk Score", f"{kpis['avg_risk_score']}")
    r3.metric("Avg Volatility Index", f"{avg_vol_score:.2f}")
    r4.metric("Assets Outside Range", kpis["assets_outside_range"])

    st.divider()

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.subheader("Risk Score Distribution")
        st.plotly_chart(risk_score_distribution(df), width="stretch")
    with col_r2:
        st.subheader("Volatility by Asset Class")
        st.plotly_chart(volatility_by_asset(df), width="stretch")

    st.subheader("Risk Heatmap — Asset Class × Market Sentiment")
    st.plotly_chart(risk_heatmap(df), width="stretch")

    st.subheader("High-Risk Asset Exposure")
    high_risk_df = df[df["Risk_Score"] >= 7][
        [
            "Portfolio_ID",
            "Asset_Class",
            "Current_Allocation",
            "Risk_Score",
            "Volatility",
            "Market_Sentiment",
            "Drift_Status",
        ]
    ].sort_values("Risk_Score", ascending=False)
    st.dataframe(high_risk_df, width="stretch", height=300)

    with st.expander("Risk Label Guide"):
        st.markdown(
            """
| Risk Score | Label |
|------------|-------|
| 1 – 3 | Low |
| 4 – 6 | Medium |
| 7 – 8 | High |
| 9 – 10 | Critical |
"""
        )


# ── Historical Trends ──────────────────────────────────────────────────────────
elif section == "Historical Trends":
    st.title("Historical Trends")
    st.caption("Time-series analysis of returns, risk scores, and allocation drift over time.")

    st.subheader("Average Monthly Return Over Time")
    st.plotly_chart(monthly_return_trend(df), width="stretch")

    st.subheader("Average Risk Score Over Time")
    st.plotly_chart(risk_trend(df), width="stretch")

    st.divider()
    st.subheader("Allocation Trend by Asset Class")
    asset_options = sorted(df["Asset_Class"].unique().tolist())
    if asset_options:
        chosen = st.selectbox("Select Asset Class", asset_options, key="hist_asset")
        st.plotly_chart(allocation_trend(df, chosen), width="stretch")

    st.divider()
    st.subheader("Drift Frequency Over Time")
    drift_time = (
        df.groupby(["Month", "Drift_Status"]).size().reset_index(name="Count")
    )
    import plotly.express as px
    fig = px.area(
        drift_time,
        x="Month",
        y="Count",
        color="Drift_Status",
        color_discrete_map={
            "Above Range": "#ef4444",
            "Below Range": "#f97316",
            "Within Range": "#22c55e",
        },
    )
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Records",
        legend_title="Drift Status",
        margin=dict(t=20, b=40, l=40, r=20),
        height=320,
    )
    st.plotly_chart(fig, width="stretch")


# ── Institutional Insights ────────────────────────────────────────────────────
elif section == "Institutional Insights":
    st.title("Institutional Insights")
    st.caption("Stakeholder mapping and institutional reporting panel.")

    st.subheader("Market Sentiment Overview")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.plotly_chart(market_sentiment_donut(df), width="stretch")
    with col_s2:
        st.plotly_chart(sentiment_by_asset(df), width="stretch")

    st.divider()
    st.subheader("Target User Requirements")

    user_df = (
        df[["Target_User", "What_They_Are_Looking_For", "Why_They_Matter"]]
        .drop_duplicates()
        .sort_values("Target_User")
        .reset_index(drop=True)
    )
    user_df.columns = ["Target User", "What They Are Looking For", "Why They Matter"]
    st.dataframe(user_df, width="stretch", height=360)

    st.divider()
    st.subheader("Portfolio Coverage by Stakeholder")
    user_counts = df["Target_User"].value_counts().reset_index()
    user_counts.columns = ["Target User", "Records"]
    import plotly.express as px
    fig = px.bar(
        user_counts,
        x="Target User",
        y="Records",
        color="Target User",
        text="Records",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False,
        xaxis_tickangle=-25,
        margin=dict(t=20, b=80, l=40, r=20),
        height=360,
    )
    st.plotly_chart(fig, width="stretch")

    st.divider()
    st.subheader("Governance & Compliance Summary")
    gov_df = df[df["Target_User"].isin(["Regulators", "Investment Committees", "Pension Funds"])][
        [
            "Portfolio_ID",
            "Asset_Class",
            "Current_Allocation",
            "Target_Allocation",
            "Drift_Status",
            "Risk_Score",
            "Market_Sentiment",
            "Target_User",
        ]
    ].sort_values(["Target_User", "Risk_Score"], ascending=[True, False])
    st.dataframe(gov_df, width="stretch", height=320)

    st.download_button(
        label="⬇ Download Institutional Report (CSV)",
        data=generate_csv_report(user_df),
        file_name="institutional_stakeholder_report.csv",
        mime="text/csv",
    )


# ── Week 3 Task 1: Target Users & Needs ──────────────────────────────────────
elif section == "1. Target Users & Needs":
    st.title("Task 1 — Define Target Users & Decision-Making Needs")
    st.caption("Week 3: Problem Definition and Scope")

    st.info(
        "**Objective:** Identify who will use this system, what decisions they need to make, "
        "and what information they need to make those decisions effectively."
    )

    st.subheader("What This Task Involves")
    st.markdown(
        """
This task focuses on clearly defining the people and organisations that will interact with the
AI-Assisted Portfolio Rebalancing System. Understanding the target users is the foundation of
good system design — without knowing who uses it, we cannot design for their real needs.

For each user type, we answer three questions:
- **Who are they?** Their role in the organisation.
- **What do they need?** The specific information or output they require.
- **Why do they matter?** Their stake in portfolio management outcomes.
"""
    )

    st.divider()
    st.subheader("Identified Target Users")

    users = [
        {
            "User": "Portfolio Managers",
            "Role": "Primary decision-makers responsible for investment allocation and performance.",
            "Decision-Making Needs": "Real-time allocation visibility, rebalancing recommendations, risk-adjusted return improvement signals.",
            "Pain Points": "Manual drift monitoring is slow; lack of automated alerts for threshold breaches.",
        },
        {
            "User": "Pension Funds / Institutional Investors",
            "Role": "Manage large pools of capital on behalf of beneficiaries.",
            "Decision-Making Needs": "Stable long-term returns, governance transparency, low drawdown environments.",
            "Pain Points": "Compliance and governance reporting is time-consuming without automated tooling.",
        },
        {
            "User": "Investment Analysts",
            "Role": "Support investment teams with data-driven insights and analytics.",
            "Decision-Making Needs": "Clean structured data, portfolio analytics, performance tracking, volatility analysis.",
            "Pain Points": "Data is fragmented across spreadsheets; difficult to run quick scenario analyses.",
        },
        {
            "User": "Risk Management Teams",
            "Role": "Ensure portfolio exposure stays within approved risk thresholds.",
            "Decision-Making Needs": "Drift detection, exposure monitoring, compliance visibility.",
            "Pain Points": "Risk events are often identified too late due to infrequent manual reviews.",
        },
        {
            "User": "Investment Committees",
            "Role": "Approve investment strategies and oversee governance.",
            "Decision-Making Needs": "Executive summaries, strategic alignment reports, clear rebalancing rationale.",
            "Pain Points": "Lack of a single dashboard view that consolidates portfolio health into executive-ready output.",
        },
        {
            "User": "Regulators",
            "Role": "Ensure compliance, governance, and financial transparency.",
            "Decision-Making Needs": "Risk reporting, transparency into allocation decisions, audit-ready documentation.",
            "Pain Points": "Difficulty accessing structured evidence of compliant portfolio management practices.",
        },
    ]

    for u in users:
        with st.expander(f"**{u['User']}**"):
            st.markdown(f"**Role:** {u['Role']}")
            st.markdown(f"**Decision-Making Needs:** {u['Decision-Making Needs']}")
            st.markdown(f"**Pain Points:** {u['Pain Points']}")

    st.divider()
    st.subheader("User Coverage in Dataset")
    user_counts = df_full["Target_User"].value_counts().reset_index()
    user_counts.columns = ["Target User", "Records in Dataset"]
    st.dataframe(user_counts, width="stretch", height=280)

    st.success(
        "**Output:** A clearly defined user map confirms the system serves 6 distinct institutional "
        "user types, each with specific decision-making needs captured in the dataset."
    )


# ── Week 3 Task 2: Use Cases & Success Criteria ───────────────────────────────
elif section == "2. Use Cases & Success Criteria":
    st.title("Task 2 — Use Cases & Success Criteria")
    st.caption("Week 3: Problem Definition and Scope")

    st.info(
        "**Objective:** Capture concrete use cases the system must support, and define measurable "
        "success criteria for each so outcomes can be evaluated objectively."
    )

    st.subheader("What This Task Involves")
    st.markdown(
        """
Use cases describe specific scenarios in which a user interacts with the system to achieve a goal.
Each use case is paired with a **success criterion** — a measurable condition that tells us
whether the system has fulfilled its purpose for that scenario.

This prevents vague requirements and ensures that every feature built has a clear, testable purpose.
"""
    )

    st.divider()
    st.subheader("Core Use Cases")

    use_cases = [
        {
            "ID": "UC-01",
            "Use Case": "Drift Detection",
            "Actor": "Risk Management Team",
            "Scenario": "A risk manager opens the dashboard and immediately sees which portfolios have breached their allocation range.",
            "Success Criterion": "System correctly flags all records where Current_Allocation < Min_Range or > Max_Range with colour-coded indicators.",
            "Priority": "High",
        },
        {
            "ID": "UC-02",
            "Use Case": "Rebalancing Recommendation",
            "Actor": "Portfolio Manager",
            "Scenario": "A portfolio manager selects a portfolio and receives a BUY/SELL/HOLD recommendation with the allocation gap.",
            "Success Criterion": "Recommendations align 100% with SAA threshold rules; gap calculation is accurate to 2 decimal places.",
            "Priority": "High",
        },
        {
            "ID": "UC-03",
            "Use Case": "Executive Reporting",
            "Actor": "Investment Committee",
            "Scenario": "A committee member downloads a one-page analytics summary before a board meeting.",
            "Success Criterion": "Report includes KPIs, drift summary, and top alerts; downloads successfully in under 3 seconds.",
            "Priority": "High",
        },
        {
            "ID": "UC-04",
            "Use Case": "Risk Analytics Review",
            "Actor": "Investment Analyst",
            "Scenario": "An analyst views the risk heatmap to identify which asset classes carry highest risk under bearish sentiment.",
            "Success Criterion": "Heatmap renders correctly with risk scores averaged by asset class and sentiment.",
            "Priority": "Medium",
        },
        {
            "ID": "UC-05",
            "Use Case": "Historical Trend Analysis",
            "Actor": "Financial Researcher",
            "Scenario": "A researcher tracks how drift frequency and average returns have evolved month-over-month.",
            "Success Criterion": "Time-series charts display all available months with correct aggregated values.",
            "Priority": "Medium",
        },
        {
            "ID": "UC-06",
            "Use Case": "Compliance Transparency",
            "Actor": "Regulator",
            "Scenario": "A regulator filters portfolios by drift status to audit how many assets were outside range in a given period.",
            "Success Criterion": "Filter produces a correctly scoped dataset matching the selected criteria.",
            "Priority": "Medium",
        },
    ]

    priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}

    for uc in use_cases:
        with st.expander(f"{uc['ID']} — {uc['Use Case']}  {priority_color[uc['Priority']]} {uc['Priority']} Priority"):
            st.markdown(f"**Actor:** {uc['Actor']}")
            st.markdown(f"**Scenario:** {uc['Scenario']}")
            st.markdown(f"**Success Criterion:** {uc['Success Criterion']}")

    st.divider()
    st.subheader("Use Case Priority Summary")
    import pandas as pd
    uc_df = pd.DataFrame([(u["ID"], u["Use Case"], u["Actor"], u["Priority"]) for u in use_cases],
                         columns=["ID", "Use Case", "Actor", "Priority"])
    st.dataframe(uc_df, width="stretch", height=260)

    st.success(
        "**Output:** 6 prioritised use cases with explicit success criteria provide a testable "
        "specification for every major feature in the system."
    )


# ── Week 3 Task 3: In-Scope & Out-of-Scope ───────────────────────────────────
elif section == "3. In-Scope & Out-of-Scope":
    st.title("Task 3 — In-Scope & Out-of-Scope Boundaries")
    st.caption("Week 3: Problem Definition and Scope")

    st.info(
        "**Objective:** Clearly establish what the system will and will not do, preventing scope "
        "creep and setting realistic expectations for stakeholders and the development team."
    )

    st.subheader("What This Task Involves")
    st.markdown(
        """
Defining scope boundaries is one of the most critical steps in project planning.
Without clear in-scope and out-of-scope definitions, projects grow uncontrollably,
timelines slip, and the final product fails to solve the original problem effectively.

This task documents what is **included** in this prototype and what has been **deliberately excluded**,
along with the reasoning for each exclusion.
"""
    )

    st.divider()

    col_in, col_out = st.columns(2)

    with col_in:
        st.subheader("In Scope")
        in_scope = [
            ("Portfolio drift detection", "Core requirement — identifies allocation breaches automatically."),
            ("AI rebalancing recommendations (BUY/SELL/HOLD)", "Rule-based SAA engine; deterministic and explainable."),
            ("Risk analytics dashboard", "Risk scores, volatility breakdown, and heatmap visualisation."),
            ("Historical trend visualisation", "Monthly returns, risk trends, and drift frequency over time."),
            ("Institutional stakeholder reporting", "User mapping, governance panel, and compliance summary."),
            ("Market sentiment analysis", "Bullish/Bearish/Neutral distribution across asset classes."),
            ("Global filter panel", "Filter by Portfolio ID, Asset Class, Sentiment, Drift Status, User."),
            ("Downloadable reports (CSV & TXT)", "One-click exports for executive and audit purposes."),
            ("Synthetic dataset integration", "1,001-record CSV dataset simulating institutional portfolio data."),
        ]
        for item, reason in in_scope:
            with st.expander(f"✅ {item}"):
                st.caption(reason)

    with col_out:
        st.subheader("Out of Scope")
        out_scope = [
            ("Live market data feeds", "Requires paid API subscriptions (Bloomberg, Refinitiv). Not feasible for internship prototype."),
            ("Trade execution engine", "Executing actual buy/sell orders requires brokerage integration and regulatory licensing."),
            ("User authentication & access control", "Out of scope for Week 3 prototype; would be added in production phase."),
            ("Machine learning model training", "ML-based recommendations require labelled outcome data not yet available."),
            ("Multi-currency support", "All allocations are percentage-based; currency conversion is not modelled."),
            ("Real-time portfolio updates", "Dataset is static CSV; streaming ingestion is a future-phase concern."),
            ("Third-party audit trail", "Formal audit logging requires compliance infrastructure beyond prototype scope."),
        ]
        for item, reason in out_scope:
            with st.expander(f"❌ {item}"):
                st.caption(reason)

    st.divider()
    st.success(
        "**Output:** A documented boundary between in-scope and out-of-scope items protects the "
        "prototype timeline and gives stakeholders a clear understanding of what this system delivers."
    )


# ── Week 3 Task 4: Assumptions & Constraints ─────────────────────────────────
elif section == "4. Assumptions & Constraints":
    st.title("Task 4 — Key Assumptions & Known Constraints")
    st.caption("Week 3: Problem Definition and Scope")

    st.info(
        "**Objective:** Surface the assumptions baked into this design and the real constraints "
        "that limit what can be built, so stakeholders can challenge them early."
    )

    st.subheader("What This Task Involves")
    st.markdown(
        """
Every system is built on assumptions. Making them explicit is critical — hidden assumptions
become risks. A constraint is a real-world limitation (time, data, technology, budget) that the
system must work within.

This task catalogues both so that the design phase begins with a shared, honest understanding
of what the system is built on and what it cannot change.
"""
    )

    st.divider()

    st.subheader("Key Assumptions")
    assumptions = [
        ("A1", "Data", "The synthetic dataset accurately represents real institutional portfolio structures, including typical allocation ranges, drift patterns, and risk profiles."),
        ("A2", "Rebalancing Logic", "The SAA threshold engine (Min/Max Range boundaries) is an accepted and sufficient proxy for institutional rebalancing decision-making in a prototype context."),
        ("A3", "Users", "Target users are familiar with basic portfolio management terminology (SAA, drift, volatility, rebalancing) and do not require onboarding tutorials within the tool."),
        ("A4", "Frequency", "Portfolio monitoring is assumed to be reviewed on a monthly basis, consistent with the monthly return data in the dataset."),
        ("A5", "Risk Scoring", "Risk scores (1–10) in the dataset are pre-computed and accepted as valid inputs; no recalculation methodology is required for the prototype."),
        ("A6", "Market Sentiment", "Market sentiment labels (Bullish, Bearish, Neutral) are external inputs and are not computed or predicted by this system."),
    ]

    for code, category, text in assumptions:
        st.markdown(f"**{code} [{category}]** — {text}")

    st.divider()
    st.subheader("Known Constraints")

    constraints = [
        ("C1", "Time", "This is a Week 3 internship prototype with a limited development window. Feature depth is scoped accordingly."),
        ("C2", "Data", "The dataset is synthetic and static (CSV). No live data pipeline exists, limiting real-time applicability."),
        ("C3", "Technology", "The system is built entirely in Python and Streamlit. No dedicated backend, database, or API layer is included in this phase."),
        ("C4", "Budget", "No paid APIs, cloud infrastructure, or external data subscriptions are available for this prototype."),
        ("C5", "Regulatory", "The system is not certified or validated for use in regulated financial environments. It is a demonstration prototype only."),
        ("C6", "Data Privacy", "No real portfolio or investor data is used. All data is synthetic and publicly shareable."),
    ]

    for code, category, text in constraints:
        col1, col2 = st.columns([1, 8])
        col1.error(code)
        col2.markdown(f"**[{category}]** {text}")

    st.divider()
    st.success(
        "**Output:** 6 explicit assumptions and 6 known constraints give the design team a clear "
        "foundation to build from, and signal to reviewers what would need to change for production."
    )


# ── Week 3 Task 5: Measurable Goals ──────────────────────────────────────────
elif section == "5. Measurable Goals":
    st.title("Task 5 — Measurable Goals for the Design Phase")
    st.caption("Week 3: Problem Definition and Scope")

    st.info(
        "**Objective:** Convert the problem statement and use cases into specific, measurable goals "
        "that the design phase can be evaluated against — moving from intent to accountability."
    )

    st.subheader("What This Task Involves")
    st.markdown(
        """
Goals without measurements are wishes. This task converts the system's objectives into
**SMART goals** — Specific, Measurable, Achievable, Relevant, and Time-bound.

Each goal is linked to the problem it addresses, the metric that proves success, and the
target value the design phase must achieve. These goals become the evaluation criteria
for the next phase of the internship project.
"""
    )

    st.divider()
    st.subheader("SMART Goals for the Design Phase")

    goals = [
        {
            "Goal": "G1 — Drift Detection Accuracy",
            "Problem Addressed": "Portfolio managers currently identify drift manually and inconsistently.",
            "Metric": "Percentage of records correctly classified as Above Range / Below Range / Within Range.",
            "Target": "100% classification accuracy against SAA threshold rules.",
            "Linked Use Case": "UC-01",
            "Status": "Achieved in prototype",
        },
        {
            "Goal": "G2 — Rebalancing Coverage",
            "Problem Addressed": "Rebalancing decisions are made without systematic AI support.",
            "Metric": "Percentage of out-of-range records that receive a BUY or SELL recommendation.",
            "Target": "100% of drifted records generate an actionable recommendation.",
            "Linked Use Case": "UC-02",
            "Status": "Achieved in prototype",
        },
        {
            "Goal": "G3 — Report Availability",
            "Problem Addressed": "Investment committees lack ready-made, downloadable executive summaries.",
            "Metric": "Number of downloadable report formats available.",
            "Target": "At least 2 formats (CSV data export, TXT analytics report).",
            "Linked Use Case": "UC-03",
            "Status": "Achieved in prototype",
        },
        {
            "Goal": "G4 — Stakeholder Coverage",
            "Problem Addressed": "The system must serve multiple institutional user types, not just one role.",
            "Metric": "Number of distinct target user personas addressed by dashboard features.",
            "Target": "At least 5 user personas with dedicated content or data views.",
            "Linked Use Case": "UC-04, UC-06",
            "Status": "Achieved in prototype",
        },
        {
            "Goal": "G5 — Filter Responsiveness",
            "Problem Addressed": "Users need to slice data by their specific context without generating separate reports.",
            "Metric": "Number of filter dimensions available globally across all dashboard sections.",
            "Target": "At least 4 independent filter dimensions (Portfolio ID, Asset Class, Sentiment, Drift Status).",
            "Linked Use Case": "UC-06",
            "Status": "Achieved in prototype",
        },
        {
            "Goal": "G6 — Design Phase Readiness",
            "Problem Addressed": "The project must graduate from problem definition to design with a documented foundation.",
            "Metric": "Completion of all 5 Week 3 deliverables (problem statement, scope, use cases, assumptions, goals).",
            "Target": "All 5 tasks documented and demonstrable in the dashboard.",
            "Linked Use Case": "All",
            "Status": "In progress",
        },
    ]

    for g in goals:
        status_icon = "✅" if g["Status"] == "Achieved in prototype" else "🔄"
        with st.expander(f"{status_icon} {g['Goal']}"):
            st.markdown(f"**Problem Addressed:** {g['Problem Addressed']}")
            st.markdown(f"**Metric:** {g['Metric']}")
            st.markdown(f"**Target:** {g['Target']}")
            st.markdown(f"**Linked Use Case(s):** {g['Linked Use Case']}")
            st.markdown(f"**Status:** {g['Status']}")

    st.divider()
    st.subheader("Goals Tracker")
    goals_df = pd.DataFrame([
        (g["Goal"].split(" — ")[0], g["Goal"].split(" — ")[1], g["Target"], g["Status"])
        for g in goals
    ], columns=["ID", "Goal", "Target", "Status"])
    st.dataframe(goals_df, width="stretch", height=260)

    st.divider()
    st.subheader("Problem Statement (v1)")
    st.markdown(
        """
> **Problem Statement:**
> Institutional portfolio managers and risk teams currently rely on manual, periodic reviews
> to detect allocation drift and generate rebalancing decisions. This process is slow, inconsistent,
> and not scalable across large portfolios with multiple asset classes. The result is delayed
> responses to market movements, increased compliance risk, and suboptimal risk-adjusted returns.
>
> **This system addresses that problem** by providing an AI-assisted dashboard that automates
> drift detection, generates deterministic rebalancing recommendations, and delivers executive-ready
> risk analytics — enabling faster, more consistent, and more transparent investment decision-making
> across all institutional stakeholder types.
"""
    )

    st.success(
        "**Output:** 6 SMART goals with defined metrics and targets, plus a v1 Problem Statement "
        "that anchors the entire design phase."
    )

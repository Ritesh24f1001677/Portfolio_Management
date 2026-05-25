import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


DRIFT_COLOR_MAP = {
    "Above Range": "#ef4444",
    "Below Range": "#f97316",
    "Within Range": "#22c55e",
}

SENTIMENT_COLOR_MAP = {
    "Bullish": "#22c55e",
    "Bearish": "#ef4444",
    "Neutral": "#94a3b8",
}


def allocation_pie_chart(df: pd.DataFrame, allocation_type: str = "Target_Allocation") -> go.Figure:
    agg = df.groupby("Asset_Class")[allocation_type].mean().reset_index()
    fig = px.pie(
        agg,
        names="Asset_Class",
        values=allocation_type,
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig.update_traces(textposition="outside", textinfo="percent+label")
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v", x=1.05),
        margin=dict(t=20, b=20, l=20, r=20),
        height=380,
    )
    return fig


def drift_status_bar(df: pd.DataFrame) -> go.Figure:
    counts = df["Drift_Status"].value_counts().reset_index()
    counts.columns = ["Drift_Status", "Count"]
    fig = px.bar(
        counts,
        x="Drift_Status",
        y="Count",
        color="Drift_Status",
        color_discrete_map=DRIFT_COLOR_MAP,
        text="Count",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="Drift Status",
        yaxis_title="Number of Records",
        showlegend=False,
        margin=dict(t=20, b=40, l=40, r=20),
        height=320,
    )
    return fig


def monthly_return_trend(df: pd.DataFrame) -> go.Figure:
    trend = df.groupby("Month")["Monthly_Return"].mean().reset_index()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=trend["Month"],
            y=trend["Monthly_Return"],
            mode="lines+markers",
            line=dict(color="#6366f1", width=2.5),
            marker=dict(size=6),
            fill="tozeroy",
            fillcolor="rgba(99,102,241,0.15)",
            name="Avg Monthly Return",
        )
    )
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Average Monthly Return (%)",
        margin=dict(t=20, b=40, l=40, r=20),
        height=320,
    )
    return fig


def risk_score_distribution(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        df,
        x="Risk_Score",
        nbins=10,
        color_discrete_sequence=["#f59e0b"],
        labels={"Risk_Score": "Risk Score"},
    )
    fig.update_layout(
        xaxis_title="Risk Score",
        yaxis_title="Frequency",
        bargap=0.1,
        margin=dict(t=20, b=40, l=40, r=20),
        height=300,
    )
    return fig


def volatility_by_asset(df: pd.DataFrame) -> go.Figure:
    vol_order = ["Very Low", "Low", "Medium", "High"]
    counts = df.groupby(["Asset_Class", "Volatility"]).size().reset_index(name="Count")
    fig = px.bar(
        counts,
        x="Asset_Class",
        y="Count",
        color="Volatility",
        barmode="stack",
        category_orders={"Volatility": vol_order},
        color_discrete_sequence=["#22c55e", "#86efac", "#f59e0b", "#ef4444"],
    )
    fig.update_layout(
        xaxis_title="Asset Class",
        yaxis_title="Count",
        legend_title="Volatility",
        margin=dict(t=20, b=40, l=40, r=20),
        height=320,
    )
    return fig


def market_sentiment_donut(df: pd.DataFrame) -> go.Figure:
    counts = df["Market_Sentiment"].value_counts().reset_index()
    counts.columns = ["Sentiment", "Count"]
    fig = px.pie(
        counts,
        names="Sentiment",
        values="Count",
        hole=0.55,
        color="Sentiment",
        color_discrete_map=SENTIMENT_COLOR_MAP,
    )
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(
        showlegend=True,
        margin=dict(t=20, b=20, l=20, r=20),
        height=340,
    )
    return fig


def sentiment_by_asset(df: pd.DataFrame) -> go.Figure:
    counts = df.groupby(["Asset_Class", "Market_Sentiment"]).size().reset_index(name="Count")
    fig = px.bar(
        counts,
        x="Asset_Class",
        y="Count",
        color="Market_Sentiment",
        barmode="group",
        color_discrete_map=SENTIMENT_COLOR_MAP,
    )
    fig.update_layout(
        xaxis_title="Asset Class",
        yaxis_title="Count",
        legend_title="Market Sentiment",
        margin=dict(t=20, b=40, l=40, r=20),
        height=320,
    )
    return fig


def risk_heatmap(df: pd.DataFrame) -> go.Figure:
    pivot = df.pivot_table(
        values="Risk_Score",
        index="Asset_Class",
        columns="Market_Sentiment",
        aggfunc="mean",
    ).round(2)
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale="RdYlGn_r",
            text=pivot.values,
            texttemplate="%{text}",
            showscale=True,
            colorbar=dict(title="Risk Score"),
        )
    )
    fig.update_layout(
        xaxis_title="Market Sentiment",
        yaxis_title="Asset Class",
        margin=dict(t=20, b=60, l=100, r=20),
        height=340,
    )
    return fig


def allocation_trend(df: pd.DataFrame, asset_class: str) -> go.Figure:
    sub = df[df["Asset_Class"] == asset_class].groupby("Month")[
        ["Target_Allocation", "Current_Allocation"]
    ].mean().reset_index()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=sub["Month"], y=sub["Target_Allocation"],
            mode="lines", name="Target Allocation",
            line=dict(color="#6366f1", width=2, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=sub["Month"], y=sub["Current_Allocation"],
            mode="lines+markers", name="Current Allocation",
            line=dict(color="#f59e0b", width=2),
            marker=dict(size=5),
            fill="tonexty",
            fillcolor="rgba(245,158,11,0.1)",
        )
    )
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Allocation (%)",
        legend=dict(orientation="h", y=1.1),
        margin=dict(t=30, b=40, l=40, r=20),
        height=300,
    )
    return fig


def risk_trend(df: pd.DataFrame) -> go.Figure:
    trend = df.groupby("Month")["Risk_Score"].mean().reset_index()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=trend["Month"],
            y=trend["Risk_Score"],
            mode="lines+markers",
            line=dict(color="#ef4444", width=2.5),
            marker=dict(size=6),
            fill="tozeroy",
            fillcolor="rgba(239,68,68,0.12)",
            name="Avg Risk Score",
        )
    )
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Average Risk Score",
        margin=dict(t=20, b=40, l=40, r=20),
        height=300,
    )
    return fig


def rebalance_action_bar(df: pd.DataFrame) -> go.Figure:
    action_colors = {"Hold": "#94a3b8", "BUY": "#22c55e", "SELL": "#ef4444"}
    df = df.copy()
    df["AI_Action_Clean"] = df["Recommended_Action"].apply(
        lambda x: "SELL" if "Sell" in str(x) else ("BUY" if "Buy" in str(x) else "Hold")
    )
    counts = df["AI_Action_Clean"].value_counts().reset_index()
    counts.columns = ["Action", "Count"]
    fig = px.bar(
        counts,
        x="Action",
        y="Count",
        color="Action",
        color_discrete_map=action_colors,
        text="Count",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="Recommended Action",
        yaxis_title="Count",
        showlegend=False,
        margin=dict(t=20, b=40, l=40, r=20),
        height=300,
    )
    return fig

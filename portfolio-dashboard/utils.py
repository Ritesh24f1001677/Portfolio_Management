import pandas as pd
import numpy as np


def load_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    df["Allocation_Deviation"] = df["Current_Allocation"] - df["Target_Allocation"]
    df["Allocation_Deviation_Pct"] = (
        (df["Current_Allocation"] - df["Target_Allocation"]) / df["Target_Allocation"] * 100
    ).round(2)
    return df


def compute_kpis(df: pd.DataFrame) -> dict:
    total_portfolios = df["Portfolio_ID"].nunique()
    avg_return = df["Monthly_Return"].mean()
    avg_risk_score = df["Risk_Score"].mean()
    assets_outside_range = df[df["Drift_Status"] != "Within Range"].shape[0]
    total_rebalance_alerts = df[df["Recommended_Action"] != "Hold"].shape[0]
    portfolio_health_score = max(
        0,
        round(
            100
            - (assets_outside_range / max(len(df), 1) * 50)
            - (df["Risk_Score"].mean() * 2),
            1,
        ),
    )
    return {
        "total_portfolios": total_portfolios,
        "avg_return": round(avg_return, 2),
        "avg_risk_score": round(avg_risk_score, 2),
        "assets_outside_range": assets_outside_range,
        "total_rebalance_alerts": total_rebalance_alerts,
        "portfolio_health_score": portfolio_health_score,
    }


def apply_filters(
    df: pd.DataFrame,
    portfolio_ids: list,
    asset_classes: list,
    sentiments: list,
    drift_statuses: list,
    target_users: list,
) -> pd.DataFrame:
    if portfolio_ids:
        df = df[df["Portfolio_ID"].isin(portfolio_ids)]
    if asset_classes:
        df = df[df["Asset_Class"].isin(asset_classes)]
    if sentiments:
        df = df[df["Market_Sentiment"].isin(sentiments)]
    if drift_statuses:
        df = df[df["Drift_Status"].isin(drift_statuses)]
    if target_users:
        df = df[df["Target_User"].isin(target_users)]
    return df


def generate_rebalance_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    rec_df = df.copy()
    rec_df["AI_Action"] = np.where(
        rec_df["Current_Allocation"] > rec_df["Max_Range"],
        "SELL",
        np.where(rec_df["Current_Allocation"] < rec_df["Min_Range"], "BUY", "HOLD"),
    )
    rec_df["Allocation_Gap"] = (rec_df["Current_Allocation"] - rec_df["Target_Allocation"]).round(2)
    return rec_df


def drift_color(status: str) -> str:
    mapping = {
        "Above Range": "🔴",
        "Below Range": "🟠",
        "Within Range": "🟢",
    }
    return mapping.get(status, "⚪")


def get_risk_label(score: float) -> str:
    if score <= 3:
        return "Low"
    elif score <= 6:
        return "Medium"
    elif score <= 8:
        return "High"
    return "Critical"


def generate_csv_report(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def generate_analytics_report(df: pd.DataFrame, kpis: dict) -> bytes:
    lines = [
        "INSTITUTIONAL PORTFOLIO ANALYTICS REPORT",
        "=" * 50,
        f"Total Portfolios Monitored: {kpis['total_portfolios']}",
        f"Average Monthly Return: {kpis['avg_return']}%",
        f"Average Risk Score: {kpis['avg_risk_score']}",
        f"Assets Outside Allocation Range: {kpis['assets_outside_range']}",
        f"Total Rebalance Alerts: {kpis['total_rebalance_alerts']}",
        f"Portfolio Health Score: {kpis['portfolio_health_score']}",
        "",
        "DRIFT STATUS BREAKDOWN",
        "-" * 30,
    ]
    for status, count in df["Drift_Status"].value_counts().items():
        lines.append(f"  {status}: {count}")
    lines += [
        "",
        "ASSET CLASS SUMMARY",
        "-" * 30,
    ]
    for asset, grp in df.groupby("Asset_Class"):
        lines.append(
            f"  {asset}: Avg Return={grp['Monthly_Return'].mean():.2f}%, "
            f"Avg Risk={grp['Risk_Score'].mean():.2f}"
        )
    lines += [
        "",
        "REBALANCING ACTIONS REQUIRED",
        "-" * 30,
    ]
    alerts = df[df["Recommended_Action"] != "Hold"][
        ["Portfolio_ID", "Asset_Class", "Recommended_Action", "Current_Allocation", "Target_Allocation"]
    ]
    for _, row in alerts.iterrows():
        lines.append(
            f"  {row['Portfolio_ID']} | {row['Asset_Class']} | "
            f"Action: {row['Recommended_Action']} | "
            f"Current: {row['Current_Allocation']}% | Target: {row['Target_Allocation']}%"
        )
    return "\n".join(lines).encode("utf-8")

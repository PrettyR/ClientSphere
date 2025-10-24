from flask import Blueprint, jsonify
from flask_cors import cross_origin
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
try:
    import plotly.express as px
except Exception:  # keep server running if plotly is missing
    px = None

from routes.graph_data import _load_clients_df

# Recompute charts from processed CSV or DB and save PNG/HTML files
charts_bp = Blueprint("charts_gen", __name__)


def _ensure_dirs(path: str):
    os.makedirs(path, exist_ok=True)


def _get_charts_dir() -> str:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    charts_dir = os.path.join(base_dir, "ML assets", "charts")
    _ensure_dirs(charts_dir)
    return charts_dir


@charts_bp.route("/charts/regenerate", methods=["POST", "GET"])  # allow quick manual trigger
@cross_origin(origins="http://localhost:5173")
def regenerate_charts():
    df = _load_clients_df()
    if df.empty:
        return jsonify({"message": "No data available to generate charts"}), 200

    # Normalize columns
    if "cluster_label" not in df.columns:
        for alt in ["cluster", "segment", "Cluster"]:
            if alt in df.columns:
                df = df.rename(columns={alt: "cluster_label"})
                break
    if "balance" not in df.columns:
        for alt in ["Balance", "account_balance", "avg_balance"]:
            if alt in df.columns:
                df = df.rename(columns={alt: "balance"})
                break

    df["balance"] = pd.to_numeric(df.get("balance", 0), errors="coerce").fillna(0.0)

    charts_dir = _get_charts_dir()

    # 1) Balance by cluster (bar chart)
    plt.figure(figsize=(8, 5))
    agg = (
        df.groupby("cluster_label")["balance"].sum().sort_values(ascending=False)
    )
    sns.barplot(x=agg.index, y=agg.values, palette="Reds_r")
    plt.xticks(rotation=30, ha="right")
    plt.title("Total Balance by Cluster")
    plt.ylabel("Total Balance")
    bar_path = os.path.join(charts_dir, "balance_analysis.png")
    plt.tight_layout()
    plt.savefig(bar_path)
    plt.close()

    # 2) Cluster distribution (pie)
    plt.figure(figsize=(6, 6))
    counts = df["cluster_label"].value_counts()
    plt.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=140)
    plt.title("Client Distribution by Cluster")
    pie_path = os.path.join(charts_dir, "segment_distribution.png")
    plt.tight_layout()
    plt.savefig(pie_path)
    plt.close()

    # 3) Balance boxplot per cluster
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=df, x="cluster_label", y="balance", palette="Blues")
    plt.xticks(rotation=30, ha="right")
    plt.title("Balance Distribution by Cluster")
    box_path = os.path.join(charts_dir, "balance_box.png")
    plt.tight_layout()
    plt.savefig(box_path)
    plt.close()

    # 4) Interactive scatter using Plotly: balance vs predicted_value with 4 standardized segments
    interactive_path = None
    if px is not None:
        # Always standardize to 4 bins by balance so legend shows Bronze/Silver/Gold/Platinum
        color_col = "__segment4"
        try:
            df[color_col] = pd.qcut(
                pd.to_numeric(df["balance"], errors="coerce").fillna(0).rank(method="first"),
                4,
                labels=["bronze", "silver", "gold", "platinum"],
            )
        except Exception:
            color_col = None

        # Ensure predicted_value exists for all rows; derive simple fallback if missing
        if "predicted_value" not in df.columns:
            # heuristic: use balance and optional income to synthesize
            income_col = None
            for cand in ["Monthly_Income", "monthly_income", "income"]:
                if cand in df.columns:
                    income_col = cand
                    break
            if income_col is not None:
                df["predicted_value"] = df["balance"].fillna(0) * 1.8 + df[income_col].fillna(0) * 6.5
            else:
                df["predicted_value"] = df["balance"].fillna(0) * 2.0

        # Build interactive chart if we have the essentials
        if color_col is not None:
            fig = px.scatter(
                df,
                x="balance",
                y="predicted_value",
                color=color_col,
                title="Client Segments: Balance vs Predicted Value",
                labels={"balance": "Account Balance ($)", "predicted_value": "Predicted Value ($)", color_col: "Client Segment"},
                category_orders={color_col: ["bronze", "silver", "gold", "platinum"]},
            )
            interactive_path = os.path.join(charts_dir, "interactive_scatter.html")
            fig.write_html(interactive_path, include_plotlyjs="cdn")

    # 5) Interactive: Monthly Income vs Balance
    interactive_income = None
    if px is not None:
        income_col = None
        for cand in ["Monthly_Income", "monthly_income", "income"]:
            if cand in df.columns:
                income_col = cand
                break
        if income_col is not None and "balance" in df.columns:
            fig2 = px.scatter(
                df,
                x=income_col,
                y="balance",
                color="cluster_label",
                title="Client Segments: Income vs Balance",
                labels={income_col: "Monthly Income ($)", "balance": "Account Balance ($)", "cluster_label": "Client Segment"},
            )
            interactive_income = os.path.join(charts_dir, "interactive_income_balance.html")
            fig2.write_html(interactive_income, include_plotlyjs="cdn")

    # 6) Interactive: Transactions vs Predicted Value
    interactive_tx_pred = None
    if px is not None and "predicted_value" in df.columns:
        tx_col = None
        for cand in ["tx_count", "Transaction_Frequency", "transactions"]:
            if cand in df.columns:
                tx_col = cand
                break
        if tx_col is not None:
            fig3 = px.scatter(
                df,
                x=tx_col,
                y="predicted_value",
                color="cluster_label",
                title="Client Segments: Transactions vs Predicted Value",
                labels={tx_col: "Transactions", "predicted_value": "Predicted Value ($)", "cluster_label": "Client Segment"},
            )
            interactive_tx_pred = os.path.join(charts_dir, "interactive_tx_pred.html")
            fig3.write_html(interactive_tx_pred, include_plotlyjs="cdn")

    return jsonify({
        "charts": {
            "balance_bar": bar_path,
            "segment_pie": pie_path,
            "balance_box": box_path,
            "interactive_scatter": interactive_path,
            "interactive_income_balance": interactive_income,
            "interactive_tx_pred": interactive_tx_pred,
        }
    })



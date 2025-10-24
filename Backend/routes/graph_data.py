# routes/graph_data.py
from flask import Blueprint, jsonify
from flask_cors import cross_origin
from models import ClientRecord
from models import db
import os
from ml_loader import CSV_PATH as DEFAULT_DATASET_PATH
import pandas as pd

graph_bp = Blueprint("graph_bp", __name__)

# Paths to ML assets CSV as fallback when DB is empty
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "ML assets", "processed_data")
CSV_FALLBACK = DEFAULT_DATASET_PATH if os.path.exists(DEFAULT_DATASET_PATH) else os.path.join(DATA_DIR, "processed_clients.csv")


def _load_clients_df():
    """Try database first; if empty or fails, fallback to processed CSV."""
    try:
        engine = db.session.get_bind()
        df = pd.read_sql_table("clients", con=engine)
        if not df.empty:
            return df
    except Exception:
        pass

    # CSV fallback
    try:
        if os.path.exists(CSV_FALLBACK):
            df = pd.read_csv(CSV_FALLBACK)
            # normalize common column names including new exported headers
            rename_map = {
                "products": "products_owned",
                "Products": "products_owned",
                "risk": "risk_score",
                "Risk": "risk_score",
                "CIFs": "client_id",
                "Age": "age",
                "Account_Balance": "balance",
                "Transaction_Frequency": "tx_count",
                "Cluster": "cluster_label",
            }
            df = df.rename(columns=rename_map)
            return df
    except Exception:
        pass

    return pd.DataFrame()

@graph_bp.route("/graph-data", methods=["GET"])
@cross_origin(origins="http://localhost:5173")
def graph_data():
    """
    Aggregate data from ClientRecord for visualization.
    Example: total balance by cluster_label.
    """
    try:
        df = _load_clients_df()
        if df.empty:
            return jsonify([])

        summary = df.groupby("cluster_label")["balance"].sum().reset_index()
        return jsonify(summary.to_dict(orient="records"))
    except Exception:
        return jsonify([])


@graph_bp.route("/charts/summary", methods=["GET"])
@cross_origin(origins="http://localhost:5173")
def charts_summary():
    """
    Returns multiple chart-ready datasets:
    - balance_by_cluster: sum of balances per cluster
    - avg_balance_by_cluster: average balance per cluster
    - tx_distribution: histogram buckets of tx_count
    - age_boxplot: five-number summary per cluster
    """
    try:
        df = _load_clients_df()
        if df.empty:
            return jsonify({
                "balance_by_cluster": [],
                "avg_balance_by_cluster": [],
                "tx_distribution": [],
                "age_boxplot": [],
                "cluster_counts": [],
                "scatter_points": []
            })

        # Ensure expected columns exist / coerce types
        if "cluster_label" not in df.columns:
            # try alternate names
            for alt in ["cluster", "segment", "Cluster"]:
                if alt in df.columns:
                    df = df.rename(columns={alt: "cluster_label"})
                    break
        if "balance" not in df.columns:
            # if there is a similarly named column
            for alt in ["Balance", "account_balance", "avg_balance"]:
                if alt in df.columns:
                    df = df.rename(columns={alt: "balance"})
                    break
        df["balance"] = pd.to_numeric(df.get("balance", 0), errors="coerce").fillna(0.0)

        balance_by_cluster = (
            df.groupby("cluster_label")["balance"].sum().reset_index()
            .rename(columns={"cluster_label": "cluster", "balance": "total_balance"})
            .to_dict(orient="records")
        )

        avg_balance_by_cluster = (
            df.groupby("cluster_label")["balance"].mean().reset_index()
            .rename(columns={"cluster_label": "cluster", "balance": "avg_balance"})
            .to_dict(orient="records")
        )

        # Histogram: prefer tx_count; fallback to products_owned; else to balance buckets
        hist_source_col = None
        for cand in ["tx_count", "products_owned", "transactions", "balance"]:
            if cand in df.columns:
                hist_source_col = cand
                break
        tx_distribution = []
        if hist_source_col is not None:
            series = pd.to_numeric(df[hist_source_col], errors="coerce").fillna(0)
            # dynamic bins based on source
            if hist_source_col == "balance":
                bins = [0, 1000, 5000, 10000, 25000, 50000, 100000, series.max()]
                labels = [
                    "0-1k", "1k-5k", "5k-10k", "10k-25k", "25k-50k", "50k-100k", ">100k"
                ]
            else:
                bins = [0, 1, 2, 3, 5, 10, 20, 50, 100, series.max()]
                labels = ["0", "1", "2", "3-5", "6-10", "11-20", "21-50", "51-100", ">100"]
            df["tx_bucket"] = pd.cut(series, bins=bins, labels=labels, right=True, include_lowest=True)
            tx_distribution = (
                df.groupby("tx_bucket").size().reset_index(name="count").to_dict(orient="records")
            )

        # Boxplot stats: prefer age; fallback to balance per cluster
        box_source_col = "age" if "age" in df.columns else "balance"
        age_boxplot = []
        for cluster, sub in df.groupby("cluster_label"):
            series = pd.to_numeric(sub[box_source_col], errors="coerce").dropna()
            if len(series) == 0:
                continue
            stats = {
                "cluster": cluster if pd.notna(cluster) else None,
                "min": float(series.min()),
                "q1": float(series.quantile(0.25)),
                "median": float(series.quantile(0.5)),
                "q3": float(series.quantile(0.75)),
                "max": float(series.max()),
            }
            age_boxplot.append(stats)

        # Cluster counts (for pie chart)
        cluster_counts = (
            df.groupby("cluster_label").size().reset_index(name="count")
            .rename(columns={"cluster_label": "cluster"})
            .to_dict(orient="records")
        )

        # Scatter points: balance vs risk_score (limit for performance)
        scatter_cols = ["balance", "risk_score", "cluster_label"]
        scatter_points = []
        if all(c in df.columns for c in scatter_cols):
            sc = df[scatter_cols].dropna().copy()
            sc["balance"] = pd.to_numeric(sc["balance"], errors="coerce").fillna(0.0)
            sc["risk_score"] = pd.to_numeric(sc["risk_score"], errors="coerce").fillna(0.0)
            sc = sc.head(1000)
            scatter_points = sc.rename(columns={"cluster_label": "cluster"}).to_dict(orient="records")

        return jsonify({
            "balance_by_cluster": balance_by_cluster,
            "avg_balance_by_cluster": avg_balance_by_cluster,
            "tx_distribution": tx_distribution,
            "age_boxplot": age_boxplot,
            "cluster_counts": cluster_counts,
            "scatter_points": scatter_points
        })
    except Exception:
        return jsonify({
            "balance_by_cluster": [],
            "avg_balance_by_cluster": [],
            "tx_distribution": [],
            "age_boxplot": [],
            "cluster_counts": [],
            "scatter_points": []
        })


@graph_bp.route("/clients/all", methods=["GET"])
@cross_origin(origins="http://localhost:5173")
def clients_all():
    try:
        df = _load_clients_df()
        if df.empty:
            return jsonify([])

        # Normalize expected columns and fill fallbacks for UI table
        if "cluster_label" not in df.columns:
            for alt in ["cluster", "segment", "Cluster"]:
                if alt in df.columns:
                    df = df.rename(columns={alt: "cluster_label"})
                    break
        if "tx_count" not in df.columns and "products_owned" in df.columns:
            df["tx_count"] = df["products_owned"]

        view_cols = [c for c in ["client_id", "age", "balance", "tx_count", "cluster_label"] if c in df.columns]
        if not view_cols:
            records = df.to_dict(orient="records")
        else:
            records = df[view_cols].to_dict(orient="records")

        # Ensure JSON-serializable and provide an 'id' key for React row keys
        for r in records:
            r.setdefault("id", r.get("client_id"))
            if r.get("age") is None:
                r["age"] = None
            if r.get("tx_count") is None:
                r["tx_count"] = None
        return jsonify(records)
    except Exception:
        return jsonify([])

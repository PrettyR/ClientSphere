from flask import Blueprint, jsonify, send_from_directory, current_app
import os, json
import pandas as pd

dashboard_bp = Blueprint("dashboard", __name__)

# === CONFIG PATHS ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "ML assets", "processed_data")
CHARTS_DIR = os.path.join(BASE_DIR, "ML assets", "charts")


@dashboard_bp.route("/dashboard/overview", methods=["GET"])
def dashboard_overview():
    """Return summary statistics.

    Prefer computing live from processed_clients.csv to reflect latest schema
    (supports new headers like CIFs, Account_Balance, Transaction_Frequency, Cluster).
    Fallback to summary_stats.json if CSV is missing.
    """
    csv_path = os.path.join(DATA_DIR, "processed_clients.csv")
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)

            # Normalize column names to expected keys
            rename_map = {}
            if "CIFs" in df.columns:
                rename_map["CIFs"] = "client_id"
            if "Age" in df.columns:
                rename_map["Age"] = "age"
            if "Account_Balance" in df.columns:
                rename_map["Account_Balance"] = "balance"
            if "Transaction_Frequency" in df.columns:
                rename_map["Transaction_Frequency"] = "tx_count"
            if "Cluster" in df.columns:
                rename_map["Cluster"] = "cluster_label"

            # Apply renames without dropping existing expected columns
            if rename_map:
                df = df.rename(columns=rename_map)

            # Coerce numeric fields
            if "balance" in df.columns:
                df["balance"] = pd.to_numeric(df["balance"], errors="coerce").fillna(0.0)
            if "tx_count" in df.columns:
                df["tx_count"] = pd.to_numeric(df["tx_count"], errors="coerce").fillna(0)

            total_clients = int(len(df))
            segments_count = int(df["cluster_label"].nunique()) if "cluster_label" in df.columns else 0
            avg_balance = float(df["balance"].mean()) if "balance" in df.columns else 0.0
            total_assets = float(df["balance"].sum()) if "balance" in df.columns else 0.0
            segment_breakdown = (
                df["cluster_label"].value_counts().to_dict() if "cluster_label" in df.columns else {}
            )

            # Provide a simple timestamp using file mtime
            try:
                mtime = os.path.getmtime(csv_path)
                from datetime import datetime
                export_timestamp = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                export_timestamp = None

            return jsonify({
                "total_clients": total_clients,
                "segments_count": segments_count,
                "avg_balance": avg_balance,
                "total_assets": total_assets,
                "segment_breakdown": segment_breakdown,
                "export_timestamp": export_timestamp,
            })
        except Exception as e:
            # If anything goes wrong, fall back to summary_stats.json
            pass

    # Fallback to precomputed summary file
    summary_path = os.path.join(DATA_DIR, "summary_stats.json")
    if os.path.exists(summary_path):
        with open(summary_path, "r") as f:
            summary = json.load(f)
        return jsonify(summary)

    return jsonify({"error": "No summary available"}), 404


@dashboard_bp.route("/segments/distribution", methods=["GET"])
def segments_distribution():
    """Return per-cluster summary from processed_clients.csv"""
    csv_path = os.path.join(DATA_DIR, "processed_clients.csv")

    if not os.path.exists(csv_path):
        return jsonify({"error": "Processed clients file not found"}), 404

    df = pd.read_csv(csv_path)

    # Generate cluster summary
    cluster_summary = (
        df.groupby("cluster_label")
        .agg({
            "balance": "mean",
            "products_owned": "mean",
            "risk_score": "mean"
        })
        .reset_index()
        .rename(columns={
            "cluster_label": "Cluster",
            "balance": "Avg_Balance",
            "products_owned": "Avg_Products",
            "risk_score": "Avg_Risk_Score"
        })
    )

    return jsonify({
        "total_clusters": len(cluster_summary),
        "data": cluster_summary.to_dict(orient="records")
    })


@dashboard_bp.route("/charts/<path:filename>", methods=["GET"])
def serve_chart(filename):
    """Serve static chart images or HTML plots."""
    if not os.path.exists(os.path.join(CHARTS_DIR, filename)):
        return jsonify({"error": f"Chart not found: {filename}"}), 404

    return send_from_directory(CHARTS_DIR, filename)

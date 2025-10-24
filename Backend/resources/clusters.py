from flask import Blueprint, jsonify, send_from_directory, current_app
from models import ClientRecord, db
from ml_loader import load_dataset
from utils import ResponseTemplate, ErrorHandler
import os

# Define the Blueprint (only once)
clusters_bp = Blueprint("clusters", __name__)

# -------------------------------------------
# 1️⃣ Database-based endpoints
# -------------------------------------------

@clusters_bp.route("/summary", methods=["GET"])
def cluster_summary():
    """Return aggregated cluster counts and basic stats from the database."""
    try:
        rows = (
            ClientRecord.query
            .with_entities(ClientRecord.cluster_label, db.func.count(ClientRecord.id))
            .group_by(ClientRecord.cluster_label)
            .all()
        )
        summary = [{"cluster": r[0], "count": r[1]} for r in rows]
        
        return ResponseTemplate.success(
            message="Cluster summary retrieved successfully",
            data=summary,
            metadata={"total_clusters": len(summary)}
        )
    except Exception as e:
        return ErrorHandler.handle_exception(e, "cluster summary")


@clusters_bp.route("/clients/<int:cluster_label>", methods=["GET"])
def clients_in_cluster(cluster_label):
    """Return all clients belonging to a given cluster."""
    try:
        recs = ClientRecord.query.filter_by(cluster_label=cluster_label).all()
        clients = [
            {
                "client_id": r.client_id,
                "age": r.age,
                "balance": r.balance,
                "tx_count": r.tx_count,
                "client_metadata": r.client_metadata,
            }
            for r in recs
        ]
        
        return ResponseTemplate.success(
            message=f"Clients in cluster {cluster_label} retrieved successfully",
            data=clients,
            metadata={
                "cluster_label": cluster_label,
                "total_clients": len(clients)
            }
        )
    except Exception as e:
        return ErrorHandler.handle_exception(e, f"clients in cluster {cluster_label}")


@clusters_bp.route("/plot/<path:filename>", methods=["GET"])
def cluster_plot(filename):
    """Serve static plot images exported from Jupyter (placed in uploads folder)."""
    uploads = current_app.config.get("UPLOAD_FOLDER", "uploads")
    return send_from_directory(uploads, filename)


# -------------------------------------------
# 2️⃣ ML Data Loading Endpoints
# -------------------------------------------

@clusters_bp.route("/datasets/<dataset_name>", methods=["GET"])
def get_dataset(dataset_name):
    """
    Endpoint to load datasets dynamically from ML assets.
    Example: /api/datasets/processed
    """
    try:
        df = load_dataset(dataset_name)
        data = df.head(100).to_dict(orient="records")  # limit to first 100 rows for performance
        
        return ResponseTemplate.success(
            message=f"Dataset '{dataset_name}' loaded successfully",
            data={
                "dataset": dataset_name,
                "rows": len(df),
                "columns": list(df.columns),
                "data": data
            },
            metadata={
                "total_rows": len(df),
                "columns_count": len(df.columns),
                "sample_size": len(data)
            }
        )
    except Exception as e:
        return ErrorHandler.handle_exception(e, f"load dataset {dataset_name}")

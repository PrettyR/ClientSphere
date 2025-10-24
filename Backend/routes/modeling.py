from flask import Blueprint, jsonify, request
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score

from ml_loader import load_dataset
from preprocessing import prepare_features, build_numeric_preprocess_pipeline


modeling_bp = Blueprint("modeling", __name__)


@modeling_bp.route("/kmeans", methods=["POST"])
def run_kmeans():
    payload = request.get_json(silent=True) or {}
    n_clusters = int(payload.get("n_clusters", 3))

    df = load_dataset()
    drop_columns = ["cluster_label", "client_id"] if "client_id" in df.columns else ["cluster_label"]
    X, feature_columns = prepare_features(df, drop_columns=drop_columns)
    pipeline = build_numeric_preprocess_pipeline()
    X_scaled = pipeline.fit_transform(X)

    km = KMeans(n_clusters=n_clusters, n_init="auto", random_state=42)
    labels = km.fit_predict(X_scaled)

    sil = float(silhouette_score(X_scaled, labels)) if n_clusters > 1 else None
    centers = km.cluster_centers_.tolist()

    return jsonify({
        "n_clusters": n_clusters,
        "silhouette": sil,
        "centers": centers,
        "labels": np.asarray(labels).astype(int).tolist(),
        "features": feature_columns,
    })


@modeling_bp.route("/dbscan", methods=["POST"])
def run_dbscan():
    payload = request.get_json(silent=True) or {}
    eps = float(payload.get("eps", 0.5))
    min_samples = int(payload.get("min_samples", 5))

    df = load_dataset()
    drop_columns = ["cluster_label", "client_id"] if "client_id" in df.columns else ["cluster_label"]
    X, _ = prepare_features(df, drop_columns=drop_columns)
    pipeline = build_numeric_preprocess_pipeline()
    X_scaled = pipeline.fit_transform(X)

    dbs = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbs.fit_predict(X_scaled)
    unique_labels = sorted(set(labels))
    n_clusters = len([l for l in unique_labels if l != -1])

    sil = None
    if n_clusters > 1 and len(set(labels)) > 1 and (labels != -1).any():
        try:
            sil = float(silhouette_score(X_scaled, labels))
        except Exception:
            sil = None

    return jsonify({
        "eps": eps,
        "min_samples": min_samples,
        "n_clusters": n_clusters,
        "labels": np.asarray(labels).astype(int).tolist(),
        "silhouette": sil,
    })


@modeling_bp.route("/silhouette", methods=["POST"])
def compute_silhouette():
    payload = request.get_json(silent=True) or {}
    n_clusters = int(payload.get("n_clusters", 3))

    df = load_dataset()
    drop_columns = ["cluster_label", "client_id"] if "client_id" in df.columns else ["cluster_label"]
    X, _ = prepare_features(df, drop_columns=drop_columns)
    pipeline = build_numeric_preprocess_pipeline()
    X_scaled = pipeline.fit_transform(X)

    if n_clusters < 2:
        return jsonify({"error": "n_clusters must be >= 2 for silhouette"}), 400

    km = KMeans(n_clusters=n_clusters, n_init="auto", random_state=42)
    labels = km.fit_predict(X_scaled)
    sil = float(silhouette_score(X_scaled, labels))
    return jsonify({"n_clusters": n_clusters, "silhouette": sil})



from flask import Blueprint, jsonify, request
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from scipy import stats

from ml_loader import load_dataset
from preprocessing import prepare_features, build_numeric_preprocess_pipeline


analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.route("/correlation", methods=["GET"])
def correlation_matrix():
    df = load_dataset()
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr(numeric_only=True).fillna(0.0)
    return jsonify({"columns": corr.columns.tolist(), "matrix": corr.values.tolist()})


@analysis_bp.route("/anova", methods=["GET"])
def anova_across_clusters():
    df = load_dataset()
    if "cluster_label" not in df.columns:
        return jsonify({"error": "cluster_label not found in dataset"}), 400

    numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c != "cluster_label"]
    groups = {int(k): v for k, v in df.groupby("cluster_label").groups.items()}

    results = []
    for col in numeric_cols:
        samples = [df.loc[idx_list, col].dropna().values for _, idx_list in groups.items()]
        if len([s for s in samples if len(s) > 1]) < 2:
            results.append({"feature": col, "f_stat": None, "p_value": None})
            continue
        f_stat, p_value = stats.f_oneway(*samples)
        results.append({"feature": col, "f_stat": float(f_stat), "p_value": float(p_value)})

    return jsonify({"results": results})


@analysis_bp.route("/feature-importance", methods=["POST"])
def feature_importance():
    df = load_dataset()
    if "cluster_label" not in df.columns:
        return jsonify({"error": "cluster_label not found in dataset"}), 400

    drop_columns = ["cluster_label", "client_id"] if "client_id" in df.columns else ["cluster_label"]
    X, feature_columns = prepare_features(df, drop_columns=drop_columns)
    y = df["cluster_label"].astype(int).values

    pipeline = build_numeric_preprocess_pipeline()
    X_transformed = pipeline.fit_transform(X)

    clf = RandomForestClassifier(n_estimators=200, random_state=42)
    clf.fit(X_transformed, y)
    importances = clf.feature_importances_.tolist()

    return jsonify({"features": feature_columns, "importances": importances})



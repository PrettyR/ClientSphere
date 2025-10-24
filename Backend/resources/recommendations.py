from flask import Blueprint, jsonify
from models import ClientRecord
recs_bp = Blueprint("recs", __name__)

# rule-based recommendation for demonstration
RULES = {
    0: ["Premium Wealth Plan", "High-yield savings"],
    1: ["Investment Advisory", "Estate planning"],
    2: ["Credit Line", "Short-term loans"]
}

@recs_bp.route("/for-cluster/<int:cluster>", methods=["GET"])
def recs_for_cluster(cluster):
    return jsonify({"cluster": cluster, "recommendations": RULES.get(cluster, [])})


@recs_bp.route("/for-client/<client_id>", methods=["GET"])
def recs_for_client(client_id: str):
    rec = ClientRecord.query.filter_by(client_id=str(client_id)).first()
    if not rec or rec.cluster_label is None:
        return jsonify({"client_id": client_id, "recommendations": [], "cluster": None})
    cluster = int(rec.cluster_label)
    return jsonify({
        "client_id": client_id,
        "cluster": cluster,
        "recommendations": RULES.get(cluster, [])
    })

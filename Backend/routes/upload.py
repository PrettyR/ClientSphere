# routes/upload.py
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import pandas as pd
from models import db, ClientRecord

upload_bp = Blueprint("upload_bp", __name__)

def safe_int(val):
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0

def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0

@upload_bp.route("/upload", methods=["POST"])
@cross_origin(origins="http://localhost:5173")  # allow requests from your frontend
def upload_csv():
    """
    Upload a CSV file and insert/update ClientRecord table.
    """
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        df = pd.read_csv(file)
    except Exception as e:
        print("CSV read error:", e)
        return jsonify({"error": f"Failed to read CSV: {str(e)}"}), 400

    with db.session.begin():
        for _, row in df.iterrows():
            # Handle different column name variations
            client_id = str(row.get("client_id") or row.get("CIFs") or row.get("CIF"))
            existing = ClientRecord.query.filter_by(client_id=client_id).first()

            # Keep cluster_label as-is (string or number)
            cluster_label = row.get("cluster_label") or row.get("Cluster") or row.get("cluster")
            age = safe_int(row.get("age") or row.get("Age"))
            balance = safe_float(row.get("balance") or row.get("Account_Balance") or row.get("Account Balance"))
            tx_count = safe_int(row.get("tx_count") or row.get("Transaction_Frequency") or row.get("Transaction Frequency"))

            if existing:
                existing.cluster_label = cluster_label
                existing.age = age
                existing.balance = balance
                existing.tx_count = tx_count
                existing.client_metadata = row.to_dict()
            else:
                new_rec = ClientRecord(
                    client_id=client_id,
                    age=age,
                    balance=balance,
                    tx_count=tx_count,
                    cluster_label=cluster_label,
                    client_metadata=row.to_dict(),
                )
                db.session.add(new_rec)

    return jsonify({"message": "CSV uploaded and data inserted/updated successfully."}), 200

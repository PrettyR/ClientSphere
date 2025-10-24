import os
import pandas as pd
from models import db, ClientRecord

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

CSV_PATH = os.getenv(
    "EXPORT_CSV",
    r"C:\Users\elohe\Desktop\Bank System\Backend\ML assets\processed_data\processed_clients.csv"
)

# -------------------------------------------------------------------
# 1️⃣ Load Clients into DB
# -------------------------------------------------------------------

def load_clients(app, csv_path: str = CSV_PATH):
    """
    Load client data into the database or update existing entries.
    `app` must be passed to provide the Flask application context.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found at {csv_path}")

    df = pd.read_csv(csv_path)
    # Normalize new exported headers to expected keys
    df = df.rename(columns={
        "CIFs": "client_id",
        "Age": "age",
        "Account_Balance": "balance",
        "Transaction_Frequency": "tx_count",
        "Cluster": "cluster_label",
    })

    with app.app_context():
        for _, row in df.iterrows():
            client_id = str(row.get("client_id"))
            existing = ClientRecord.query.filter_by(client_id=client_id).first()
            cluster_label = int(row["cluster_label"]) if not pd.isna(row.get("cluster_label")) else None

            if existing:
                existing.cluster_label = cluster_label
                existing.age = int(row.get("age") or 0)
                existing.balance = float(row.get("balance") or 0)
                existing.tx_count = int(row.get("tx_count") or 0)
                existing.client_metadata = row.to_dict()
            else:
                new_rec = ClientRecord(
                    client_id=client_id,
                    age=int(row.get("age") or 0),
                    balance=float(row.get("balance") or 0),
                    tx_count=int(row.get("tx_count") or 0),
                    cluster_label=cluster_label,
                    client_metadata=row.to_dict(),
                )
                db.session.add(new_rec)

        db.session.commit()
        print(f"✅ Loaded {len(df)} client records into the database.")


# -------------------------------------------------------------------
# 2️⃣ Load Preprocessed Dataset
# -------------------------------------------------------------------

def load_dataset(file_path: str = CSV_PATH):
    """
    Load the preprocessed dataset into a pandas DataFrame.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found: {file_path}")

    df = pd.read_csv(file_path)
    print(f"✅ Loaded dataset from '{file_path}' with {len(df)} rows.")
    return df


# -------------------------------------------------------------------
# Script Execution
# -------------------------------------------------------------------

if __name__ == "__main__":
    # Lazy import of app to avoid circular imports
    from app import create_app
    app = create_app()
    load_clients(app)
    print("🎉 Client data successfully loaded into the database.")

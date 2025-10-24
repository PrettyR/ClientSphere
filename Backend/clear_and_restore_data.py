#!/usr/bin/env python3
"""
Script to clear the database and restore the original dataset
"""

from app import create_app
from models import db, ClientRecord
from ml_loader import load_clients
import os

def clear_and_restore():
    """Clear all client data and restore from original CSV"""
    app = create_app()
    
    with app.app_context():
        print("🗑️  Clearing existing client data...")
        
        # Delete all existing client records
        ClientRecord.query.delete()
        db.session.commit()
        
        print("✅ Cleared all client data from database")
        
        # Check if original CSV exists
        csv_path = os.path.join("ML assets", "processed_data", "processed_clients.csv")
        if os.path.exists(csv_path):
            print(f"📁 Found original CSV: {csv_path}")
            print("🔄 Loading original dataset...")
            
            # Load the original dataset
            load_clients(app, csv_path)
            
            # Check how many records were loaded
            count = ClientRecord.query.count()
            print(f"✅ Successfully loaded {count} client records from original dataset")
            
            # Show sample of loaded data
            sample = ClientRecord.query.first()
            if sample:
                print(f"📊 Sample record: ID={sample.client_id}, Balance={sample.balance}, Cluster={sample.cluster_label}")
        else:
            print(f"❌ Original CSV not found at: {csv_path}")
            print("Available files in ML assets/processed_data/:")
            data_dir = os.path.join("ML assets", "processed_data")
            if os.path.exists(data_dir):
                for file in os.listdir(data_dir):
                    print(f"  - {file}")
            else:
                print("  No data directory found")

if __name__ == "__main__":
    clear_and_restore()

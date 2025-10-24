from app import create_app
from models import db, ActivityLog

app = create_app()
with app.app_context():
    try:
        db.create_all()
        print("✅ All tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

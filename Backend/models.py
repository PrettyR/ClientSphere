from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    # Employee identifier replaces username for authentication context
    employee_id = db.Column(db.String(80), unique=True, nullable=True)
    username = db.Column(db.String(80), unique=True, nullable=True)  # kept for backward compatibility
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="employee")
    approved = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(16), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.employee_id or self.username}>"

class ActivityLog(db.Model):
    __tablename__ = "activity_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    user_email = db.Column(db.String(255), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    resource = db.Column(db.String(100), nullable=True)
    details = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ActivityLog {self.user_email} - {self.action}>"


class ClientRecord(db.Model):
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(128), unique=True, nullable=False)
    age = db.Column(db.Integer)
    balance = db.Column(db.Float)
    tx_count = db.Column(db.Integer)
    cluster_label = db.Column(db.Integer, nullable=True)
    client_metadata = db.Column(db.JSON)

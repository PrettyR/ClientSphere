from flask import Blueprint, request, jsonify
from models import db, ActivityLog, User
from flask_jwt_extended import jwt_required, get_jwt
from utils import ResponseTemplate, ErrorHandler

activity_bp = Blueprint("activity", __name__)

def log_activity(action, resource=None, details=None, user_id=None, user_email=None, ip_address=None):
    """Helper function to log user activities"""
    try:
        log = ActivityLog(
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Failed to log activity: {e}")

def is_admin():
    claims = get_jwt()
    return claims.get("role") == "admin"

@activity_bp.route("/logs", methods=["GET"])
@jwt_required()
def get_logs():
    try:
        if not is_admin():
            return ResponseTemplate.authorization_error(
                message="Administrator access required",
                user_action="Contact your administrator for access"
            )
        
        limit = request.args.get("limit", 100, type=int)
        logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(limit).all()
        
        log_data = [{
            "id": l.id,
            "user_email": l.user_email,
            "action": l.action,
            "resource": l.resource,
            "details": l.details,
            "ip_address": l.ip_address,
            "created_at": l.created_at.isoformat() if l.created_at else None
        } for l in logs]
        
        return ResponseTemplate.success(
            message="Activity logs retrieved successfully",
            data=log_data,
            metadata={"total_logs": len(log_data), "limit": limit}
        )
    except Exception as e:
        return ErrorHandler.handle_exception(e, "get activity logs")

@activity_bp.route("/logs/user/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user_logs(user_id):
    try:
        if not is_admin():
            return ResponseTemplate.authorization_error(
                message="Administrator access required",
                user_action="Contact your administrator for access"
            )
        
        logs = ActivityLog.query.filter_by(user_id=user_id).order_by(ActivityLog.created_at.desc()).limit(50).all()
        
        log_data = [{
            "id": l.id,
            "action": l.action,
            "resource": l.resource,
            "details": l.details,
            "ip_address": l.ip_address,
            "created_at": l.created_at.isoformat() if l.created_at else None
        } for l in logs]
        
        return ResponseTemplate.success(
            message=f"Activity logs for user {user_id} retrieved successfully",
            data=log_data,
            metadata={"user_id": user_id, "total_logs": len(log_data)}
        )
    except Exception as e:
        return ErrorHandler.handle_exception(e, f"get user {user_id} activity logs")

@activity_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    try:
        if not is_admin():
            return ResponseTemplate.authorization_error(
                message="Administrator access required",
                user_action="Contact your administrator for access"
            )
        
        total_logs = ActivityLog.query.count()
        unique_users = db.session.query(ActivityLog.user_email).distinct().count()
        
        # Most active users
        from sqlalchemy import func
        top_users = db.session.query(
            ActivityLog.user_email,
            func.count(ActivityLog.id).label("count")
        ).group_by(ActivityLog.user_email).order_by(func.count(ActivityLog.id).desc()).limit(10).all()
        
        # Most accessed resources
        top_resources = db.session.query(
            ActivityLog.resource,
            func.count(ActivityLog.id).label("count")
        ).filter(ActivityLog.resource.isnot(None)).group_by(ActivityLog.resource).order_by(func.count(ActivityLog.id).desc()).limit(10).all()
        
        stats_data = {
            "total_logs": total_logs,
            "unique_users": unique_users,
            "top_users": [{"email": u[0], "count": u[1]} for u in top_users],
            "top_resources": [{"resource": r[0], "count": r[1]} for r in top_resources]
        }
        
        return ResponseTemplate.success(
            message="Activity statistics retrieved successfully",
            data=stats_data,
            metadata={"total_logs": total_logs, "unique_users": unique_users}
        )
    except Exception as e:
        return ErrorHandler.handle_exception(e, "get activity statistics")


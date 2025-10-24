from flask import Blueprint, request, jsonify
from models import db, User
from flask_jwt_extended import jwt_required, get_jwt
from utils import ResponseTemplate, ValidationHelper, ErrorHandler
from utils.email_service import send_verification_code_email, send_account_approved_email
from urllib.parse import quote
import os
import random
import string

users_bp = Blueprint("users", __name__)

def is_admin():
    claims = get_jwt()
    return claims.get("role") == "admin"

@users_bp.route("/", methods=["GET"])
@jwt_required()
def list_users():
    try:
        users = User.query.all()
        user_data = [{
            "id": u.id, 
            "email": u.email, 
            "role": u.role, 
            "employee_id": u.employee_id, 
            "approved": u.approved,
            "email_verified": u.email_verified,
            "created_at": u.created_at.isoformat() if u.created_at else None
        } for u in users]
        
        return ResponseTemplate.success(
            message="Users retrieved successfully",
            data=user_data,
            metadata={"total_users": len(user_data)}
        )
    except Exception as e:
        return ErrorHandler.handle_exception(e, "list users")

@users_bp.route("/assign-role", methods=["POST"])
@jwt_required()
def assign_role():
    try:
        # Check admin permissions
        if not is_admin():
            return ResponseTemplate.authorization_error(
                message="Administrator access required",
                user_action="Contact your administrator for access"
            )
        
        data = request.get_json()
        if not data:
            return ResponseTemplate.validation_error(
                message="No data provided",
                user_action="Please provide user and role information"
            )
        
        user_id = data.get("user_id")
        role = data.get("role")
        
        # Validate required fields
        validation_error = ValidationHelper.validate_required_fields(
            data, ["user_id", "role"]
        )
        if validation_error:
            return validation_error
        
        # Validate role
        if role not in ["employee", "manager", "admin"]:
            return ResponseTemplate.validation_error(
                message="Invalid role specified",
                errors={"role": "Must be one of: employee, manager, admin"},
                user_action="Please select a valid role"
            )
        
        user = User.query.get(user_id)
        if not user:
            return ResponseTemplate.not_found_error(
                message="User not found",
                user_action="Please check the user ID and try again"
            )
        
        old_role = user.role
        user.role = role
        db.session.commit()
        
        return ResponseTemplate.success(
            message="User role updated successfully",
            data={
                "user_id": user.id,
                "old_role": old_role,
                "new_role": role,
                "user_email": user.email
            }
        )
    except Exception as e:
        return ErrorHandler.handle_exception(e, "assign user role")


@users_bp.route("/pending", methods=["GET"])
@jwt_required()
def list_pending():
    try:
        if not is_admin():
            return ResponseTemplate.authorization_error(
                message="Administrator access required",
                user_action="Contact your administrator for access"
            )
        
        users = User.query.filter_by(approved=False).all()
        pending_users = [{
            "id": u.id, 
            "email": u.email, 
            "employee_id": u.employee_id, 
            "role": u.role, 
            "approved": u.approved,
            "email_verified": u.email_verified,
            "created_at": u.created_at.isoformat() if u.created_at else None
        } for u in users]
        
        return ResponseTemplate.success(
            message="Pending users retrieved successfully",
            data=pending_users,
            metadata={"total_pending": len(pending_users)}
        )
    except Exception as e:
        return ErrorHandler.handle_exception(e, "list pending users")


@users_bp.route("/approve", methods=["POST"])
@jwt_required()
def approve_user():
    try:
        if not is_admin():
            return ResponseTemplate.authorization_error(
                message="Administrator access required",
                user_action="Contact your administrator for access"
            )
        
        data = request.get_json()
        if not data:
            return ResponseTemplate.validation_error(
                message="No data provided",
                user_action="Please provide user ID"
            )
        
        user_id = data.get("user_id")
        if not user_id:
            return ResponseTemplate.validation_error(
                message="User ID is required",
                user_action="Please provide a valid user ID"
            )
        
        user = User.query.get(user_id)
        if not user:
            return ResponseTemplate.not_found_error(
                message="User not found",
                user_action="Please check the user ID and try again"
            )
        
        if user.approved:
            return ResponseTemplate.error(
                message="User is already approved",
                error_code="USER_ALREADY_APPROVED",
                status_code=409,
                user_action="This user has already been approved"
            )
        
        user.approved = True
        db.session.commit()
        
        # Send approval notification email
        try:
            send_account_approved_email(
                email=user.email,
                user_name=user.employee_id or user.username
            )
        except Exception as e:
            print(f"Failed to send approval email to {user.email}: {e}")
        
        return ResponseTemplate.success(
            message="User approved successfully",
            data={
                "user_id": user.id,
                "user_email": user.email,
                "employee_id": user.employee_id,
                "role": user.role
            }
        )
    except Exception as e:
        return ErrorHandler.handle_exception(e, "approve user")


@users_bp.route("/delete/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    try:
        if not is_admin():
            return ResponseTemplate.authorization_error(
                message="Administrator access required",
                user_action="Contact your administrator for access"
            )
        
        user = User.query.get(user_id)
        if not user:
            return ResponseTemplate.not_found_error(
                message="User not found",
                user_action="Please check the user ID and try again"
            )
        
        user_email = user.email
        user_employee_id = user.employee_id
        # Remove dependent rows to satisfy FK constraints (e.g., activity logs)
        try:
            from models import ActivityLog
            # Either delete logs or null out user_id; here we delete logs
            ActivityLog.query.filter_by(user_id=user_id).delete(synchronize_session=False)
        except Exception as _:
            # If ActivityLog model or table is unavailable, continue with best effort
            pass

        db.session.delete(user)
        db.session.commit()
        
        return ResponseTemplate.success(
            message="User deleted successfully",
            data={
                "deleted_user_email": user_email,
                "deleted_employee_id": user_employee_id
            }
        )
    except Exception as e:
        return ErrorHandler.handle_exception(e, "delete user")


@users_bp.route("/send-code", methods=["POST"])
def send_code():
    try:
        data = request.get_json() or {}
        email = data.get("email")
        
        if not email:
            return ResponseTemplate.validation_error(
                message="Email address is required",
                user_action="Please provide your email address"
            )
        
        # Validate email format
        email_validation = ValidationHelper.validate_email(email)
        if email_validation:
            return email_validation
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return ResponseTemplate.not_found_error(
                message="No account found for this email",
                user_action="Please check your email address or register for a new account"
            )
        
        code = "".join(random.choices(string.digits, k=6))
        user.verification_code = code
        db.session.commit()
        
        # Send verification code via email
        email_sent = send_verification_code_email(
            email=email, 
            code=code, 
            user_name=user.employee_id or user.username
        )
        
        if email_sent:
            return ResponseTemplate.success(
                message="Verification code sent successfully",
                data={"email": email},
                metadata={"note": "Check your email for the verification code"}
            )
        else:
            # Fallback: still return success but log the code for manual verification
            print(f"[Email Failed] Verification code for {email}: {code}")
            return ResponseTemplate.success(
                message="Verification code generated",
                data={"email": email, "code": code},  # Include code in response for manual verification
                metadata={"note": "Email delivery failed. Please use the code provided in the response."}
            )
    except Exception as e:
        return ErrorHandler.handle_exception(e, "send verification code")


@users_bp.route("/verify-email", methods=["POST"])
def verify_email():
    try:
        data = request.get_json() or {}
        email = data.get("email")
        code = data.get("code")
        
        # Validate required fields
        validation_error = ValidationHelper.validate_required_fields(
            data, ["email", "code"]
        )
        if validation_error:
            return validation_error
        
        # Validate email format
        email_validation = ValidationHelper.validate_email(email)
        if email_validation:
            return email_validation
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return ResponseTemplate.not_found_error(
                message="No account found for this email",
                user_action="Please check your email address or register for a new account"
            )
        
        if not code or code != (user.verification_code or ""):
            return ResponseTemplate.validation_error(
                message="Invalid verification code",
                user_action="Please check the code and try again"
            )
        
        user.email_verified = True
        user.verification_code = None
        db.session.commit()
        
        return ResponseTemplate.success(
            message="Email verified successfully",
            data={
                "email": email,
                "email_verified": True
            }
        )
    except Exception as e:
        return ErrorHandler.handle_exception(e, "verify email")


@users_bp.route("/verify", methods=["GET"])  # e.g. /api/users/verify?email=...&code=...
def verify_email_via_link():
    try:
        email = request.args.get("email")
        code = request.args.get("code")

        # Validate required fields
        if not email or not code:
            return ResponseTemplate.validation_error(
                message="Missing email or code",
                user_action="Use the verification link from your email"
            )

        # Validate email format
        email_validation = ValidationHelper.validate_email(email)
        if email_validation:
            return email_validation

        user = User.query.filter_by(email=email).first()
        if not user:
            return ResponseTemplate.not_found_error(
                message="No account found for this email",
                user_action="Please check the email address"
            )

        if not user.verification_code or code != user.verification_code:
            return ResponseTemplate.validation_error(
                message="Invalid or expired verification code",
                user_action="Request a new verification email"
            )

        user.email_verified = True
        user.verification_code = None
        db.session.commit()

        return ResponseTemplate.success(
            message="Email verified successfully",
            data={"email": email, "email_verified": True}
        )
    except Exception as e:
        return ErrorHandler.handle_exception(e, "verify email via link")

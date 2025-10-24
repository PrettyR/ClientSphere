from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

from models import db, User, ClientRecord, ActivityLog
from resources.clusters import clusters_bp
from resources.recommendations import recs_bp
from resources.activity_logs import activity_bp
from routes.dashboard import dashboard_bp
from utils import setup_error_handling, ResponseTemplate, ValidationHelper, ErrorHandler
import config

def create_app():
    app = Flask(__name__)

    # -----------------------------
    # Configurations
    # -----------------------------
    app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
    app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "uploads")
    app.config["MAIL_SENDER"] = os.getenv("MAIL_SENDER", "no-reply@clientsphere.local")

    # -----------------------------
    # Initialize extensions
    # -----------------------------
    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)
    # ✅ Correct global CORS setup
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

    # -----------------------------
    # Database setup
    # -----------------------------
    with app.app_context():
        db.create_all()

    # -----------------------------
    # Setup error handling
    # -----------------------------
    setup_error_handling(app)

    # -----------------------------
    # Root route
    # -----------------------------
    @app.route("/")
    def root():
        return ResponseTemplate.success(
            message="ClientSphere backend is running",
            data={"status": "ClientSphere backend running"}
        )

    # -----------------------------
    # Registration
    # -----------------------------
    @app.route("/api/register", methods=["POST"])
    def register_user():
        try:
            data = request.get_json()
            if not data:
                return ResponseTemplate.validation_error(
                    message="No data provided",
                    user_action="Please provide registration information"
                )

            employee_id = data.get("employee_id") or data.get("username")
            email = data.get("email")
            password = data.get("password")
            confirm = data.get("confirm_password")
            role = data.get("role", "employee")

            # Validate required fields
            validation_error = ValidationHelper.validate_required_fields(
                data, ["employee_id", "email", "password"]
            )
            if validation_error:
                return validation_error

            # Validate email format
            email_validation = ValidationHelper.validate_email(email)
            if email_validation:
                return email_validation

            # Validate password strength
            password_validation = ValidationHelper.validate_password_strength(password)
            if password_validation:
                return password_validation

            # Check password confirmation
            if confirm is not None and confirm != password:
                return ResponseTemplate.validation_error(
                    message="Passwords do not match",
                    user_action="Please ensure both password fields match"
                )

            # Check for existing email
            if User.query.filter_by(email=email).first():
                return ResponseTemplate.error(
                    message="Email already registered",
                    error_code="EMAIL_EXISTS",
                    status_code=409,
                    user_action="Please use a different email address or try logging in"
                )

            # Check for existing employee ID
            if User.query.filter((User.employee_id==employee_id) | (User.username==employee_id)).first():
                return ResponseTemplate.error(
                    message="Employee ID already taken",
                    error_code="EMPLOYEE_ID_EXISTS",
                    status_code=409,
                    user_action="Please use a different employee ID"
                )

            # Create new user
            from werkzeug.security import generate_password_hash
            hashed_password = generate_password_hash(password)
            new_user = User(
                employee_id=employee_id,
                email=email,
                password_hash=hashed_password,
                role=role,
                approved=False
            )
            db.session.add(new_user)
            db.session.commit()

            return ResponseTemplate.success(
                message="Registration submitted successfully",
                data={"status": "pending_approval"},
                status_code=201
            )

        except Exception as e:
            return ErrorHandler.handle_exception(e, "user registration")

    # -----------------------------
    # Login
    # -----------------------------
    @app.route("/api/login", methods=["POST"])
    def login_user():
        try:
            data = request.get_json()
            if not data:
                return ResponseTemplate.validation_error(
                    message="No data provided",
                    user_action="Please provide login credentials"
                )

            email = data.get("email")
            password = data.get("password")

            # Validate required fields
            validation_error = ValidationHelper.validate_required_fields(
                data, ["email", "password"]
            )
            if validation_error:
                return validation_error

            from werkzeug.security import check_password_hash
            
            # Check default admin login
            default_admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "prettyraradza@gmail.com")
            default_admin_pass = os.getenv("DEFAULT_ADMIN_PASS", "Password#")
            if email == default_admin_email and password == default_admin_pass:
                from flask_jwt_extended import create_access_token
                from datetime import timedelta
                access_token = create_access_token(
                    identity="admin_default", 
                    expires_delta=timedelta(days=1), 
                    additional_claims={"role": "admin"}
                )
                
                # Log admin login
                try:
                    from resources.activity_logs import log_activity
                    log_activity("login", "admin", {"role": "admin"}, None, email, request.remote_addr)
                except Exception as e:
                    print(f"Activity logging failed: {e}")
                
                return ResponseTemplate.success(
                    message="Welcome back, Admin!",
                    data={
                        "access_token": access_token,
                        "role": "admin",
                        "user_id": "admin_default"
                    }
                )

            # Regular user login
            user = User.query.filter_by(email=email).first()
            if not user or not check_password_hash(user.password_hash, password):
                return ResponseTemplate.authentication_error(
                    message="Invalid email or password",
                    user_action="Please check your credentials and try again"
                )
            
            if not user.approved:
                return ResponseTemplate.authentication_error(
                    message="Your account is pending admin approval",
                    user_action="Please contact your administrator for account approval"
                )
            
            if not user.email_verified:
                return ResponseTemplate.authentication_error(
                    message="Please verify your email before logging in",
                    user_action="Check your email for verification instructions"
                )

            from flask_jwt_extended import create_access_token
            from datetime import timedelta
            access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=1))
            
            # Log user login
            try:
                from resources.activity_logs import log_activity
                log_activity("login", "auth", {"role": user.role}, user.id, user.email, request.remote_addr)
            except Exception as e:
                print(f"Activity logging failed: {e}")

            return ResponseTemplate.success(
                message=f"Welcome back, {user.employee_id or user.username}!",
                data={
                    "access_token": access_token,
                    "role": user.role,
                    "user_id": user.id
                }
            )

        except Exception as e:
            return ErrorHandler.handle_exception(e, "user login")

    # -----------------------------
    # Register blueprints
    # -----------------------------
    app.register_blueprint(clusters_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(recs_bp, url_prefix="/api/recommendations")
    app.register_blueprint(activity_bp, url_prefix="/api/activity")
    from resources.users import users_bp
    app.register_blueprint(users_bp, url_prefix="/api/users")

    # Upload and graph blueprints
    from routes.upload import upload_bp
    from routes.graph_data import graph_bp
    from routes.generate_charts import charts_bp
    from routes.analysis import analysis_bp
    from routes.modeling import modeling_bp

    # ✅ Make sure upload route matches React fetch URL
    app.register_blueprint(upload_bp, url_prefix="/api")  # final upload URL: /api/upload
    app.register_blueprint(graph_bp, url_prefix="/api")
    app.register_blueprint(charts_bp, url_prefix="/api")
    app.register_blueprint(analysis_bp, url_prefix="/api/analysis")
    app.register_blueprint(modeling_bp, url_prefix="/api/model")

    return app


# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    pwd = data.get("password")
    if User.query.filter_by(email=email).first():
        return jsonify({"msg":"Email exists"}), 400
    hashed = generate_password_hash(pwd)
    u = User(email=email, password_hash=hashed)
    db.session.add(u)
    db.session.commit()
    return jsonify({"msg":"registered"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data.get("email")).first()
    if not user or not check_password_hash(user.password_hash, data.get("password")):
        return jsonify({"msg":"Bad credentials"}), 401
    token = create_access_token(identity={"id": user.id, "role": user.role, "email": user.email})
    return jsonify({"access_token": token})

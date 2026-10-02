from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required
from app.extensions import db
from app.models import User
from app.schemas import UserValidator, ValidationError

users_bp = Blueprint("users", __name__)


@users_bp.get('/')
def us_get():
    return 'hello world'


@users_bp.post("/register")
def users_register():
    data = request.get_json(silent=True) or {}

    try:
        clean = UserValidator.validate(data)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    if User.query.filter_by(email=clean["email"]).first():
        return jsonify({"error": "Email уже занят"}), 409

    user = User(
        first_name=clean["first_name"],
        last_name=clean["last_name"],
        email=clean["email"],
    )
    user.set_password(clean["password"])

    db.session.add(user)
    db.session.commit()
    login_user(user)

    return jsonify({**user.to_dict(), "message": "Регистрация успешна"}), 201


@users_bp.post("/login")
def users_login():
    data = request.get_json(silent=True) or {}
    email = data.get("email").strip().lower()
    password = data.get('password')

    if not password or not email:
        return jsonify({"error": "Необходим пароль и email"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Неверный пароль "}), 401

    login_user(user)

    return jsonify({**user.to_dict(), "message": "Вы вошли в систему"}), 200


@users_bp.post("/logout")
@login_required
def users_logout():
    logout_user()
    return jsonify({"message": "Вы вышли из системы"}), 200
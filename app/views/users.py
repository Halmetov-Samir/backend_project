from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required,current_user
from app.extensions import db
from app.models import User,Role
from app.schemas import UserValidator, ValidationError
from app.decorators import require_permission

users_bp = Blueprint("users", __name__)


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
    email = (data.get("email") or "").strip().lower()
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


@users_bp.put("/profile")
@login_required
def update_profile():
    data = request.get_json(silent=True) or {}

    try:
        clean = UserValidator.validate(data, partial=True)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400


    if "email" in clean and clean["email"] != current_user.email:
        if User.query.filter_by(email=clean["email"]).first():
            return jsonify({"error": "Email уже занят"}), 409

    if "password" in clean:
        current_user.set_password(clean.pop("password"))


    for key, value in clean.items():
        setattr(current_user, key, value)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Не удалось обновить профиль"}), 500

    return jsonify({
        "message": "Профиль обновлён",
        "user": current_user.to_dict(),
    }), 200


@users_bp.get("/<int:user_id>")
@require_permission("users.list")
def get_user(user_id:int):
    user = db.session.get(User,user_id)
    if not user:
        return jsonify({'error':"Пользователь не найден"}),404
    return jsonify(user.to_dict()),200



@users_bp.get("")
@require_permission("users.list")
def get_users():
    users = User.query.all()
    return jsonify({
        "users": [u.to_dict() for u in users],
        "count": len(users),
    }), 200


@users_bp.delete("/profile")
@login_required
def delete_user():
    try:
        current_user.is_active = False
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Не удалось удалить аккаунт"}), 500

    logout_user()
    return jsonify({"message": "Аккаунт удалён"}), 200


@users_bp.put("/<int:user_id>/role")
@require_permission("roles.manage")
def change_role(user_id: int):
    user = db.session.get(User,user_id)
    if not user:
        return jsonify({'error': "Пользователь не найден"}), 404

    data = request.get_json(silent=True) or {}
    role_str = data.get('role')

    if role_str not in {r.value for r in Role}:
        return jsonify({"error": "Некорректная роль"}), 400
    if user.id == current_user.id:
        return jsonify({"error": "Нельзя менять свою роль"}), 400

    old_role = user.role.value
    user.role = Role(role_str)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Не удалось изменить роль"}), 500

    return jsonify({
        "message": f"Роль изменена с {old_role} на {user.role.value}",
        "user": user.to_dict(),
    }), 200



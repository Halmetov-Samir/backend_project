from functools import wraps
from flask import jsonify
from flask_login import current_user


def require_permission(permission: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args,**kwargs):
            if not current_user.is_authenticated:
                return jsonify({"error": "Требуется авторизация"}), 401

            if not current_user.has_permission(permission):
                return jsonify({"error": "Недостаточно прав"}), 403
            return fn(*args,**kwargs)
        return wrapper
    return decorator
import os
from flask import Flask, jsonify
from app.config import config
from app.extensions import db, migrate, login_manager
from app.views import users_bp, products_bp

def create_app(config_name: str | None = None) -> Flask:
    config_name = config_name or os.environ.get("FLASK_ENV", "default")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    app.register_blueprint(users_bp, url_prefix="/users")

    app.register_blueprint(products_bp, url_prefix="/products")

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    return app
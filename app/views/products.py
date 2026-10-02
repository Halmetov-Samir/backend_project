from flask import Blueprint, request, jsonify

from app.extensions import db
from app.models import Product
from app.schemas import ProductValidator, ValidationError
from app.decorators import require_permission


products_bp = Blueprint("products", __name__)


@products_bp.post("")
@require_permission("products.write")
def create_product():
    data = request.get_json(silent=True) or {}

    try:
        clean = ProductValidator.validate(data)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    product = Product(**clean)

    try:
        db.session.add(product)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Не удалось создать товар"}), 500

    return jsonify({
        "message": "Товар создан",
        "product": product.to_dict(),
    }), 201
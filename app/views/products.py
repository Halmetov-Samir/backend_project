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


@products_bp.get('')
@require_permission("products.read")
def list_product():
    products = Product.query.filter_by(is_active=True).all()
    return jsonify({
        "products": [p.to_dict() for p in products],
        "count": len(products),
    }), 200


@products_bp.get("/<int:product_id>")
@require_permission("products.read")
def get_product(product_id:int):
    product = db.session.get(Product,product_id)
    if not product or product.is_active:
        return jsonify({'error':"Товар не найден"}),404
    return jsonify(product.to_dict()),200


@products_bp.put("/<int:product_id>")
@require_permission("products.write")
def put_product(product_id:int):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': "Товар не найден"}), 404

    data = request.get_json(silent=True) or {}

    try:
        clean = ProductValidator.validate(data,partial=True)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

    for key,value in clean.items():
        setattr(product,key,value)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Не удалось обновить товар"}), 500

    return jsonify({
        "message":"Товар обновлён",
        "product":product.to_dict(),
    }), 200


@products_bp.delete("/<int:product_id>")
@require_permission("products.delete")
def delete_product(product_id:int):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': "Товар не найден"}), 404

    try:
        product.is_active = False
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Не удалось удалить товар"}), 500

    return jsonify({
        "message":"Товар удален",
    }), 200


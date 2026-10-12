def test_create_product_as_admin(admin_client, product_data):
    response = admin_client.post("/products", json=product_data)

    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Товар создан"
    assert data["product"]["name"] == "Ноутбук"
    assert data["product"]["price"] == 50000.0
    assert data["product"]["quantity"] == 10
    assert data["product"]["is_active"] is True


def test_create_product_as_user_forbidden(auth_client, product_data):
    response = auth_client.post("/products", json=product_data)

    assert response.status_code == 403


def test_create_product_without_auth(client, product_data):
    response = client.post("/products", json=product_data)

    assert response.status_code == 401


def test_create_product_empty_name(admin_client):
    response = admin_client.post("/products", json={
        "name": "",
        "price": 50000,
        "quantity": 10,
    })

    assert response.status_code == 400


def test_create_product_negative_price(admin_client):
    response = admin_client.post("/products", json={
        "name": "Ноутбук",
        "price": -100,
        "quantity": 10,
    })

    assert response.status_code == 400


def test_create_product_invalid_price(admin_client):
    response = admin_client.post("/products", json={
        "name": "Ноутбук",
        "price": "дорого",
        "quantity": 10,
    })

    assert response.status_code == 400


def test_create_product_invalid_quantity(admin_client):
    response = admin_client.post("/products", json={
        "name": "Ноутбук",
        "price": 50000,
        "quantity": "много",
    })

    assert response.status_code == 400


def test_create_product_missing_fields(admin_client):
    response = admin_client.post("/products", json={})

    assert response.status_code == 400


def test_list_products_empty(admin_client):
    response = admin_client.get("/products")

    assert response.status_code == 200
    data = response.get_json()
    assert data["products"] == []
    assert data["count"] == 0


def test_list_products_with_items(admin_client, product_data):
    admin_client.post("/products", json=product_data)
    admin_client.post("/products", json={
        "name": "Мышь",
        "price": 1000,
        "quantity": 50,
    })

    response = admin_client.get("/products")

    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 2


def test_list_products_as_user(auth_client, app, product_data):
    from app.models import Product
    from app.extensions import db as _db

    with app.app_context():
        product = Product(
            name=product_data["name"],
            price=product_data["price"],
            quantity=product_data["quantity"],
        )
        _db.session.add(product)
        _db.session.commit()

    response = auth_client.get("/products")

    assert response.status_code == 200


def test_list_products_without_auth(client):
    response = client.get("/products")

    assert response.status_code == 401


def test_get_product_by_id(admin_client, product_data):
    create = admin_client.post("/products", json=product_data)
    product_id = create.get_json()["product"]["id"]

    response = admin_client.get(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.get_json()["name"] == "Ноутбук"


def test_get_nonexistent_product(admin_client):
    response = admin_client.get("/products/9999")

    assert response.status_code == 404


def test_get_product_without_auth(client):
    response = client.get("/products/1")

    assert response.status_code == 401


def test_update_product_price_only(admin_client, product_data):
    create = admin_client.post("/products", json=product_data)
    product_id = create.get_json()["product"]["id"]

    response = admin_client.put(f"/products/{product_id}", json={
        "price": 60000,
    })

    assert response.status_code == 200
    data = response.get_json()["product"]
    assert data["price"] == 60000.0
    assert data["name"] == "Ноутбук"
    assert data["quantity"] == 10


def test_update_product_name(admin_client, product_data):
    create = admin_client.post("/products", json=product_data)
    product_id = create.get_json()["product"]["id"]

    response = admin_client.put(f"/products/{product_id}", json={
        "name": "Ноутбук Pro",
    })

    assert response.status_code == 200
    assert response.get_json()["product"]["name"] == "Ноутбук Pro"


def test_update_product_as_user_forbidden(auth_client, app, product_data):
    from app.models import Product
    from app.extensions import db as _db

    with app.app_context():
        product = Product(
            name=product_data["name"],
            price=product_data["price"],
            quantity=product_data["quantity"],
        )
        _db.session.add(product)
        _db.session.commit()
        product_id = product.id

    response = auth_client.put(f"/products/{product_id}", json={
        "price": 60000,
    })

    assert response.status_code == 403


def test_update_nonexistent_product(admin_client):
    response = admin_client.put("/products/9999", json={
        "price": 100,
    })

    assert response.status_code == 404


def test_delete_product_soft(admin_client, product_data):
    create = admin_client.post("/products", json=product_data)
    product_id = create.get_json()["product"]["id"]

    response = admin_client.delete(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Товар удалён"

    response = admin_client.get(f"/products/{product_id}")
    assert response.status_code == 404

    response = admin_client.get("/products")
    assert response.get_json()["count"] == 0


def test_delete_product_as_user_forbidden(auth_client, app, product_data):
    from app.models import Product
    from app.extensions import db as _db

    with app.app_context():
        product = Product(
            name=product_data["name"],
            price=product_data["price"],
            quantity=product_data["quantity"],
        )
        _db.session.add(product)
        _db.session.commit()
        product_id = product.id

    response = auth_client.delete(f"/products/{product_id}")

    assert response.status_code == 403


def test_delete_nonexistent_product(admin_client):
    response = admin_client.delete("/products/9999")

    assert response.status_code == 404


def test_delete_product_without_auth(client):
    response = client.delete("/products/1")

    assert response.status_code == 401
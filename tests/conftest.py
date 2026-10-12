import pytest

from app import create_app
from app.extensions import db as _db
from app.models import User, Product, Role


@pytest.fixture
def app():
    app = create_app("testing")

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user_data():
    return {
        "first_name": "Samir",
        "last_name": "Halmetov",
        "email": "user@test.com",
        "password": "password123",
    }


@pytest.fixture
def admin_data():
    return {
        "first_name": "Admin",
        "last_name": "Root",
        "email": "admin@test.com",
        "password": "admin12345",
    }


@pytest.fixture
def product_data():
    return {
        "name": "Ноутбук",
        "price": 50000,
        "quantity": 10,
    }


@pytest.fixture
def auth_client(client, user_data):
    client.post("/users/register", json=user_data)
    return client


@pytest.fixture
def admin_client(client, app, admin_data):
    with app.app_context():
        admin = User(
            first_name=admin_data["first_name"],
            last_name=admin_data["last_name"],
            email=admin_data["email"],
            role=Role.ADMIN,
        )
        admin.set_password(admin_data["password"])
        _db.session.add(admin)
        _db.session.commit()

    client.post("/users/login", json={
        "email": admin_data["email"],
        "password": admin_data["password"],
    })
    return client
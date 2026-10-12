def test_get_profile_without_auth(client):
    response = client.get("/users/profile")
    assert response.status_code == 401


def test_get_profile(auth_client):
    response = auth_client.get("/users/profile")
    assert response.status_code == 200
    data = response.get_json()
    assert data["email"] == "user@test.com"
    assert data["role"] == "user"
    assert data["is_active"] is True


def test_update_profile(auth_client):
    response = auth_client.put("/users/profile", json={
        "first_name": "Новое",
        "last_name": "Имя",
    })
    assert response.status_code == 200
    data = response.get_json()["user"]
    assert data["first_name"] == "Новое"
    assert data["last_name"] == "Имя"


def test_update_profile_email_taken(auth_client, app):
    from app.models import User
    from app.extensions import db as _db

    with app.app_context():
        other = User(
            first_name="Other",
            last_name="User",
            email="other@test.com",
        )
        other.set_password("password123")
        _db.session.add(other)
        _db.session.commit()

    response = auth_client.put("/users/profile", json={
        "email": "other@test.com",
    })

    assert response.status_code == 409


def test_update_profile_invalid_email(auth_client):
    response = auth_client.put("/users/profile", json={
        "email": "not-an-email",
    })
    assert response.status_code == 400


def test_update_profile_without_auth(client):
    response = client.put("/users/profile", json={
        "first_name": "X",
    })
    assert response.status_code == 401


def test_delete_profile(auth_client):
    response = auth_client.delete("/users/profile")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Аккаунт удалён"


def test_profile_after_delete(auth_client):
    auth_client.delete("/users/profile")
    response = auth_client.get("/users/profile")
    assert response.status_code == 401


def test_delete_profile_without_auth(client):
    response = client.delete("/users/profile")
    assert response.status_code == 401


def test_list_users_as_user(auth_client):
    response = auth_client.get("/users")
    assert response.status_code == 403


def test_list_users_as_admin(admin_client):
    response = admin_client.get("/users")
    assert response.status_code == 200
    data = response.get_json()
    assert "users" in data
    assert "count" in data


def test_list_users_without_auth(client):
    response = client.get("/users")
    assert response.status_code == 401


def test_get_user_by_id_admin(admin_client, app):
    from app.models import User
    from app.extensions import db as _db

    with app.app_context():
        other = User(
            first_name="Other",
            last_name="User",
            email="other@test.com",
        )
        other.set_password("password123")
        _db.session.add(other)
        _db.session.commit()
        user_id = other.id

    response = admin_client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.get_json()["email"] == "other@test.com"


def test_get_none_user(admin_client):
    response = admin_client.get("/users/9999")
    assert response.status_code == 404


def test_get_user_id_forbidden(auth_client, app):
    from app.models import User

    with app.app_context():
        admin = User.query.filter_by(email="admin@test.com").first()
        admin_id = admin.id if admin else 1

    response = auth_client.get(f"/users/{admin_id}")
    assert response.status_code == 403


def test_change_role(admin_client, app):
    from app.models import User
    from app.extensions import db as _db

    with app.app_context():
        user = User(
            first_name="Other",
            last_name="User",
            email="other@test.com",
        )
        user.set_password("password123")
        _db.session.add(user)
        _db.session.commit()
        user_id = user.id

    response = admin_client.put(f"/users/{user_id}/role", json={
        "role": "admin",
    })
    assert response.status_code == 200
    assert response.get_json()["user"]["role"] == "admin"


def test_change_role_invalid(admin_client, app):
    from app.models import User
    from app.extensions import db as _db

    with app.app_context():
        user = User(
            first_name="Other",
            last_name="User",
            email="other@test.com",
        )
        user.set_password("password123")
        _db.session.add(user)
        _db.session.commit()
        user_id = user.id

    response = admin_client.put(f"/users/{user_id}/role", json={
        "role": "superadmin",
    })
    assert response.status_code == 400


def test_change_own_role_forbidden(admin_client, app):
    from app.models import User

    with app.app_context():
        admin = User.query.filter_by(email="admin@test.com").first()
        admin_id = admin.id

    response = admin_client.put(f"/users/{admin_id}/role", json={
        "role": "user",
    })
    assert response.status_code == 400


def test_change_role_as_user_forbidden(auth_client, app):
    from app.models import User

    with app.app_context():
        user = User.query.filter_by(email="user@test.com").first()
        user_id = user.id

    response = auth_client.put(f"/users/{user_id}/role", json={
        "role": "admin",
    })
    assert response.status_code == 403
from app import create_app
from app.extensions import db
from app.models import User, Role

app = create_app()
with app.app_context():
    existing = User.query.filter_by(email="admin@example.com").first()

    if existing:
        print(f"Админ уже есть: id={existing.id}, role={existing.role.value}")
    else:
        admin = User(
            first_name="Admin",
            last_name="Root",
            email="admin@example.com",
            role=Role.ADMIN,
        )
        admin.set_password("admin12345")
        db.session.add(admin)
        db.session.commit()
        print(f"Админ создан: id={admin.id}")
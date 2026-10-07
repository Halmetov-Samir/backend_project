from enum import Enum
from sqlalchemy import Numeric
from flask_login import UserMixin
from app.extensions import db, bcrypt


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.ADMIN: {
        "profile.read", "profile.write", "profile.delete",
        "users.list", "roles.manage",
        "products.read", "products.write", "products.delete",
    },
    Role.USER: {
        "profile.read", "profile.write", "profile.delete",
        "products.read",
    },
    Role.GUEST: set(),
}


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False, default=Role.USER)
    is_active = db.Column(db.Boolean,nullable=False,default=True)

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode()

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def has_permission(self, permission: str) -> bool:
        return permission in ROLE_PERMISSIONS.get(self.role, set())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "role": self.role.value,
            "is_active":self.is_active
        }


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "price": float(self.price),
            "quantity": self.quantity,
            "is_active":self.is_active
        }
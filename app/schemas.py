import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ValidationError(Exception):
    pass


class UserValidator:
    MAX_FIRST_NAME_LENGTH = 100
    MAX_LAST_NAME_LENGTH = 100
    MAX_EMAIL_LENGTH = 255
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128

    @classmethod
    def validate(cls, data: dict, *, partial: bool = False) -> dict:
        if not isinstance(data, dict):
            raise ValidationError("Тело запроса должно быть объектом")

        result = {}

        if "first_name" in data or not partial:
            result["first_name"] = cls._validate_first_name(data.get("first_name"))

        if "last_name" in data or not partial:
            result["last_name"] = cls._validate_last_name(data.get("last_name"))

        if "email" in data or not partial:
            result["email"] = cls._validate_email(data.get("email"))

        if "password" in data or not partial:
            result["password"] = cls._validate_password(data.get("password"))

        return result

    @classmethod
    def _validate_first_name(cls, value) -> str:
        first_name = (value or "").strip()
        if not first_name:
            raise ValidationError("Имя обязательно")
        if len(first_name) > cls.MAX_FIRST_NAME_LENGTH:
            raise ValidationError(f"Имя до {cls.MAX_FIRST_NAME_LENGTH} символов")
        return first_name

    @classmethod
    def _validate_last_name(cls, value) -> str:
        last_name = (value or "").strip()
        if not last_name:
            raise ValidationError("Фамилия обязательна")
        if len(last_name) > cls.MAX_LAST_NAME_LENGTH:
            raise ValidationError(f"Фамилия до {cls.MAX_LAST_NAME_LENGTH} символов")
        return last_name

    @classmethod
    def _validate_email(cls, value) -> str:
        email = (value or "").strip().lower()
        if not email:
            raise ValidationError("Почта обязательна")
        if len(email) > cls.MAX_EMAIL_LENGTH:
            raise ValidationError(f"Почта до {cls.MAX_EMAIL_LENGTH} символов")
        if not EMAIL_RE.match(email):
            raise ValidationError("Некорректный email")
        return email

    @classmethod
    def _validate_password(cls, value) -> str:
        password = value or ""
        if not password:
            raise ValidationError("Пароль обязателен")
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            raise ValidationError(f"Пароль минимум {cls.MIN_PASSWORD_LENGTH} символов")
        if len(password) > cls.MAX_PASSWORD_LENGTH:
            raise ValidationError(f"Пароль до {cls.MAX_PASSWORD_LENGTH} символов")
        return password


class ProductValidator:
    MAX_NAME_LENGTH = 255
    MAX_PRICE = 1_000_000_000
    MAX_QUANTITY = 1_000_000

    @classmethod
    def validate(cls, data: dict, *, partial: bool = False) -> dict:
        if not isinstance(data, dict):
            raise ValidationError("Тело запроса должно быть объектом")

        result = {}

        if "name" in data or not partial:
            result["name"] = cls._validate_name(data.get("name"))

        if "price" in data or not partial:
            result["price"] = cls._validate_price(data.get("price"))

        if "quantity" in data or not partial:
            result["quantity"] = cls._validate_quantity(data.get("quantity"))

        return result

    @classmethod
    def _validate_name(cls, value) -> str:
        name = (value or "").strip()
        if not name:
            raise ValidationError("Название обязательно")
        if len(name) > cls.MAX_NAME_LENGTH:
            raise ValidationError(f"Название до {cls.MAX_NAME_LENGTH} символов")
        return name

    @classmethod
    def _validate_price(cls, value) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValidationError("Цена должна быть числом")
        if value < 0:
            raise ValidationError("Цена не может быть отрицательной")
        if value > cls.MAX_PRICE:
            raise ValidationError(f"Цена не может быть больше {cls.MAX_PRICE}")
        return float(value)

    @classmethod
    def _validate_quantity(cls, value) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValidationError("Количество должно быть целым числом")
        if value < 0:
            raise ValidationError("Количество не может быть отрицательным")
        if value > cls.MAX_QUANTITY:
            raise ValidationError(f"Количество не может быть больше {cls.MAX_QUANTITY}")
        return value
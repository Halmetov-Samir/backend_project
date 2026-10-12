# Flask Auth RBAC

REST API с аутентификацией, ролями и разграничением прав доступа.

Проект демонстрирует разделение прав между ролями ADMIN, USER и GUEST
на основе permission-модели.

## Эндпоинты

### Аутентификация

| Метод | URL | Доступ | Описание |
|---|---|---|---|
| POST | /users/register | все | Регистрация |
| POST | /users/login | все | Вход |
| POST | /users/logout | залогинен | Выход |

### Профиль

| Метод | URL | Доступ | Описание |
|---|---|---|---|
| GET | /users/profile | залогинен | Свой профиль |
| PUT | /users/profile | залогинен | Обновить профиль |
| DELETE | /users/profile | залогинен | Удалить аккаунт (soft delete) |

### Управление пользователями (ADMIN)

| Метод | URL | Доступ | Описание |
|---|---|---|---|
| GET | /users | ADMIN | Список пользователей |
| GET | /users/<id> | ADMIN | Один пользователь |
| PUT | /users/<id>/role | ADMIN | Сменить роль |

### Товары

| Метод | URL | Доступ | Описание |
|---|---|---|---|
| GET | /products | USER, ADMIN | Список товаров |
| GET | /products/<id> | USER, ADMIN | Один товар |
| POST | /products | ADMIN | Создать товар |
| PUT | /products/<id> | ADMIN | Обновить товар |
| DELETE | /products/<id> | ADMIN | Удалить товар (soft delete) |

## Роли

- ADMIN — полный доступ
- USER — чтение товаров, свой профиль
- GUEST — только публичные страницы

## Права

| Permission | ADMIN | USER | GUEST |
|---|:---:|:---:|:---:|
| profile.read | ✅ | ✅ | — |
| profile.write | ✅ | ✅ | — |
| profile.delete | ✅ | ✅ | — |
| products.read | ✅ | ✅ | — |
| products.write | ✅ | — | — |
| products.delete | ✅ | — | — |
| users.list | ✅ | — | — |
| roles.manage | ✅ | — | — |

## Слои

- views/ — HTTP-слой. Принимает запрос, вызывает сервис, отдаёт JSON.
- schemas/ — валидация входных данных. Отдельно от моделей (SRP).
- models/ — структура БД. SQLAlchemy-модели.
- decorators/ — проверка прав доступа на уровне роута.
- extensions.py — объекты расширений, создаются без app.
- config.py — настройки по окружениям.

## Тесты

Запуск:

    pytest -v
    pytest --cov=app --cov-report=term-missing

42 теста, 88% покрытия.

Покрыто:
- Регистрация, логин, логаут
- Профиль (GET, PUT, DELETE)
- RBAC (401, 403, 200 для разных ролей)
- CRUD товаров
- Soft delete
- Валидация входных данных

## Примеры запросов

### Регистрация

    POST http://127.0.0.1:5000/users/register
    Content-Type: application/json

    {
      "first_name": "Samir",
      "last_name": "Halmetov",
      "email": "samir@example.com",
      "password": "password123"
    }

Ответ (201):

    {
      "id": 1,
      "first_name": "Samir",
      "last_name": "Halmetov",
      "email": "samir@example.com",
      "role": "user",
      "message": "Регистрация успешна"
    }

### Логин

    POST http://127.0.0.1:5000/users/login
    Content-Type: application/json

    {
      "email": "samir@example.com",
      "password": "password123"
    }

Ответ (200):

    {
      "id": 1,
      "first_name": "Samir",
      "last_name": "Halmetov",
      "email": "samir@example.com",
      "role": "user",
      "message": "Вы вошли в систему"
    }

### Создание товара (ADMIN)

    POST http://127.0.0.1:5000/products
    Content-Type: application/json

    {
      "name": "Ноутбук",
      "price": 50000,
      "quantity": 10
    }

Ответ (201):

    {
      "message": "Товар создан",
      "product": {
        "id": 1,
        "name": "Ноутбук",
        "price": 50000.0,
        "quantity": 10,
        "is_active": true
      }
    }

### Смена роли (ADMIN)

    PUT http://127.0.0.1:5000/users/1/role
    Content-Type: application/json

    {
      "role": "admin"
    }

Ответ (200):

    {
      "message": "Роль изменена с user на admin",
      "user": {
        "id": 1,
        "first_name": "Samir",
        "last_name": "Halmetov",
        "email": "samir@example.com",
        "role": "admin",
        "is_active": true
      }
    }

## Создание первого ADMIN

Регистрация через API всегда даёт роль USER. Первый админ создаётся скриптом:

    python create_admin.py

Логин: admin@example.com / admin12345
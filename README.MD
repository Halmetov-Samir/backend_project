# Flask Auth RBAC

REST API с аутентификацией, ролями и разграничением прав доступа.

Проект демонстрирует разделение прав между ролями ADMIN, USER и GUEST
на основе permission-модели

## Эндпоинты

| Метод | URL | Доступ | Описание |
|---|---|---|---|
| POST | /users/register | все | Регистрация |
| POST | /users/login | все | Вход |
| POST | /users/logout | залогинен | Выход |
| POST | /products | ADMIN | Создать товар |

## Роли

- ADMIN — полный доступ
- USER — чтение товаров, свой профиль
- GUEST — только публичные страницы

## Права

- profile.read, profile.write, profile.delete
- products.read, products.write, products.delete
- users.list, roles.manage 


Слои:

- `views/` — HTTP-слой. Принимает запрос, вызывает сервис, отдаёт JSON.
- `schemas/` — валидация входных данных. Отдельно от моделей (SRP).
- `models/` — структура БД. SQLAlchemy-модели.
- `decorators/` — проверка прав доступа на уровне роута.
- `extensions.py` — объекты расширений, создаются без app.
- `config.py` — настройки по окружениям.


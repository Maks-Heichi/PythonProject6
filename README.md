# LMS API на Django + DRF

API для курсов и уроков: пользователь с входом по email, CRUD курса (ViewSet) и урока (Generic-классы).

## База PostgreSQL (pgAdmin4)

1. Запусти PostgreSQL.
2. В pgAdmin4: **Databases** → **Create** → **Database** → имя `pythonproject` → **Save**.
3. В корне проекта:
   ```bash
   copy .env.example .env
   ```
4. В `.env` укажи `DB_PASSWORD` (пароль пользователя `postgres`).

Таблицы создаёт Django: `python manage.py migrate`.

## Как запустить

```bash
cd PycharmProjects/pythonProject

python -m venv .venv
.venv\Scripts\activate

pip install django djangorestframework pillow psycopg2-binary python-dotenv
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

Или через Poetry:

```bash
poetry install
copy .env.example .env
poetry run python manage.py migrate
poetry run python manage.py runserver
```

API: http://127.0.0.1:8000/  
Админка: http://127.0.0.1:8000/admin/

Суперпользователь: `python manage.py createsuperuser` (вход по email)

## Эндпоинты для Postman

**Курсы (ViewSet):**
- `GET/POST` `/courses/`
- `GET/PUT/PATCH/DELETE` `/courses/{id}/`

**Уроки (Generic):**
- `GET` `/lessons/`
- `POST` `/lessons/create/`
- `GET` `/lessons/{id}/`
- `PUT/PATCH` `/lessons/{id}/update/`
- `DELETE` `/lessons/{id}/delete/`

Пример создания урока:

```json
{
  "title": "Введение",
  "description": "Первый урок",
  "video_url": "https://example.com/video",
  "course": 1
}
```

Для картинок в Postman: Body → form-data, поле `preview` типа File.

## Файлы проекта

- **manage.py** — команды Django
- **pyproject.toml** — зависимости (Django, DRF, Pillow, PostgreSQL)
- **.env.example** — пример настроек БД
- **.env** — пароль БД (только у себя, в Git не попадает)
- **.flake8** — настройки flake8

**config/settings.py** — настройки, PostgreSQL, DRF, пользователь, media  
**config/urls.py** — главные адреса  
**config/wsgi.py** — запуск на сервере  
**config/asgi.py** — асинхронный запуск  

**users/models.py** — модель пользователя (email, телефон, город, аватар)  
**users/managers.py** — создание пользователя и суперпользователя  
**users/admin.py** — админка пользователя  
**users/apps.py** — приложение  
**users/migrations/0001_initial.py** — таблицы пользователя  

**materials/models.py** — модели курса и урока  
**materials/serializers.py** — сериализаторы  
**materials/views.py** — ViewSet курса и Generic-классы урока  
**materials/urls.py** — адреса API  
**materials/admin.py** — админка Django  
**materials/apps.py** — приложение  
**materials/migrations/0001_initial.py** — таблицы курса и урока  

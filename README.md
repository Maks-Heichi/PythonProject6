# LMS API на Django + DRF

API для курсов и уроков: пользователь с входом по email, CRUD курса (ViewSet) и урока (Generic-классы).

## Как запустить

```bash
cd PycharmProjects/pythonProject

python -m venv .venv
.venv\Scripts\activate

pip install django djangorestframework pillow
python manage.py migrate
python manage.py runserver
```

Или через Poetry:

```bash
poetry install
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
- **pyproject.toml** — зависимости (Django, DRF, Pillow)

**config/settings.py** — настройки, DRF, пользователь, media  
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

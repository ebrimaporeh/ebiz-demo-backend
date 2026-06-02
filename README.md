# ebiz-demo-backend

Django REST Framework backend for the GAMBIH Internal Data Platform demo.

## Stack
- Django 4.2 + DRF 3.15
- PostgreSQL via Supabase (Transaction Pooler, port 6543)
- Supabase S3-compatible file storage
- JWT authentication (SimpleJWT)

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add credentials
python manage.py migrate
python manage.py runserver
```

## Project layout

```
backend/
├── apps/        ← all Django apps go here
├── config/
│   ├── settings/
│   │   ├── base.py        ← shared config
│   │   ├── development.py ← dev overrides
│   │   └── production.py  ← prod overrides
│   ├── urls.py            ← root URL conf
│   ├── wsgi.py
│   └── asgi.py
└── manage.py
```

## Creating a new app

```bash
mkdir -p apps/my_app
python manage.py startapp my_app apps/my_app
```

Then add `'apps.my_app'` to `LOCAL_APPS` in `config/settings/base.py`.

## API base URL

`http://localhost:8000/api/v1/`

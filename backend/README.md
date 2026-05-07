# Earthbucks API

FastAPI + SQLAlchemy + Alembic backend for Earthbucks.

## Quick start

```bash
# 1. From the backend/ directory, create a venv and install
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# edit .env — at minimum, set SECRET_KEY

# 3. Generate the initial migration (first time only)
alembic revision --autogenerate -m "initial schema"
alembic upgrade head

# 4. Seed from the legacy JSON files
python -m seed.seed

# 5. Run
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for the interactive API docs.

## Layout

```
backend/
├── alembic.ini
├── alembic/                # migrations
│   ├── env.py
│   └── versions/
├── app/
│   ├── main.py             # FastAPI entrypoint
│   ├── config.py           # env-driven settings
│   ├── database.py         # engine, SessionLocal, Base
│   ├── models.py           # SQLAlchemy ORM models
│   ├── schemas.py          # Pydantic request/response schemas
│   ├── crud.py             # DB operations
│   ├── auth.py             # password hashing + JWT
│   └── routers/            # one module per resource
├── seed/
│   ├── seed.py             # loads JSON snapshot into the DB
│   └── data/               # copied from /data/causes
├── requirements.txt
├── .env.example
└── .gitignore
```

## Authentication

JWT bearer tokens. Hit `POST /auth/signup`, then `POST /auth/login`
(OAuth2 password flow — `username` may be email or handle), then send
`Authorization: Bearer <token>` on protected routes.

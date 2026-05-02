# Python Flask Boilerplate

A production-ready Flask REST API boilerplate. Clone it, run one command, and have a fully working API in minutes.

**Stack**: Flask · SQLAlchemy 2.0 · Flask-JWT-Extended · Marshmallow · Swagger UI · Flask-Limiter · Docker

[![CI](https://github.com/asadiqbal791/python-flask-boilerplate/actions/workflows/ci.yml/badge.svg)](https://github.com/asadiqbal791/python-flask-boilerplate/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Quick Start

```bash
git clone https://github.com/asadiqbal791/python-flask-boilerplate.git
cd python-flask-boilerplate
bash setup.sh
```

`setup.sh` will:
- Create a virtual environment
- Install all dependencies
- Generate a `.env` with random secrets
- Ask which database you want (PostgreSQL / MySQL / SQLite / MongoDB)
- Run migrations
- Optionally seed sample data

Then start the server:
```bash
source .venv/bin/activate
flask run
```

API: `http://localhost:5000` · Docs: `http://localhost:5000/docs/`

---

## Features

### Authentication
| Feature | Details |
|---------|---------|
| **Custom JWT** | Access + refresh tokens, rotation, blacklisting |
| **Firebase Auth** | Verify ID token → auto create/login user |
| **Google OAuth** | Access-token flow (works web + mobile) |
| **GitHub OAuth** | Access-token flow |
| **Facebook OAuth** | Access-token flow |
| **Email verification** | Send link via SMTP, verify endpoint |
| **Password reset** | Forgot password → SMTP email → reset |

### Security
| Feature | Details |
|---------|---------|
| **DDoS / Rate limiting** | Flask-Limiter — 20/min on auth, 5/min on forgot-password |
| **Security headers** | CSP, HSTS, X-Frame-Options, X-XSS, Referrer-Policy |
| **CORS** | Configurable origins via `CORS_ORIGINS` env var |
| **JWT blacklisting** | Revoked tokens rejected on every request |
| **RBAC** | Role-based access control — `user` / `admin` |
| **Password hashing** | bcrypt via Werkzeug |

### Database
| Engine | How to enable |
|--------|--------------|
| **PostgreSQL** | `DB_ENGINE=postgresql` (default) |
| **MySQL** | `DB_ENGINE=mysql` |
| **SQLite** | `DATABASE_URL=sqlite:///flask_dev.db` |
| **MongoDB** | `MONGO_ENABLED=true` |

Switch database with **one env var**. No code changes. All services work for both SQL and MongoDB.

---

## Project Structure

```
app/
├── __init__.py          # App factory — create_app()
├── db.py                # DB abstraction (one place for SQL ↔ Mongo switch)
├── cli.py               # Flask CLI commands
├── config/
│   ├── config.py        # Dev / Test / Prod config + env validation
│   ├── roles.py         # RBAC role definitions
│   └── tokens.py        # Token type enums
├── models/
│   ├── sql/             # SQLAlchemy 2.0 models (User, Token)
│   └── mongo/           # MongoEngine models (MongoUser, MongoToken)
├── services/            # Business logic — one file per domain
│   ├── auth_service.py
│   ├── user_service.py
│   ├── token_service.py
│   ├── email_service.py
│   ├── firebase_service.py
│   └── social_auth_service.py
├── controllers/         # Request handlers (call services, return responses)
├── routes/v1/           # URL routing — auth_routes.py, user_routes.py
├── middlewares/         # @auth(), @validate(), error handler, rate limiter
├── validations/         # Marshmallow schemas
├── utils/               # ApiError, ApiResponse, pagination helpers
└── docs/                # Swagger / OpenAPI 3.0 config
```

**Architecture flow**: `Route → Controller → Service → DB abstraction → Model`

---

## CLI Commands

```bash
flask seed                  # seed DB with 4 sample users
flask seed --fresh          # drop all tables, recreate, then seed
flask create-admin          # create an admin user interactively
flask drop-db               # drop all SQL tables (confirmation required)
flask db-status             # show which DB engine is active + connection info
flask routes                # list all registered routes with methods
flask shell                 # Python REPL with User, Token, services pre-loaded
flask db migrate -m "msg"   # create a new Alembic migration (SQL only)
flask db upgrade            # apply pending migrations (SQL only)
flask db downgrade          # revert last migration (SQL only)
```

---

## API Reference

### Auth — `/v1/auth`

```
POST   /register           Register (email + password)
POST   /login              Login → access + refresh tokens
POST   /logout             Revoke refresh token
POST   /refresh-tokens     Rotate token pair
POST   /forgot-password    Send reset email
POST   /reset-password     Reset with token
GET    /verify-email       Verify email (token in query string)
GET    /me                 Get current user  [JWT required]
POST   /firebase           Login via Firebase ID token
POST   /google             Login via Google access token
POST   /github             Login via GitHub access token
POST   /facebook           Login via Facebook access token
```

### Users — `/v1/users`

```
GET    /                   List users, paginated  [admin]
POST   /                   Create user            [admin]
GET    /:id                Get user by ID         [admin]
PATCH  /:id                Update user            [admin]
DELETE /:id                Delete user            [admin]
GET    /me                 Get own profile        [JWT required]
PATCH  /me                 Update own profile     [JWT required]
```

---

## Environment Variables

Copy `.env.example` → `.env` and fill in what you need.

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | ✅ | Flask secret key |
| `JWT_SECRET_KEY` | ✅ | JWT signing key |
| `DATABASE_URL` | ✅* | SQL connection URL |
| `MONGO_ENABLED` | — | Set `true` to use MongoDB instead of SQL |
| `MONGODB_URI` | ✅* | MongoDB connection URI (if Mongo enabled) |
| `FIREBASE_CREDENTIALS_PATH` | — | Path to Firebase service account JSON |
| `GOOGLE_CLIENT_ID/SECRET` | — | Google OAuth credentials |
| `GITHUB_CLIENT_ID/SECRET` | — | GitHub OAuth app credentials |
| `SMTP_HOST/PORT/USERNAME/PASSWORD` | — | Email delivery |
| `REDIS_URL` | — | Redis for rate limiting + caching in production |
| `CORS_ORIGINS` | — | Allowed origins (default `*`) |

*One of `DATABASE_URL` or `MONGODB_URI` required depending on engine.

---

## Using the Auth Decorator

```python
from app.middlewares import auth

@auth()                     # Any authenticated user
@auth("manageUsers")        # Must have the manageUsers right
@auth("deleteUsers")        # Must have the deleteUsers right
def my_endpoint():
    ...
```

Rights per role:

| Right | user | admin |
|-------|------|-------|
| `getUsers` | ✅ | ✅ |
| `manageUsers` | ✅ | ✅ |
| `deleteUsers` | ❌ | ✅ |
| `manageSettings` | ❌ | ✅ |

---

## Switching Databases

The entire SQL ↔ Mongo switch lives in one file: [`app/database.py`](app/database.py).
All services call `_db.get_user_model()`, `_db.save()`, `_db.find_one()` etc.
You never touch service code when changing databases.

```env
# PostgreSQL (default)
MONGO_ENABLED=false
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mydb

# MongoDB
MONGO_ENABLED=true
MONGODB_URI=mongodb://localhost:27017/mydb

# SQLite (local dev — no server needed)
MONGO_ENABLED=false
DATABASE_URL=sqlite:///flask_dev.db
```

---

## Docker

```bash
# Development (hot-reload, no need for local postgres/redis)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# With MongoDB
docker-compose --profile mongo up
```

---

## Testing

```bash
pytest                      # run all tests
pytest --cov=app            # with coverage
pytest tests/integration/test_auth.py   # single file
```

Tests use SQLite in-memory so no database setup is needed.

---

## Adding a New Resource

1. **Model**: add `app/models/sql/post.py` (and `app/models/mongo/post.py` if you use Mongo)
2. **Service**: add `app/services/post_service.py` (use `app.db` helpers)
3. **Validation**: add `app/validations/post_validation.py` (Marshmallow schema)
4. **Controller**: add `app/controllers/post_controller.py`
5. **Routes**: add `app/routes/v1/post_routes.py` and register in `app/routes/v1/__init__.py`

That's the pattern. Every resource follows it identically.

---

## License

MIT

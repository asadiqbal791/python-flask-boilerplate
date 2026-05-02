import pytest
from app import create_app
from app.config.config import TestingConfig
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    _app = create_app(TestingConfig)
    with _app.app_context():
        _db.create_all()
        yield _app
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        yield _db
        _db.session.rollback()
        # Clean all tables between tests
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture
def admin_user(db):
    from app.models.sql import User
    user = User(name="Admin User", email="admin@test.com", role="admin", is_email_verified=True)
    user.set_password("Admin1234!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def regular_user(db):
    from app.models.sql import User
    user = User(name="Regular User", email="user@test.com", role="user", is_email_verified=True)
    user.set_password("User1234!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_tokens(client, admin_user):
    resp = client.post("/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "Admin1234!",
    })
    return resp.get_json()["data"]["tokens"]


@pytest.fixture
def user_tokens(client, regular_user):
    resp = client.post("/v1/auth/login", json={
        "email": "user@test.com",
        "password": "User1234!",
    })
    return resp.get_json()["data"]["tokens"]


def auth_header(tokens: dict) -> dict:
    return {"Authorization": f"Bearer {tokens['access']['token']}"}

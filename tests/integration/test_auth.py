import pytest
from tests.conftest import auth_header


class TestRegister:
    def test_register_success(self, client, db):
        resp = client.post("/v1/auth/register", json={
            "name": "New User",
            "email": "new@test.com",
            "password": "NewUser123!",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["success"] is True
        assert "tokens" in data["data"]
        assert data["data"]["user"]["email"] == "new@test.com"

    def test_register_duplicate_email(self, client, regular_user):
        resp = client.post("/v1/auth/register", json={
            "name": "Duplicate",
            "email": "user@test.com",
            "password": "Duplicate123!",
        })
        assert resp.status_code == 409

    def test_register_invalid_password(self, client):
        resp = client.post("/v1/auth/register", json={
            "name": "Bad",
            "email": "bad@test.com",
            "password": "weak",
        })
        assert resp.status_code == 400

    def test_register_missing_fields(self, client):
        resp = client.post("/v1/auth/register", json={"email": "x@x.com"})
        assert resp.status_code == 400


class TestLogin:
    def test_login_success(self, client, regular_user):
        resp = client.post("/v1/auth/login", json={
            "email": "user@test.com",
            "password": "User1234!",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["data"]["tokens"]["access"]["token"]

    def test_login_wrong_password(self, client, regular_user):
        resp = client.post("/v1/auth/login", json={
            "email": "user@test.com",
            "password": "WrongPass1!",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_email(self, client):
        resp = client.post("/v1/auth/login", json={
            "email": "ghost@test.com",
            "password": "Ghost1234!",
        })
        assert resp.status_code == 401


class TestLogout:
    def test_logout_success(self, client, user_tokens):
        resp = client.post("/v1/auth/logout", json={
            "refreshToken": user_tokens["refresh"]["token"]
        })
        assert resp.status_code == 200

    def test_logout_invalid_token(self, client):
        resp = client.post("/v1/auth/logout", json={"refreshToken": "invalid"})
        assert resp.status_code == 401


class TestRefreshTokens:
    def test_refresh_success(self, client, user_tokens):
        resp = client.post("/v1/auth/refresh-tokens", json={
            "refreshToken": user_tokens["refresh"]["token"]
        })
        assert resp.status_code == 200
        assert resp.get_json()["data"]["tokens"]["access"]["token"]


class TestGetMe:
    def test_get_me_authenticated(self, client, regular_user, user_tokens):
        resp = client.get("/v1/auth/me", headers=auth_header(user_tokens))
        assert resp.status_code == 200
        assert resp.get_json()["data"]["user"]["email"] == "user@test.com"

    def test_get_me_unauthenticated(self, client):
        resp = client.get("/v1/auth/me")
        assert resp.status_code == 401


class TestForgotResetPassword:
    def test_forgot_password_always_200(self, client):
        resp = client.post("/v1/auth/forgot-password", json={"email": "ghost@ghost.com"})
        assert resp.status_code == 200

    def test_reset_password_invalid_token(self, client):
        resp = client.post("/v1/auth/reset-password", json={
            "token": "badtoken",
            "password": "NewPass123!",
        })
        assert resp.status_code == 401

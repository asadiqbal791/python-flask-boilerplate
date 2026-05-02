import pytest
from tests.conftest import auth_header


class TestGetUsers:
    def test_admin_can_get_users(self, client, admin_user, regular_user, admin_tokens):
        resp = client.get("/v1/users/", headers=auth_header(admin_tokens))
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert data["totalResults"] >= 2

    def test_unauthenticated_cannot_get_users(self, client):
        resp = client.get("/v1/users/")
        assert resp.status_code == 401


class TestGetUser:
    def test_admin_can_get_any_user(self, client, regular_user, admin_tokens):
        resp = client.get(f"/v1/users/{regular_user.id}", headers=auth_header(admin_tokens))
        assert resp.status_code == 200
        assert resp.get_json()["data"]["user"]["id"] == regular_user.id

    def test_get_nonexistent_user(self, client, admin_tokens):
        resp = client.get("/v1/users/nonexistent-id", headers=auth_header(admin_tokens))
        assert resp.status_code == 404


class TestUpdateUser:
    def test_admin_can_update_user(self, client, regular_user, admin_tokens):
        resp = client.patch(
            f"/v1/users/{regular_user.id}",
            json={"name": "Updated Name"},
            headers=auth_header(admin_tokens),
        )
        assert resp.status_code == 200
        assert resp.get_json()["data"]["user"]["name"] == "Updated Name"

    def test_user_cannot_update_others(self, client, admin_user, user_tokens):
        resp = client.patch(
            f"/v1/users/{admin_user.id}",
            json={"name": "Hacker"},
            headers=auth_header(user_tokens),
        )
        assert resp.status_code == 403


class TestDeleteUser:
    def test_admin_can_delete_user(self, client, db, admin_tokens):
        from app.models.sql import User
        victim = User(name="ToDelete", email="delete@test.com", role="user")
        victim.set_password("Delete123!")
        db.session.add(victim)
        db.session.commit()

        resp = client.delete(f"/v1/users/{victim.id}", headers=auth_header(admin_tokens))
        assert resp.status_code == 204

    def test_user_cannot_delete(self, client, admin_user, user_tokens):
        resp = client.delete(f"/v1/users/{admin_user.id}", headers=auth_header(user_tokens))
        assert resp.status_code == 403


class TestProfile:
    def test_get_own_profile(self, client, regular_user, user_tokens):
        resp = client.get("/v1/users/me", headers=auth_header(user_tokens))
        assert resp.status_code == 200
        assert resp.get_json()["data"]["user"]["email"] == "user@test.com"

    def test_update_own_profile(self, client, regular_user, user_tokens):
        resp = client.patch(
            "/v1/users/me",
            json={"name": "My New Name"},
            headers=auth_header(user_tokens),
        )
        assert resp.status_code == 200
        assert resp.get_json()["data"]["user"]["name"] == "My New Name"

    def test_cannot_escalate_own_role(self, client, regular_user, user_tokens):
        resp = client.patch(
            "/v1/users/me",
            json={"role": "admin"},
            headers=auth_header(user_tokens),
        )
        # Role field is stripped, so update succeeds but role stays 'user'
        assert resp.status_code == 200
        assert resp.get_json()["data"]["user"]["role"] == "user"

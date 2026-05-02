"""Social OAuth2 service — Google, GitHub, Facebook.

Accepts an OAuth access token from the client (works for both web-redirect
and mobile flows). Verifies it with the provider, then upserts the user.
"""
import requests
from app.utils.api_error import ApiError
import app.database as _db
from . import user_service, token_service


def login_with_google_token(access_token: str):
    resp = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    if resp.status_code != 200:
        raise ApiError.unauthorized("Invalid Google token")
    info = resp.json()
    return _upsert_social_user(
        provider="google",
        provider_id=info["sub"],
        email=info.get("email", ""),
        name=info.get("name", ""),
        avatar=info.get("picture"),
        is_email_verified=info.get("email_verified", False),
    )


def login_with_github_token(access_token: str):
    headers = {"Authorization": f"token {access_token}"}
    user_resp = requests.get("https://api.github.com/user", headers=headers, timeout=10)
    if user_resp.status_code != 200:
        raise ApiError.unauthorized("Invalid GitHub token")
    info = user_resp.json()

    email = info.get("email")
    if not email:
        email_resp = requests.get("https://api.github.com/user/emails", headers=headers, timeout=10)
        if email_resp.status_code == 200:
            for entry in email_resp.json():
                if entry.get("primary") and entry.get("verified"):
                    email = entry["email"]
                    break

    return _upsert_social_user(
        provider="github",
        provider_id=str(info["id"]),
        email=email or "",
        name=info.get("name") or info.get("login", ""),
        avatar=info.get("avatar_url"),
        is_email_verified=True,
    )


def login_with_facebook_token(access_token: str):
    resp = requests.get(
        "https://graph.facebook.com/me",
        params={"fields": "id,name,email,picture", "access_token": access_token},
        timeout=10,
    )
    if resp.status_code != 200:
        raise ApiError.unauthorized("Invalid Facebook token")
    info = resp.json()
    pic = info.get("picture", {})
    avatar = pic.get("data", {}).get("url") if isinstance(pic, dict) else None
    return _upsert_social_user(
        provider="facebook",
        provider_id=info["id"],
        email=info.get("email", ""),
        name=info.get("name", ""),
        avatar=avatar,
        is_email_verified=bool(info.get("email")),
    )


def _upsert_social_user(provider: str, provider_id: str, email: str,
                         name: str, avatar, is_email_verified: bool):
    user = user_service.get_user_by_social_id(provider, provider_id)

    if not user and email:
        user = user_service.get_user_by_email(email)

    if user:
        updates: dict = {}
        if not getattr(user, f"{provider}_id", None):
            updates[f"{provider}_id"] = provider_id
        if avatar and not user.avatar:
            updates["avatar"] = avatar
        if updates:
            user = user_service.update_user(_db.record_id(user), updates)
    else:
        if not email:
            raise ApiError.bad_request("Could not retrieve email from provider")
        user = user_service.create_user({
            "name": name,
            "email": email,
            f"{provider}_id": provider_id,
            "avatar": avatar,
            "is_email_verified": is_email_verified,
        })

    tokens = token_service.generate_auth_tokens(_db.record_id(user))
    return user, tokens

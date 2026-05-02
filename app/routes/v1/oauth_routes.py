"""OAuth callback routes — handles server-side authorization code exchange.

GitHub OAuth requires:
  1. Browser → GitHub (get code)
  2. GitHub → /v1/oauth/github/callback?code=xxx (exchange code for token)
  3. Server → GitHub API (get access token with client secret)
  4. Server → our login service → return JWT tokens
"""
import requests
from flask import Blueprint, request, redirect, jsonify, current_app

oauth_bp = Blueprint("oauth", __name__, url_prefix="/oauth")


@oauth_bp.get("/github/callback")
def github_callback():
    code  = request.args.get("code")
    error = request.args.get("error")

    if error or not code:
        return _html_result(error=error or "No code received from GitHub")

    # Exchange code for access token
    cfg = current_app.config
    resp = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        json={
            "client_id":     cfg.get("GITHUB_CLIENT_ID"),
            "client_secret": cfg.get("GITHUB_CLIENT_SECRET"),
            "code":          code,
        },
        timeout=10,
    )

    if resp.status_code != 200:
        return _html_result(error=f"GitHub token exchange failed: {resp.text}")

    data = resp.json()
    if "error" in data:
        return _html_result(error=data.get("error_description", data["error"]))

    access_token = data.get("access_token")
    if not access_token:
        return _html_result(error="No access_token in GitHub response")

    # Call our own login endpoint
    from app.services.social_auth_service import login_with_github_token
    from app.utils.api_error import ApiError
    try:
        user, tokens = login_with_github_token(access_token)
        return _html_result(user=user.to_dict(), tokens=tokens)
    except ApiError as e:
        return _html_result(error=e.message)
    except Exception as e:
        current_app.logger.error("GitHub callback error: %s", e)
        return _html_result(error=str(e))


def _html_result(user=None, tokens=None, error=None):
    """Return a tiny HTML page that posts the result back to the opener window."""
    import json
    if error:
        payload = json.dumps({"success": False, "error": error})
    else:
        payload = json.dumps({"success": True, "user": user, "tokens": tokens})

    return f"""<!DOCTYPE html>
<html>
<head><title>OAuth Result</title></head>
<body>
<script>
  const result = {payload};
  if (window.opener) {{
    window.opener.postMessage(result, '*');
    window.close();
  }} else {{
    document.body.innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
  }}
</script>
<p>Completing login, this window should close automatically...</p>
</body>
</html>"""

from flask import current_app, render_template_string
from flask_mail import Message
from app.extensions import mail


_RESET_PASSWORD_TEMPLATE = """
<h2>Reset Your Password</h2>
<p>Click the link below to reset your password. This link expires in
{{ expiry_minutes }} minutes.</p>
<p><a href="{{ link }}">Reset Password</a></p>
<p>If you didn't request this, ignore this email.</p>
"""

_VERIFY_EMAIL_TEMPLATE = """
<h2>Verify Your Email</h2>
<p>Click the link below to verify your email address. This link expires in
{{ expiry_minutes }} minutes.</p>
<p><a href="{{ link }}">Verify Email</a></p>
"""


def _send(to: str, subject: str, html_body: str):
    msg = Message(subject=subject, recipients=[to], html=html_body)
    try:
        mail.send(msg)
    except Exception as exc:
        current_app.logger.error("Failed to send email to %s: %s", to, exc)


def send_reset_password_email(to: str, token: str):
    cfg = current_app.config
    link = f"{cfg['FRONTEND_URL']}/auth/reset-password?token={token}"
    expiry = cfg.get("JWT_RESET_PASSWORD_EXPIRATION_MINUTES", 10)
    html = render_template_string(
        _RESET_PASSWORD_TEMPLATE, link=link, expiry_minutes=expiry
    )
    _send(to, "Reset your password", html)


def send_verify_email(to: str, token: str):
    cfg = current_app.config
    link = f"{cfg['APP_URL']}/v1/auth/verify-email?token={token}"
    expiry = cfg.get("JWT_VERIFY_EMAIL_EXPIRATION_MINUTES", 10)
    html = render_template_string(
        _VERIFY_EMAIL_TEMPLATE, link=link, expiry_minutes=expiry
    )
    _send(to, "Verify your email address", html)

from datetime import datetime, timezone
from mongoengine import (
    Document, StringField, BooleanField, DateTimeField, EmailField
)
from werkzeug.security import generate_password_hash, check_password_hash
from app.config.roles import Role


def _utcnow():
    return datetime.now(timezone.utc)


class MongoUser(Document):
    meta = {
        "collection": "users",
        "indexes": ["email", "google_id", "github_id", "firebase_uid"],
    }

    name = StringField(required=True, max_length=128)
    email = EmailField(required=True, unique=True)
    password_hash = StringField()
    role = StringField(default=Role.USER, choices=[r for r in Role])
    is_email_verified = BooleanField(default=False)
    is_active = BooleanField(default=True)

    # Social
    google_id = StringField(unique=True, sparse=True)
    github_id = StringField(unique=True, sparse=True)
    facebook_id = StringField(unique=True, sparse=True)
    firebase_uid = StringField(unique=True, sparse=True)
    avatar = StringField()

    created_at = DateTimeField(default=_utcnow)
    updated_at = DateTimeField(default=_utcnow)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def save(self, *args, **kwargs):
        self.updated_at = _utcnow()
        return super().save(*args, **kwargs)

    def to_dict(self, include_private=False):
        data = {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "isEmailVerified": self.is_email_verified,
            "isActive": self.is_active,
            "avatar": self.avatar,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_private:
            data["googleId"] = self.google_id
            data["githubId"] = self.github_id
            data["firebaseUid"] = self.firebase_uid
        return data

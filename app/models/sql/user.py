import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.config.roles import Role


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)  # store as naive UTC — works on all DBs


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[str]               = mapped_column(String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str]             = mapped_column(String(128), nullable=False)
    email: Mapped[str]            = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    role: Mapped[str]             = mapped_column(String(32),  nullable=False, default=Role.USER)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool]       = mapped_column(Boolean, nullable=False, default=True)

    # Social identifiers — String, never Text, never indexed as Text
    google_id: Mapped[Optional[str]]    = mapped_column(String(128), nullable=True, unique=True, index=True)
    github_id: Mapped[Optional[str]]    = mapped_column(String(128), nullable=True, unique=True, index=True)
    facebook_id: Mapped[Optional[str]]  = mapped_column(String(128), nullable=True, unique=True, index=True)
    firebase_uid: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, unique=True, index=True)
    avatar: Mapped[Optional[str]]       = mapped_column(String(512), nullable=True)  # String not Text — MySQL safe

    # Naive UTC timestamps — compatible with MySQL, PostgreSQL, SQLite
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)

    tokens: Mapped[list["Token"]] = relationship(  # noqa: F821
        "Token", back_populates="user", cascade="all, delete-orphan", lazy="dynamic"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_private: bool = False) -> dict:
        data: dict = {
            "id":              self.id,
            "name":            self.name,
            "email":           self.email,
            "role":            self.role,
            "isEmailVerified": self.is_email_verified,
            "isActive":        self.is_active,
            "avatar":          self.avatar,
            "createdAt":       self.created_at.isoformat() + "Z" if self.created_at else None,
            "updatedAt":       self.updated_at.isoformat() + "Z" if self.updated_at else None,
        }
        if include_private:
            data.update({
                "googleId":    self.google_id,
                "githubId":    self.github_id,
                "firebaseUid": self.firebase_uid,
            })
        return data

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"

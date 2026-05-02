import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.extensions import db


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)  # naive UTC — works on all DBs


class Token(db.Model):
    __tablename__ = "tokens"

    id: Mapped[str]       = mapped_column(String(36),  primary_key=True, default=lambda: str(uuid.uuid4()))
    token: Mapped[str]    = mapped_column(String(512), nullable=False, index=True)  # String not Text — MySQL requires length for indexes
    type: Mapped[str]     = mapped_column(String(32),  nullable=False)
    expires: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    blacklisted: Mapped[bool] = mapped_column(Boolean,  nullable=False, default=False)
    user_id: Mapped[str]  = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=_utcnow)

    user: Mapped["User"] = relationship("User", back_populates="tokens")  # noqa: F821

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "token":       self.token,
            "type":        self.type,
            "expires":     self.expires.isoformat() + "Z" if self.expires else None,
            "blacklisted": self.blacklisted,
            "userId":      self.user_id,
        }

    def __repr__(self) -> str:
        return f"<Token type={self.type} user={self.user_id}>"

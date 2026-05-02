from datetime import datetime, timezone
from mongoengine import (
    Document, StringField, BooleanField, DateTimeField, ReferenceField
)
from app.config.tokens import TokenType


def _utcnow():
    return datetime.now(timezone.utc)


class MongoToken(Document):
    meta = {
        "collection": "tokens",
        "indexes": ["token", "user", "type"],
    }

    token = StringField(required=True)
    type = StringField(required=True, choices=[t.value for t in TokenType])
    expires = DateTimeField(required=True)
    blacklisted = BooleanField(default=False)
    user = ReferenceField("MongoUser", required=True)
    created_at = DateTimeField(default=_utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "token": self.token,
            "type": self.type,
            "expires": self.expires.isoformat() if self.expires else None,
            "blacklisted": self.blacklisted,
            "userId": str(self.user.id) if self.user else None,
        }

"""Initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing = inspector.get_table_names()

    if "users" not in existing:
        op.create_table(
            "users",
            sa.Column("id",               sa.String(36),  primary_key=True),
            sa.Column("name",             sa.String(128), nullable=False),
            sa.Column("email",            sa.String(255), nullable=False),
            sa.Column("password_hash",    sa.String(256), nullable=True),
            sa.Column("role",             sa.String(32),  nullable=False, server_default="user"),
            sa.Column("is_email_verified",sa.Boolean(),   nullable=False, server_default=sa.false()),
            sa.Column("is_active",        sa.Boolean(),   nullable=False, server_default=sa.true()),
            sa.Column("google_id",        sa.String(128), nullable=True),
            sa.Column("github_id",        sa.String(128), nullable=True),
            sa.Column("facebook_id",      sa.String(128), nullable=True),
            sa.Column("firebase_uid",     sa.String(128), nullable=True),
            sa.Column("avatar",           sa.String(512), nullable=True),
            sa.Column("created_at",       sa.DateTime(),  nullable=False),
            sa.Column("updated_at",       sa.DateTime(),  nullable=False),
        )
        op.create_index("ix_users_email",       "users", ["email"],       unique=True)
        op.create_index("ix_users_google_id",   "users", ["google_id"],   unique=True)
        op.create_index("ix_users_github_id",   "users", ["github_id"],   unique=True)
        op.create_index("ix_users_facebook_id", "users", ["facebook_id"], unique=True)
        op.create_index("ix_users_firebase_uid","users", ["firebase_uid"],unique=True)

    if "tokens" not in existing:
        op.create_table(
            "tokens",
            sa.Column("id",          sa.String(36),  primary_key=True),
            sa.Column("token",       sa.String(512), nullable=False),
            sa.Column("type",        sa.String(32),  nullable=False),
            sa.Column("expires",     sa.DateTime(),  nullable=False),
            sa.Column("blacklisted", sa.Boolean(),   nullable=False, server_default=sa.false()),
            sa.Column("user_id",     sa.String(36),  nullable=False),
            sa.Column("created_at",  sa.DateTime(),  nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        )
        op.create_index("ix_tokens_token", "tokens", ["token"], unique=False)


def downgrade():
    op.drop_table("tokens")
    op.drop_table("users")

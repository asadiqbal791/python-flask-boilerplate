"""Flask CLI commands — run with `flask <command>`

  flask seed              seed DB with sample users
  flask seed --fresh      drop + recreate tables first, then seed
  flask create-admin      create an admin user interactively
  flask drop-db           drop all SQL tables (with confirmation)
  flask db-reset          nuclear reset: wipe DB + alembic state, migrate fresh, seed
  flask routes            list all registered routes
  flask db-status         show which DB engine is active
"""
import click
from flask import current_app
from flask.cli import with_appcontext


def register_commands(app):
    app.cli.add_command(seed)
    app.cli.add_command(create_admin)
    app.cli.add_command(drop_db)
    app.cli.add_command(db_reset)
    app.cli.add_command(db_status)
    app.cli.add_command(routes)


# ── seed ─────────────────────────────────────────────────────────────────────

@click.command("seed")
@click.option("--fresh", is_flag=True, help="Drop and recreate tables before seeding.")
@with_appcontext
def seed(fresh):
    """Seed the database with sample data."""
    mongo = current_app.config.get("MONGO_ENABLED")

    if not mongo:
        from app.extensions import db
        if fresh:
            click.echo("Dropping all tables...")
            db.drop_all()
            click.echo("Recreating tables...")
            db.create_all()
        _seed_sql()
    else:
        _seed_mongo()

    click.secho("Database seeded successfully.", fg="green")


def _seed_sql():
    from app.extensions import db
    from app.models.sql import User, Token

    if User.query.count() > 0:
        click.echo("Database already has users — skipping seed. Use --fresh to reseed.")
        return

    users = [
        {"name": "Admin User",  "email": "admin@example.com",  "password": "Admin123!", "role": "admin",  "verified": True},
        {"name": "John Doe",    "email": "john@example.com",   "password": "User1234!", "role": "user",   "verified": True},
        {"name": "Jane Smith",  "email": "jane@example.com",   "password": "User1234!", "role": "user",   "verified": True},
        {"name": "Bob Wilson",  "email": "bob@example.com",    "password": "User1234!", "role": "user",   "verified": False},
    ]

    for u in users:
        user = User(
            name=u["name"],
            email=u["email"],
            role=u["role"],
            is_email_verified=u["verified"],
        )
        user.set_password(u["password"])
        db.session.add(user)
        click.echo(f"  + {u['role']:5}  {u['email']}")

    db.session.commit()


def _seed_mongo():
    from app.models.mongo import MongoUser

    if MongoUser.objects.count() > 0:
        click.echo("Database already has users — skipping seed. Delete users manually to reseed.")
        return

    users = [
        {"name": "Admin User",  "email": "admin@example.com",  "password": "Admin123!", "role": "admin",  "verified": True},
        {"name": "John Doe",    "email": "john@example.com",   "password": "User1234!", "role": "user",   "verified": True},
        {"name": "Jane Smith",  "email": "jane@example.com",   "password": "User1234!", "role": "user",   "verified": True},
        {"name": "Bob Wilson",  "email": "bob@example.com",    "password": "User1234!", "role": "user",   "verified": False},
    ]

    for u in users:
        user = MongoUser(
            name=u["name"],
            email=u["email"],
            role=u["role"],
            is_email_verified=u["verified"],
        )
        user.set_password(u["password"])
        user.save()
        click.echo(f"  + {u['role']:5}  {u['email']}")


# ── create-admin ──────────────────────────────────────────────────────────────

@click.command("create-admin")
@with_appcontext
def create_admin():
    """Interactively create an admin user."""
    click.echo("Create Admin User")
    click.echo("-" * 30)

    name  = click.prompt("Name")
    email = click.prompt("Email")
    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)

    mongo = current_app.config.get("MONGO_ENABLED")

    if not mongo:
        from app.extensions import db
        from app.models.sql import User
        if User.query.filter_by(email=email.lower()).first():
            click.secho(f"User {email} already exists.", fg="red")
            return
        user = User(name=name, email=email.lower(), role="admin", is_email_verified=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
    else:
        from app.models.mongo import MongoUser
        if MongoUser.objects(email=email.lower()).first():
            click.secho(f"User {email} already exists.", fg="red")
            return
        user = MongoUser(name=name, email=email.lower(), role="admin", is_email_verified=True)
        user.set_password(password)
        user.save()

    click.secho(f"Admin user '{email}' created.", fg="green")


# ── drop-db ───────────────────────────────────────────────────────────────────

@click.command("drop-db")
@with_appcontext
def drop_db():
    """Drop all SQL tables. Irreversible — requires confirmation."""
    if current_app.config.get("MONGO_ENABLED"):
        click.secho("MongoDB mode — use the mongo shell to drop collections.", fg="yellow")
        return

    click.secho("WARNING: This will drop ALL tables and data.", fg="red", bold=True)
    confirm = click.prompt("Type 'yes' to confirm")
    if confirm != "yes":
        click.echo("Aborted.")
        return

    from app.extensions import db
    db.drop_all()
    click.secho("All tables dropped.", fg="green")


# ── db-reset ─────────────────────────────────────────────────────────────────

@click.command("db-reset")
@with_appcontext
def db_reset():
    """Nuclear reset: wipe DB + alembic state, run fresh migration, seed.

    Fixes broken migration states (partial upgrades, wrong column types, etc).
    Safe to run any number of times. All existing data will be lost.
    """
    if current_app.config.get("MONGO_ENABLED"):
        click.secho("MongoDB mode — drop collections manually via mongo shell.", fg="yellow")
        return

    click.secho("\n  WARNING: This will drop ALL tables, reset migration state and reseed.", fg="red", bold=True)
    confirm = click.prompt("  Type 'reset' to confirm")
    if confirm != "reset":
        click.echo("  Aborted.")
        return

    from app.extensions import db
    from sqlalchemy import text, inspect

    click.echo("\n  [1/4] Dropping all tables...")
    # Drop with FK checks disabled so order doesn't matter
    with db.engine.connect() as conn:
        dialect = db.engine.dialect.name
        if dialect == "mysql":
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        inspector = inspect(db.engine)
        for tbl in inspector.get_table_names():
            conn.execute(text(f"DROP TABLE IF EXISTS `{tbl}`") if dialect == "mysql"
                         else text(f'DROP TABLE IF EXISTS "{tbl}" CASCADE'))
        if dialect == "mysql":
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()
    click.secho("  ✓ Tables dropped", fg="green")

    click.echo("\n  [2/4] Resetting Alembic version...")
    with db.engine.connect() as conn:
        # alembic_version was just dropped above — nothing to do
        conn.commit()
    click.secho("  ✓ Migration state cleared", fg="green")

    click.echo("\n  [3/4] Running migrations...")
    from flask_migrate import upgrade as _upgrade
    _upgrade()
    click.secho("  ✓ Migrations applied", fg="green")

    click.echo("\n  [4/4] Seeding database...")
    _seed_sql()
    click.secho("  ✓ Seed complete", fg="green")

    click.secho("\n  Database reset successfully.\n", fg="green", bold=True)


# ── db-status ─────────────────────────────────────────────────────────────────

@click.command("db-status")
@with_appcontext
def db_status():
    """Show active database engine and connection info."""
    mongo = current_app.config.get("MONGO_ENABLED")
    env   = current_app.config.get("FLASK_ENV", "development")

    click.echo(f"\n  Environment : {env}")

    if mongo:
        uri = current_app.config.get("MONGODB_URI", "")
        safe_uri = uri.split("@")[-1] if "@" in uri else uri
        click.secho(f"  Engine      : MongoDB", fg="green")
        click.echo(f"  URI         : {safe_uri}")
    else:
        uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
        engine = uri.split("://")[0] if "://" in uri else "unknown"
        safe_uri = uri.split("@")[-1] if "@" in uri else uri
        click.secho(f"  Engine      : SQL ({engine})", fg="cyan")
        click.echo(f"  URI         : {safe_uri}")

    click.echo()


# ── routes ────────────────────────────────────────────────────────────────────

@click.command("routes")
@with_appcontext
def routes():
    """Print all registered routes."""
    from flask import current_app as _app
    rules = sorted(_app.url_map.iter_rules(), key=lambda r: r.rule)
    click.echo(f"\n  {'Method':<10} {'Endpoint':<40} {'URL'}")
    click.echo("  " + "-" * 75)
    for rule in rules:
        methods = ",".join(sorted(m for m in rule.methods if m not in ("HEAD", "OPTIONS")))
        click.echo(f"  {methods:<10} {rule.endpoint:<40} {rule.rule}")
    click.echo()

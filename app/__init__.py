import logging
from flask import Flask

from app.config import get_config
from app.extensions import db, jwt, mail, limiter, cors, ma, migrate, cache
from app.middlewares.error_handler import register_error_handlers
from app.middlewares.rate_limiter import init_rate_limiter
from app.middlewares.security import init_security_headers
from app.routes.v1 import v1_bp
from app.docs import docs_bp
from app.cli import register_commands


def create_app(config_class=None) -> Flask:
    app = Flask(__name__)

    cfg = config_class or get_config()
    app.config.from_object(cfg)

    logging.basicConfig(
        level=logging.DEBUG if app.config.get("DEBUG") else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # Extensions
    jwt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})
    ma.init_app(app)
    cache.init_app(app)

    if app.config.get("MONGO_ENABLED"):
        import mongoengine
        mongoengine.connect(host=app.config["MONGODB_URI"])
    else:
        db.init_app(app)
        migrate.init_app(app, db)

    # JWT callbacks
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload.get("jti")
        if not jti:
            return False
        if app.config.get("MONGO_ENABLED"):
            from app.models.mongo import MongoToken
            return MongoToken.objects(token=jti, blacklisted=True).count() > 0
        from app.models.sql import Token
        return Token.query.filter_by(token=jti, blacklisted=True).first() is not None

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        from flask import jsonify
        return jsonify({"success": False, "message": "Token has been revoked"}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        from flask import jsonify
        return jsonify({"success": False, "message": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        from flask import jsonify
        return jsonify({"success": False, "message": "Invalid token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        from flask import jsonify
        return jsonify({"success": False, "message": "Authorization token is missing"}), 401

    # Security headers + rate limiter
    init_security_headers(app)
    init_rate_limiter(app)
    register_error_handlers(app)

    # CLI + shell context
    register_commands(app)

    @app.shell_context_processor
    def make_shell_context():
        from app.services import user_service, token_service, auth_service
        ctx = {"db": db, "user_service": user_service,
               "token_service": token_service, "auth_service": auth_service}
        if app.config.get("MONGO_ENABLED"):
            from app.models.mongo import MongoUser, MongoToken
            ctx.update({"User": MongoUser, "Token": MongoToken})
        else:
            from app.models.sql import User, Token
            ctx.update({"User": User, "Token": Token})
        return ctx

    # Blueprints
    app.register_blueprint(v1_bp)
    app.register_blueprint(docs_bp)

    @app.get("/health")
    def health():
        from flask import jsonify
        return jsonify({"status": "ok", "message": "Server is running"}), 200

    return app

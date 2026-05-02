import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Required environment variable '{key}' is missing.")
    return value


class BaseConfig:
    # Core
    SECRET_KEY = os.getenv("SECRET_KEY", "changeme-in-production")
    DEBUG = False
    TESTING = False

    # Database — SQL (PostgreSQL default, swap for MySQL/SQLite)
    DB_ENGINE = os.getenv("DB_ENGINE", "postgresql")  # postgresql | mysql | sqlite
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"{os.getenv('DB_ENGINE', 'postgresql')}://"
        f"{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres')}"
        f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}"
        f"/{os.getenv('DB_NAME', 'flask_db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Database — MongoDB
    MONGO_ENABLED = os.getenv("MONGO_ENABLED", "false").lower() == "true"
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/flask_db")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "changeme-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_EXPIRATION_MINUTES", 30))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv("JWT_REFRESH_EXPIRATION_DAYS", 30))
    )
    JWT_RESET_PASSWORD_EXPIRATION_MINUTES = int(
        os.getenv("JWT_RESET_PASSWORD_EXPIRATION_MINUTES", 10)
    )
    JWT_VERIFY_EMAIL_EXPIRATION_MINUTES = int(
        os.getenv("JWT_VERIFY_EMAIL_EXPIRATION_MINUTES", 10)
    )
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # Firebase
    FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "")
    FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY", "")

    # OAuth — Google
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

    # OAuth — GitHub
    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")

    # OAuth — Facebook
    FACEBOOK_CLIENT_ID = os.getenv("FACEBOOK_CLIENT_ID", "")
    FACEBOOK_CLIENT_SECRET = os.getenv("FACEBOOK_CLIENT_SECRET", "")

    # Email (SMTP)
    MAIL_SERVER = os.getenv("SMTP_HOST", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("SMTP_PORT", 587))
    MAIL_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL = os.getenv("SMTP_USE_SSL", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("SMTP_USERNAME", "")
    MAIL_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("EMAIL_FROM", "noreply@example.com")

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    # Rate limiting (DDoS / brute-force protection)
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200 per day;50 per hour")
    RATELIMIT_AUTH = os.getenv("RATELIMIT_AUTH", "20 per minute")
    RATELIMIT_STORAGE_URL = os.getenv("RATELIMIT_STORAGE_URL", "memory://")

    # Caching
    CACHE_TYPE = os.getenv("CACHE_TYPE", "SimpleCache")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))
    CACHE_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # App URL (used in emails)
    APP_URL = os.getenv("APP_URL", "http://localhost:5000")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Pagination
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")
    MONGODB_URI = os.getenv("TEST_MONGODB_URI", "mongodb://localhost:27017/flask_test")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1)
    RATELIMIT_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    # In production, storage should be redis for distributed rate limiting
    RATELIMIT_STORAGE_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


_config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config():
    env = os.getenv("FLASK_ENV", "development")
    return _config_map.get(env, DevelopmentConfig)

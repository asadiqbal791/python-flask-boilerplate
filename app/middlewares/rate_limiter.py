"""Rate limiting / DDoS protection configuration.

Uses flask-limiter. Limits are applied at:
 - Global default (all routes)
 - Auth endpoints (stricter)
 - Specific sensitive endpoints
"""
from http import HTTPStatus
from flask import jsonify
from app.extensions import limiter

# Reusable limit decorators — apply to route functions
auth_limit = limiter.limit("20 per minute")
strict_limit = limiter.limit("5 per minute")
api_limit = limiter.limit("200 per hour")


def init_rate_limiter(app):
    """Attach custom error response for rate-limit exceeded."""
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            "success": False,
            "message": "Too many requests. Please try again later.",
            "statusCode": HTTPStatus.TOO_MANY_REQUESTS,
            "retryAfter": str(e.description),
        }), HTTPStatus.TOO_MANY_REQUESTS

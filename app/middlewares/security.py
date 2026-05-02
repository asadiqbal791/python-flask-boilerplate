"""Security headers middleware (equivalent of Helmet.js).

Adds CSP, HSTS, X-Frame-Options, X-Content-Type, Referrer-Policy etc.
"""
from flask import Flask, request


def init_security_headers(app: Flask):
    @app.after_request
    def set_security_headers(response):
        # Docs pages need CDN access — skip strict CSP for /docs/*
        is_docs = request.path.startswith("/docs")

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        if is_docs:
            # Allow CDN scripts/styles for Swagger UI and ReDoc
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' https://unpkg.com https://cdn.redoc.ly 'unsafe-inline'; "
                "style-src 'self' https://unpkg.com 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://fonts.gstatic.com; "
                "worker-src blob:;"
            )
        else:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "frame-ancestors 'none';"
            )

        if not app.debug:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        response.headers.pop("Server", None)
        response.headers.pop("X-Powered-By", None)
        return response

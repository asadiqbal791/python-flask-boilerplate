"""OpenAPI 3.0 spec + Swagger UI / ReDoc routes.

Serves:
  GET /docs/          → Swagger UI  (interactive)
  GET /docs/redoc     → ReDoc UI    (clean read-only)
  GET /docs/openapi.json → raw OpenAPI 3.0 JSON spec
"""
import json
from flask import Blueprint, jsonify, render_template_string

docs_bp = Blueprint("docs", __name__)

# ── OpenAPI 3.0 spec ──────────────────────────────────────────────────────────

def build_openapi_spec(app):
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Python Flask Boilerplate API",
            "description": (
                "Production-ready Flask REST API boilerplate.\n\n"
                "**Auth flows:** Custom JWT · Firebase · Google · GitHub · Facebook OAuth\n\n"
                "**Databases:** PostgreSQL · MySQL · SQLite · MongoDB\n\n"
                "**Security:** Rate limiting · RBAC · JWT blacklisting · Security headers"
            ),
            "version": "1.0.0",
            "contact": {"email": "admin@example.com"},
            "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
        },
        "servers": [
            {"url": "http://localhost:5000", "description": "Development"},
            {"url": "https://api.github.com/asadiqbal791/python-flask-boilerplate", "description": "Production"},
        ],
        "security": [{"bearerAuth": []}],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            },
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id":              {"type": "string", "example": "550e8400-e29b-41d4-a716-446655440000"},
                        "name":            {"type": "string", "example": "John Doe"},
                        "email":           {"type": "string", "format": "email", "example": "john@example.com"},
                        "role":            {"type": "string", "enum": ["user", "admin"]},
                        "isEmailVerified": {"type": "boolean"},
                        "isActive":        {"type": "boolean"},
                        "avatar":          {"type": "string", "nullable": True},
                        "createdAt":       {"type": "string", "format": "date-time"},
                        "updatedAt":       {"type": "string", "format": "date-time"},
                    },
                },
                "AuthTokens": {
                    "type": "object",
                    "properties": {
                        "access":  {"$ref": "#/components/schemas/TokenPair"},
                        "refresh": {"$ref": "#/components/schemas/TokenPair"},
                    },
                },
                "TokenPair": {
                    "type": "object",
                    "properties": {
                        "token":   {"type": "string"},
                        "expires": {"type": "string", "format": "date-time"},
                    },
                },
                "SuccessResponse": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean", "example": True},
                        "message": {"type": "string", "example": "Success"},
                        "data":    {"type": "object"},
                    },
                },
                "ErrorResponse": {
                    "type": "object",
                    "properties": {
                        "success":    {"type": "boolean", "example": False},
                        "message":    {"type": "string", "example": "Unauthorized"},
                        "statusCode": {"type": "integer", "example": 401},
                    },
                },
            },
            "responses": {
                "Unauthorized": {
                    "description": "Missing or invalid token",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}},
                },
                "Forbidden": {
                    "description": "Insufficient permissions",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}},
                },
                "NotFound": {
                    "description": "Resource not found",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}},
                },
                "ValidationError": {
                    "description": "Request validation failed",
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}},
                },
            },
        },
        "paths": {
            # ── Auth ──────────────────────────────────────────────────────────
            "/v1/auth/register": {
                "post": {
                    "tags": ["Auth"],
                    "summary": "Register a new user",
                    "security": [],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {
                        "type": "object", "required": ["name", "email", "password"],
                        "properties": {
                            "name":     {"type": "string", "example": "John Doe"},
                            "email":    {"type": "string", "format": "email", "example": "john@example.com"},
                            "password": {"type": "string", "example": "Secret123!", "minLength": 8},
                        },
                    }}}},
                    "responses": {
                        "201": {"description": "Registered", "content": {"application/json": {"schema": {
                            "allOf": [{"$ref": "#/components/schemas/SuccessResponse"}],
                            "properties": {"data": {"type": "object", "properties": {
                                "user":   {"$ref": "#/components/schemas/User"},
                                "tokens": {"$ref": "#/components/schemas/AuthTokens"},
                            }}},
                        }}}},
                        "400": {"$ref": "#/components/responses/ValidationError"},
                        "409": {"description": "Email already taken"},
                    },
                }
            },
            "/v1/auth/login": {
                "post": {
                    "tags": ["Auth"],
                    "summary": "Login with email and password",
                    "security": [],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {
                        "type": "object", "required": ["email", "password"],
                        "properties": {
                            "email":    {"type": "string", "format": "email", "example": "admin@example.com"},
                            "password": {"type": "string", "example": "Admin123!"},
                        },
                    }}}},
                    "responses": {
                        "200": {"description": "Login successful", "content": {"application/json": {"schema": {
                            "allOf": [{"$ref": "#/components/schemas/SuccessResponse"}],
                            "properties": {"data": {"type": "object", "properties": {
                                "user":   {"$ref": "#/components/schemas/User"},
                                "tokens": {"$ref": "#/components/schemas/AuthTokens"},
                            }}},
                        }}}},
                        "401": {"description": "Incorrect credentials"},
                    },
                }
            },
            "/v1/auth/logout": {
                "post": {
                    "tags": ["Auth"],
                    "summary": "Logout (revoke refresh token)",
                    "security": [],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {
                        "type": "object", "required": ["refreshToken"],
                        "properties": {"refreshToken": {"type": "string"}},
                    }}}},
                    "responses": {
                        "200": {"description": "Logged out"},
                        "401": {"$ref": "#/components/responses/Unauthorized"},
                    },
                }
            },
            "/v1/auth/refresh-tokens": {
                "post": {
                    "tags": ["Auth"],
                    "summary": "Rotate token pair",
                    "security": [],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {
                        "type": "object", "required": ["refreshToken"],
                        "properties": {"refreshToken": {"type": "string"}},
                    }}}},
                    "responses": {
                        "200": {"description": "New token pair"},
                        "401": {"$ref": "#/components/responses/Unauthorized"},
                    },
                }
            },
            "/v1/auth/forgot-password": {
                "post": {
                    "tags": ["Auth"],
                    "summary": "Send password reset email",
                    "security": [],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {
                        "type": "object", "required": ["email"],
                        "properties": {"email": {"type": "string", "format": "email"}},
                    }}}},
                    "responses": {"200": {"description": "Reset email sent (always 200 to prevent enumeration)"}},
                }
            },
            "/v1/auth/reset-password": {
                "post": {
                    "tags": ["Auth"],
                    "summary": "Reset password using token",
                    "security": [],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {
                        "type": "object", "required": ["token", "password"],
                        "properties": {
                            "token":    {"type": "string"},
                            "password": {"type": "string", "minLength": 8},
                        },
                    }}}},
                    "responses": {
                        "200": {"description": "Password reset"},
                        "401": {"$ref": "#/components/responses/Unauthorized"},
                    },
                }
            },
            "/v1/auth/verify-email": {
                "get": {
                    "tags": ["Auth"],
                    "summary": "Verify email address",
                    "security": [],
                    "parameters": [{"name": "token", "in": "query", "required": True, "schema": {"type": "string"}}],
                    "responses": {
                        "200": {"description": "Email verified"},
                        "401": {"$ref": "#/components/responses/Unauthorized"},
                    },
                }
            },
            "/v1/auth/me": {
                "get": {
                    "tags": ["Auth"],
                    "summary": "Get current authenticated user",
                    "responses": {
                        "200": {"description": "Current user", "content": {"application/json": {"schema": {
                            "properties": {"data": {"type": "object", "properties": {
                                "user": {"$ref": "#/components/schemas/User"}
                            }}}
                        }}}},
                        "401": {"$ref": "#/components/responses/Unauthorized"},
                    },
                }
            },
            "/v1/auth/firebase": {
                "post": {
                    "tags": ["Auth — Social"],
                    "summary": "Login via Firebase ID token",
                    "security": [],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {
                        "type": "object", "required": ["idToken"],
                        "properties": {"idToken": {"type": "string"}},
                    }}}},
                    "responses": {"200": {"description": "Login successful"}},
                }
            },
            "/v1/auth/google": {
                "post": {
                    "tags": ["Auth — Social"],
                    "summary": "Login via Google OAuth access token",
                    "security": [],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {
                        "type": "object", "required": ["accessToken"],
                        "properties": {"accessToken": {"type": "string"}},
                    }}}},
                    "responses": {"200": {"description": "Login successful"}},
                }
            },
            "/v1/auth/github": {
                "post": {
                    "tags": ["Auth — Social"],
                    "summary": "Login via GitHub OAuth access token",
                    "security": [],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {
                        "type": "object", "required": ["accessToken"],
                        "properties": {"accessToken": {"type": "string"}},
                    }}}},
                    "responses": {"200": {"description": "Login successful"}},
                }
            },
            "/v1/auth/facebook": {
                "post": {
                    "tags": ["Auth — Social"],
                    "summary": "Login via Facebook OAuth access token",
                    "security": [],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {
                        "type": "object", "required": ["accessToken"],
                        "properties": {"accessToken": {"type": "string"}},
                    }}}},
                    "responses": {"200": {"description": "Login successful"}},
                }
            },
            # ── Users ─────────────────────────────────────────────────────────
            "/v1/users/": {
                "get": {
                    "tags": ["Users"],
                    "summary": "List users (paginated)",
                    "parameters": [
                        {"name": "page",  "in": "query", "schema": {"type": "integer", "default": 1}},
                        {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 10}},
                        {"name": "role",  "in": "query", "schema": {"type": "string", "enum": ["user", "admin"]}},
                        {"name": "name",  "in": "query", "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {"description": "Paginated user list"},
                        "401": {"$ref": "#/components/responses/Unauthorized"},
                        "403": {"$ref": "#/components/responses/Forbidden"},
                    },
                },
                "post": {
                    "tags": ["Users"],
                    "summary": "Create a user (admin)",
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {
                        "type": "object", "required": ["name", "email", "password"],
                        "properties": {
                            "name":     {"type": "string"},
                            "email":    {"type": "string", "format": "email"},
                            "password": {"type": "string", "minLength": 8},
                            "role":     {"type": "string", "enum": ["user", "admin"]},
                        },
                    }}}},
                    "responses": {
                        "201": {"description": "User created"},
                        "409": {"description": "Email already taken"},
                    },
                },
            },
            "/v1/users/{id}": {
                "get": {
                    "tags": ["Users"],
                    "summary": "Get user by ID",
                    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "responses": {
                        "200": {"description": "User found"},
                        "404": {"$ref": "#/components/responses/NotFound"},
                    },
                },
                "patch": {
                    "tags": ["Users"],
                    "summary": "Update user by ID",
                    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {
                        "type": "object",
                        "properties": {
                            "name":  {"type": "string"},
                            "email": {"type": "string", "format": "email"},
                            "role":  {"type": "string", "enum": ["user", "admin"]},
                        },
                    }}}},
                    "responses": {
                        "200": {"description": "User updated"},
                        "404": {"$ref": "#/components/responses/NotFound"},
                    },
                },
                "delete": {
                    "tags": ["Users"],
                    "summary": "Delete user by ID",
                    "parameters": [{"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}],
                    "responses": {
                        "204": {"description": "Deleted"},
                        "404": {"$ref": "#/components/responses/NotFound"},
                    },
                },
            },
            "/v1/users/me": {
                "get": {
                    "tags": ["Users"],
                    "summary": "Get own profile",
                    "responses": {
                        "200": {"description": "Profile"},
                        "401": {"$ref": "#/components/responses/Unauthorized"},
                    },
                },
                "patch": {
                    "tags": ["Users"],
                    "summary": "Update own profile",
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {
                        "type": "object",
                        "properties": {
                            "name":     {"type": "string"},
                            "email":    {"type": "string", "format": "email"},
                            "password": {"type": "string", "minLength": 8},
                        },
                    }}}},
                    "responses": {
                        "200": {"description": "Profile updated"},
                        "401": {"$ref": "#/components/responses/Unauthorized"},
                    },
                },
            },
        },
        "tags": [
            {"name": "Auth",          "description": "JWT authentication endpoints"},
            {"name": "Auth — Social", "description": "Firebase, Google, GitHub, Facebook"},
            {"name": "Users",         "description": "User management (admin + self-service)"},
        ],
    }


# ── routes ────────────────────────────────────────────────────────────────────

@docs_bp.get("/docs/openapi.json")
def openapi_json():
    from flask import current_app
    spec = build_openapi_spec(current_app)
    return jsonify(spec)


@docs_bp.get("/docs/")
@docs_bp.get("/docs")
def swagger_ui():
    html = """<!DOCTYPE html>
<html>
<head>
  <title>Flask Boilerplate API — Swagger UI</title>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
  <style>body{margin:0} .topbar{display:none}</style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({
      url: "/docs/openapi.json",
      dom_id: "#swagger-ui",
      presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
      layout: "BaseLayout",
      deepLinking: true,
      persistAuthorization: true,
    })
  </script>
</body>
</html>"""
    return html


@docs_bp.get("/docs/redoc")
def redoc_ui():
    html = """<!DOCTYPE html>
<html>
<head>
  <title>Flask Boilerplate API — ReDoc</title>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>body{margin:0}</style>
</head>
<body>
  <redoc spec-url="/docs/openapi.json"></redoc>
  <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
</body>
</html>"""
    return html

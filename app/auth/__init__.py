"""
Authentication Module

Exposes authentication and user management blueprints.

Provides two separate blueprints:
- auth_bp: Authentication endpoints (login, register)
- user_bp: User management endpoints (CRUD, roles)

Both blueprints are registered under /auth prefix.
"""
from app.auth.routes.auth_routes import auth_bp
from app.auth.routes.user_routes import user_bp

# Export blueprints for registration in main app
__all__ = [
    'auth_bp',
    'user_bp'
]

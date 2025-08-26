"""
Authentication Module

Exposes the authentication blueprint and route registration.
"""
from flask import Blueprint

# Create auth blueprint
auth_bp = Blueprint('auth', __name__)

# Import routes after blueprint creation to avoid circular imports
from app.auth.routes.auth_routes import register_auth_routes

# Register routes with the blueprint
register_auth_routes(auth_bp)

# Export main components for easy importing
__all__ = [
    'auth_bp',
    'auth_routes'
]

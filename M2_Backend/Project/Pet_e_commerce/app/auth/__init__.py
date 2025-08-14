"""
Authentication Module

This module provides comprehensive user authentication and authorization functionality including:
- User registration and login
- JWT token-based authentication
- Role-based access control (admin/user)
- Password security and validation
- Session management

The module is organized into:
- Models: User data structures and authentication logic
- Services: Authentication operations and security functions
- Schemas: User data validation and serialization  
- Routes: RESTful API endpoints for authentication

Blueprint: auth_bp - handles all authentication-related routes
Features:
- Secure password hashing
- JWT token generation and validation
- Role-based decorators for route protection
- Comprehensive input validation
"""
from flask import Blueprint

# Create auth blueprint
auth_bp = Blueprint('auth', __name__)

# Import routes after blueprint creation to avoid circular imports
from app.auth.routes import auth_routes

# Export main components for easy importing
__all__ = [
    'auth_bp',
    'auth_routes'
]

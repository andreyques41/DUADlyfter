"""
Security Configuration Module
Centralized configuration for JWT and other security settings
"""

import os

# JWT Configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
if JWT_SECRET_KEY is None:
    raise RuntimeError("JWT_SECRET_KEY environment variable must be set for security reasons.")
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

def get_jwt_secret():
    """Get the JWT secret key from environment or default."""
    return JWT_SECRET_KEY

def get_jwt_algorithm():
    """Get the JWT algorithm."""
    return JWT_ALGORITHM

def get_jwt_expiration_hours():
    """Get the JWT token expiration time in hours."""
    return JWT_EXPIRATION_HOURS

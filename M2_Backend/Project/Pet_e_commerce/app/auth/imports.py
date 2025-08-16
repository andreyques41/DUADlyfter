"""
Auth Domain Imports Module

Centralized imports for the authentication domain to reduce import complexity
and provide a single source for all auth-related dependencies.

Usage:
    from app.auth.imports import (
        User, AuthService, SecurityService,
        user_registration_schema, user_login_schema,
        token_required, admin_required,
        generate_jwt_token, verify_jwt_token
    )
"""

# Models
from app.auth.models.user import User

# Services
from app.auth.services.auth_service import AuthService
from app.auth.services.security_service import SecurityService, hash_password, verify_password

# Schemas
from app.auth.schemas.user_schema import (
    user_registration_schema,
    user_login_schema,
    user_response_schema,
    user_update_schema,
    users_response_schema,
    user_password_change_schema
)

# Decorators
from app.auth.services.auth_decorators import (
    token_required,
    admin_required,
    customer_or_admin
)

# JWT utilities
from app.shared.utils.jwt_utils import generate_jwt_token, verify_jwt_token

# User utilities
from app.shared.utils.user_utils import get_user_by_id, get_user_by_username

# Auth utilities
from app.shared.utils.auth_utils import (
    is_admin_user,
    require_admin_access,
    require_user_or_admin_access,
    require_user_id_match
)

# Database paths
from app.shared.json_db import USERS_DB_PATH

# Enums
from app.shared.enums import UserRole

# Export all auth-related items
__all__ = [
    # Models
    'User',
    
    # Services
    'AuthService', 'SecurityService', 'hash_password', 'verify_password',
    
    # Schemas
    'user_registration_schema', 'user_login_schema', 'user_response_schema',
    'user_update_schema', 'users_response_schema',
    'user_password_change_schema',
    
    # Decorators
    'token_required', 'admin_required', 'customer_or_admin',
    
    # JWT utilities
    'generate_jwt_token', 'verify_jwt_token',
    
    # User utilities
    'get_user_by_id', 'get_user_by_username',
    
    # Auth utilities
    'is_admin_user', 'require_admin_access', 'require_user_or_admin_access',
    'require_user_id_match',
    
    # Database
    'USERS_DB_PATH',
    
    # Enums
    'UserRole'
]

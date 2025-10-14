"""
Auth Domain Imports Module (DEPRECATED - Use direct imports instead)

This file is kept for backward compatibility but should be replaced
with direct imports in new code.

Recommended approach:
    from app.auth.models import User
    from app.auth.services import AuthService
    from app.auth.schemas import user_registration_schema
    from app.shared.middleware import token_required
"""

# Models
from app.auth.models import User, Role, RoleUser

# Repositories
from app.auth.repositories import UserRepository

# Services
from app.auth.services import AuthService, SecurityService, hash_password, verify_password

# Schemas
from app.auth.schemas import (
    user_registration_schema,
    user_login_schema,
    user_response_schema,
    user_update_schema,
    users_response_schema,
    user_password_change_schema
)

# Middleware (moved from auth.services)
from app.core.middleware import (
    token_required,
    admin_required,
    customer_or_admin
)

# JWT utilities
from app.core.lib.jwt import generate_jwt_token, verify_jwt_token

# User utilities
from app.core.lib.users import get_user_by_id, get_user_by_username

# Auth utilities
from app.core.lib.auth import (
    is_admin_user,
    require_admin_access,
    require_user_or_admin_access,
    check_user_id_match as require_user_id_match
)

# Enums
from app.core.enums import UserRole

# Export all auth-related items
__all__ = [
    # Models
    'User', 'Role', 'RoleUser',
    
    # Repositories
    'UserRepository',
    
    # Services
    'AuthService', 'SecurityService', 'hash_password', 'verify_password',
    
    # Schemas
    'user_registration_schema', 'user_login_schema', 'user_response_schema',
    'user_update_schema', 'users_response_schema', 'user_password_change_schema',
    
    # Middleware
    'token_required', 'admin_required', 'customer_or_admin',
    
    # JWT utilities
    'generate_jwt_token', 'verify_jwt_token',
    
    # User utilities
    'get_user_by_id', 'get_user_by_username',
    
    # Auth utilities
    'is_admin_user', 'require_admin_access', 'require_user_or_admin_access',
    'require_user_id_match',
    
    # Enums
    'UserRole'
]

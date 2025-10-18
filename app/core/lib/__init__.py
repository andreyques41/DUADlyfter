"""
Core library utilities - Consolidated Auth System

Provides:
- auth: Authorization helper functions (user_has_role, is_admin_user, is_user_or_admin)
- jwt: JWT token generation and verification
- users: User data access functions (for use in decorators)
"""

from app.core.lib.auth import (
    user_has_role,
    is_admin_user,
    is_user_or_admin
)

from app.core.lib.jwt import (
    generate_jwt_token,
    verify_jwt_token
)

from app.core.lib.users import (
    get_user_by_id,
    get_user_by_username
)

__all__ = [
    # Auth utilities
    'user_has_role',
    'is_admin_user',
    'is_user_or_admin',
    # JWT utilities
    'generate_jwt_token',
    'verify_jwt_token',
    # User utilities
    'get_user_by_id',
    'get_user_by_username'
]

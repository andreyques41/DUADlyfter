"""
Core library utilities

Provides:
- auth: Authorization utility functions
- jwt: JWT token generation and verification
- users: User data access functions (for use in decorators)
"""

from app.core.lib.auth import (
    is_admin_user,
    check_admin_access,
    check_user_or_admin_access,
    check_user_id_match,
    require_admin_access,
    require_user_or_admin_access
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
    'is_admin_user',
    'check_admin_access',
    'check_user_or_admin_access',
    'check_user_id_match',
    'require_admin_access',
    'require_user_or_admin_access',
    # JWT utilities
    'generate_jwt_token',
    'verify_jwt_token',
    # User utilities
    'get_user_by_id',
    'get_user_by_username',
]

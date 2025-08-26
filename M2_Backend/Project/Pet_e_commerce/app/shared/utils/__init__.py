"""
Shared utilities package - exports commonly used utility functions.

This module provides convenient access to all shared utilities without
requiring knowledge of internal module structure.

Usage Examples:
    # Import commonly used functions
    from app.shared.utils import (
        save_models_to_json, load_models_from_json,
        generate_jwt_token, verify_jwt_token,
        get_user_by_id, is_admin_user
    )
    
    # Or import specific categories
    from app.shared.utils.auth_utils import require_admin_access
    from app.shared.utils.jwt_utils import generate_jwt_token
"""

# Auth utilities - access control and authorization
from .auth_utils import (
    is_admin_user,
    check_admin_access,
    check_user_or_admin_access,
    check_user_id_match,
    require_admin_access,
    require_user_or_admin_access,
    require_user_id_match
)

# User utilities - database access without circular imports
from .user_utils import (
    get_user_by_id,
    get_user_by_username
)

# JWT utilities - token management
from .jwt_utils import (
    generate_jwt_token,
    verify_jwt_token
)

# JSON handling utilities - low-level file operations
from ..json_db.json_handler import (
    read_json,
    write_json
)

# CRUD utilities - high-level data persistence operations
from .crud_utils import (
    save_models_to_json,
    load_models_from_json,
    load_single_model_by_field,
    generate_next_id
)

# Export all commonly used utilities for easy access
__all__ = [
    # Auth utilities
    'is_admin_user', 'check_admin_access', 'check_user_or_admin_access',
    'check_user_id_match', 'require_admin_access', 'require_user_or_admin_access',
    'require_user_id_match',
    
    # User utilities
    'get_user_by_id', 'get_user_by_username',
    
    # JWT utilities
    'generate_jwt_token', 'verify_jwt_token',
    
    # JSON handling
    'read_json', 'write_json',
    
    # CRUD utilities
    'save_models_to_json', 'load_models_from_json',
    'load_single_model_by_field', 'generate_next_id'
]
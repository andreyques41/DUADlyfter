"""
Shared utilities package - exports commonly used utility functions.
"""

# Auth utilities - most commonly imported
from .auth_utils import (
    is_admin_user,
    require_admin_access,
    require_user_or_admin_access,
    require_user_id_match
)

# JSON handling utilities
from .json_handler import *  # Import whatever functions exist in json_handler

# This allows much cleaner imports:
# from app.shared.utils import is_admin_user, require_admin_access
# Instead of: from app.shared.utils.auth_utils import is_admin_user, require_admin_access
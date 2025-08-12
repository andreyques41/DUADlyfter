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

# CRUD utilities - for data persistence and ID generation
from .crud_utils import (
    save_models_to_json,
    load_models_from_json,
    load_single_model_from_json,
    generate_next_id
)

# This allows much cleaner imports:
# from app.shared.utils import is_admin_user, require_admin_access, save_models_to_json
# Instead of: from app.shared.utils.auth_utils import is_admin_user, require_admin_access
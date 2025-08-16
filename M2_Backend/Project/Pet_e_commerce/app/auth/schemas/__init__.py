"""
Auth schemas package - exports user-related schemas.
"""

from .user_schema import (
    user_registration_schema,
    user_login_schema,
    user_update_schema,
    user_response_schema,
    users_response_schema,
    user_password_change_schema
)

# This allows cleaner imports like:
# from app.auth.schemas import user_registration_schema
# Instead of: from app.auth.schemas.user_schema import user_registration_schema
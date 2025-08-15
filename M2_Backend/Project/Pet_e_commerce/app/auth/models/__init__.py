"""
Auth models package - exports commonly used models and enums.
"""

from .user import User
from app.shared.enums import UserRole

# This allows: from app.auth.models import User, UserRole
# Instead of: from app.auth.models.user import User, UserRole
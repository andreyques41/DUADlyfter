"""
Core Middleware Module

Authentication and authorization decorators for Flask routes.
Compatible with multi-role system.

MAIN DECORATORS:
- token_required_with_repo: Validates token, loads user from DB
- admin_required_with_repo: Validates token + requires admin role (all-in-one)
"""
from app.core.middleware.auth_decorators import (
    token_required_with_repo,
    admin_required_with_repo
)

__all__ = [
    'token_required_with_repo',
    'admin_required_with_repo'
]

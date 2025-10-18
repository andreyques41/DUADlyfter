"""
Authorization utility functions for consistent access control across modules.
Compatible with multi-role system (users can have multiple roles).

This module provides HELPER FUNCTIONS for authorization checks.
For decorators, use app.core.middleware.
"""
import logging
from flask import g

logger = logging.getLogger(__name__)

def user_has_role(user, role_name: str) -> bool:
    """
    Check if a user has a specific role.
    Supports multiple roles per user.
    
    Args:
        user: User object with user_roles relationship
        role_name: Role name to check (e.g., 'admin', 'user')
        
    Returns:
        bool: True if user has the role, False otherwise
        
    Example:
        if user_has_role(current_user, 'admin'):
            # Grant admin access
    """
    if not user or not hasattr(user, 'user_roles') or not user.user_roles:
        return False
    
    user_roles = [ur.role.name for ur in user.user_roles]
    return role_name in user_roles


def is_admin_user() -> bool:
    """
    Check if current authenticated user (in g.current_user) is an admin.
    Safe to call even when no user is authenticated.
    Supports users with multiple roles.
    
    Returns:
        bool: True if user is admin, False otherwise (including when no user is logged in)
        
    Example:
        # In a route with optional authentication
        if is_admin_user():
            # Show admin-only data
    """
    return hasattr(g, 'current_user') and g.current_user and user_has_role(g.current_user, 'admin')


def is_user_or_admin(user_id: int) -> bool:
    """
    Check if current user can access a specific user's data.
    Users can access their own data, admins can access any user's data.
    
    Args:
        user_id: ID of the user being accessed
        
    Returns:
        bool: True if access is allowed, False otherwise
        
    Example:
        # In a route that requires token
        if not is_user_or_admin(requested_user_id):
            return jsonify({"error": "Access denied"}), 403
    """
    if not hasattr(g, 'current_user') or not g.current_user:
        return False
    
    return user_has_role(g.current_user, 'admin') or g.current_user.id == user_id

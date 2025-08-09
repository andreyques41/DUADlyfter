"""
Authorization utility functions for consistent access control across modules.
"""
from flask import jsonify, g
from app.auth.models.user import UserRole


def is_admin_user():
    """
    Check if current user is an admin.
    Safe to call even when no user is authenticated.
    
    Returns:
        bool: True if user is admin, False otherwise (including when no user is logged in)
    """
    return hasattr(g, 'current_user') and g.current_user and g.current_user.role == UserRole.ADMIN


def check_admin_access():
    """
    Check if current user has admin privileges.
    
    Returns:
        tuple: (success: bool, response: dict or None, status_code: int or None)
            If success is False, response and status_code contain error details.
    """
    if g.current_user.role != UserRole.ADMIN:
        return False, {"error": "Admin access required"}, 403
    return True, None, None


def check_user_or_admin_access(user_id):
    """
    Check if current user can access a specific user's data.
    Users can only access their own data, admins can access any user's data.
    
    Args:
        user_id (int): ID of the user being accessed
        
    Returns:
        tuple: (success: bool, response: dict or None, status_code: int or None)
            If success is False, response and status_code contain error details.
    """
    if g.current_user.role != UserRole.ADMIN and g.current_user.id != user_id:
        return False, {"error": "Access denied"}, 403
    return True, None, None


def check_user_id_match(user_id):
    """
    Check if current user ID matches the provided user ID.
    Strict check - only the exact user can perform this action.
    
    Args:
        user_id (int): ID of the user being accessed
        
    Returns:
        tuple: (success: bool, response: dict or None, status_code: int or None)
            If success is False, response and status_code contain error details.
    """
    if g.current_user.id != user_id:
        return False, {"error": "Access denied - user ID mismatch"}, 403
    return True, None, None


def require_admin_access():
    """
    Decorator-like function that returns a JSON response if admin access is denied.
    Use this for immediate response generation.
    
    Returns:
        Flask response or None: Returns error response if access denied, None if allowed
    """
    success, error_response, status_code = check_admin_access()
    if not success:
        return jsonify(error_response), status_code
    return None


def require_user_or_admin_access(user_id):
    """
    Decorator-like function that returns a JSON response if user/admin access is denied.
    Use this for immediate response generation.
    
    Args:
        user_id (int): ID of the user being accessed
        
    Returns:
        Flask response or None: Returns error response if access denied, None if allowed
    """
    success, error_response, status_code = check_user_or_admin_access(user_id)
    if not success:
        return jsonify(error_response), status_code
    return None


def require_user_id_match(user_id):
    """
    Decorator-like function that returns a JSON response if user ID doesn't match.
    Use this for immediate response generation.
    
    Args:
        user_id (int): ID of the user being accessed
        
    Returns:
        Flask response or None: Returns error response if access denied, None if allowed
    """
    success, error_response, status_code = check_user_id_match(user_id)
    if not success:
        return jsonify(error_response), status_code
    return None

"""
Authentication Decorators Module

Provides Flask route decorators for authentication and authorization:
- @token_required: Validates JWT tokens and sets g.current_user
- @admin_required: Restricts access to admin users only
- @customer_or_admin: Allows both customer and admin access

Usage:
    from app.shared.middleware import token_required, admin_required
    
    @token_required
    @admin_required  
    def admin_only_route():
        return jsonify({"user": g.current_user.username})

Dependencies:
- user_utils for user retrieval
- jwt_utils for token verification
- Flask g object for user session storage
"""

from functools import wraps
from flask import request, jsonify, g
from app.core.lib.users import get_user_by_id
from app.core.lib.jwt import verify_jwt_token
from app.core.enums import UserRole
from config.logging import get_logger, EXC_INFO_LOG_ERRORS

# Module-level logger
logger = get_logger(__name__)

def token_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # "Bearer <token>" → "<token>"
                logger.debug("Extracted token from Authorization header.")
            except Exception as e:
                logger.warning(f"Invalid token format in Authorization header: {auth_header}")
                return jsonify({'error': 'Invalid token format'}), 401
        else:
            logger.warning("Authorization header missing in request.")
            return jsonify({'error': 'Authorization header missing'}), 401
        
        try:
            # Decode JWT token
            logger.debug("Verifying JWT token.")
            data = verify_jwt_token(token)
            
            if not data:
                logger.warning("Invalid or expired JWT token.")
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Get user from database using user_id
            logger.debug(f"Looking up user with id {data.get('user_id')} from token.")
            current_user = get_user_by_id(data['user_id'])
            
            if not current_user:
                logger.warning(f"User not found for id {data.get('user_id')} from token.")
                return jsonify({'error': 'User not found'}), 401
            
            # Store user in Flask's g object for access in the actual route function
            g.current_user = current_user
            logger.info(f"Authenticated user {getattr(current_user, 'username', None)} (id={getattr(current_user, 'id', None)}) via JWT.")
        except Exception as e:
            logger.error(f"Token validation failed: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({'error': 'Token validation failed'}), 401
        
        return function(*args, **kwargs)
    
    return decorated

def admin_required(function):
    """Decorator to require admin role (must be used with @token_required)"""
    @wraps(function)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'current_user'):
            logger.warning("Admin access denied: No authenticated user in context.")
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get user's role name from the role relationship
        if not hasattr(g.current_user, 'user_roles') or not g.current_user.user_roles:
            logger.warning(f"Admin access denied: User {getattr(g.current_user, 'username', None)} has no roles assigned.")
            return jsonify({'error': 'Admin access required'}), 403
        
        user_role_name = g.current_user.user_roles[0].role.name
        
        if user_role_name != UserRole.ADMIN.value:
            logger.warning(f"Admin access denied for user {getattr(g.current_user, 'username', None)} (id={getattr(g.current_user, 'id', None)}), role={user_role_name}.")
            return jsonify({'error': 'Admin access required'}), 403
        
        logger.info(f"Admin access granted for user {getattr(g.current_user, 'username', None)} (id={getattr(g.current_user, 'id', None)}).")
        return function(*args, **kwargs)
    
    return decorated

def customer_or_admin(function):
    """Decorator that allows both customers and admins (must be used with @token_required)"""
    @wraps(function)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'current_user'):
            logger.warning("Access denied: No authenticated user in context.")
            return jsonify({'error': 'Authentication required'}), 401
        logger.info(f"Access granted for user {getattr(g.current_user, 'username', None)} (id={getattr(g.current_user, 'id', None)}), role={getattr(g.current_user, 'role', None)}.")
        return function(*args, **kwargs)
    
    return decorated

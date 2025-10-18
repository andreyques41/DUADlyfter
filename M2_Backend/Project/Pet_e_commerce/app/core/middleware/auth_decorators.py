"""
Authentication Decorators Module

Provides Flask route decorators for authentication and authorization:
- @token_required: Validates JWT tokens and sets g.current_user
- @admin_required: Restricts access to admin users only
- @customer_or_admin: Allows both customer and admin access
- @token_required_with_repo: Validates token and verifies role in DB
- @admin_required_with_repo: Validates token and verifies admin in DB

Usage:
    from app.core.middleware import token_required, admin_required
    
    @token_required
    @admin_required  
    def admin_only_route():
        return jsonify({"user": g.current_user.username})
    
    # With repo verification (for critical operations)
    @token_required_with_repo
    def critical_route():
        user_id = g.current_user.id
        is_admin = g.is_admin  # Verified in DB

Dependencies:
- user_utils for user retrieval
- jwt_utils for token verification
- Flask g object for user session storage

Migration Note:
- Removed UserRole enum dependency (now uses string comparison with "admin")
- Compatible with normalized roles table
"""

from functools import wraps
from flask import request, jsonify, g
from app.core.lib.users import get_user_by_id
from app.core.lib.jwt import verify_jwt_token
from config.logging import get_logger, EXC_INFO_LOG_ERRORS

# Module-level logger
logger = get_logger(__name__)

def _user_has_role(user, role_name: str) -> bool:
    """
    Helper function to check if a user has a specific role.
    Supports multiple roles per user.
    
    Args:
        user: User object with user_roles relationship
        role_name: Role name to check (e.g., 'admin', 'user')
        
    Returns:
        bool: True if user has the role, False otherwise
    """
    if not hasattr(user, 'user_roles') or not user.user_roles:
        return False
    
    user_roles = [ur.role.name for ur in user.user_roles]
    return role_name in user_roles

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
    """
    Decorator to require admin role (must be used with @token_required).
    Supports users with multiple roles - checks if 'admin' is among them.
    """
    @wraps(function)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'current_user'):
            logger.warning("Admin access denied: No authenticated user in context.")
            return jsonify({'error': 'Admin access required'}), 403
        
        # Check if user has admin role
        if not _user_has_role(g.current_user, 'admin'):
            user_roles = []
            if hasattr(g.current_user, 'user_roles') and g.current_user.user_roles:
                user_roles = [ur.role.name for ur in g.current_user.user_roles]
            
            logger.warning(
                f"Admin access denied for user {getattr(g.current_user, 'username', None)} "
                f"(id={getattr(g.current_user, 'id', None)}), roles={user_roles}."
            )
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


def token_required_with_repo(function):
    """
    Decorator that validates JWT token AND verifies user role in database.
    Sets g.current_user and g.is_admin (verified in DB).
    
    Use this decorator when:
    - Role verification is critical
    - User roles can change frequently
    - You need up-to-date role information from DB
    
    Usage:
        @token_required_with_repo
        def get_data():
            user_id = g.current_user.id
            is_admin = g.is_admin  # Verified in DB
    """
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
            
            # Get user from database using user_id (FRESH DATA FROM DB)
            logger.debug(f"Looking up user with id {data.get('user_id')} from token.")
            current_user = get_user_by_id(data['user_id'])
            
            if not current_user:
                logger.warning(f"User not found for id {data.get('user_id')} from token.")
                return jsonify({'error': 'User not found'}), 401
            
            # Verify role from database (not from token)
            is_admin = False
            if hasattr(current_user, 'user_roles') and current_user.user_roles:
                user_role_name = current_user.user_roles[0].role.name
                is_admin = (user_role_name == "admin")
                logger.debug(f"User role verified from DB: {user_role_name}, is_admin={is_admin}")
            
            # Store user and admin status in Flask's g object
            g.current_user = current_user
            g.is_admin = is_admin
            
            logger.info(f"Authenticated user {current_user.username} (id={current_user.id}) via JWT with DB verification.")
        except Exception as e:
            logger.error(f"Token validation failed: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({'error': 'Token validation failed'}), 401
        
        return function(*args, **kwargs)
    
    return decorated


def admin_required_with_repo(function):
    """
    Decorator that validates JWT token AND verifies admin role in database.
    Automatically includes token validation and DB role verification.
    
    Use this decorator for admin-only endpoints when:
    - Admin status might change
    - Security is critical
    - You want fresh data from DB
    
    Usage:
        @admin_required_with_repo
        def delete_user():
            # Only verified admins can reach here
            pass
    """
    @wraps(function)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
                logger.debug("Extracted token from Authorization header.")
            except Exception:
                logger.warning(f"Invalid token format in Authorization header.")
                return jsonify({'error': 'Invalid token format'}), 401
        else:
            logger.warning("Authorization header missing in request.")
            return jsonify({'error': 'Authorization header missing'}), 401
        
        try:
            # Decode JWT token
            data = verify_jwt_token(token)
            
            if not data:
                logger.warning("Invalid or expired JWT token.")
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Get user from database
            current_user = get_user_by_id(data['user_id'])
            
            if not current_user:
                logger.warning(f"User not found for id {data.get('user_id')}.")
                return jsonify({'error': 'User not found'}), 401
            
            # Verify admin role from database
            if not hasattr(current_user, 'user_roles') or not current_user.user_roles:
                logger.warning(f"Admin access denied: User {current_user.username} has no roles assigned.")
                return jsonify({'error': 'Admin access required'}), 403
            
            user_role_name = current_user.user_roles[0].role.name
            
            if user_role_name != "admin":
                logger.warning(f"Admin access denied for user {current_user.username} (role={user_role_name}).")
                return jsonify({'error': 'Admin access required'}), 403
            
            # Store user and admin status
            g.current_user = current_user
            g.is_admin = True
            
            logger.info(f"Admin access granted for user {current_user.username} (id={current_user.id}).")
        except Exception as e:
            logger.error(f"Token validation failed: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({'error': 'Token validation failed'}), 401
        
        return function(*args, **kwargs)
    
    return decorated


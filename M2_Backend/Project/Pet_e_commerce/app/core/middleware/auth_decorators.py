"""
Authentication Decorators Module

Provides Flask route decorators for authentication and authorization.
Compatible with multi-role system (users can have multiple roles).

DECORATORS PROVIDED:
1. @token_required_with_repo - Validates token, loads user from DB, sets g.current_user
2. @admin_required_with_repo - Validates token + requires admin role (all-in-one)

USAGE PATTERNS:
    # Pattern 1: User or Admin access (users can access their own data)
    @token_required_with_repo
    def get_user_cart(user_id):
        if not is_user_or_admin(user_id):
            return jsonify({"error": "Access denied"}), 403
        # ... proceed
    
    # Pattern 2: Admin-only access (strict)
    @admin_required_with_repo
    def delete_user(user_id):
        # Only admins reach here
        # ... proceed
    
    # Pattern 3: Optional authentication (e.g., public products with admin extras)
    def get_products():
        # Call _try_authenticate() manually
        # Then check: if is_admin_user(): show_admin_data
        
Dependencies:
- app.core.lib.users for user retrieval
- app.core.lib.jwt for token verification
- app.core.lib.auth for role checking (user_has_role)
- Flask g object for user session storage
"""

from functools import wraps
from flask import request, jsonify, g
from app.core.lib.users import get_user_by_id
from app.core.lib.jwt import verify_jwt_token
from app.core.lib.auth import user_has_role
from config.logging import get_logger, EXC_INFO_LOG_ERRORS

# Module-level logger
logger = get_logger(__name__)


def token_required_with_repo(function):
    """
    Decorator that validates JWT token AND loads fresh user data from database.
    Sets g.current_user with up-to-date information including roles.
    
    Use this decorator when:
    - You need authentication
    - You want fresh user data from DB (not cached in token)
    - You need to check user roles or permissions
    
    After decoration, you can:
    - Access g.current_user (User object with user_roles loaded)
    - Use is_admin_user() to check admin status
    - Use is_user_or_admin(user_id) to check ownership
    
    Example:
        @token_required_with_repo
        def get_cart(user_id):
            if not is_user_or_admin(user_id):
                return jsonify({"error": "Access denied"}), 403
            # ... proceed
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
            except Exception:
                logger.warning(f"Invalid token format in Authorization header.")
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
            
            # Get FRESH user from database (includes roles)
            logger.debug(f"Looking up user with id {data.get('user_id')} from token.")
            current_user = get_user_by_id(data['user_id'])
            
            if not current_user:
                logger.warning(f"User not found for id {data.get('user_id')} from token.")
                return jsonify({'error': 'User not found'}), 401
            
            # Store user in Flask's g object
            g.current_user = current_user
            
            logger.info(
                f"Authenticated user {current_user.username} (id={current_user.id}) via JWT. "
                f"Roles: {[ur.role.name for ur in current_user.user_roles] if current_user.user_roles else []}"
            )
        except Exception as e:
            logger.error(f"Token validation failed: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({'error': 'Token validation failed'}), 401
        
        return function(*args, **kwargs)
    
    return decorated


def admin_required_with_repo(function):
    """
    Decorator that validates JWT token AND requires admin role (all-in-one).
    Combines authentication + authorization in a single decorator.
    
    Use this decorator for admin-only endpoints:
    - Validates JWT token
    - Loads fresh user from DB
    - Verifies user has 'admin' role (supports multi-role)
    - Sets g.current_user if successful
    
    Example:
        @admin_required_with_repo
        def delete_user(user_id):
            # Only admins reach here
            # g.current_user is set
            # ... proceed with admin operation
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
            
            # Get FRESH user from database
            current_user = get_user_by_id(data['user_id'])
            
            if not current_user:
                logger.warning(f"User not found for id {data.get('user_id')}.")
                return jsonify({'error': 'User not found'}), 401
            
            # Verify admin role from database (supports multi-role system)
            if not user_has_role(current_user, 'admin'):
                user_roles = [ur.role.name for ur in current_user.user_roles] if current_user.user_roles else []
                logger.warning(
                    f"Admin access denied for user {current_user.username} "
                    f"(id={current_user.id}, roles={user_roles})."
                )
                return jsonify({'error': 'Admin access required'}), 403
            
            # Store user in g object
            g.current_user = current_user
            
            logger.info(f"Admin access granted for user {current_user.username} (id={current_user.id}).")
        except Exception as e:
            logger.error(f"Token validation failed: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({'error': 'Token validation failed'}), 401
        
        return function(*args, **kwargs)
    
    return decorated

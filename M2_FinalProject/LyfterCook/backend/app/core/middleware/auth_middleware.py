"""
Authentication Middleware
JWT token verification decorators.
"""

from functools import wraps
from flask import request, g
from app.core.lib.error_utils import error_response
from app.auth.services import AuthService
from app.auth.repositories import UserRepository
from app.auth.models import User
from app.core.database import get_db
from config.logging import get_logger

logger = get_logger(__name__)


def jwt_required(f):
    """
    Decorator to require valid JWT token.
    Stores user object in Flask's g context.
    
    Usage:
        @jwt_required
        def protected_route():
            user = g.current_user
            return {'message': f'Hello {user.username}'}
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return error_response('Missing authorization header', 401)
        
        # Extract token from "Bearer <token>"
        try:
            token_type, token = auth_header.split(' ')
            if token_type.lower() != 'bearer':
                return error_response('Invalid token type. Use Bearer token', 401)
        except ValueError:
            return error_response('Invalid authorization header format', 401)
        
        # Verify token
        db = get_db()
        user_repo = UserRepository(db)
        auth_service = AuthService(user_repo)
        
        payload = auth_service.verify_jwt_token(token)
        if not payload:
            return error_response('Invalid or expired token', 401)
        
        # Get user from database (cached)
        user_dict = auth_service.get_user_by_id(payload['user_id'])
        if not user_dict or not user_dict.get('is_active'):
            return error_response('User not found or inactive', 401)
        
        # Store user dict in Flask's g context
        g.current_user = user_dict
        g.user_id = user_dict['id']
        
        return f(*args, **kwargs)
    
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin role.
    Must be used after @jwt_required.
    
    Usage:
        @jwt_required
        @admin_required
        def admin_only_route():
            return {'message': 'Admin access granted'}
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user'):
            return error_response('Authentication required', 401)
        
        if g.current_user.get('role') != 'admin':
            return error_response('Admin access required', 403)
        
        return f(*args, **kwargs)
    
    return decorated_function


def optional_auth(f):
    """
    Decorator for optional authentication.
    Sets g.current_user if token is valid, otherwise continues without auth.
    
    Usage:
        @optional_auth
        def public_route():
            if hasattr(g, 'current_user'):
                return {'message': f'Hello {g.current_user["username"]}'}
            return {'message': 'Hello guest'}
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token_type, token = auth_header.split(' ')
                if token_type.lower() == 'bearer':
                    db = get_db()
                    user_repo = UserRepository(db)
                    auth_service = AuthService(user_repo)
                    
                    payload = auth_service.verify_jwt_token(token)
                    if payload:
                        user_dict = auth_service.get_user_by_id(payload['user_id'])
                        if user_dict and user_dict.get('is_active'):
                            g.current_user = user_dict
                            g.user_id = user_dict['id']
            except Exception as e:
                logger.warning(f"Optional auth failed: {e}")
                # Continue without authentication
        
        return f(*args, **kwargs)
    
    return decorated_function

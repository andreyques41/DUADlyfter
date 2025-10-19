"""
JWT Authentication Decorators
Provides decorators for route protection and role-based access control.
"""

from functools import wraps
from flask import request, jsonify, g
from app.utilities.jwt_manager import JWT_Manager

jwt_manager = JWT_Manager()


def require_auth(f):
    """
    Decorator to require valid JWT token.
    Adds user data to Flask's g object for use in the route.
    
    Usage:
        @require_auth
        def get(self):
            user_id = g.user_data['user_id']
            username = g.user_data['username']
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract and verify token
        user_data = jwt_manager.get_user_from_request()
        
        if not user_data:
            return jsonify({"error": "Unauthorized - Invalid or missing token"}), 401
        
        # Store user data in Flask's g object for access in the route
        g.user_data = user_data
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_admin(f):
    """
    Decorator to require admin role (role_id = 1).
    Automatically includes authentication check.
    
    Usage:
        @require_admin
        def delete(self, user_id):
            # Only admins can access this
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract and verify token
        user_data = jwt_manager.get_user_from_request()
        
        if not user_data:
            return jsonify({"error": "Unauthorized - Invalid or missing token"}), 401
        
        # Check if user is admin
        if not user_data.get('is_admin') and user_data.get('role_id') != 1:
            return jsonify({"error": "Forbidden - Admin access required"}), 403
        
        # Store user data in Flask's g object
        g.user_data = user_data
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_auth_with_repo(repository_attr='user_repository'):
    """
    Decorator factory for routes that need authentication with repository access.
    This is useful when you need to check admin status via repository.
    
    Args:
        repository_attr: Name of the repository attribute in self
    
    Usage:
        @require_auth_with_repo('user_repository')
        def get(self):
            user_id = g.user_data['user_id']
            is_admin = g.is_admin
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(self, *args, **kwargs):
            # Extract and verify token
            user_data = jwt_manager.get_user_from_request()
            
            if not user_data:
                return jsonify({"error": "Unauthorized - Invalid or missing token"}), 401
            
            # Store user data
            g.user_data = user_data
            
            # Check admin status via repository if available
            if hasattr(self, repository_attr):
                repo = getattr(self, repository_attr)
                g.is_admin = repo.is_admin(user_data['user_id'])
            else:
                g.is_admin = user_data.get('is_admin', False)
            
            return f(self, *args, **kwargs)
        
        return decorated_function
    return decorator


def require_admin_with_repo(repository_attr='user_repository'):
    """
    Decorator factory for routes that require admin access with repository check.
    
    Args:
        repository_attr: Name of the repository attribute in self
    
    Usage:
        @require_admin_with_repo('user_repository')
        def delete(self, product_id):
            # Only admins can access this
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(self, *args, **kwargs):
            # Extract and verify token
            user_data = jwt_manager.get_user_from_request()
            
            if not user_data:
                return jsonify({"error": "Unauthorized - Invalid or missing token"}), 401
            
            # Check admin status
            user_id = user_data['user_id']
            
            if hasattr(self, repository_attr):
                repo = getattr(self, repository_attr)
                is_admin = repo.is_admin(user_id)
            else:
                is_admin = user_data.get('is_admin', False)
            
            if not is_admin:
                return jsonify({"error": "Forbidden - Admin access required"}), 403
            
            # Store user data
            g.user_data = user_data
            g.is_admin = True
            
            return f(self, *args, **kwargs)
        
        return decorated_function
    return decorator

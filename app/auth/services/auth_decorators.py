from functools import wraps
from flask import request, jsonify, g
import jwt
from app.auth.services.auth_service import AuthService
from app.auth.models.user import UserRole
from config.security_config import get_jwt_secret, get_jwt_algorithm

DB_PATH = './users.json'

def token_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # "Bearer <token>" → "<token>"
            except:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Decode JWT token using AuthService
            auth_service = AuthService(DB_PATH)
            data = auth_service.verify_jwt_token(token)
            
            if not data:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Get user from database
            current_user = auth_service.get_user_by_id(data['user_id'])
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            
            # Store user in Flask's g object for access in the actual route function
            # g.current_user will be available in any route using @token_required
            g.current_user = current_user
            
        except Exception as e:
            return jsonify({'error': 'Token validation failed'}), 401
        
        return function(*args, **kwargs)
    
    return decorated

def admin_required(function):
    """Decorator to require admin role (must be used with @token_required)"""
    @wraps(function)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'current_user') or g.current_user.role != UserRole.ADMIN:
            return jsonify({'error': 'Admin access required'}), 403
        
        return function(*args, **kwargs)
    
    return decorated

def customer_or_admin(function):
    """Decorator that allows both customers and admins (must be used with @token_required)"""
    @wraps(function)
    def decorated(*args, **kwargs):
        if not hasattr(g, 'current_user'):
            return jsonify({'error': 'Authentication required'}), 401
        
        return function(*args, **kwargs)
    
    return decorated
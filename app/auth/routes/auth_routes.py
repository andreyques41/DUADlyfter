from flask import request, jsonify
import logging
import os
from flask.views import MethodView
from app.auth.models.user import User, UserRole
from app.auth.services.auth_service import get_user

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = './users.json'

class AuthAPI(MethodView):
    """Handle user login authentication"""
    # Configure logging at module level
    init_every_request = False

    def __init__(self):
        self.logger = logger

    def post(self):
        # POST: User login
        pass

class RegisterAPI(MethodView):
    """Handle new user registration"""
    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.db_path = DB_PATH

    def post(self):
        # POST: User registration
        pass

class UserAPI(MethodView):
    """CRUD operations for user profiles"""
    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.db_path = DB_PATH
        self.model = User

    def get(self, user_id=None):
        # GET: Retrieve user profile
        try:
            result = get_user(self.db_path, self.model, id=user_id)
            
            if user_id is None:
                # Return all users as list of dictionaries
                return jsonify([user.to_dict() for user in result])
            else:
                # Return specific user as dictionary
                if result is None:
                    return jsonify({"error": "User not found"}), 404
                return jsonify(result.to_dict())
                
        except Exception as e:
            self.logger.error(f"Error retrieving user(s): {e}")
            return jsonify({"error": "Failed to retrieve user(s)"}), 500

    def put(self, user_id):
        # PUT: Update user profile
        pass

    def delete(self, user_id):
        # DELETE: Delete user account
        pass

class LogoutAPI(MethodView):
    """Handle user logout and session termination"""
    init_every_request = False

    def __init__(self):
        self.logger = logger

    def post(self):
        # POST: User logout
        pass

# Import blueprint from auth module
from app.auth import auth_bp

def register_auth_routes():
    """Register all authentication routes with the auth blueprint"""
    auth_bp.add_url_rule('/login', view_func=AuthAPI.as_view('login'))
    auth_bp.add_url_rule('/register', view_func=RegisterAPI.as_view('register'))
    auth_bp.add_url_rule('/logout', view_func=LogoutAPI.as_view('logout'))
    auth_bp.add_url_rule('/users/<int:user_id>', view_func=UserAPI.as_view('user'))
    auth_bp.add_url_rule('/users', view_func=UserAPI.as_view('users'))

# Call the function to register routes
register_auth_routes()
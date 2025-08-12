"""
Authentication Routes Module

Provides RESTful API endpoints for user authentication and management:
- POST /auth/login - User authentication 
- POST /auth/register - User registration
- GET /auth/users - List all users (admin only)
- GET /auth/users/<id> - Get specific user (user/admin)
- PUT /auth/users/<id> - Update user profile or password
- DELETE /auth/users/<id> - Delete user account

Security Features:
- JWT token-based authentication
- Role-based access control (admin/customer)
- Password hashing with bcrypt
- Input validation with Marshmallow schemas
"""
from flask import request, jsonify
import logging
from flask.views import MethodView
from marshmallow import ValidationError
from flask import g
from app.auth.models import UserRole
from app.auth.services import AuthService, hash_password, verify_password, token_required, admin_required
from app.auth.schemas import (
    user_registration_schema, 
    user_login_schema, 
    user_update_schema, 
    user_response_schema, 
    users_response_schema,
    user_password_change_schema
)
from app.shared.utils import require_admin_access, require_user_or_admin_access
from config.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)

DB_PATH = './users.json'

class AuthAPI(MethodView):
    """Handle user login authentication."""
    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.auth_service = AuthService(DB_PATH)

    def post(self):
        """Authenticate user with username/password and return JWT token."""
        try:
            # Validate incoming JSON data
            validated_data = user_login_schema.load(request.json)
            
            # Find user by username using service
            user = self.auth_service.get_user_by_username(validated_data['username'])
            
            if not user:
                self.logger.warning(f"Login attempt for non-existent user: {validated_data['username']}")
                return jsonify({"error": "Invalid credentials"}), 401
            
            # Check password
            if not verify_password(validated_data['password'], user.password_hash):
                self.logger.warning(f"Failed login attempt for user: {user.username}")
                return jsonify({"error": "Invalid credentials"}), 401
            
            # Generate JWT token
            token = self.auth_service.generate_jwt_token(user)
            if not token:
                return jsonify({"error": "Token generation failed"}), 500

            # Return success response
            return jsonify({
                "message": "Login successful",
                "user": user_response_schema.dump(user),
                "token" : token,
                "token_type": "Bearer"
            }), 200
            
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return jsonify({"error": "Login failed"}), 500

class RegisterAPI(MethodView):
    """Handle new user registration."""
    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.auth_service = AuthService(DB_PATH)

    def post(self):
        """Create new user account with validation and secure password hashing."""
        try:
            # Validate incoming JSON data
            validated_data = user_registration_schema.load(request.json)
            
            # Check if username or email already exists using service
            if self.auth_service.check_username_exists(validated_data['username']):
                return jsonify({"error": "Username already exists"}), 409
            if self.auth_service.check_email_exists(validated_data['email']):
                return jsonify({"error": "Email already exists"}), 409
            
            # Hash password
            password_hash = hash_password(validated_data['password'])
            
            # Create user using service
            new_user, error = self.auth_service.create_user(validated_data, password_hash)
            if error:
                return jsonify({"error": error}), 500
            
            # Return success response (without password)
            return jsonify({
                "message": "User registered successfully",
                "user": user_response_schema.dump(new_user)
            }), 201
            
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            return jsonify({"error": "User registration failed"}), 500

class UserAPI(MethodView):
    """CRUD operations for user profiles."""
    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.auth_service = AuthService(DB_PATH)

    @token_required
    def get(self, user_id=None):
        """Retrieve user profile(s) - specific user by ID or all users."""
        try:
            # Authorization check based on whether getting single user or all users
            if user_id is None:
                # Only admins can see all users
                auth_error = require_admin_access()
                if auth_error:
                    return auth_error
                schema = users_response_schema
            else:
                # Users can only see their own profile, admins can see any
                auth_error = require_user_or_admin_access(user_id)
                if auth_error:
                    return auth_error
                schema = user_response_schema
            
            # Single unified service call
            result = self.auth_service.get_users(user_id)
            
            # Handle single user not found case
            if user_id is not None and result is None:
                return jsonify({"error": "User not found"}), 404
            
            return jsonify(schema.dump(result))
                
        except Exception as e:
            self.logger.error(f"Error retrieving user(s): {e}")
            return jsonify({"error": "Failed to retrieve user data"}), 500

    @token_required
    def put(self, user_id):
        """Update user profile or password based on request content."""
        try:
            # Authorization: Users can only update their own profile, admins can update any
            auth_error = require_user_or_admin_access(user_id)
            if auth_error:
                return auth_error
            
            # Check if this is a password change request
            if request.json and 'current_password' in request.json:
                return self._change_password(user_id)
            else:
                return self._update_profile(user_id)
        except Exception as e:
            self.logger.error(f"Error updating user: {e}")
            return jsonify({"error": "User update failed"}), 500
    
    def _change_password(self, user_id):
        """Handle password change requests. Requires current_password and new_password."""
        try:
            # Validate password change data
            validated_data = user_password_change_schema.load(request.json)
            
            # Get user (using path parameter, not g.current_user)
            user = self.auth_service.get_users(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Verify current password
            if not verify_password(validated_data['current_password'], user.password_hash):
                return jsonify({"error": "Current password is incorrect"}), 401
            
            # Update password using service (using path parameter)
            new_password_hash = hash_password(validated_data['new_password'])
            updated_user, error = self.auth_service.update_user_password(user_id, new_password_hash)
            
            if error:
                return jsonify({"error": error}), 500
            
            return jsonify({"message": "Password updated successfully"}), 200
            
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
    
    def _update_profile(self, user_id):
        """Handle profile updates (non-password fields)."""
        try:
            # Validate profile update data
            validated_data = user_update_schema.load(request.json)
            
            # Update user using service (using path parameter, not g.current_user)
            updated_user, error = self.auth_service.update_user_profile(user_id, validated_data)
            
            if error:
                if error == "User not found":
                    return jsonify({"error": error}), 404
                return jsonify({"error": error}), 500
            
            return jsonify({
                "message": "User profile updated successfully",
                "user": user_response_schema.dump(updated_user)
            }), 200
            
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400

    @token_required
    def delete(self, user_id):
        """Delete user account by ID."""
        try:
            # Authorization: Users can only delete their own account, admins can delete any
            auth_error = require_user_or_admin_access(user_id)
            if auth_error:
                return auth_error
            
            success, error = self.auth_service.delete_user(user_id)
            
            if error:
                if error == "User not found":
                    return jsonify({"error": error}), 404
                return jsonify({"error": error}), 500
            
            return jsonify({"message": "User deleted successfully"}), 200
            
        except Exception as e:
            self.logger.error(f"Error deleting user: {e}")
            return jsonify({"error": "User deletion failed"}), 500

# Import blueprint from auth module
from app.auth import auth_bp

def register_auth_routes():
    """Register all authentication routes with the auth blueprint."""
    auth_bp.add_url_rule('/login', view_func=AuthAPI.as_view('login'))
    auth_bp.add_url_rule('/register', view_func=RegisterAPI.as_view('register'))
    auth_bp.add_url_rule('/users/<int:user_id>', view_func=UserAPI.as_view('user'))
    auth_bp.add_url_rule('/users', view_func=UserAPI.as_view('users'))
    # Password change can be done via PUT /users/<id> with password fields

# Call the function to register routes
register_auth_routes()
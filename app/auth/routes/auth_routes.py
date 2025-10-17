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

# Common imports
from flask import Blueprint, request, jsonify, g
from flask.views import MethodView
from marshmallow import ValidationError
from config.logging import get_logger, EXC_INFO_LOG_ERRORS

# Auth services and middleware
from app.auth.services import AuthService
from app.auth.services.security_service import hash_password, verify_password
from app.core.middleware import token_required_with_repo, admin_required_with_repo
from app.core.lib.jwt import generate_jwt_token

# Schemas
from app.auth.schemas import (
    user_registration_schema,
    user_login_schema,
    user_update_schema,
    user_response_schema,
    users_response_schema,
    user_password_change_schema
)

# Get logger for this module
logger = get_logger(__name__)

class AuthAPI(MethodView):
    """Handle user login authentication."""
    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.auth_service = AuthService()

    def post(self):
        """Authenticate user with username/password and return JWT token."""
        # NO AUTHENTICATION REQUIRED - Public endpoint for login
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
            token = generate_jwt_token(user)
            if not token:
                self.logger.error(f"Token generation failed for user: {user.username}")
                return jsonify({"error": "Token generation failed"}), 500

            self.logger.info(f"User {user.username} logged in successfully.")
            return jsonify({
                "message": "Login successful",
                "user": user_response_schema.dump(user),
                "token" : token,
                "token_type": "Bearer"
            }), 200

        except ValidationError as err:
            self.logger.warning(f"Login validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Login error: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Login failed"}), 500

class RegisterAPI(MethodView):
    """Handle new user registration."""
    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.auth_service = AuthService()

    def post(self):
        """Create new user account with validation and secure password hashing."""
        # NO AUTHENTICATION REQUIRED - Public endpoint for registration
        try:
            # Validate and extract data
            validated_data = user_registration_schema.load(request.json)
            
            # Extract password from original request
            password = request.json.get('password')
            
            # Hash password
            password_hash = hash_password(password)
            
            # Create user using service
            new_user, error = self.auth_service.create_user(
                username=validated_data.get('username'),
                email=validated_data.get('email'),
                password_hash=password_hash,
                first_name=validated_data.get('first_name'),
                last_name=validated_data.get('last_name'),
                phone=validated_data.get('phone')
            )
            
            if error:
                self.logger.warning(f"User registration failed: {error}")
                status_code = 409 if "already exists" in error else 500
                return jsonify({"error": error}), status_code

            self.logger.info(f"User {new_user.username} registered successfully.")
            return jsonify({
                "message": "User registered successfully",
                "user": user_response_schema.dump(new_user)
            }), 201

        except ValidationError as err:
            self.logger.warning(f"Registration validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Registration error: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "User registration failed"}), 500

class UserAPI(MethodView):
    """CRUD operations for user profiles."""
    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.auth_service = AuthService()

    @token_required_with_repo  # Validates JWT token, verifies role in DB, sets g.current_user and g.is_admin
    def get(self, user_id=None):
        """Retrieve user profile(s) - specific user by ID or all users."""
        # CONTEXTUAL ACCESS CONTROL - Different rules based on what's being accessed
        try:
            # Authorization check based on whether getting single user or all users
            if user_id is None:
                # Only admins can see all users
                if not g.is_admin:
                    self.logger.warning(f"Non-admin user {g.current_user.id} attempted to list all users.")
                    return jsonify({"error": "Admin access required"}), 403
                
                # Get all users
                result = self.auth_service.get_all_users()
                self.logger.info("All users retrieved")
                return jsonify(users_response_schema.dump(result))
            else:
                # Users can only see their own profile, admins can see any
                if not g.is_admin and g.current_user.id != user_id:
                    self.logger.warning(f"User {g.current_user.id} attempted to access user {user_id} profile.")
                    return jsonify({"error": "Access denied"}), 403
                
                # Get specific user
                result = self.auth_service.get_user_by_id(user_id)
                
                if result is None:
                    self.logger.warning(f"User not found: {user_id}")
                    return jsonify({"error": "User not found"}), 404

                self.logger.info(f"User retrieved: {user_id}")
                return jsonify(user_response_schema.dump(result))

        except Exception as e:
            self.logger.error(f"Error retrieving user(s): {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to retrieve user data"}), 500

    @token_required_with_repo  # Validates JWT token, verifies role in DB, sets g.current_user and g.is_admin
    def put(self, user_id):
        """Update user profile or password based on request content."""
        # USER OR ADMIN ACCESS - Users can update own profile, admins can update any
        try:
            # Authorization: Users can only update their own profile, admins can update any
            if not g.is_admin and g.current_user.id != user_id:
                self.logger.warning(f"User {g.current_user.id} attempted to update user {user_id}")
                return jsonify({"error": "Access denied"}), 403

            # Check if this is a password change request
            if request.json and 'current_password' in request.json:
                return self._change_password(user_id)
            else:
                return self._update_profile(user_id)
        except Exception as e:
            self.logger.error(f"Error updating user: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "User update failed"}), 500
    
    def _change_password(self, user_id):
        """Handle password change requests. Requires current_password and new_password."""
        # ACCESS ALREADY VERIFIED - Called from PUT method after authorization check
        try:
            # Validate password change data
            validated_data = user_password_change_schema.load(request.json)
            
            # Get user
            user = self.auth_service.get_user_by_id(user_id)
            if not user:
                self.logger.warning(f"Password change attempt for non-existent user: {user_id}")
                return jsonify({"error": "User not found"}), 404

            # Verify current password
            if not verify_password(validated_data['current_password'], user.password_hash):
                self.logger.warning(f"Incorrect current password for user: {user.username}")
                return jsonify({"error": "Current password is incorrect"}), 401

            # Update password using service
            new_password_hash = hash_password(validated_data['new_password'])
            updated_user, error = self.auth_service.update_user_password(user_id, new_password_hash)

            if error:
                self.logger.error(f"Password update failed for user {user_id}: {error}")
                return jsonify({"error": error}), 500

            self.logger.info(f"Password updated for user {user_id}")
            return jsonify({"message": "Password updated successfully"}), 200

        except ValidationError as err:
            self.logger.warning(f"Password change validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
    
    def _update_profile(self, user_id):
        """Handle profile updates (non-password fields)."""
        # ACCESS ALREADY VERIFIED - Called from PUT method after authorization check
        try:
            # Validate profile update data
            validated_data = user_update_schema.load(request.json)
            
            # Update user using service
            updated_user, error = self.auth_service.update_user_profile(user_id, **validated_data)
            
            if error:
                if error == "User not found":
                    self.logger.warning(f"Profile update attempt for non-existent user: {user_id}")
                    return jsonify({"error": error}), 404
                self.logger.error(f"Profile update failed for user {user_id}: {error}")
                return jsonify({"error": error}), 500

            self.logger.info(f"Profile updated for user {user_id}")
            return jsonify({
                "message": "User profile updated successfully",
                "user": user_response_schema.dump(updated_user)
            }), 200

        except ValidationError as err:
            self.logger.warning(f"Profile update validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400

    @token_required_with_repo  # Validates JWT token, verifies role in DB, sets g.current_user and g.is_admin
    def delete(self, user_id):
        """Delete user account by ID."""
        # USER OR ADMIN ACCESS - Users can delete own account, admins can delete any
        try:
            # Authorization: Users can only delete their own account, admins can delete any
            if not g.is_admin and g.current_user.id != user_id:
                self.logger.warning(f"User {g.current_user.id} attempted to delete user {user_id}")
                return jsonify({"error": "Access denied"}), 403

            # Delete user
            success, error = self.auth_service.delete_user(user_id)

            if error:
                if error == "User not found":
                    self.logger.warning(f"Delete attempt for non-existent user: {user_id}")
                    return jsonify({"error": error}), 404
                self.logger.error(f"User deletion failed for user {user_id}: {error}")
                return jsonify({"error": error}), 500

            self.logger.info(f"User deleted: {user_id}")
            return jsonify({"message": "User deleted successfully"}), 200

        except Exception as e:
            self.logger.error(f"Error deleting user: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "User deletion failed"}), 500

# Register routes when this module is imported by auth/__init__.py
def register_auth_routes(auth_bp):
    """Register all authentication routes with the auth blueprint."""
    auth_bp.add_url_rule('/login', view_func=AuthAPI.as_view('login'))
    auth_bp.add_url_rule('/register', view_func=RegisterAPI.as_view('register'))
    auth_bp.add_url_rule('/users/<int:user_id>', view_func=UserAPI.as_view('user_detail'))
    auth_bp.add_url_rule('/users', view_func=UserAPI.as_view('user_list'))
    # Password change can be done via PUT /users/<id> with password fields

from flask import request, jsonify
import logging
from flask.views import MethodView
from marshmallow import ValidationError

from app.auth.services.auth_service import AuthService
from app.auth.services.security_service import (
    hash_password, 
    verify_password
)
from app.auth.schemas.user_schema import (
    user_registration_schema, 
    user_login_schema, 
    user_update_schema, 
    user_response_schema, 
    users_response_schema,
    user_password_change_schema
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = './users.json'

class AuthAPI(MethodView):
    """Handle user login authentication."""
    # Configure logging at module level
    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.auth_service = AuthService(DB_PATH)

    def post(self):
        """Authenticate user with username/password and return user data on success."""
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
            
            # Return success response
            return jsonify({
                "message": "Login successful",
                "user": user_response_schema.dump(user)
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

    def get(self, user_id=None):
        """Retrieve user profile(s). Returns specific user by ID or all users if no ID provided."""
        try:
            if user_id is None:
                # Return all users as list of dictionaries
                result = self.auth_service.get_all_users()
                return jsonify(users_response_schema.dump(result))
            else:
                # Return specific user as dictionary
                result = self.auth_service.get_user_by_id(user_id)
                if result is None:
                    return jsonify({"error": "User not found"}), 404
                return jsonify(user_response_schema.dump(result))
                
        except Exception as e:
            self.logger.error(f"Error retrieving user(s): {e}")
            return jsonify({"error": "Failed to retrieve user data"}), 500

    def put(self, user_id):
        """Update user profile or password based on request content."""
        try:
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
            
            # Get user
            user = self.auth_service.get_user_by_id(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Verify current password
            if not verify_password(validated_data['current_password'], user.password_hash):
                return jsonify({"error": "Current password is incorrect"}), 401
            
            # Update password using service
            new_password_hash = hash_password(validated_data['new_password'])
            updated_user, error = self.auth_service.update_user_password(user_id, new_password_hash)
            
            if error:
                return jsonify({"error": error}), 500
            
            return jsonify({"message": "Password updated successfully"}), 200
            
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
    
    def _update_profile(self, user_id):
        """Handle profile updates (non-password fields like name, email, phone)."""
        try:
            # Validate profile update data
            validated_data = user_update_schema.load(request.json)
            
            # Update user using service
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

    def delete(self, user_id):
        """Delete user account by ID."""
        try:
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
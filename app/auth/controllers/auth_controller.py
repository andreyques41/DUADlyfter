"""
AuthController: Handles HTTP responses for authentication endpoints.
Delegates business logic to AuthService.

Features:
- User login (JWT token generation)
- User registration
- Input validation with Marshmallow schemas
- Comprehensive error handling and logging
"""
from flask import request, jsonify, g
from marshmallow import ValidationError
from config.logging import get_logger, EXC_INFO_LOG_ERRORS

# Auth services
from app.auth.services import AuthService
from app.auth.services.security_service import hash_password, verify_password
from app.core.lib.jwt import generate_jwt_token

# Schemas
from app.auth.schemas import (
    user_registration_schema,
    user_login_schema,
    user_response_schema
)

# Get logger for this module
logger = get_logger(__name__)


class AuthController:
    """
    Controller layer for authentication operations.
    Handles HTTP responses, validation, and delegates to AuthService.
    """
    
    def __init__(self):
        self.logger = logger
        self.auth_service = AuthService()
    
    def login(self):
        """
        POST /auth/login
        Authenticate user with username/password and return JWT token.
        
        Public access - no authentication required.
        """
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
                "token": token,
                "token_type": "Bearer"
            }), 200

        except ValidationError as err:
            self.logger.warning(f"Login validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Login error: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Login failed"}), 500
    
    def register(self):
        """
        POST /auth/register
        Register a new user account.
        
        Public access - no authentication required.
        """
        try:
            # Validate incoming JSON data
            validated_data = user_registration_schema.load(request.json)
            
            # Check if username already exists
            existing_user = self.auth_service.get_user_by_username(validated_data['username'])
            if existing_user:
                self.logger.warning(f"Registration attempt with existing username: {validated_data['username']}")
                return jsonify({"error": "Username already exists"}), 409
            
            # Check if email already exists
            existing_email = self.auth_service.get_user_by_email(validated_data['email'])
            if existing_email:
                self.logger.warning(f"Registration attempt with existing email: {validated_data['email']}")
                return jsonify({"error": "Email already exists"}), 409
            
            # Create user using service
            user, error = self.auth_service.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data.get('first_name'),
                last_name=validated_data.get('last_name')
            )
            
            if error:
                self.logger.error(f"User registration failed: {error}")
                return jsonify({"error": "Registration failed", "details": error}), 500
            
            if not user:
                self.logger.error("User creation returned None without error")
                return jsonify({"error": "Registration failed"}), 500
            
            self.logger.info(f"New user registered: {user.username}")
            return jsonify({
                "message": "Registration successful",
                "user": user_response_schema.dump(user)
            }), 201
            
        except ValidationError as err:
            self.logger.warning(f"Registration validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Registration error: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Registration failed"}), 500

"""
Auth Controller
HTTP request/response handling for authentication endpoints.
"""

from flask import request, g
from marshmallow import ValidationError
from app.auth.schemas import UserRegisterSchema, UserLoginSchema, UserResponseSchema
from app.auth.services import AuthService
from app.auth.repositories import UserRepository
from app.core.lib.error_utils import error_response, success_response
from app.core.database import get_db
from config.logging import get_logger

logger = get_logger(__name__)


class AuthController:
    """Controller for authentication operations."""
    
    @staticmethod
    def register():
        """
        Handle user registration request.
        
        Request body:
            {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "secure_password123",
                "role": "chef"  // optional, defaults to 'chef'
            }
        
        Returns:
            201: User created successfully
            400: Validation error or duplicate user
            500: Server error
        """
        try:
            # Get request data
            data = request.get_json()
            
            if not data:
                return error_response('Request body is required', 400)
            
            # Validate with schema
            schema = UserRegisterSchema()
            try:
                validated_data = schema.load(data)
            except ValidationError as e:
                return error_response('Validation failed', 400, details=e.messages)
            
            # Create user via service
            db = get_db()
            user_repo = UserRepository(db)
            auth_service = AuthService(user_repo)
            
            try:
                user = auth_service.register_user(
                    username=validated_data['username'],
                    email=validated_data['email'],
                    password=validated_data['password'],
                    role=validated_data.get('role', 'chef')
                )
            except ValueError as e:
                return error_response(str(e), 400)
            
            if not user:
                return error_response('Failed to create user', 500)
            
            # Serialize response
            response_schema = UserResponseSchema()
            user_data = response_schema.dump(user)
            
            logger.info(f"User registered successfully: {user.username}")
            return success_response(
                user_data,
                message='User registered successfully',
                status_code=201
            )
            
        except Exception as e:
            logger.error(f"Registration error: {e}", exc_info=True)
            return error_response('Internal server error', 500)
    
    @staticmethod
    def login():
        """
        Handle user login request.
        
        Request body:
            {
                "username": "john_doe",
                "password": "secure_password123"
            }
        
        Returns:
            200: Login successful with JWT token
            400: Validation error
            401: Invalid credentials
            500: Server error
        """
        try:
            # Get request data
            data = request.get_json()
            
            if not data:
                return error_response('Request body is required', 400)
            
            # Validate with schema
            schema = UserLoginSchema()
            try:
                validated_data = schema.load(data)
            except ValidationError as e:
                return error_response('Validation failed', 400, details=e.messages)
            
            # Authenticate user via service
            db = get_db()
            user_repo = UserRepository(db)
            auth_service = AuthService(user_repo)
            
            user = auth_service.authenticate_user(
                username=validated_data['username'],
                password=validated_data['password']
            )
            
            if not user:
                return error_response('Invalid username or password', 401)
            
            # Generate JWT token
            try:
                token = auth_service.generate_jwt_token(user)
            except Exception as e:
                logger.error(f"Token generation failed: {e}", exc_info=True)
                return error_response('Failed to generate authentication token', 500)
            
            # Serialize user data
            response_schema = UserResponseSchema()
            user_data = response_schema.dump(user)
            
            response_data = {
                'user': user_data,
                'token': token,
                'token_type': 'Bearer'
            }
            
            logger.info(f"User logged in successfully: {user.username}")
            return success_response(
                response_data,
                message='Login successful',
                status_code=200
            )
            
        except Exception as e:
            logger.error(f"Login error: {e}", exc_info=True)
            return error_response('Internal server error', 500)
    
    @staticmethod
    def get_current_user():
        """
        Get current authenticated user info (cached).
        Requires JWT token in Authorization header.
        
        Returns:
            200: User data
            401: Unauthorized
            500: Server error
        """
        try:
            # User dict is already loaded by @jwt_required decorator (from cache)
            user_dict = g.current_user
            
            # User data is already in the correct format (dict)
            # No need to serialize again since it comes from cache
            return success_response(user_dict, status_code=200)
            
        except Exception as e:
            logger.error(f"Get current user error: {e}", exc_info=True)
            return error_response('Internal server error', 500)

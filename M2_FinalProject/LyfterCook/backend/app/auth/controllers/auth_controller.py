"""
Auth Controller
HTTP request/response handling for authentication endpoints.
"""

from flask import request, g
from app.auth.schemas import UserRegisterSchema, UserLoginSchema, UserResponseSchema
from app.auth.services import AuthService
from app.auth.repositories import UserRepository
from app.core.lib.error_utils import error_response, success_response
from app.core.database import get_db
from app.core.middleware.request_decorators import validate_json
from app.core.email_service import EmailService
from config.logging import get_logger

logger = get_logger(__name__)


class AuthController:
    """Controller for authentication operations."""
    
    def __init__(self):
        """Initialize controller with logger."""
        self.logger = logger
    
    def _get_service(self):
        """
        Get auth service with database session.
        Creates new instances per request using Flask's g.db.
        """
        db = get_db()
        user_repo = UserRepository(db)
        return AuthService(user_repo)
    
    @validate_json(UserRegisterSchema)
    def register(self):
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
            400: Validation error, malformed JSON, or duplicate user
            500: Server error
        """
        try:
            # Get validated data from decorator
            validated_data = request.validated_data
            
            # Create user via service
            auth_service = self._get_service()
            
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
            
            self.logger.info(f"User registered successfully: {user.username}")

            # Best-effort welcome email (does not affect registration outcome)
            try:
                EmailService.send_welcome_email(to_email=user.email, username=user.username)
            except Exception:
                self.logger.warning("Welcome email failed", exc_info=True)

            return success_response(
                user_data,
                message='User registered successfully',
                status_code=201
            )
            
        except Exception as e:
            self.logger.error(f"Registration error: {e}", exc_info=True)
            return error_response('Internal server error', 500)
    
    @validate_json(UserLoginSchema)
    def login(self):
        """
        Handle user login request.
        
        Request body:
            {
                "username": "john_doe",
                "password": "secure_password123"
            }
        
        Returns:
            200: Login successful with JWT token
            400: Validation error or malformed JSON
            401: Invalid credentials
            500: Server error
        """
        try:
            # Get validated data from decorator
            validated_data = request.validated_data
            
            # Authenticate user via service
            auth_service = self._get_service()
            
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
                self.logger.error(f"Token generation failed: {e}", exc_info=True)
                return error_response('Failed to generate authentication token', 500)
            
            # Serialize user data
            response_schema = UserResponseSchema()
            user_data = response_schema.dump(user)
            
            response_data = {
                'user': user_data,
                'token': token,
                'token_type': 'Bearer'
            }
            
            self.logger.info(f"User logged in successfully: {user.username}")
            return success_response(
                response_data,
                message='Login successful',
                status_code=200
            )
            
        except Exception as e:
            self.logger.error(f"Login error: {e}", exc_info=True)
            return error_response('Internal server error', 500)
    
    def get_current_user(self):
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

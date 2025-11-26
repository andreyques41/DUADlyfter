"""
Auth Service
Business logic for user authentication and registration.
"""

from typing import Optional, Dict
from datetime import datetime, timedelta
import jwt
from flask import current_app
from app.auth.models import User, UserRole
from app.auth.repositories import UserRepository
from app.auth.services.security_service import SecurityService
from config.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    """Service for authentication business logic."""
    
    def __init__(self, user_repository: UserRepository):
        """
        Initialize service with dependencies.
        
        Args:
            user_repository: UserRepository instance
        """
        self.user_repo = user_repository
        self.security = SecurityService()
    
    def register_user(self, username: str, email: str, password: str, role: str = 'chef') -> Optional[User]:
        """
        Register a new user.
        
        Args:
            username: Unique username
            email: Unique email address
            password: Plain text password (will be hashed)
            role: User role ('chef' or 'admin')
            
        Returns:
            Created User object or None if registration failed
            
        Raises:
            ValueError: If username or email already exists
        """
        # Check if username already exists
        existing_user = self.user_repo.get_by_username(username)
        if existing_user:
            logger.warning(f"Registration failed: Username '{username}' already exists")
            raise ValueError(f"Username '{username}' is already taken")
        
        # Check if email already exists
        existing_email = self.user_repo.get_by_email(email)
        if existing_email:
            logger.warning(f"Registration failed: Email '{email}' already exists")
            raise ValueError(f"Email '{email}' is already registered")
        
        # Hash password
        try:
            password_hash = self.security.hash_password(password)
        except Exception as e:
            logger.error(f"Failed to hash password for user '{username}': {e}")
            raise ValueError("Failed to process password")
        
        # Convert role string to UserRole enum
        user_role = UserRole.ADMIN if role == 'admin' else UserRole.CHEF
        
        # Create user
        user = self.user_repo.create(
            username=username,
            email=email,
            password_hash=password_hash,
            role=user_role
        )
        
        if user:
            logger.info(f"User registered successfully: {username} ({user_role.value})")
        else:
            logger.error(f"Failed to create user in database: {username}")
        
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        # Get user by username
        user = self.user_repo.get_by_username(username)
        
        if not user:
            logger.warning(f"Authentication failed: User '{username}' not found")
            return None
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Authentication failed: User '{username}' is inactive")
            return None
        
        # Verify password
        if not self.security.verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed: Invalid password for user '{username}'")
            return None
        
        logger.info(f"User authenticated successfully: {username}")
        return user
    
    def generate_jwt_token(self, user: User) -> str:
        """
        Generate JWT token for authenticated user.
        
        Args:
            user: User object
            
        Returns:
            JWT token string
        """
        try:
            payload = {
                'user_id': user.id,
                'username': user.username,
                'role': user.role.value,
                'exp': datetime.utcnow() + timedelta(hours=24),  # 24 hour expiration
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(
                payload,
                current_app.config['JWT_SECRET_KEY'],
                algorithm='HS256'
            )
            
            logger.info(f"JWT token generated for user: {user.username}")
            return token
            
        except Exception as e:
            logger.error(f"Error generating JWT token for user {user.username}: {e}", exc_info=True)
            raise
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None
        """
        return self.user_repo.get_by_id(user_id)

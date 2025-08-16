"""
JWT Utilities Module

Provides JWT token generation and verification functions for authentication.
Centralized JWT handling to avoid code duplication across services.

Features:
- JWT token generation with configurable expiration
- Token verification with proper error handling
- Comprehensive logging for security events
- Easy integration with authentication services

Usage:
    from app.shared.utils.jwt_utils import generate_jwt_token, verify_jwt_token
    
    # Generate token
    token = generate_jwt_token(user)
    
    # Verify token
    payload = verify_jwt_token(token)
"""
import jwt
from datetime import datetime, timedelta
from config.security_config import get_jwt_secret, get_jwt_algorithm, get_jwt_expiration_hours
from config.logging_config import get_logger, EXC_INFO_LOG_ERRORS

logger = get_logger(__name__)

def generate_jwt_token(user):
    """Generate JWT token for authenticated user.
    
    Args:
        user: User object with id, username, and role attributes
        
    Returns:
        str or None: JWT token string on success, None on failure
    """
    try:
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role.value,
            'exp': datetime.utcnow() + timedelta(hours=get_jwt_expiration_hours()),
            'iat': datetime.utcnow()
        }

        token = jwt.encode(payload, get_jwt_secret(), algorithm=get_jwt_algorithm())
        logger.info(f"JWT token generated for user: {user.username}")
        return token

    except Exception as e:
        logger.error(f"Error generating JWT token: {e}", exc_info=EXC_INFO_LOG_ERRORS)
        return None
    
def verify_jwt_token(token):
    """Verify and decode JWT token.
    
    Args:
        token (str): JWT token to verify
        
    Returns:
        dict or None: Decoded payload on success, None on failure
    """
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[get_jwt_algorithm()])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid JWT token")
        return None
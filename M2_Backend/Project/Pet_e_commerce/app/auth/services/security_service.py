"""
Security Service Module

Handles authentication security functions including:
- Password hashing and verification with bcrypt
- Application-wide pepper implementation for additional security
- Configurable security parameters

Security Features:
- bcrypt with configurable rounds (default: 14)
- Application-wide pepper for additional password protection
- Secure password verification with timing-safe comparison

Environment Variables:
- APP_PEPPER: Application-wide secret (should be set in production)

Usage:
    from app.auth.services.security_service import hash_password, verify_password
    
    # Hash a password
    hashed = hash_password("user_password")
    
    # Verify a password
    is_valid = verify_password("user_password", hashed)
"""
import os
import bcrypt

# Application-wide pepper (secret not stored in database)
# IMPORTANT: Set APP_PEPPER environment variable in production!
APP_PEPPER = os.environ.get('APP_PEPPER', 'dev-only-pepper-change-in-production')

# Security configuration
SECURITY_CONFIG = {
    'bcrypt_rounds': 14,
}

class SecurityService:
    """Centralized security service for password hashing and verification."""
    
    @staticmethod
    def hash_password(password):
        """Hash password using bcrypt with salt and application pepper"""
        # Add application-wide pepper (stored separately from database)
        peppered_password = password + APP_PEPPER
        # Generate salt with configurable cost factor
        salt = bcrypt.gensalt(rounds=SECURITY_CONFIG['bcrypt_rounds'])
        hashed = bcrypt.hashpw(peppered_password.encode('utf-8'), salt)
        return hashed.decode('utf-8') # decode for JSON compatibility
    
    @staticmethod
    def verify_password(password, hashed_password):
        """Verify password against bcrypt hash with pepper"""
        # Add same pepper before verification
        peppered_password = password + APP_PEPPER
        return bcrypt.checkpw(peppered_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Convenience functions for backward compatibility and easy imports
def hash_password(password):
    """Convenience function for password hashing with pepper and salt."""
    return SecurityService.hash_password(password)

def verify_password(password, hashed_password):
    """Convenience function for password verification with pepper."""
    return SecurityService.verify_password(password, hashed_password)

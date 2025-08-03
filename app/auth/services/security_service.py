"""
Security Service Module
Handles authentication security functions including:
- Password hashing and verification with pepper and salt
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
        return bcrypt.hashpw(peppered_password.encode('utf-8'), salt)
    
    @staticmethod
    def verify_password(password, hashed_password):
        """Verify password against bcrypt hash with pepper"""
        # Add same pepper before verification
        peppered_password = password + APP_PEPPER
        return bcrypt.checkpw(peppered_password.encode('utf-8'), hashed_password)

# Convenience functions for backward compatibility and easy imports
def hash_password(password):
    """Convenience function for password hashing with pepper and salt."""
    return SecurityService.hash_password(password)

def verify_password(password, hashed_password):
    """Convenience function for password verification with pepper."""
    return SecurityService.verify_password(password, hashed_password)

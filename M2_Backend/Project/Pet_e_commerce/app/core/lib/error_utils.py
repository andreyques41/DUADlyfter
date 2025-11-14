"""
Error Handling Utilities

Provides consistent error response formatting across the application.
Automatically shows detailed errors in development mode and generic
messages in production for security.

Usage:
    from app.core.lib.error_utils import error_response
    
    try:
        # ... some operation
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)
        return error_response("Operation failed", e, status_code=500)
"""
import os
from flask import jsonify
from typing import Union, Tuple


def error_response(
    generic_message: str,
    exception: Exception = None,
    status_code: int = 500
) -> Tuple[dict, int]:
    """
    Create a consistent error response that shows details in development
    and generic messages in production.
    
    Args:
        generic_message: Generic error message for production
        exception: The exception object (optional)
        status_code: HTTP status code (default: 500)
        
    Returns:
        Tuple of (jsonify response, status_code)
        
    Example:
        >>> try:
        ...     user = get_user(123)
        ... except Exception as e:
        ...     return error_response("Failed to retrieve user", e, 500)
        
        Development response:
        {"error": "Failed to retrieve user: User not found in database"}
        
        Production response:
        {"error": "Failed to retrieve user"}
    """
    is_development = os.getenv('FLASK_ENV') == 'development'
    
    if is_development and exception:
        # Show detailed error in development
        error_msg = f"{generic_message}: {str(exception)}"
    else:
        # Show generic message in production
        error_msg = generic_message
    
    return jsonify({"error": error_msg}), status_code


def validation_error_response(errors: dict) -> Tuple[dict, int]:
    """
    Format validation errors from Marshmallow schemas.
    
    Args:
        errors: Dictionary of validation errors from schema.validate()
        
    Returns:
        Tuple of (jsonify response, 400)
        
    Example:
        >>> errors = {"email": ["Not a valid email address"]}
        >>> return validation_error_response(errors)
        {"error": "Validation failed", "details": {...}}
    """
    return jsonify({
        "error": "Validation failed",
        "details": errors
    }), 400

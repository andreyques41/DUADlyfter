"""
Error Utilities
Centralized error response formatting.
"""

from flask import jsonify
from config.logging import get_logger

logger = get_logger(__name__)


def error_response(message: str, status_code: int, details: dict = None):
    """
    Create standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        details: Optional additional error details
        
    Returns:
        Flask JSON response tuple
    """
    response = {
        'error': message,
        'status_code': status_code
    }
    
    if details:
        response['details'] = details
    
    logger.error(f"Error response: {status_code} - {message}")
    
    return jsonify(response), status_code


def success_response(data: dict, message: str = None, status_code: int = 200):
    """
    Create standardized success response.
    
    Args:
        data: Response data
        message: Optional success message
        status_code: HTTP status code (default: 200)
        
    Returns:
        Flask JSON response tuple
    """
    response = {'data': data}
    
    if message:
        response['message'] = message
    
    return jsonify(response), status_code

"""
Error Utilities
Centralized error response formatting with Envelope v1 standard.

Envelope v1 Format:
{
    "success": true/false,
    "message": "Descriptive message",
    "data": <payload or null>
}
"""

from flask import jsonify
from config.logging import get_logger

logger = get_logger(__name__)


def error_response(message: str, status_code: int, details: dict = None):
    """
    Create Envelope v1 compliant error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        details: Optional error details (will be placed in data field)
        
    Returns:
        Flask JSON response tuple with format:
        {
            "success": false,
            "message": "Error message",
            "data": <details or null>
        }
    """
    response = {
        'success': False,
        'message': message,
        'data': details
    }
    
    logger.error(f"Error response: {status_code} - {message}")
    
    return jsonify(response), status_code


def success_response(data=None, message: str = None, status_code: int = 200):
    """
    Create Envelope v1 compliant success response.
    
    Args:
        data: Response payload (can be dict, list, or None)
        message: Success message (defaults to "Operation successful")
        status_code: HTTP status code (default: 200)
        
    Returns:
        Flask JSON response tuple with format:
        {
            "success": true,
            "message": "Success message",
            "data": <payload or null>
        }
    """
    response = {
        'success': True,
        'message': message or 'Operation successful',
        'data': data
    }
    
    return jsonify(response), status_code

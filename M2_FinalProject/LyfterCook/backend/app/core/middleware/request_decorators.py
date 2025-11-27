"""
Request Decorators
Reusable decorators for request validation and processing.
"""

from functools import wraps
from flask import request
from marshmallow import ValidationError, Schema
from app.core.lib.error_utils import error_response
from config.logging import get_logger

logger = get_logger(__name__)


def validate_json(schema_class: type[Schema] = None):
    """
    Decorator to validate JSON request body.
    
    Args:
        schema_class: Optional Marshmallow schema class for validation
        
    Usage:
        @validate_json()  # Just parse JSON, no schema validation
        def my_endpoint():
            data = request.get_json()
            
        @validate_json(UserRegisterSchema)  # Parse and validate
        def register():
            validated_data = request.validated_data
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Parse JSON
            try:
                data = request.get_json()
            except Exception as e:
                logger.warning(f"Invalid JSON in request to {request.path}: {e}")
                return error_response('Invalid JSON format', 400)
            
            if data is None:
                return error_response('Request body is required', 400)
            
            # Validate with schema if provided
            if schema_class:
                try:
                    schema = schema_class()
                    validated_data = schema.load(data)
                    # Store validated data in request object
                    request.validated_data = validated_data
                except ValidationError as e:
                    logger.warning(f"Validation error in {request.path}: {e.messages}")
                    return error_response('Validation failed', 400, details=e.messages)
            
            return f(*args, **kwargs)
        return wrapper
    return decorator


def require_content_type(content_type='application/json'):
    """
    Decorator to enforce specific Content-Type header.
    
    Args:
        content_type: Required Content-Type value
        
    Usage:
        @require_content_type('application/json')
        def my_endpoint():
            ...
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if request.content_type != content_type:
                logger.warning(f"Invalid Content-Type for {request.path}: {request.content_type}")
                return error_response(
                    f'Content-Type must be {content_type}',
                    415  # Unsupported Media Type
                )
            return f(*args, **kwargs)
        return wrapper
    return decorator

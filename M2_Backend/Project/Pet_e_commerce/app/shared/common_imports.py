"""
Common Imports Module

Most commonly used imports across the application to reduce repetitive import statements.
Import this module in your routes, services, and other files to get all the essential dependencies.

Usage:
    from app.shared.common_imports import *
    
    # Now you have access to:
    # - Flask essentials (request, jsonify, g, MethodView)
    # - Validation (ValidationError)
    # - Logging (get_logger, EXC_INFO_LOG_ERRORS)
    # - Common types (Optional, List, Tuple, Dict, Any)
    # - Date/time utilities
"""

# Flask essentials
from flask import request, jsonify, g
from flask.views import MethodView

# Validation
from marshmallow import ValidationError

# Logging
from config.logging_config import get_logger, EXC_INFO_LOG_ERRORS

# Common types for better type hints
from typing import Optional, List, Tuple, Dict, Any

# Date/time utilities
from datetime import datetime, timedelta

# Export all commonly used items
__all__ = [
    # Flask
    'request', 'jsonify', 'g', 'MethodView',
    
    # Validation
    'ValidationError',
    
    # Logging
    'get_logger', 'EXC_INFO_LOG_ERRORS',
    
    # Types
    'Optional', 'List', 'Tuple', 'Dict', 'Any',
    
    # Date/time
    'datetime', 'timedelta'
]

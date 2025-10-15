"""
Pet E-commerce Application Factory

This module contains the Flask application factory for the Pet E-commerce platform.
The application provides a comprehensive e-commerce solution with:

Core Modules:
- Authentication: User registration, login, JWT-based auth, role management
- Products: Product catalog, inventory, filtering, public browsing
- Sales: Shopping carts, orders, billing, returns processing

Architecture:
- Modular blueprint-based organization
- Service layer for business logic
- Repository pattern for data access
- Schema-based validation with Marshmallow
- JWT authentication with role-based access control
- PostgreSQL database with SQLAlchemy ORM
- Comprehensive logging and error handling

Features:
- RESTful API design
- Public product browsing
- Secure user authentication
- Admin vs user role separation
- Complete e-commerce workflow
"""
from flask import Flask
import logging

def create_app() -> Flask:
    """
    Application factory function.
    
    Creates and configures the Flask application with all necessary
    blueprints, logging, and middleware.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Configure logging once for the entire application
    from config.logging import setup_logging
    setup_logging()
    
    # Register all blueprints from app/blueprints.py, each with its url_prefix
    from app.blueprints import blueprints
    for bp, prefix in blueprints:
        app.register_blueprint(bp, url_prefix=prefix)

    # Centralized error handler for API
    @app.errorhandler(Exception)
    def handle_exception(e):
        """
        Global exception handler for all unhandled errors.
        
        Behavior:
        - Logs all errors with full stack trace
        - In development: Returns detailed error info for debugging
        - In production: Returns generic error message for security
        - Respects HTTP exceptions (404, 403, etc.) with proper status codes
        """
        from flask import jsonify
        import traceback
        import os
        from config.logging import get_logger, EXC_INFO_LOG_ERRORS
        
        logger = get_logger(__name__)
        
        # Always log the error with full details for debugging
        logger.error(
            f"Unhandled exception: {type(e).__name__}: {str(e)}",
            exc_info=EXC_INFO_LOG_ERRORS
        )
        
        # Check if it's an HTTP exception (404, 403, etc.)
        # These have a 'code' attribute and should be handled differently
        if hasattr(e, 'code'):
            return jsonify({
                "error": e.description if hasattr(e, 'description') else str(e),
                "status": e.code
            }), e.code
        
        # Determine if we're in development mode
        is_development = os.getenv('FLASK_ENV', 'production') == 'development'
        
        if is_development:
            # In development: show detailed error information for debugging
            return jsonify({
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc().split('\n')
            }), 500
        else:
            # In production: return generic error message (security best practice)
            # Never expose internal error details to clients in production
            return jsonify({
                "error": "An internal server error occurred. Please try again later.",
                "status": 500
            }), 500

    return app

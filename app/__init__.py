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
- Schema-based validation with Marshmallow
- JWT authentication with role-based access control
- JSON file-based persistence
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
    from config.logging_config import configure_app_logging
    configure_app_logging()
    
    # Register all blueprints from app/blueprints.py, each with its url_prefix
    from app.blueprints import blueprints
    for bp, prefix in blueprints:
        app.register_blueprint(bp, url_prefix=prefix)

    # Centralized error handler for API
    @app.errorhandler(Exception)
    def handle_exception(e):
        from flask import jsonify
        import traceback
        # Log the error here if desired
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500

    return app

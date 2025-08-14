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

def create_app():
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
    
    # Register blueprints with URL prefixes
    # Products module - handles product catalog and inventory
    from app.products import products_bp
    app.register_blueprint(products_bp, url_prefix='/products')
    
    # Authentication module - handles user auth and authorization
    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Sales module - handles carts, orders, bills, returns
    from app.sales import sales_bp
    app.register_blueprint(sales_bp, url_prefix='/sales')
    
    return app

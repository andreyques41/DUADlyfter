"""
Blueprint Registration
Centralized registration of all Flask blueprints.
"""

from flask import Flask
from app.auth.routes import auth_bp
from app.chefs.routes import chef_bp
from config.logging import get_logger

logger = get_logger(__name__)


def register_blueprints(app: Flask):
    """
    Register all application blueprints.
    
    Args:
        app: Flask application instance
    """
    # Register auth blueprint
    app.register_blueprint(auth_bp)
    logger.info("Auth blueprint registered at /auth")
    
    # Register chefs blueprint
    app.register_blueprint(chef_bp)
    logger.info("Chefs blueprint registered at /chefs")
    
    # Future blueprints will be registered here:
    # app.register_blueprint(clients_bp)
    # app.register_blueprint(dishes_bp)
    # etc.
    
    logger.info("All blueprints registered successfully")

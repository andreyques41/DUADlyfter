"""
Blueprint Registration
Centralized registration of all Flask blueprints.
"""

from flask import Flask
from app.auth.routes import auth_bp
from app.chefs.routes import chef_bp
from app.clients.routes import client_bp
from app.dishes.routes import dish_bp
from app.menus.routes import menu_bp
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
    
    # Register clients blueprint
    app.register_blueprint(client_bp)
    logger.info("Clients blueprint registered at /clients")
    
    # Register dishes blueprint
    app.register_blueprint(dish_bp)
    logger.info("Dishes blueprint registered at /dishes")
    
    # Register menus blueprint
    app.register_blueprint(menu_bp)
    logger.info("Menus blueprint registered at /menus")
    
    # Future blueprints will be registered here:
    # app.register_blueprint(quotations_bp)
    # etc.
    
    logger.info("All blueprints registered successfully")

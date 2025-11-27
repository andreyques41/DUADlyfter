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
from app.quotations.routes import quotation_bp
from app.appointments.routes import appointment_bp
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
    
    # Register quotations blueprint
    app.register_blueprint(quotation_bp)
    logger.info("Quotations blueprint registered at /quotations")
    
    # Register appointments blueprint
    app.register_blueprint(appointment_bp)
    logger.info("Appointments blueprint registered at /appointments")
    
    # Future blueprints will be registered here:
    # app.register_blueprint(scraper_bp)
    # etc.
    
    logger.info("All blueprints registered successfully")

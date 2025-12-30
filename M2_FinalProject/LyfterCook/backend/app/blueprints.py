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
from app.public.routes import public_bp
from app.admin.routes.admin_routes import admin_bp
from config.logging import get_logger

# Optional scraper blueprint (requires beautifulsoup4)
try:
    from app.scrapers.routes import scraper_bp
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False
    scraper_bp = None

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
    
    # Register scrapers blueprint (optional)
    if SCRAPER_AVAILABLE:
        app.register_blueprint(scraper_bp)
        logger.info("Scrapers blueprint registered at /scrapers")
    else:
        logger.warning("Scrapers blueprint skipped (beautifulsoup4 not installed)")
    
    # Register public blueprint
    app.register_blueprint(public_bp)
    logger.info("Public blueprint registered at /public")
    
    # Register admin blueprint
    app.register_blueprint(admin_bp)
    logger.info("Admin blueprint registered at /admin")
    
    logger.info("All blueprints registered successfully")

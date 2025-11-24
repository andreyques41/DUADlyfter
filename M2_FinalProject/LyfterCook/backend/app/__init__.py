"""
LyfterCook Application Factory
Flask application setup and configuration.
"""
from flask import Flask
from flask_cors import CORS
import logging


def create_app():
    """
    Application factory function.
    
    Creates and configures the Flask application with all necessary
    blueprints, middleware, and extensions.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Configure logging
    from config.logging import setup_logging
    setup_logging()
    
    # Load configuration
    from config import settings
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['DEBUG'] = settings.FLASK_DEBUG
    
    # Setup CORS
    CORS(app, origins=settings.ALLOWED_ORIGINS, supports_credentials=True)
    
    # Initialize database
    from app.core.database import init_db, close_db
    init_db()
    app.teardown_appcontext(close_db)
    
    # Register blueprints (will add as we build them)
    # from app.auth.routes import auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Global error handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Global exception handler for all unhandled errors."""
        from flask import jsonify
        import traceback
        
        logger = logging.getLogger(__name__)
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        
        if app.config['DEBUG']:
            return jsonify({
                'error': str(e),
                'traceback': traceback.format_exc()
            }), 500
        
        return jsonify({'error': 'Internal server error'}), 500
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Simple health check endpoint."""
        return {'status': 'healthy', 'service': 'LyfterCook API'}, 200
    
    logger = logging.getLogger(__name__)
    logger.info("LyfterCook application initialized successfully")
    
    return app

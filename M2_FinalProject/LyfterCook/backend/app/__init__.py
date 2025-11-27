"""
LyfterCook Application Factory
Flask application setup and configuration.
"""
from flask import Flask, request
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
    app.config['JWT_SECRET_KEY'] = settings.JWT_SECRET_KEY
    app.config['DEBUG'] = settings.FLASK_DEBUG
    
    # Setup CORS
    CORS(app, origins=settings.ALLOWED_ORIGINS, supports_credentials=True)
    
    # Request logging middleware
    @app.before_request
    def log_request():
        """Log all incoming requests"""
        logger = logging.getLogger('flask.request')
        logger.info(f"{request.method} {request.path} - {request.remote_addr}")
    
    @app.after_request
    def log_response(response):
        """Log all outgoing responses"""
        logger = logging.getLogger('flask.request')
        logger.info(f"{request.method} {request.path} - Status: {response.status_code}")
        return response
    
    # Initialize database
    from app.core.database import init_db, close_db
    init_db()
    app.teardown_appcontext(close_db)
    
    # Register blueprints
    from app.blueprints import register_blueprints
    register_blueprints(app)
    
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
    
    # Test endpoint for debugging
    @app.route('/test', methods=['GET', 'POST'])
    def test_endpoint():
        """Test endpoint to verify request handling."""
        logger = logging.getLogger(__name__)
        logger.info(f"Test endpoint called: {request.method}")
        return {
            'method': request.method,
            'path': request.path,
            'data_received': bool(request.get_json()) if request.method == 'POST' else None
        }, 200
    
    logger = logging.getLogger(__name__)
    logger.info("LyfterCook application initialized successfully")
    
    return app

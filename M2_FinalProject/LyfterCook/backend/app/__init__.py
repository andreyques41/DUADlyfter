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
    
    # HTTP error handlers (must be before generic Exception handler)
    @app.errorhandler(400)
    def bad_request(e):
        """Handle 400 Bad Request errors."""
        from flask import jsonify
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': str(e.description) if hasattr(e, 'description') else 'Invalid request'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(e):
        """Handle 401 Unauthorized errors."""
        from flask import jsonify
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': str(e.description) if hasattr(e, 'description') else 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(e):
        """Handle 403 Forbidden errors."""
        from flask import jsonify
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': str(e.description) if hasattr(e, 'description') else 'Access denied'
        }), 403
    
    @app.errorhandler(404)
    def not_found(e):
        """Handle 404 Not Found errors."""
        from flask import jsonify
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': str(e.description) if hasattr(e, 'description') else 'Resource not found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        """Handle 405 Method Not Allowed errors."""
        from flask import jsonify
        valid_methods = e.valid_methods if hasattr(e, 'valid_methods') else []
        return jsonify({
            'success': False,
            'error': 'Method Not Allowed',
            'message': f"The method is not allowed for the requested URL. Valid methods: {', '.join(valid_methods) if valid_methods else 'None'}",
            'valid_methods': list(valid_methods) if valid_methods else []
        }), 405
    
    @app.errorhandler(422)
    def unprocessable_entity(e):
        """Handle 422 Unprocessable Entity errors."""
        from flask import jsonify
        return jsonify({
            'success': False,
            'error': 'Unprocessable Entity',
            'message': str(e.description) if hasattr(e, 'description') else 'Validation failed'
        }), 422
    
    # Global error handler for unhandled exceptions
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Global exception handler for all unhandled errors."""
        from flask import jsonify
        from werkzeug.exceptions import HTTPException
        import traceback
        
        logger = logging.getLogger(__name__)
        
        # If it's an HTTP exception, let it pass through with correct status code
        if isinstance(e, HTTPException):
            logger.warning(f"HTTP exception: {e.code} - {str(e)}")
            return jsonify({
                'success': False,
                'error': e.name,
                'message': e.description
            }), e.code
        
        # For all other exceptions, return 500
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        
        if app.config['DEBUG']:
            return jsonify({
                'success': False,
                'error': 'Internal Server Error',
                'message': str(e),
                'traceback': traceback.format_exc()
            }), 500
        
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
    
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

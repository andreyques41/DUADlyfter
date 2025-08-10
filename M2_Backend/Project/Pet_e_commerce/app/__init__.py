from flask import Flask

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    
    # Configure logging once for the entire application
    from config.logging_config import configure_app_logging
    configure_app_logging()
    
    # Register blueprints with URL prefixes
    from app.products import products_bp
    app.register_blueprint(products_bp, url_prefix='/products')
    
    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Add other blueprints as needed
    # from app.sales import sales_bp
    # app.register_blueprint(sales_bp, url_prefix='/sales')
    
    return app

"""
Products Module

Exposes the products blueprint and route registration.
"""

from flask import Blueprint

# Create products blueprint
products_bp = Blueprint('products', __name__)

# Import routes after blueprint creation to avoid circular imports
from app.products.routes.product_routes import register_product_routes

# Register routes with the blueprint
register_product_routes(products_bp)

# Export main components for easy importing
__all__ = [
    'products_bp',
    'product_routes'
]

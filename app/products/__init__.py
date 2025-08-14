"""
Products Module

This module provides comprehensive product management functionality including:
- Product catalog management
- Inventory tracking
- Category and filtering support
- Public product browsing
- Admin product management

The module is organized into:
- Models: Product data structures and business logic
- Services: Product operations and data management
- Schemas: Product validation and serialization
- Routes: RESTful API endpoints for product operations

Blueprint: products_bp - handles all product-related routes
Features:
- Public access for product browsing (e-commerce)
- Admin-only access for product management
- Advanced filtering and search capabilities
"""
from flask import Blueprint

# Create products blueprint
products_bp = Blueprint('products', __name__)

# Import routes after blueprint creation to avoid circular imports
from app.products.routes import product_routes

# Export main components for easy importing
__all__ = [
    'products_bp',
    'product_routes'
]

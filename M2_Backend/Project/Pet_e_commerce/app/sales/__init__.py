"""
Sales Module

This module provides comprehensive e-commerce sales functionality including:
- Shopping cart management
- Order processing and tracking
- Billing and payment tracking
- Returns and refunds processing

The module is organized into:
- Models: Data structures for carts, orders, bills, returns
- Services: Business logic and data operations
- Schemas: Data validation and serialization
- Routes: RESTful API endpoints

Blueprint: sales_bp - handles all sales-related routes
"""
from flask import Blueprint

# Create sales blueprint
sales_bp = Blueprint('sales', __name__)

# Import and register routes after blueprint creation to avoid circular imports
from app.sales.routes.cart_routes import register_cart_routes
from app.sales.routes.order_routes import register_orders_routes
from app.sales.routes.bills_routes import register_bills_routes
from app.sales.routes.returns_routes import register_returns_routes

# Register all routes with the blueprint
register_cart_routes(sales_bp)
register_orders_routes(sales_bp)
register_bills_routes(sales_bp)
register_returns_routes(sales_bp)

# Export main components for easy importing
__all__ = [
    'sales_bp'
]

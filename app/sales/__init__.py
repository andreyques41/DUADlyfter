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

# Import routes after blueprint creation to avoid circular imports
from app.sales.routes import cart_routes, order_routes, bills_routes, returns_routes

# Export main components for easy importing
__all__ = [
    'sales_bp',
    'cart_routes',
    'order_routes', 
    'bills_routes',
    'returns_routes'
]

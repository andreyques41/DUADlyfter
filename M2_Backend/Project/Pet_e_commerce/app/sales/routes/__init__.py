"""
Sales Routes Package

This package contains all RESTful API route definitions for the sales module:
- cart_routes: Shopping cart management endpoints
- order_routes: Order processing and tracking endpoints  
- bills_routes: Billing and payment tracking endpoints
- returns_routes: Returns and refunds processing endpoints

Each route module provides:
- RESTful CRUD operations
- User authentication and authorization
- Input validation using schemas
- Business logic integration through services
- Comprehensive error handling
"""

# Import route modules to register them with the blueprint
from . import cart_routes
from . import order_routes
from . import bills_routes  
from . import returns_routes

__all__ = [
    'cart_routes',
    'order_routes',
    'bills_routes',
    'returns_routes'
]
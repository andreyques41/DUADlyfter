"""
Sales Services Package

This package contains all business logic services for the sales module:
- CartService: Shopping cart management and business logic
- OrdersService: Order processing and lifecycle management
- BillsService: Billing and payment tracking
- ReturnsService: Returns and refunds processing

Each service handles:
- CRUD operations for their respective domain
- Business logic validation
- Data persistence operations
- User access control
"""

from .cart_service import CartService
from .order_service import OrdersService
from .bills_services import BillsService
from .returns_service import ReturnsService

__all__ = [
    'CartService',
    'OrdersService', 
    'BillsService',
    'ReturnsService'
]
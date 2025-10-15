"""
Sales Services Package

This package contains all business logic services for the sales module:
- CartService: Shopping cart management and business logic
- OrderService: Order processing and lifecycle management
- InvoiceService: Invoice and payment tracking
- ReturnService: Returns and refunds processing

Each service handles:
- CRUD operations for their respective domain
- Business logic validation
- Repository-based data access
- User access control
"""

from .cart_service import CartService
from .order_service import OrderService
from .invoice_service import InvoiceService
from .returns_service import ReturnService

__all__ = [
    'CartService',
    'OrderService', 
    'InvoiceService',
    'ReturnService'
]
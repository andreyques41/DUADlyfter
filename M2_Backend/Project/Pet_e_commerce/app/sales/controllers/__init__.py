"""
Sales Controllers Package

HTTP request processing layer for sales operations.

Controllers handle:
- Request validation and deserialization
- HTTP-specific logic and response formatting
- Delegation to service layer for business logic
- Error handling and logging

Exports:
- CartController: Shopping cart operations
- OrderController: Order management (to be added)
- InvoiceController: Invoice operations (to be added)
- ReturnController: Returns and refunds (to be added)

Note: Controllers do not contain business logic - they delegate to services.
"""

from app.sales.controllers.cart_controller import CartController
from app.sales.controllers.order_controller import OrderController
# from app.sales.controllers.invoice_controller import InvoiceController
# from app.sales.controllers.return_controller import ReturnController

__all__ = [
    'CartController',
    'OrderController',
    # 'InvoiceController',
    # 'ReturnController'
]

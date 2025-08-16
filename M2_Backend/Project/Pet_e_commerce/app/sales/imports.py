"""
Sales Domain Imports Module

Centralized imports for the sales domain to reduce import complexity
and provide a single source for all sales-related dependencies.

Usage:
    from app.sales.imports import (
        Cart, CartItem, Order, Bill, Return,
        CartService, OrderService, BillService, ReturnService,
        cart_registration_schema, order_response_schema,
        CARTS_DB_PATH, ORDERS_DB_PATH, BILLS_DB_PATH, RETURNS_DB_PATH
    )
"""

# Models
from app.sales.models.cart import Cart, CartItem
from app.sales.models.order import Order, OrderItem
from app.sales.models.bills import Bill
from app.sales.models.returns import Return

# NOTE: Services are not imported here to avoid circular imports
# Import services directly in route files when needed:
# from app.sales.services.cart_service import CartService
# from app.sales.services.order_service import OrdersService
# from app.sales.services.bills_services import BillsService  
# from app.sales.services.returns_service import ReturnsService

# Schemas
from app.sales.schemas.cart_schema import (
    cart_registration_schema,
    cart_response_schema,
    cart_update_schema,
    carts_response_schema
)
from app.sales.schemas.order_schema import (
    order_registration_schema,
    order_response_schema,
    order_update_schema,
    orders_response_schema,
    order_status_update_schema
)
from app.sales.schemas.bill_schema import (
    bill_registration_schema,
    bill_response_schema,
    bill_update_schema,
    bills_response_schema,
    bill_status_update_schema
)
from app.sales.schemas.returns_schema import (
    return_registration_schema,
    return_response_schema,
    return_update_schema,
    returns_response_schema,
    return_status_update_schema
)

# Database paths
from app.shared.json_db import (
    CARTS_DB_PATH,
    ORDERS_DB_PATH,
    BILLS_DB_PATH,
    RETURNS_DB_PATH
)

# Enums
from app.shared.enums import OrderStatus, BillStatus, ReturnStatus

# Shared utilities
from app.shared.utils.crud_utils import (
    save_models_to_json,
    load_models_from_json,
    load_single_model_by_field,
    generate_next_id
)

# Export all sales-related items
__all__ = [
    # Models
    'Cart', 'CartItem', 'Order', 'OrderItem', 'Bill', 'Return',
    
    # NOTE: Services not exported to avoid circular imports
    # Import them directly: from app.sales.services.cart_service import CartService
    
    # Cart schemas
    'cart_registration_schema', 'cart_response_schema', 'cart_update_schema', 'carts_response_schema',
    
    # Order schemas
    'order_registration_schema', 'order_response_schema', 'order_update_schema', 'orders_response_schema', 'order_status_update_schema',
    
    # Bill schemas
    'bill_registration_schema', 'bill_response_schema', 'bill_update_schema', 'bills_response_schema', 'bill_status_update_schema',
    
    # Return schemas
    'return_registration_schema', 'return_response_schema', 'return_update_schema', 'returns_response_schema', 'return_status_update_schema',
    
    # Database paths
    'CARTS_DB_PATH', 'ORDERS_DB_PATH', 'BILLS_DB_PATH', 'RETURNS_DB_PATH',
    
    # Enums
    'OrderStatus', 'BillStatus', 'ReturnStatus',
    
    # Utilities
    'save_models_to_json', 'load_models_from_json',
    'load_single_model_by_field', 'generate_next_id'
]

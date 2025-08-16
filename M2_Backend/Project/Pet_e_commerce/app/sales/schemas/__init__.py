"""
Sales Schemas Package

This package contains all Marshmallow schemas for sales data validation and serialization:
- cart_schema: Cart and cart item validation/serialization
- order_schema: Order and order item validation/serialization  
- bill_schema: Bill validation/serialization
- returns_schema: Return request validation/serialization

Each schema module provides:
- Input validation for API requests
- Data serialization for API responses
- Business logic integration
- Error handling and validation messages
"""

# Import schema instances for easy access
from .cart_schema import (
    cart_registration_schema,
    cart_response_schema,
    cart_update_schema,
    carts_response_schema,
    CartItemSchema,
    CartRegistrationSchema,
    CartResponseSchema,
    CartUpdateSchema
)

from .order_schema import (
    order_registration_schema,
    order_update_schema,
    order_status_update_schema,
    order_response_schema,
    orders_response_schema,
    OrderItemSchema,
    OrderRegistrationSchema,
    OrderUpdateSchema,
    OrderStatusUpdateSchema,
    OrderResponseSchema
)

from .bill_schema import (
    bill_registration_schema,
    bill_update_schema,
    bill_status_update_schema,
    bill_response_schema,
    bills_response_schema,
    BillRegistrationSchema,
    BillUpdateSchema,
    BillStatusUpdateSchema,
    BillResponseSchema
)

from .returns_schema import (
    return_registration_schema,
    return_update_schema,
    return_status_update_schema,
    return_response_schema,
    returns_response_schema,
    ReturnRegistrationSchema,
    ReturnUpdateSchema,
    ReturnStatusUpdateSchema,
    ReturnResponseSchema
)

__all__ = [
    # Cart schemas
    'cart_registration_schema',
    'cart_response_schema', 
    'cart_update_schema',
    'carts_response_schema',
    'CartItemSchema',
    'CartRegistrationSchema',
    'CartResponseSchema',
    'CartUpdateSchema',
    
    # Order schemas
    'order_registration_schema',
    'order_update_schema',
    'order_status_update_schema', 
    'order_response_schema',
    'orders_response_schema',
    'OrderItemSchema',
    'OrderRegistrationSchema',
    'OrderUpdateSchema',
    'OrderStatusUpdateSchema',
    'OrderResponseSchema',
    
    # Bill schemas
    'bill_registration_schema',
    'bill_update_schema',
    'bill_status_update_schema',
    'bill_response_schema', 
    'bills_response_schema',
    'BillRegistrationSchema',
    'BillUpdateSchema',
    'BillStatusUpdateSchema',
    'BillResponseSchema',
    
    # Return schemas
    'return_registration_schema',
    'return_update_schema',
    'return_status_update_schema',
    'return_response_schema',
    'returns_response_schema',
    'ReturnRegistrationSchema',
    'ReturnUpdateSchema', 
    'ReturnStatusUpdateSchema',
    'ReturnResponseSchema'
]
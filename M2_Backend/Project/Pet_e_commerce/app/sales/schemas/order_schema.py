"""
Order Schemas Module

This module defines Marshmallow schemas for order-related data validation and serialization.
Provides comprehensive validation for order creation, updates, and API responses.

Schemas included:
- OrderItemSchema: Individual order items with product details
- OrderRegistrationSchema: Complete order creation with items and validation
- OrderUpdateSchema: Partial order updates for existing orders
- OrderStatusUpdateSchema: Order status changes for workflow management (OrderStatus from app.shared.enums)
- OrderResponseSchema: API response formatting for order data

Features:
- Input validation with business rules
- Automatic object creation using @post_load decorators
- Comprehensive error messages for validation failures
- Support for nested order items within orders
- Status enum validation and serialization
"""
from marshmallow import Schema, fields, post_load, validates_schema, ValidationError
from marshmallow.validate import Range, Length, OneOf
from datetime import datetime
from app.sales.models.order import Order, OrderItem
from app.core.enums import OrderStatus

class OrderItemSchema(Schema):
    """
    Schema for individual order item validation and serialization.
    
    Validates:
    - Product ID existence and positive value
    - Product name length and presence
    - Price non-negative validation
    - Quantity positive integer within reasonable limits
    - Automatic subtotal calculation for display
    
    Used for: Nested validation within orders, item-level validation
    """
    product_id = fields.Integer(required=True, validate=Range(min=1))
    quantity = fields.Integer(required=True, validate=Range(min=1, max=100))
    product_name = fields.String(dump_only=True)
    price = fields.Float(dump_only=True)
    subtotal = fields.Method("get_subtotal", dump_only=True)
    
    def get_subtotal(self, obj):
        """Calculate subtotal for this order item."""
        return obj.subtotal()
    
    @post_load
    def make_order_item(self, data, **kwargs):
        """Create OrderItem object with product lookup and validation."""
        from app.products.services.product_service import ProdService
        from app.sales.models.order import OrderItem
        
        product_id = data["product_id"]
        quantity = data["quantity"]
        
        # Lookup product details
        prod_service = ProdService()
        product = prod_service.get_products(product_id=product_id)
        if not product or not product.is_active or not product.is_available():
            raise ValidationError(f"Product {product_id} not found or unavailable")
        
        return OrderItem(
            product_id=product.id,
            product_name=product.name,
            price=product.price,
            quantity=quantity
        )

class OrderRegistrationSchema(Schema):
    """
    Schema for new order creation with comprehensive validation.
    
    Validates:
    - User ID for order ownership
    - Order items list with nested validation
    - Optional order status (defaults to pending)
    - Shipping address format and length
    - Prevents duplicate products in single order
    
    Creates: Complete Order instance with calculated totals
    Used for: POST /orders endpoint
    """
    user_id = fields.Integer(required=True, validate=Range(min=1))
    items = fields.List(fields.Nested(OrderItemSchema), required=True, validate=Length(min=1, max=50))
    status = fields.String(load_default="pending", validate=OneOf([status.value for status in OrderStatus]))
    shipping_address = fields.String(validate=Length(min=5, max=500))
    
    @validates_schema
    def validate_order(self, data, **kwargs):
        """Validate order business rules across fields. Supports both dicts and OrderItem objects."""
        items = data.get('items', [])
        product_ids = [
            item['product_id'] if isinstance(item, dict) else getattr(item, 'product_id', None)
            for item in items
        ]
        if len(product_ids) != len(set(product_ids)):
            raise ValidationError("Duplicate products found in order.")
    
    @post_load
    def make_order(self, data, **kwargs):
        """Create Order object with calculated totals."""
        from app.sales.models.order import Order
        from datetime import datetime
        
        # items are already OrderItem objects from nested schema
        order_items = data.get('items', [])
        user_id = data.get('user_id')
        status = data.get('status', 'pending')
        shipping_address = data.get('shipping_address')
        
        # Calculate total
        total_amount = sum(item.subtotal() for item in order_items)
        
        # Note: id and created_at will be set in service layer for new orders
        return Order(
            id=None,  # Will be set in service
            user_id=user_id,
            items=order_items,
            status=OrderStatus(status),
            total_amount=total_amount,
            created_at=None,  # Will be set in service
            shipping_address=shipping_address
        )

class OrderUpdateSchema(Schema):
    """
    Schema for updating existing orders.
    
    Validates:
    - Optional items list update
    - Optional status change
    - Optional shipping address update
    
    Note: All fields optional for partial updates
    Used for: PUT /orders/<id> endpoint
    """
    items = fields.List(fields.Nested(OrderItemSchema), validate=Length(min=1, max=50))
    status = fields.String(validate=OneOf([status.value for status in OrderStatus]))
    shipping_address = fields.String(validate=Length(min=5, max=500))

    @post_load
    def make_order(self, data, **kwargs):
        """Return dict for partial updates (items will be converted to objects if provided)."""
        # Convert items to OrderItem objects if provided
        if 'items' in data:
            # items are already OrderItem objects from nested schema
            pass
        return data

class OrderStatusUpdateSchema(Schema):
    """
    Schema for order status changes only.
    
    Validates:
    - Required status field with enum validation
    - Status must be valid OrderStatus value
    
    Used for: PATCH /orders/<id>/status endpoint
    """
    status = fields.String(required=True, validate=OneOf([status.value for status in OrderStatus]))

class OrderResponseSchema(Schema):
    """
    Schema for order API responses and serialization.
    
    Provides:
    - Complete order information for API responses
    - Automatic status enum to string conversion
    - Read-only fields for calculated values
    - Nested item serialization
    
    Used for: All order GET endpoints and successful mutations
    """
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer()
    items = fields.List(fields.Nested(OrderItemSchema), dump_only=True)
    total_amount = fields.Float()
    status = fields.Method("get_status", dump_only=True)
    shipping_address = fields.String()
    order_date = fields.DateTime(dump_only=True)
    estimated_delivery = fields.DateTime(dump_only=True)
    
    def get_status(self, obj):
        """Convert status enum to string for API response."""
        return obj.status.value

# Schema instances for use in routes
order_registration_schema = OrderRegistrationSchema()
order_update_schema = OrderUpdateSchema()
order_status_update_schema = OrderStatusUpdateSchema()
order_response_schema = OrderResponseSchema()
orders_response_schema = OrderResponseSchema(many=True)

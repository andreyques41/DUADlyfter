"""
Cart Schema Module

This module defines Marshmallow schemas for cart-related data validation and serialization:
- CartItemSchema: Individual cart item validation and serialization
- CartRegistrationSchema: New cart creation with validation
- CartUpdateSchema: Cart update operations
- CartResponseSchema: Cart data serialization for API responses

Features:
- Comprehensive validation for cart items and quantities
- Automatic subtotal calculation for items
- Duplicate product validation
- Business logic integration for cart totals and counts
"""
from marshmallow import Schema, fields, post_load, validates_schema, ValidationError
from marshmallow.validate import Range, Length
from app.sales.models.cart import Cart, CartItem

class CartItemSchema(Schema):
    """
    Schema for individual cart items with validation and serialization.
    
    Validates product information, quantities, and calculates subtotals.
    """
    product_id = fields.Integer(required=True, validate=Range(min=1))
    product_name = fields.String(required=True, validate=Length(min=1, max=100))
    price = fields.Float(required=True, validate=Range(min=0))
    quantity = fields.Integer(required=True, validate=Range(min=1, max=50))
    subtotal = fields.Method("get_subtotal", dump_only=True)
    
    def get_subtotal(self, obj):
        """
        Calculate subtotal for this cart item.
        
        Args:
            obj (CartItem): Cart item instance
            
        Returns:
            float: Subtotal (price * quantity)
        """
        return obj.subtotal()
    
    @post_load
    def make_cart_item(self, data, **kwargs):
        """
        Convert validated data to CartItem instance.
        
        Args:
            data (dict): Validated cart item data
            
        Returns:
            CartItem: Cart item model instance
        """
        return CartItem(**data)

class CartRegistrationSchema(Schema):
    """
    Schema for creating new carts with comprehensive validation.
    
    Validates user ownership, item lists, and prevents duplicate products.
    """
    user_id = fields.Integer(required=True, validate=Range(min=1))
    items = fields.List(fields.Nested(CartItemSchema), required=True, validate=Length(min=1, max=100))
    
    @validates_schema
    def validate_cart(self, data, **kwargs):
        """
        Validate entire cart data including duplicate product checks.
        Supports both dicts and CartItem objects.
        """
        items = data.get('items', [])
        product_ids = [
            item['product_id'] if isinstance(item, dict) else getattr(item, 'product_id', None)
            for item in items
        ]
        if len(product_ids) != len(set(product_ids)):
            raise ValidationError("Duplicate products found in cart.")
    
    @post_load
    def make_cart(self, data, **kwargs):
        """
        Convert validated data to Cart instance.
        
        Args:
            data (dict): Validated cart data
            
        Returns:
            Cart: Cart model instance with ID=0 (to be set by service)
        """
        return Cart(id=0, **data)

class CartResponseSchema(Schema):
    """
    Schema for cart API responses with calculated fields.
    
    Provides cart data with business logic calculations like totals and counts.
    """
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer()
    items = fields.List(fields.Nested(CartItemSchema), dump_only=True)
    total = fields.Method("get_total", dump_only=True)
    item_count = fields.Method("get_item_count", dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    
    def get_total(self, obj):
        """
        Calculate total cart value.
        
        Args:
            obj (Cart): Cart instance
            
        Returns:
            float: Total cart value
        """
        return obj.total()
    
    def get_item_count(self, obj):
        """
        Calculate total item count in cart.
        
        Args:
            obj (Cart): Cart instance
            
        Returns:
            int: Total number of items
        """
        return obj.item_count()

class CartUpdateSchema(Schema):
    """
    Schema for updating existing cart contents.
    
    Validates new item list for cart updates.
    """
    items = fields.List(fields.Nested(CartItemSchema), required=True)

# Schema instances for easy import
cart_registration_schema = CartRegistrationSchema()
cart_response_schema = CartResponseSchema()
cart_update_schema = CartUpdateSchema()
carts_response_schema = CartResponseSchema(many=True)

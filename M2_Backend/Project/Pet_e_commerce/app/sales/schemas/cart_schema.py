"""
Cart Schema Module

This module defines Marshmallow schemas for cart-related data validation and serialization:
- CartItemSchema: Individual cart item validation and serialization
- CartRegistrationSchema: New cart creation with validation
- CartUpdateSchema: Cart update operations
- CartResponseSchema: Cart data serialization for API responses

Features:
- Comprehensive validation for cart items and quantities
- Automatic amount calculation for items
- Duplicate product validation
- Business logic integration for cart totals and counts
"""
from marshmallow import Schema, fields, post_load, validates_schema, ValidationError
from marshmallow.validate import Range, Length
from app.sales.models.cart import Cart, CartItem

class CartItemSchema(Schema):
    """
    Schema for individual cart items with validation and serialization.
    
    Validates product information, quantities, and returns stored amount.
    Note: amount is stored in DB as (price * quantity) and calculated in service layer.
    """
    product_id = fields.Integer(required=True, validate=Range(min=1))
    quantity = fields.Integer(required=True, validate=Range(min=1, max=50))
    product_name = fields.String(dump_only=True)
    price = fields.Float(dump_only=True)
    amount = fields.Float(dump_only=True)  # Read directly from DB field
    
    @post_load
    def make_cart_item(self, data, **kwargs):
        """
        Create CartItem dict with product lookup and validation.
        Returns dict for service layer to create actual CartItem with calculated amount.
        """
        from app.products.services.product_service import ProductService
        
        product_id = data["product_id"]
        quantity = data["quantity"]
        
        # Lookup product details
        prod_service = ProductService()
        product = prod_service.get_product_by_id(product_id)
        if not product or not product.is_active or not product.is_available():
            raise ValidationError(f"Product {product_id} not found or unavailable")
        
        # Return dict with all needed data, service will calculate amount
        return {
            'product_id': product.id,
            'product_name': product.description,  # Product model uses 'description' field
            'price': product.price,
            'quantity': quantity,
            'amount': product.price * quantity  # Calculate amount here
        }

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
        Return validated cart data as dict.
        Items are dicts with calculated amounts from nested schema.
        Service layer will create actual Cart and CartItem ORM objects.
        """
        return {
            'user_id': data.get('user_id'),
            'items': data.get('items', [])  # List of dicts with amount already calculated
        }

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
        if not obj.items:
            return 0.0
        return sum(item.amount for item in obj.items)
    
    def get_item_count(self, obj):
        """
        Calculate total item count in cart.
        
        Args:
            obj (Cart): Cart instance
            
        Returns:
            int: Total number of items
        """
        if not obj.items:
            return 0
        return sum(item.quantity for item in obj.items)

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

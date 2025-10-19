"""
Returns Schemas Module

This module defines Marshmallow schemas for return-related data validation and serialization.
Provides comprehensive validation for return requests, updates, and API responses.

Schemas included:
- ReturnRegistrationSchema: New return request creation with product validation
- ReturnUpdateSchema: Partial return updates for existing requests
- ReturnStatusUpdateSchema: Return status changes for processing workflow
- ReturnResponseSchema: API response formatting with processing timestamps

Features:
- Input validation with business rules
- Product and order reference validation
- Refund amount validation with positive values
- Status validation using ReferenceData against return_status table
- Return reason tracking for customer service

Key Changes:
- Uses ReferenceData for status validation instead of enums
- Validates status names against database return_status table
- Converts return_status_id to status name in API responses
"""
from marshmallow import Schema, fields, post_load, validates, validates_schema, ValidationError
from marshmallow.validate import Range, Length
from datetime import datetime
from app.sales.models.returns import Return, ReturnItem
from app.core.reference_data import ReferenceData

class ReturnItemSchema(Schema):
    """
    Schema for individual return item validation and serialization.
    
    Validates:
    - Product ID existence and positive value
    - Quantity positive integer within reasonable limits  
    - Return reason with appropriate length
    
    Server-side enrichment:
    - Product name fetched from product database
    - Refund amount calculated from product price × quantity (or custom amount)
    """
    product_id = fields.Integer(required=True, validate=Range(min=1))
    quantity = fields.Integer(required=True, validate=Range(min=1, max=100))
    reason = fields.String(required=True, validate=Length(min=1, max=500))
    refund_amount = fields.Float(validate=Range(min=0.01))  # Optional, can derive from product price
    product_name = fields.String(dump_only=True)  # Enriched server-side
    
    @post_load
    def make_return_item(self, data, **kwargs):
        """Create ReturnItem object with product lookup and validation."""
        from app.products.services.product_service import ProductService
        
        product_id = data["product_id"]
        quantity = data["quantity"]
        reason = data["reason"]
        
        # Lookup product details for validation and price calculation
        prod_service = ProductService()
        product = prod_service.get_product_by_id(product_id)
        if not product:
            raise ValidationError(f"Product {product_id} not found")
        
        # Use provided refund amount or calculate from product price
        refund_amount = data.get('refund_amount', product.price * quantity)
        
        return ReturnItem(
            product_id=product.id,
            quantity=quantity,
            reason=reason,
            amount=refund_amount  # Model uses 'amount', not 'refund_amount'
        )

class ReturnRegistrationSchema(Schema):
    """
    Schema for new return request creation with comprehensive validation.
    
    Validates:
    - Order ID for return reference and validation
    - Return items with product lookup and enrichment
    - Optional status (defaults to requested)
    
    Server-side enrichment:
    - User ID derived from authenticated user context
    - Validates order belongs to the user
    - Total refund calculated from enriched items
    """
    order_id = fields.Integer(required=True, validate=Range(min=1))
    items = fields.List(fields.Nested(ReturnItemSchema), required=True, validate=Length(min=1, max=50))
    status = fields.String(load_default="requested")
    
    @validates('status')
    def validate_status(self, value):
        """Validate status against database return_status table."""
        if not ReferenceData.is_valid_return_status(value):
            raise ValidationError(
                f"Invalid return status: {value}. Must be a valid status from return_status table."
            )
    
    @post_load
    def make_return(self, data, **kwargs):
        """Create Return instance with validation and enrichment."""
        from app.sales.services.order_service import OrderService
        from flask import g
        
        order_id = data["order_id"]
        
        # Derive user_id from authenticated user context
        user_id = g.current_user.id if hasattr(g, 'current_user') else data.get('user_id')
        if not user_id:
            raise ValidationError("Unable to determine user context")
        
        # Validate order exists and belongs to user
        order_service = OrderService()
        order = order_service.get_order_by_id(order_id)
        if not order:
            raise ValidationError(f"Order {order_id} not found")
        if order.user_id != user_id:
            raise ValidationError(f"Order {order_id} does not belong to current user")
        
        # Items are already ReturnItem objects from nested schema
        # Calculate total refund from enriched items
        total_refund = sum(item.amount for item in data['items'])  # Use 'amount', not 'refund_amount'
        
        return Return(
            id=None,
            user_id=user_id,
            order_id=order_id,
            items=data['items'],
            status=data.get('status'),  # Will be converted to ID in service layer
            total_refund=total_refund,
            created_at=None  # Will be set in service
        )

class ReturnUpdateSchema(Schema):
    """
    Schema for updating existing return requests.
    
    Allows updating:
    - Return items (with product lookup and enrichment)
    - Status changes (validated against database)
    
    Server-side enrichment:
    - Product details fetched for any new/updated items
    - Total refund recalculated from updated items
    """
    items = fields.List(fields.Nested(ReturnItemSchema), validate=Length(min=1, max=50))
    status = fields.String()
    
    @validates('status')
    def validate_status(self, value):
        """Validate status against database return_status table."""
        if not ReferenceData.is_valid_return_status(value):
            raise ValidationError(
                f"Invalid return status: {value}. Must be a valid status from return_status table."
            )

    @post_load
    def make_return_update(self, data, **kwargs):
        """Create object-like structure for updates with enriched data."""
        class ReturnUpdate:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    if key == 'items' and value:
                        # Items are already ReturnItem objects from nested schema
                        # Recalculate total_refund when items are updated
                        self.total_refund = sum(item.amount for item in value)  # Use 'amount', not 'refund_amount'
                    setattr(self, key, value)
        
        return ReturnUpdate(**data)

class ReturnStatusUpdateSchema(Schema):
    """
    Schema for return status changes only.
    Validates status against database return_status table.
    """
    status = fields.String(required=True)
    
    @validates('status')
    def validate_status(self, value):
        """Validate status against database return_status table."""
        if not ReferenceData.is_valid_return_status(value):
            raise ValidationError(
                f"Invalid return status: {value}. Must be a valid status from return_status table."
            )

class ReturnResponseSchema(Schema):
    """
    Schema for return API responses and serialization.
    Converts return_status_id to user-friendly status name.
    """
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer()
    order_id = fields.Integer()
    items = fields.List(fields.Nested(ReturnItemSchema), dump_only=True)
    status = fields.Method("get_status_name", dump_only=True)
    total_refund = fields.Float(dump_only=True)  # ✅ Read-only: calculated from items
    created_at = fields.DateTime(dump_only=True)
    
    def get_status_name(self, obj):
        """Convert return_status_id to status name for API response."""
        if hasattr(obj, 'return_status_id') and obj.return_status_id:
            return ReferenceData.get_return_status_name(obj.return_status_id)
        return None

# Schema instances for use in routes
return_registration_schema = ReturnRegistrationSchema()
return_update_schema = ReturnUpdateSchema()
return_status_update_schema = ReturnStatusUpdateSchema()
return_response_schema = ReturnResponseSchema()
returns_response_schema = ReturnResponseSchema(many=True)

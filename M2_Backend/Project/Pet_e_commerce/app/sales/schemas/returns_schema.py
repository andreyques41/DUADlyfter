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
- Status enum validation and serialization
- Return reason tracking for customer service
"""
from marshmallow import Schema, fields, post_load, validates_schema, ValidationError
from marshmallow.validate import Range, Length, OneOf
from datetime import datetime, timedelta
from app.sales.models import Return
from app.shared.enums import ReturnStatus

class ReturnRegistrationSchema(Schema):
    """
    Schema for new return request creation with comprehensive validation.
    
    Validates:
    - User ID for return ownership
    - Order ID reference for original purchase
    - Product ID for specific item being returned
    - Quantity within reasonable limits
    - Return reason with appropriate detail
    - Refund amount with positive validation
    - Optional status (defaults to pending)
    
    Creates: Complete Return instance for processing
    Used for: POST /returns endpoint
    """
    user_id = fields.Integer(required=True, validate=Range(min=1))
    order_id = fields.Integer(required=True, validate=Range(min=1))
    product_id = fields.Integer(required=True, validate=Range(min=1))
    quantity = fields.Integer(required=True, validate=Range(min=1, max=100))
    reason = fields.String(required=True, validate=Length(min=1, max=500))
    refund_amount = fields.Float(required=True, validate=Range(min=0.01))
    status = fields.String(load_default="pending", validate=OneOf([status.value for status in ReturnStatus]))
    
    @post_load
    def make_return(self, data, **kwargs):
        """Create Return instance from validated data."""
        if 'status' in data:
            data['status'] = ReturnStatus(data['status'])
        return Return(id=0, **data)

class ReturnUpdateSchema(Schema):
    """
    Schema for updating existing return requests.
    
    Validates:
    - Optional quantity update with limits
    - Optional reason update with length validation
    - Optional refund amount update with positive validation
    - Optional status change for processing workflow
    
    Note: All fields optional for partial updates
    Used for: PUT /returns/<id> endpoint
    """
    quantity = fields.Integer(validate=Range(min=1, max=100))
    reason = fields.String(validate=Length(min=1, max=500))
    refund_amount = fields.Float(validate=Range(min=0.01))
    status = fields.String(validate=OneOf([status.value for status in ReturnStatus]))

class ReturnStatusUpdateSchema(Schema):
    """
    Schema for return status changes only.
    
    Validates:
    - Required status field with enum validation
    - Status must be valid ReturnStatus value
    
    Used for: PATCH /returns/<id>/status endpoint
    """
    status = fields.String(required=True, validate=OneOf([status.value for status in ReturnStatus]))

class ReturnResponseSchema(Schema):
    """
    Schema for return API responses and serialization.
    
    Provides:
    - Complete return information for API responses
    - Automatic status enum to string conversion
    - Processing timestamp tracking
    - Read-only fields for system-generated values
    
    Used for: All return GET endpoints and successful mutations
    """
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer()
    order_id = fields.Integer()
    product_id = fields.Integer()
    quantity = fields.Integer()
    reason = fields.String()
    refund_amount = fields.Float()
    status = fields.Method("get_status", dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    processed_at = fields.DateTime(dump_only=True)
    
    def get_status(self, obj):
        """Convert status enum to string for API response."""
        return obj.status.value

# Schema instances for use in routes
return_registration_schema = ReturnRegistrationSchema()
return_update_schema = ReturnUpdateSchema()
return_status_update_schema = ReturnStatusUpdateSchema()
return_response_schema = ReturnResponseSchema()
returns_response_schema = ReturnResponseSchema(many=True)

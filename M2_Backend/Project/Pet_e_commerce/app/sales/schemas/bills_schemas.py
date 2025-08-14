"""
Bills Schemas Module

This module defines Marshmallow schemas for bill-related data validation and serialization.
Provides comprehensive validation for bill creation, updates, and API responses.

Schemas included:
- BillRegistrationSchema: New bill creation with automatic due date calculation
- BillUpdateSchema: Partial bill updates for existing bills
- BillStatusUpdateSchema: Bill status changes for payment workflow
- BillResponseSchema: API response formatting with calculated fields

Features:
- Input validation with business rules
- Automatic due date calculation (30 days default)
- Status enum validation and serialization
- Overdue status calculation for payment tracking
- Amount validation with minimum positive values
"""
from marshmallow import Schema, fields, post_load, validates_schema, ValidationError
from marshmallow.validate import Range, Length, OneOf
from datetime import datetime, timedelta
from app.sales.models.bills import Bill, BillStatus

class BillRegistrationSchema(Schema):
    """
    Schema for new bill creation with comprehensive validation.
    
    Validates:
    - User ID for bill ownership
    - Amount with minimum positive value
    - Description with appropriate length
    - Optional due date (defaults to 30 days from creation)
    - Optional status (defaults to pending)
    
    Creates: Complete Bill instance with calculated due date
    Used for: POST /bills endpoint
    """
    user_id = fields.Integer(required=True, validate=Range(min=1))
    amount = fields.Float(required=True, validate=Range(min=0.01))
    description = fields.String(required=True, validate=Length(min=1, max=500))
    due_date = fields.DateTime()
    status = fields.String(missing="pending", validate=OneOf([status.value for status in BillStatus]))
    
    @post_load
    def make_bill(self, data, **kwargs):
        """Create Bill instance with automatic due date if not provided."""
        if 'status' in data:
            data['status'] = BillStatus(data['status'])
        if 'due_date' not in data:
            data['due_date'] = datetime.now() + timedelta(days=30)
        return Bill(id=0, **data)

class BillUpdateSchema(Schema):
    """
    Schema for updating existing bills.
    
    Validates:
    - Optional amount update with positive validation
    - Optional description update with length limits
    - Optional due date update
    - Optional status change
    
    Note: All fields optional for partial updates
    Used for: PUT /bills/<id> endpoint
    """
    amount = fields.Float(validate=Range(min=0.01))
    description = fields.String(validate=Length(min=1, max=500))
    due_date = fields.DateTime()
    status = fields.String(validate=OneOf([status.value for status in BillStatus]))

class BillStatusUpdateSchema(Schema):
    """
    Schema for bill status changes only.
    
    Validates:
    - Required status field with enum validation
    - Status must be valid BillStatus value
    
    Used for: PATCH /bills/<id>/status endpoint
    """
    status = fields.String(required=True, validate=OneOf([status.value for status in BillStatus]))

class BillResponseSchema(Schema):
    """
    Schema for bill API responses and serialization.
    
    Provides:
    - Complete bill information for API responses
    - Automatic status enum to string conversion
    - Calculated overdue status for payment tracking
    - Read-only fields for system-generated values
    
    Used for: All bill GET endpoints and successful mutations
    """
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer()
    amount = fields.Float()
    description = fields.String()
    due_date = fields.DateTime()
    status = fields.Method("get_status", dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    is_overdue = fields.Method("get_is_overdue", dump_only=True)
    
    def get_status(self, obj):
        """Convert status enum to string for API response."""
        return obj.status.value
    
    def get_is_overdue(self, obj):
        """Calculate if bill is overdue based on current date."""
        return obj.is_overdue()

# Schema instances for use in routes
bill_registration_schema = BillRegistrationSchema()
bill_update_schema = BillUpdateSchema()
bill_status_update_schema = BillStatusUpdateSchema()
bill_response_schema = BillResponseSchema()
bills_response_schema = BillResponseSchema(many=True)

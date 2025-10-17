"""
Invoice Schemas Module

This module defines Marshmallow schemas for invoice-related data validation and serialization.
Provides comprehensive validation for invoice creation, updates, and API responses.

Schemas included:
- InvoiceRegistrationSchema: New invoice creation with automatic due date calculation
- InvoiceUpdateSchema: Partial invoice updates for existing invoices
- InvoiceStatusUpdateSchema: Invoice status changes for payment workflow
- InvoiceResponseSchema: API response formatting with calculated fields

Features:
- Input validation with business rules
- Automatic due date calculation (30 days default)
- Status validation using ReferenceData (not enums)
- Overdue status calculation for payment tracking
- Amount validation with minimum positive values

Key Changes:
- status: Now uses String with ReferenceData validation instead of Enum
- Converts status names to IDs in service layer
"""
from marshmallow import Schema, fields, post_load, validates, validates_schema, ValidationError
from marshmallow.validate import Range, Length
from datetime import datetime, timedelta
from app.core.reference_data import ReferenceData

class InvoiceRegistrationSchema(Schema):
	"""
	Schema for new invoice creation with comprehensive validation.
    
	Validates:
	- User ID for invoice ownership
	- Amount with minimum positive value
	- Description with appropriate length
	- Optional due date (defaults to 30 days from creation)
	- Optional status (defaults to pending) - validates against DB
    
	Returns: Dict with validated data (service converts status name to ID)
	Used for: POST /invoices endpoint
	"""
	user_id = fields.Integer(required=True, validate=Range(min=1))
	order_id = fields.Integer(required=True, validate=Range(min=1))
	amount = fields.Float(required=True, validate=Range(min=0.01))
	due_date = fields.DateTime()
	status = fields.String(load_default="pending")
	
	@validates('status')
	def validate_status(self, value):
		"""Validate status exists in database reference table."""
		if not ReferenceData.is_valid_invoice_status(value):
			valid_statuses = list(ReferenceData.get_all_invoice_statuses().keys())
			raise ValidationError(
				f"Invalid status '{value}'. Must be one of: {', '.join(valid_statuses)}"
			)
    
	@post_load
	def make_invoice_data(self, data, **kwargs):
		"""Return validated data as dict. Service layer will convert status to ID."""
		if 'due_date' not in data:
			data['due_date'] = datetime.now() + timedelta(days=30)
		return data

class InvoiceUpdateSchema(Schema):
	"""
	Schema for updating existing invoices.
	All fields optional for partial updates.
	"""
	amount = fields.Float(validate=Range(min=0.01))
	due_date = fields.DateTime()
	status = fields.String()
	
	@validates('status')
	def validate_status(self, value):
		"""Validate status exists in database reference table."""
		if not ReferenceData.is_valid_invoice_status(value):
			valid_statuses = list(ReferenceData.get_all_invoice_statuses().keys())
			raise ValidationError(
				f"Invalid status '{value}'. Must be one of: {', '.join(valid_statuses)}"
			)

	@post_load
	def make_update_data(self, data, **kwargs):
		"""Return dict for partial updates. Service will convert status to ID if present."""
		return data

class InvoiceStatusUpdateSchema(Schema):
	"""
	Schema for invoice status changes only.
    
	Validates:
	- Required status field with DB validation
	- Status must exist in invoice_status reference table
    
	Used for: PATCH /invoices/<id>/status endpoint
	"""
	status = fields.String(required=True)
	
	@validates('status')
	def validate_status(self, value):
		"""Validate status exists in database reference table."""
		if not ReferenceData.is_valid_invoice_status(value):
			valid_statuses = list(ReferenceData.get_all_invoice_statuses().keys())
			raise ValidationError(
				f"Invalid status '{value}'. Must be one of: {', '.join(valid_statuses)}"
			)

class InvoiceResponseSchema(Schema):
	"""
	Schema for invoice API responses and serialization.
    
	Provides:
	- Complete invoice information for API responses
	- Automatic status ID to name conversion
	- Calculated overdue status for payment tracking
	- Read-only fields for system-generated values
    
	Used for: All invoice GET endpoints and successful mutations
	"""
	id = fields.Integer(dump_only=True)
	user_id = fields.Integer()
	order_id = fields.Integer()
	amount = fields.Float()
	due_date = fields.DateTime()
	status = fields.Method("get_status_name", dump_only=True)
	created_at = fields.DateTime(dump_only=True)
	is_overdue = fields.Method("get_is_overdue", dump_only=True)
    
	def get_status_name(self, obj):
		"""Convert status ID to user-friendly name."""
		return ReferenceData.get_invoice_status_name(obj.invoice_status_id)
    
	def get_is_overdue(self, obj):
		"""Calculate if invoice is overdue based on current date."""
		return obj.is_overdue()

# Schema instances for use in routes
invoice_registration_schema = InvoiceRegistrationSchema()
invoice_update_schema = InvoiceUpdateSchema()
invoice_status_update_schema = InvoiceStatusUpdateSchema()
invoice_response_schema = InvoiceResponseSchema()
invoices_response_schema = InvoiceResponseSchema(many=True)

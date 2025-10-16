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
- Status enum validation and serialization
- Overdue status calculation for payment tracking
- Amount validation with minimum positive values
"""
from marshmallow import Schema, fields, post_load, validates_schema, ValidationError
from marshmallow.validate import Range, Length, OneOf
from datetime import datetime, timedelta
from app.sales.models.invoice import Invoice
from app.core.enums import InvoiceStatus

class InvoiceRegistrationSchema(Schema):
	"""
	Schema for new invoice creation with comprehensive validation.
    
	Validates:
	- User ID for invoice ownership
	- Amount with minimum positive value
	- Description with appropriate length
	- Optional due date (defaults to 30 days from creation)
	- Optional status (defaults to pending)
    
	Creates: Complete Invoice instance with calculated due date
	Used for: POST /invoices endpoint
	"""
	user_id = fields.Integer(required=True, validate=Range(min=1))
	order_id = fields.Integer(required=True, validate=Range(min=1))
	amount = fields.Float(required=True, validate=Range(min=0.01))
	due_date = fields.DateTime()
	status = fields.String(load_default="pending", validate=OneOf([status.value for status in InvoiceStatus]))
    
	@post_load
	def make_invoice(self, data, **kwargs):
		"""Create Invoice instance with automatic due date if not provided."""
		if 'status' in data:
			data['status'] = InvoiceStatus(data['status'])
		if 'due_date' not in data:
			data['due_date'] = datetime.now() + timedelta(days=30)
		return Invoice(id=None, **data)

class InvoiceUpdateSchema(Schema):
	"""
	Schema for updating existing invoices.
	"""
	amount = fields.Float(validate=Range(min=0.01))
	due_date = fields.DateTime()
	status = fields.String(validate=OneOf([status.value for status in InvoiceStatus]))

	@post_load
	def make_invoice_update(self, data, **kwargs):
		"""Create object-like dict for updates."""
		class InvoiceUpdate:
			def __init__(self, **kwargs):
				for key, value in kwargs.items():
					if key == 'status' and isinstance(value, str):
						value = InvoiceStatus(value)
					setattr(self, key, value)
		
		return InvoiceUpdate(**data)

class InvoiceStatusUpdateSchema(Schema):
	"""
	Schema for invoice status changes only.
    
	Validates:
	- Required status field with enum validation
	- Status must be valid InvoiceStatus value
    
	Used for: PATCH /invoices/<id>/status endpoint
	"""
	status = fields.String(required=True, validate=OneOf([status.value for status in InvoiceStatus]))

class InvoiceResponseSchema(Schema):
	"""
	Schema for invoice API responses and serialization.
    
	Provides:
	- Complete invoice information for API responses
	- Automatic status enum to string conversion
	- Calculated overdue status for payment tracking
	- Read-only fields for system-generated values
    
	Used for: All invoice GET endpoints and successful mutations
	"""
	id = fields.Integer(dump_only=True)
	user_id = fields.Integer()
	order_id = fields.Integer()
	amount = fields.Float()
	due_date = fields.DateTime()
	status = fields.Method("get_status", dump_only=True)
	created_at = fields.DateTime(dump_only=True)
	is_overdue = fields.Method("get_is_overdue", dump_only=True)
    
	def get_status(self, obj):
		"""Convert status enum to string for API response."""
		return obj.status.value
    
	def get_is_overdue(self, obj):
		"""Calculate if invoice is overdue based on current date."""
		return obj.is_overdue()

# Schema instances for use in routes
invoice_registration_schema = InvoiceRegistrationSchema()
invoice_update_schema = InvoiceUpdateSchema()
invoice_status_update_schema = InvoiceStatusUpdateSchema()
invoice_response_schema = InvoiceResponseSchema()
invoices_response_schema = InvoiceResponseSchema(many=True)

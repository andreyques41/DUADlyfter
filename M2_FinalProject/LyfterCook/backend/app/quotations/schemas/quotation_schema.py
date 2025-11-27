"""
Quotation schemas for validation and serialization
"""
from marshmallow import Schema, fields, validate, validates, ValidationError, validates_schema
from datetime import date


class QuotationItemSchema(Schema):
    """Schema for quotation line item"""
    dish_id = fields.Int(required=False, allow_none=True)
    item_name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(required=False, allow_none=True, validate=validate.Length(max=1000))
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    unit_price = fields.Decimal(required=True, as_string=False, validate=validate.Range(min=0))
    
    @validates_schema
    def validate_item(self, data, **kwargs):
        """Validate item has either dish_id or custom name"""
        if not data.get('dish_id') and not data.get('item_name'):
            raise ValidationError('Either dish_id or item_name must be provided')


class QuotationCreateSchema(Schema):
    """Schema for creating a new quotation"""
    client_id = fields.Int(required=False, allow_none=True)
    menu_id = fields.Int(required=False, allow_none=True)
    event_date = fields.Date(required=False, allow_none=True)
    number_of_people = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1))
    notes = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
    terms_and_conditions = fields.Str(required=False, allow_none=True, validate=validate.Length(max=5000))
    items = fields.List(fields.Nested(QuotationItemSchema), required=True, validate=validate.Length(min=1, max=100))
    
    @validates('event_date')
    def validate_event_date(self, value):
        """Validate event date is not in the past"""
        if value and value < date.today():
            raise ValidationError('Event date cannot be in the past')


class QuotationUpdateSchema(Schema):
    """Schema for updating quotation"""
    client_id = fields.Int(required=False, allow_none=True)
    menu_id = fields.Int(required=False, allow_none=True)
    event_date = fields.Date(required=False, allow_none=True)
    number_of_people = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1))
    notes = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
    terms_and_conditions = fields.Str(required=False, allow_none=True, validate=validate.Length(max=5000))
    items = fields.List(fields.Nested(QuotationItemSchema), required=False, validate=validate.Length(min=1, max=100))
    
    @validates('event_date')
    def validate_event_date(self, value):
        """Validate event date is not in the past"""
        if value and value < date.today():
            raise ValidationError('Event date cannot be in the past')


class QuotationStatusUpdateSchema(Schema):
    """Schema for updating quotation status"""
    status = fields.Str(required=True, validate=validate.OneOf(['draft', 'sent', 'accepted', 'rejected', 'expired']))


class QuotationResponseSchema(Schema):
    """Schema for quotation response"""
    id = fields.Int(dump_only=True)
    chef_id = fields.Int(dump_only=True)
    client_id = fields.Int(allow_none=True)
    menu_id = fields.Int(allow_none=True)
    quotation_number = fields.Str(dump_only=True)
    event_date = fields.Date(allow_none=True)
    number_of_people = fields.Int(allow_none=True)
    total_price = fields.Decimal(as_string=False, dump_only=True)
    status = fields.Str()
    notes = fields.Str(allow_none=True)
    terms_and_conditions = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    sent_at = fields.DateTime(dump_only=True, allow_none=True)
    responded_at = fields.DateTime(dump_only=True, allow_none=True)
    items = fields.List(fields.Dict(), dump_only=True)

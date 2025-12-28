"""
Client schemas for validation and serialization
"""
from marshmallow import Schema, fields, validate, validates, ValidationError
import re


class ClientCreateSchema(Schema):
    """Schema for creating a new client"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True, allow_none=False)
    phone = fields.Str(required=True, allow_none=False, validate=validate.Length(min=1, max=20))
    company = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    notes = fields.Str(required=False, allow_none=True, validate=validate.Length(max=1000))

    @validates('phone')
    def validate_phone(self, value):
        """Basic phone validation"""
        if value and not value.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValidationError('Phone number must contain only digits, spaces, +, -, (, )')


class ClientUpdateSchema(Schema):
    """Schema for updating client"""
    name = fields.Str(required=False, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=False, allow_none=True)
    phone = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    company = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    notes = fields.Str(required=False, allow_none=True, validate=validate.Length(max=1000))

    @validates('phone')
    def validate_phone(self, value):
        """Basic phone validation"""
        if value and not value.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValidationError('Phone number must contain only digits, spaces, +, -, (, )')


class ClientResponseSchema(Schema):
    """Schema for client response"""
    id = fields.Int(dump_only=True)
    chef_id = fields.Int(dump_only=True)
    name = fields.Str()
    email = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)
    company = fields.Str(allow_none=True)
    notes = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

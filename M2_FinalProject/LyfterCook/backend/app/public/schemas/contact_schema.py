"""Schemas for public contact form."""

from marshmallow import Schema, fields, validate


class ContactFormSchema(Schema):
    """Schema for public contact form submissions."""

    chef_id = fields.Int(required=True, strict=True)
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    phone = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    message = fields.Str(required=True, validate=validate.Length(min=10, max=2000))

"""
Chef schemas for validation and serialization
"""
from marshmallow import Schema, fields, validate, validates, ValidationError


class ChefCreateSchema(Schema):
    """Schema for creating a new chef profile"""
    bio = fields.Str(required=False, allow_none=True, validate=validate.Length(max=1000))
    specialty = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    phone = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    location = fields.Str(required=False, allow_none=True, validate=validate.Length(max=200))

    @validates('phone')
    def validate_phone(self, value):
        """Basic phone validation"""
        if value and not value.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValidationError('Phone number must contain only digits, spaces, +, -, (, )')


class ChefUpdateSchema(Schema):
    """Schema for updating chef profile"""
    bio = fields.Str(required=False, allow_none=True, validate=validate.Length(max=1000))
    specialty = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    phone = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    location = fields.Str(required=False, allow_none=True, validate=validate.Length(max=200))
    is_active = fields.Bool(required=False)

    @validates('phone')
    def validate_phone(self, value):
        """Basic phone validation"""
        if value and not value.replace('+', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            raise ValidationError('Phone number must contain only digits, spaces, +, -, (, )')


class ChefResponseSchema(Schema):
    """Schema for chef profile response (authenticated user viewing their own profile)"""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    bio = fields.Str(allow_none=True)
    specialty = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)
    location = fields.Str(allow_none=True)
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Nested user info
    user = fields.Nested('UserResponseSchema', only=['id', 'username', 'email'])


class ChefPublicSchema(Schema):
    """Schema for public chef profile (visible to anyone)"""
    id = fields.Int(dump_only=True)
    bio = fields.Str(allow_none=True)
    specialty = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)
    location = fields.Str(allow_none=True)
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    
    # User info for public view (including email for contact)
    user = fields.Nested('UserResponseSchema', only=['id', 'username', 'email'])

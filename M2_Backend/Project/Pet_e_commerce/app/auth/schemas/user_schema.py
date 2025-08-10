from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from app.auth.models import UserRole

class UserRegistrationSchema(Schema):
    """Schema for user registration"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8), load_only=True)
    role = fields.Enum(UserRole, by_value=True, load_default=UserRole.CUSTOMER)
    first_name = fields.Str(validate=validate.Length(max=50), allow_none=True)
    last_name = fields.Str(validate=validate.Length(max=50), allow_none=True)
    phone = fields.Str(validate=validate.Length(max=20), allow_none=True)

class UserLoginSchema(Schema):
    """Schema for user login"""
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class UserUpdateSchema(Schema):
    """Schema for updating user profile"""
    username = fields.Str(validate=validate.Length(min=3, max=50))
    email = fields.Email()
    first_name = fields.Str(validate=validate.Length(max=50), allow_none=True)
    last_name = fields.Str(validate=validate.Length(max=50), allow_none=True)
    phone = fields.Str(validate=validate.Length(max=20), allow_none=True)

class UserResponseSchema(Schema):
    """Schema for user response (excludes password)"""
    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Email()
    role = fields.Enum(UserRole, by_value=True)
    first_name = fields.Str(allow_none=True)
    last_name = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)

class UserPasswordChangeSchema(Schema):
    """Schema for password change"""
    current_password = fields.Str(required=True, load_only=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8), load_only=True)
    confirm_password = fields.Str(required=True, load_only=True)
    
    @validates_schema
    def validate_passwords(self, data, **kwargs):
        errors = {}
        
        # Check if new password matches confirm password
        if data.get('new_password') != data.get('confirm_password'):
            errors['confirm_password'] = ['Passwords do not match']
        
        # Check if new password is different from current password
        if data.get('new_password') == data.get('current_password'):
            errors['new_password'] = ['New password must be different from current password']
        
        if errors:
            raise ValidationError(errors)

# Schema instances for easy import
user_registration_schema = UserRegistrationSchema()
user_login_schema = UserLoginSchema()
user_update_schema = UserUpdateSchema()
user_response_schema = UserResponseSchema()
user_password_change_schema = UserPasswordChangeSchema()
users_response_schema = UserResponseSchema(many=True)

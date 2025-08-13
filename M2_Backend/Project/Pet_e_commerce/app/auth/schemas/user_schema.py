"""
User Schema Module

Provides Marshmallow schemas for user data validation and serialization:
- UserRegistrationSchema: Validates new user registration data
- UserLoginSchema: Validates user login credentials  
- UserUpdateSchema: Validates user profile updates
- UserResponseSchema: Serializes user data for API responses
- UserPasswordChangeSchema: Validates password change requests

Features:
- @post_load decorators for automatic object creation
- Comprehensive validation rules
- Password confirmation for security
- Role-based field handling

Usage:
    # Registration with automatic User object creation
    user_instance = user_registration_schema.load(request_data)
    
    # Profile updates
    update_data = user_update_schema.load(request_data)
"""
from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError, post_load
from app.auth.models import UserRole, User

class UserRegistrationSchema(Schema):
    """Schema for user registration - converts validated data to User instance"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8), load_only=True)
    role = fields.Enum(UserRole, by_value=True, load_default=UserRole.CUSTOMER)
    first_name = fields.Str(validate=validate.Length(max=50), allow_none=True)
    last_name = fields.Str(validate=validate.Length(max=50), allow_none=True)
    phone = fields.Str(validate=validate.Length(max=20), allow_none=True)

    @post_load
    def make_user(self, data, **kwargs):
        """Convert validated data to User instance (without password_hash)
        
        Note: password_hash will be set separately after hashing the password
        """
        # Extract password but don't include it in User creation
        password = data.pop('password', None)
        
        # Create User instance with temporary values for id and password_hash
        # These will be set properly by the service layer
        return User(
            id=0,  # Will be set by service with generate_next_id
            password_hash="",  # Will be set by service after password hashing
            **data
        )

class UserLoginSchema(Schema):
    """Schema for user login"""
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class UserUpdateSchema(Schema):
    """Schema for updating user profile - converts validated data to dictionary"""
    username = fields.Str(validate=validate.Length(min=3, max=50))
    email = fields.Email()
    first_name = fields.Str(validate=validate.Length(max=50), allow_none=True)
    last_name = fields.Str(validate=validate.Length(max=50), allow_none=True)
    phone = fields.Str(validate=validate.Length(max=20), allow_none=True)

    @post_load
    def make_update_data(self, data, **kwargs):
        """Return validated data as dictionary for profile updates"""
        return data

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

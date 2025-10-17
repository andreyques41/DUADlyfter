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
- Role validation using ReferenceData against roles table

Key Changes:
- Uses ReferenceData for role validation instead of enums
- Validates role names against database roles table
- Converts role_id to role name in API responses

Usage:
    # Registration with automatic User object creation
    user_instance = user_registration_schema.load(request_data)
    
    # Profile updates
    update_data = user_update_schema.load(request_data)
"""
from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError, post_load
from app.auth.models import User
from app.core.reference_data import ReferenceData

class UserRegistrationSchema(Schema):
    """Schema for user registration - converts validated data to User instance"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8), load_only=True)
    role = fields.Str(required=False, allow_none=False)  # Changed to String, validates against DB
    first_name = fields.Str(validate=validate.Length(max=50), allow_none=True)
    last_name = fields.Str(validate=validate.Length(max=50), allow_none=True)
    phone = fields.Str(validate=validate.Length(max=20), allow_none=True)
    
    @validates('role')
    def validate_role(self, value, **kwargs):
        """Validate role against database roles table."""
        # If role is not provided, it will default to 'user' in post_load
        if value is None:
            return
        if not ReferenceData.is_valid_role(value):
            raise ValidationError(
                f"Invalid role: {value}. Must be a valid role from roles table."
            )

    @post_load
    def make_user(self, data, **kwargs):
        """Convert validated data to User instance (without password_hash)
        
        Note: password_hash will be set separately after hashing the password
        Role is validated but not included in User model - handled via role assignment
        """
        # Extract password and role (these are handled separately)
        password = data.pop('password', None)
        role_name = data.pop('role', 'user')  # Keep for routes to use
        
        # Create User instance with temporary values for id and password_hash
        # These will be set properly by the service layer
        user = User(
            id=0,  # Will be set by service with generate_next_id
            password_hash="",  # Will be set by service after password hashing
            **data
        )
        
        # Attach role_name to user object for route to access
        user._role_name = role_name
        return user

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
    """Schema for user response (excludes password). Converts role_id to role name."""
    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Email()
    role = fields.Method("get_role_name", dump_only=True)
    first_name = fields.Str(allow_none=True)
    last_name = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)
    
    def get_role_name(self, obj):
        """Convert role_id to role name for API response."""
        if hasattr(obj, 'role_id') and obj.role_id:
            return ReferenceData.get_role_name(obj.role_id)
        return None

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

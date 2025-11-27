"""
User Marshmallow Schemas
Validation and serialization for User model.
"""

from marshmallow import Schema, fields, validate, validates, ValidationError


class UserRegisterSchema(Schema):
    """
    Schema for user registration request.
    
    SECURITY: The 'role' field is accepted for API compatibility
    but is IGNORED by the backend. All public registrations create 'chef' users.
    Admin users must be created via scripts/seed_admin.py or admin endpoints.
    """
    
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=50, error="Username must be between 3 and 50 characters"),
            validate.Regexp(r'^[a-zA-Z0-9_]+$', error="Username can only contain letters, numbers, and underscores")
        ]
    )
    
    email = fields.Email(
        required=True,
        validate=validate.Length(max=120, error="Email must be less than 120 characters")
    )
    
    password = fields.Str(
        required=True,
        load_only=True,  # Never serialize password
        validate=validate.Length(min=8, max=128, error="Password must be between 8 and 128 characters")
    )
    
    role = fields.Str(
        required=False,
        validate=validate.OneOf(['chef', 'admin'], error="Role must be 'chef' or 'admin'"),
        load_default='chef',
        metadata={'description': 'IGNORED - All public registrations create CHEF users. Use seed_admin.py for admin.'}
    )


class UserLoginSchema(Schema):
    """Schema for user login request."""
    
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class UserResponseSchema(Schema):
    """Schema for user response (excludes password)."""
    
    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Email()
    role = fields.Method("get_role")
    is_active = fields.Boolean()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    def get_role(self, obj):
        """Convert UserRole enum to string."""
        return obj.role.value if hasattr(obj.role, 'value') else obj.role


class UserUpdateSchema(Schema):
    """Schema for user profile update."""
    
    username = fields.Str(
        required=False,
        validate=[
            validate.Length(min=3, max=50),
            validate.Regexp(r'^[a-zA-Z0-9_]+$')
        ]
    )
    
    email = fields.Email(
        required=False,
        validate=validate.Length(max=120)
    )
    
    password = fields.Str(
        required=False,
        load_only=True,
        validate=validate.Length(min=8, max=128)
    )

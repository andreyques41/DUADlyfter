"""
Dish schemas for validation and serialization
"""
from marshmallow import Schema, fields, validate, validates, ValidationError


class IngredientSchema(Schema):
    """Schema for ingredient nested in dish"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    quantity = fields.Decimal(required=False, allow_none=True, as_string=True, places=2)
    unit = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    is_optional = fields.Bool(required=False, load_default=False)


class DishCreateSchema(Schema):
    """Schema for creating a new dish"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(required=False, allow_none=True, validate=validate.Length(max=1000))
    price = fields.Decimal(required=False, allow_none=True, as_string=True, places=2)
    category = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    preparation_steps = fields.Str(required=False, allow_none=True, validate=validate.Length(max=5000))
    prep_time = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1, max=1440))  # Max 24 hours
    servings = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1, max=100), load_default=1)
    photo_url = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))
    ingredients = fields.List(fields.Nested(IngredientSchema), required=False, load_default=[])
    
    @validates('price')
    def validate_price(self, value):
        """Validate price is positive"""
        if value is not None and value < 0:
            raise ValidationError('Price must be positive')
    
    @validates('ingredients')
    def validate_ingredients(self, value):
        """Validate ingredients list"""
        if len(value) > 50:
            raise ValidationError('Maximum 50 ingredients allowed per dish')


class DishUpdateSchema(Schema):
    """Schema for updating dish"""
    name = fields.Str(required=False, validate=validate.Length(min=1, max=100))
    description = fields.Str(required=False, allow_none=True, validate=validate.Length(max=1000))
    price = fields.Decimal(required=False, allow_none=True, as_string=True, places=2)
    category = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    preparation_steps = fields.Str(required=False, allow_none=True, validate=validate.Length(max=5000))
    prep_time = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1, max=1440))
    servings = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1, max=100))
    photo_url = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))
    is_active = fields.Bool(required=False)
    ingredients = fields.List(fields.Nested(IngredientSchema), required=False)
    
    @validates('price')
    def validate_price(self, value):
        """Validate price is positive"""
        if value is not None and value < 0:
            raise ValidationError('Price must be positive')
    
    @validates('ingredients')
    def validate_ingredients(self, value):
        """Validate ingredients list"""
        if value is not None and len(value) > 50:
            raise ValidationError('Maximum 50 ingredients allowed per dish')


class DishResponseSchema(Schema):
    """Schema for dish response"""
    id = fields.Int(dump_only=True)
    chef_id = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str(allow_none=True)
    price = fields.Decimal(allow_none=True, as_string=True, places=2)
    category = fields.Str(allow_none=True)
    preparation_steps = fields.Str(allow_none=True)
    prep_time = fields.Int(allow_none=True)
    servings = fields.Int()
    photo_url = fields.Str(allow_none=True)
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    ingredients = fields.List(fields.Nested(IngredientSchema), dump_only=True)

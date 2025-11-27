"""
Menu schemas for validation and serialization
"""
from marshmallow import Schema, fields, validate, validates, ValidationError


class MenuDishSchema(Schema):
    """Schema for dish in menu with order"""
    dish_id = fields.Int(required=True)
    order_position = fields.Int(required=False, missing=0, validate=validate.Range(min=0))


class MenuCreateSchema(Schema):
    """Schema for creating a new menu"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(required=False, allow_none=True, validate=validate.Length(max=1000))
    status = fields.Str(required=False, missing='active', validate=validate.OneOf(['active', 'inactive']))
    dish_ids = fields.List(fields.Int(), required=False, missing=[])  # Simple list of dish IDs
    
    @validates('dish_ids')
    def validate_dish_ids(self, value):
        """Validate dish IDs list"""
        if len(value) > 50:
            raise ValidationError('Maximum 50 dishes allowed per menu')
        if len(value) != len(set(value)):
            raise ValidationError('Duplicate dish IDs not allowed')


class MenuUpdateSchema(Schema):
    """Schema for updating menu"""
    name = fields.Str(required=False, validate=validate.Length(min=1, max=100))
    description = fields.Str(required=False, allow_none=True, validate=validate.Length(max=1000))
    status = fields.Str(required=False, validate=validate.OneOf(['active', 'inactive']))


class MenuAssignDishesSchema(Schema):
    """Schema for assigning dishes to menu with order"""
    dishes = fields.List(fields.Nested(MenuDishSchema), required=True)
    
    @validates('dishes')
    def validate_dishes(self, value):
        """Validate dishes list"""
        if len(value) > 50:
            raise ValidationError('Maximum 50 dishes allowed per menu')
        
        dish_ids = [d['dish_id'] for d in value]
        if len(dish_ids) != len(set(dish_ids)):
            raise ValidationError('Duplicate dish IDs not allowed')


class MenuResponseSchema(Schema):
    """Schema for menu response"""
    id = fields.Int(dump_only=True)
    chef_id = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str(allow_none=True)
    status = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    dishes = fields.List(fields.Dict(), dump_only=True)  # List of {dish_id, order_position, dish: {...}}

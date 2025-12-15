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


class MenuDishDetailSchema(Schema):
    """Dish details in menu context"""
    id = fields.Int()
    name = fields.Str()
    price = fields.Decimal(as_string=True, allow_none=True)
    category = fields.Str(allow_none=True)
    photo_url = fields.Str(allow_none=True)
    is_active = fields.Bool()


class MenuDishResponseSchema(Schema):
    """Schema for dish in menu with position"""
    dish_id = fields.Int()
    order_position = fields.Int()
    dish = fields.Nested(MenuDishDetailSchema)


class MenuResponseSchema(Schema):
    """Schema for menu response"""
    id = fields.Int(dump_only=True)
    chef_id = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str(allow_none=True)
    status = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    dishes = fields.Method("get_dishes")
    dish_count = fields.Method("get_dish_count")
    total_price = fields.Method("get_total_price")
    
    def get_dishes(self, obj):
        """Serialize dishes with structure"""
        if not hasattr(obj, 'menu_dishes'):
            return []
        
        dishes = []
        for menu_dish in obj.menu_dishes:
            if menu_dish.dish:  # Ensure dish exists
                dishes.append({
                    'dish_id': menu_dish.dish_id,
                    'order_position': menu_dish.order_position,
                    'dish': {
                        'id': menu_dish.dish.id,
                        'name': menu_dish.dish.name,
                        'price': str(menu_dish.dish.price) if menu_dish.dish.price else None,
                        'category': menu_dish.dish.category,
                        'photo_url': menu_dish.dish.photo_url,
                        'is_active': menu_dish.dish.is_active
                    }
                })
        return sorted(dishes, key=lambda x: x['order_position'])
    
    def get_dish_count(self, obj):
        """Get total number of dishes"""
        if not hasattr(obj, 'menu_dishes'):
            return 0
        return len(obj.menu_dishes)
    
    def get_total_price(self, obj):
        """Calculate total price of all dishes in menu"""
        if not hasattr(obj, 'menu_dishes'):
            return "0.00"
        
        total = sum(
            menu_dish.dish.price 
            for menu_dish in obj.menu_dishes 
            if menu_dish.dish and menu_dish.dish.price
        )
        return str(total)

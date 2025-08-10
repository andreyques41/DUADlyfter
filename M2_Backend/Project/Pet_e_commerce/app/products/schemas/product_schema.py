from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from app.products.models import *

class ProductRegistrationSchema(Schema):
    """Schema for product registration - includes all fields since only admins can create products"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    price = fields.Float(required=True, validate=validate.Range(min=0))
    category = fields.Enum(ProductCategory, by_value=True, required=True)
    pet_type = fields.Enum(PetType, by_value=True, required=True)
    stock_quantity = fields.Int(required=True, validate=validate.Range(min=0))
    brand = fields.Str(validate=validate.Length(max=50), allow_none=True)
    weight = fields.Float(validate=validate.Range(min=0), allow_none=True)
    image_url = fields.Str(allow_none=True)
    is_active = fields.Bool(load_default=True)
    #[Optional] Admin fields (available since only admins can create products)
    internal_cost = fields.Float(validate=validate.Range(min=0), allow_none=True)
    supplier_info = fields.Str(validate=validate.Length(max=200), allow_none=True)
    created_by = fields.Str(validate=validate.Length(max=50), allow_none=True)
    last_updated = fields.Str(allow_none=True)

class ProductResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str()
    price = fields.Float()
    category = fields.Enum(ProductCategory, by_value=True)
    pet_type = fields.Enum(PetType, by_value=True)
    stock_quantity = fields.Raw()  # Now returns object with status info
    brand = fields.Str(allow_none=True)
    weight = fields.Float(allow_none=True)
    image_url = fields.Str(allow_none=True)
    
    def __init__(self, include_admin_data=False, show_exact_stock=False, *args, **kwargs):
        Schema.__init__(self, *args, **kwargs)
        self.include_admin_data = include_admin_data
        self.show_exact_stock = show_exact_stock
        
        # Conditionally ADD admin field only if needed
        if include_admin_data:
            self.fields['admin_data'] = fields.Method("get_admin_data", dump_only=True)
        
        # Show exact stock for admin or special cases
        if show_exact_stock:
            self.fields['exact_stock_quantity'] = fields.Method("get_exact_stock", dump_only=True)
    
    def get_exact_stock(self, obj):
        """Return exact stock number (for admin or cart validation)"""
        return obj.stock_quantity
    
    def get_admin_data(self, obj):
        """Return admin data - only called when admin field is present"""
        admin_data = {
            "internal_cost": obj.internal_cost,
            "supplier_info": obj.supplier_info,
            "created_by": obj.created_by,
            "last_updated": obj.last_updated,
            "actual_stock_quantity": obj.stock_quantity,  # The real stock number
            "is_active": obj.is_active  # Admin-only field now
        }
        
        # Only add calculated fields if we have the required data
        if obj.internal_cost is not None and obj.price > 0:
            admin_data["profit_margin"] = round(obj.price - obj.internal_cost, 2)
            admin_data["cost_percentage"] = round((obj.internal_cost / obj.price) * 100, 2)
        
        # Add business logic flags
        admin_data["reorder_needed"] = obj.stock_quantity <= 10
        admin_data["low_stock_alert"] = obj.stock_quantity <= 5
        
        return admin_data

# Schema instances for easy import
product_registration_schema = ProductRegistrationSchema()
product_response_schema = ProductResponseSchema()
products_response_schema = ProductResponseSchema(many=True)
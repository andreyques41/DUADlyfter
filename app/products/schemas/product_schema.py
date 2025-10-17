from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError, post_load
from app.core.reference_data import ReferenceData


class ProductRegistrationSchema(Schema):
    """
    Schema for product registration - API receives names, service converts to IDs.
    
    Example input:
    {
        "name": "Premium Dog Food",
        "category": "food",      # String instead of enum
        "pet_type": "dog",       # String instead of enum
        "price": 29.99,
        ...
    }
    """
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    price = fields.Float(required=True, validate=validate.Range(min=0))
    
    # Changed: Now use Str instead of Enum
    category = fields.Str(required=True)
    pet_type = fields.Str(required=True)
    
    stock_quantity = fields.Int(required=True, validate=validate.Range(min=0))
    brand = fields.Str(validate=validate.Length(max=50), allow_none=True)
    weight = fields.Float(validate=validate.Range(min=0), allow_none=True)
    image_url = fields.Str(allow_none=True)
    is_active = fields.Bool(load_default=True)
    
    # Admin fields (available since only admins can create products)
    internal_cost = fields.Float(validate=validate.Range(min=0), allow_none=True)
    supplier_info = fields.Str(validate=validate.Length(max=200), allow_none=True)
    created_by = fields.Str(validate=validate.Length(max=50), allow_none=True)
    last_updated = fields.Str(allow_none=True)
    
    @validates('category')
    def validate_category(self, value):
        """Validate category exists in database reference table."""
        if not ReferenceData.is_valid_product_category(value):
            valid_categories = list(ReferenceData.get_all_product_categories().keys())
            raise ValidationError(
                f"Invalid category '{value}'. Must be one of: {', '.join(valid_categories)}"
            )
    
    @validates('pet_type')
    def validate_pet_type(self, value):
        """Validate pet type exists in database reference table."""
        if not ReferenceData.is_valid_pet_type(value):
            valid_types = list(ReferenceData.get_all_pet_types().keys())
            raise ValidationError(
                f"Invalid pet_type '{value}'. Must be one of: {', '.join(valid_types)}"
            )

    @post_load
    def make_product_data(self, data, **kwargs):
        """
        Return validated data as dict (not Product instance).
        Service layer will handle conversion to IDs and Product creation.
        
        Note: We return dict instead of Product because we need to convert
        category/pet_type strings to IDs first in the service layer.
        """
        # Set default values for optional fields if not provided
        if 'is_active' not in data:
            data['is_active'] = True
        
        return data

class ProductResponseSchema(Schema):
    """
    Schema for product API responses.
    Converts database IDs back to user-friendly names.
    
    Example output:
    {
        "id": 1,
        "name": "Premium Dog Food",
        "category": "food",      # Converted from product_category_id
        "pet_type": "dog",       # Converted from pet_type_id
        "price": 29.99,
        ...
    }
    """
    id = fields.Int(dump_only=True)
    sku = fields.Str(dump_only=True)
    name = fields.Str()
    description = fields.Str()
    price = fields.Float()
    
    # Changed: Use Method fields to convert IDs to names
    category = fields.Method("get_category_name")
    pet_type = fields.Method("get_pet_type_name")
    
    stock_quantity = fields.Raw()  # Returns object with status info
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
    
    def get_category_name(self, obj):
        """Convert category ID to user-friendly name."""
        return ReferenceData.get_product_category_name(obj.product_category_id)
    
    def get_pet_type_name(self, obj):
        """Convert pet type ID to user-friendly name."""
        return ReferenceData.get_pet_type_name(obj.pet_type_id)
    
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
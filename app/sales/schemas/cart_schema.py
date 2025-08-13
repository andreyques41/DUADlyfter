from marshmallow import Schema, fields, post_load, validates, validates_schema, ValidationError
from marshmallow.validate import Range, Length
from app.sales.models.cart import Cart, CartItem

class CartItemSchema(Schema):
    product_id = fields.Integer(required=True, validate=Range(min=1))
    product_name = fields.String(required=True, validate=Length(min=1, max=100))
    price = fields.Float(required=True, validate=Range(min=0))
    quantity = fields.Integer(required=True, validate=Range(min=1, max=50))  # Max 50 per item
    subtotal = fields.Method("get_subtotal", dump_only=True)
    
    def get_subtotal(self, obj):
        """Calculate subtotal for this cart item"""
        return obj.subtotal()
    
    @validates('price')
    def validate_price(self, value):
        """Custom price validation"""
        if value > 10000:  # No single item should cost more than $10,000
            raise ValidationError("Price seems unreasonably high")
    
    @post_load
    def make_cart_item(self, data, **kwargs):
        return CartItem(**data)

class CartRegistrationSchema(Schema):
    """Schema for creating new carts"""
    user_id = fields.Integer(required=True, validate=Range(min=1))
    items = fields.List(fields.Nested(CartItemSchema), required=True, validate=Length(min=1, max=100))
    
    @validates_schema
    def validate_cart(self, data, **kwargs):
        """Validate entire cart"""
        items = data.get('items', [])
        
        # Check for duplicate products
        product_ids = [item.get('product_id') for item in items]
        if len(product_ids) != len(set(product_ids)):
            raise ValidationError("Duplicate products found in cart. Combine quantities instead.")
        
        # Validate total cart value
        total_value = sum(item.get('price', 0) * item.get('quantity', 0) for item in items)
        if total_value > 50000:  # Max cart value $50,000
            raise ValidationError("Cart total exceeds maximum allowed value")
    
    @post_load
    def make_cart(self, data, **kwargs):
        return Cart(id=0, **data)  # ID will be set by database

class CartResponseSchema(Schema):
    """Schema for cart responses with business logic"""
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer()
    items = fields.List(fields.Nested(CartItemSchema), dump_only=True)
    total = fields.Method("get_total", dump_only=True)
    item_count = fields.Method("get_item_count", dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    cart_summary = fields.Method("get_cart_summary", dump_only=True)
    
    def get_total(self, obj):
        """Get cart total"""
        return obj.total()
    
    def get_item_count(self, obj):
        """Get total item count"""
        return obj.item_count()
    
    def get_cart_summary(self, obj):
        """Get cart business logic summary"""
        total = obj.total()
        item_count = obj.item_count()
        
        summary = {
            "total_value": total,
            "total_items": item_count,
            "average_item_price": round(total / item_count, 2) if item_count > 0 else 0,
            "cart_status": self._get_cart_status(total, item_count),
            "recommendations": self._get_recommendations(total, item_count)
        }
        
        # Add shipping info
        summary["shipping"] = self._get_shipping_info(total)
        
        return summary
    
    def _get_cart_status(self, total, item_count):
        """Determine cart status"""
        if total == 0:
            return {"status": "empty", "message": "Your cart is empty"}
        elif total < 25:
            return {"status": "small", "message": "Small order"}
        elif total < 100:
            return {"status": "medium", "message": "Medium order"}
        else:
            return {"status": "large", "message": "Large order"}
    
    def _get_recommendations(self, total, item_count):
        """Get cart recommendations"""
        recommendations = []
        
        if total > 0 and total < 50:
            recommendations.append("Add $%.2f more for free shipping!" % (50 - total))
        
        if item_count < 3:
            recommendations.append("Consider adding more items for better value")
        
        if total > 500:
            recommendations.append("Eligible for bulk discount!")
        
        return recommendations
    
    def _get_shipping_info(self, total):
        """Calculate shipping information"""
        if total >= 50:
            return {
                "cost": 0,
                "method": "Free Standard Shipping",
                "eligible_for_free": True
            }
        else:
            return {
                "cost": 5.99,
                "method": "Standard Shipping",
                "eligible_for_free": False,
                "amount_needed_for_free": round(50 - total, 2)
            }

class CartUpdateSchema(Schema):
    """Schema for updating cart items"""
    items = fields.List(fields.Nested(CartItemSchema), required=True)
    
    @validates_schema
    def validate_update(self, data, **kwargs):
        """Validate cart update"""
        items = data.get('items', [])
        if not items:
            raise ValidationError("Cannot update cart with empty items list")

# Schema instances for easy import
cart_registration_schema = CartRegistrationSchema()
cart_response_schema = CartResponseSchema()
cart_update_schema = CartUpdateSchema()
carts_response_schema = CartResponseSchema(many=True)

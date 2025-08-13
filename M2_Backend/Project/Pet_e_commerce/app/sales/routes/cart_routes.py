"""
Cart Routes Module

Provides RESTful API endpoints for shopping cart management:
- GET /cart/<user_id> - Get user's cart (user access)
- POST /cart/<user_id> - Add item to cart (user access)  
- PUT /cart/<user_id> - Update entire cart (user access)
- DELETE /cart/<user_id> - Clear cart (user access)
- DELETE /cart/<user_id>/items/<product_id> - Remove specific item (user access)

Features:
- User authentication required for all operations
- Users can only access their own carts (or admins can access any)
- Comprehensive cart business logic through service layer
- Input validation using schemas
- Detailed error handling and logging
"""
from flask import request, jsonify, g
from flask.views import MethodView
from marshmallow import ValidationError
from app.sales.services.cart_service import CartService
from app.sales.schemas.cart_schema import (
    cart_registration_schema,
    cart_response_schema, 
    cart_update_schema,
    CartItemSchema
)
from app.auth.services import token_required, admin_required
from app.shared.utils import is_admin_user
from config.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)

DB_PATH = './carts.json'

class CartAPI(MethodView):
    """CRUD operations for shopping carts - user authentication required"""
    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.cart_service = CartService(DB_PATH)

    def _check_user_access(self, user_id):
        """Check if current user can access the specified cart"""
        # Admins can access any cart, regular users only their own
        if is_admin_user():
            return True
        return g.current_user.id == user_id

    @token_required
    def get(self, user_id):
        """Retrieve user's cart - user can only access their own cart, admins can access any"""
        try:
            # Check access permissions
            if not self._check_user_access(user_id):
                return jsonify({"error": "Access denied. You can only view your own cart."}), 403
            
            # Get cart using service
            cart = self.cart_service.get_carts(user_id)
            
            if cart is None:
                return jsonify({
                    "message": "No cart found for this user",
                    "cart": {
                        "user_id": user_id,
                        "items": [],
                        "total": 0,
                        "item_count": 0
                    }
                }), 200
            
            return jsonify(cart_response_schema.dump(cart)), 200
                
        except Exception as e:
            self.logger.error(f"Error retrieving cart for user {user_id}: {e}")
            return jsonify({"error": "Failed to retrieve cart"}), 500

    @token_required  
    def post(self, user_id):
        """Add item to cart - create cart if doesn't exist"""
        try:
            # Check access permissions
            if not self._check_user_access(user_id):
                return jsonify({"error": "Access denied. You can only modify your own cart."}), 403
            
            # Validate request data - expecting single item to add
            item_schema = CartItemSchema()
            item_data = item_schema.load(request.json)
            
            # Add item using service
            updated_cart, error = self.cart_service.add_item_to_cart(user_id, item_data)
            
            if error:
                return jsonify({"error": error}), 400
            
            return jsonify({
                "message": "Item added to cart successfully",
                "cart": cart_response_schema.dump(updated_cart)
            }), 201
            
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error adding item to cart for user {user_id}: {e}")
            return jsonify({"error": "Failed to add item to cart"}), 500

    @token_required
    def put(self, user_id):
        """Update entire cart with new items list"""
        try:
            # Check access permissions
            if not self._check_user_access(user_id):
                return jsonify({"error": "Access denied. You can only modify your own cart."}), 403
            
            # Validate request data using cart update schema
            cart_data = cart_update_schema.load(request.json)
            
            # Create cart instance for update
            from app.sales.models.cart import Cart
            updated_cart = Cart(
                id=0,  # Will be preserved by service
                user_id=user_id,
                items=cart_data['items']
            )
            
            # Update cart using service
            result_cart, error = self.cart_service.update_cart(user_id, updated_cart)
            
            if error:
                if "No cart found" in error:
                    return jsonify({"error": error}), 404
                return jsonify({"error": error}), 400
            
            return jsonify({
                "message": "Cart updated successfully",
                "cart": cart_response_schema.dump(result_cart)
            }), 200
            
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error updating cart for user {user_id}: {e}")
            return jsonify({"error": "Failed to update cart"}), 500

    @token_required
    def delete(self, user_id):
        """Clear entire cart for user"""
        try:
            # Check access permissions
            if not self._check_user_access(user_id):
                return jsonify({"error": "Access denied. You can only modify your own cart."}), 403
            
            # Clear cart using service
            success, error = self.cart_service.clear_cart(user_id)
            
            if error:
                if "No cart found" in error:
                    return jsonify({"error": error}), 404
                return jsonify({"error": error}), 500
            
            return jsonify({"message": "Cart cleared successfully"}), 200
            
        except Exception as e:
            self.logger.error(f"Error clearing cart for user {user_id}: {e}")
            return jsonify({"error": "Failed to clear cart"}), 500

class CartItemAPI(MethodView):
    """Remove individual items from cart"""
    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.cart_service = CartService(DB_PATH)

    def _check_user_access(self, user_id):
        """Check if current user can access the specified cart"""
        # Admins can access any cart, regular users only their own
        if is_admin_user():
            return True
        return g.current_user.id == user_id

    @token_required
    def delete(self, user_id, product_id):
        """Remove specific item from cart"""
        try:
            # Check access permissions
            if not self._check_user_access(user_id):
                return jsonify({"error": "Access denied. You can only modify your own cart."}), 403
            
            # Remove item using service
            updated_cart, error = self.cart_service.remove_item_from_cart(user_id, product_id)
            
            if error:
                if "No cart found" in error or "not found in cart" in error:
                    return jsonify({"error": error}), 404
                return jsonify({"error": error}), 500
            
            return jsonify({
                "message": f"Product {product_id} removed from cart successfully",
                "cart": cart_response_schema.dump(updated_cart)
            }), 200
            
        except Exception as e:
            self.logger.error(f"Error removing item {product_id} from cart for user {user_id}: {e}")
            return jsonify({"error": "Failed to remove item from cart"}), 500

class AdminCartAPI(MethodView):
    """Admin-only cart operations - view all carts"""
    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.cart_service = CartService(DB_PATH)

    @token_required
    @admin_required  
    def get(self):
        """Get all carts - admin only"""
        try:
            all_carts = self.cart_service.get_carts()
            
            # Use schema with many=True for multiple carts
            from app.sales.schemas.cart_schema import carts_response_schema
            return jsonify({
                "total_carts": len(all_carts),
                "carts": carts_response_schema.dump(all_carts)
            }), 200
            
        except Exception as e:
            self.logger.error(f"Error retrieving all carts: {e}")
            return jsonify({"error": "Failed to retrieve carts"}), 500

# Import blueprint from sales module
from app.sales import sales_bp

def register_cart_routes():
    """Register all cart routes with the sales blueprint"""
    # User cart operations
    sales_bp.add_url_rule('/cart/<int:user_id>', view_func=CartAPI.as_view('cart'))
    sales_bp.add_url_rule('/cart/<int:user_id>/items/<int:product_id>', view_func=CartItemAPI.as_view('cart_item'))
    
    # Admin cart operations
    sales_bp.add_url_rule('/admin/carts', view_func=AdminCartAPI.as_view('admin_carts'))

# Call the function to register routes
register_cart_routes()
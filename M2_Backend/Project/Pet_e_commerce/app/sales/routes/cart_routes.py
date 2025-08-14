"""
Cart Routes Module

Provides RESTful API endpoints for shopping cart management:
- GET /cart/<user_id> - Get user's cart (user access)
- POST /cart/<user_id> - Create new cart (user access)
- PUT /cart/<user_id> - Update cart contents (user access)
- DELETE /cart/<user_id> - Clear entire cart (user access)
- DELETE /cart/<user_id>/items/<product_id> - Remove specific item (user access)
- GET /admin/carts - Get all carts (admin only)

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
    cart_update_schema
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
        """Initialize the cart API with service dependency."""
        self.logger = logger
        self.cart_service = CartService(DB_PATH)

    @token_required
    def get(self, user_id):
        """
        Retrieve user's cart - user can only access their own cart, admins can access any.
        
        Args:
            user_id (int): ID of the user whose cart to retrieve
            
        Returns:
            JSON response with cart data or error message
        """
        # USER ACCESS - Users can only view their own cart, admins can view any
        try:
            if not is_admin_user() and g.current_user.id != user_id:
                return jsonify({"error": "Access denied"}), 403
            
            cart = self.cart_service.get_carts(user_id)
            if cart is None:
                return jsonify({
                    "message": "No cart found",
                    "cart": {"user_id": user_id, "items": [], "total": 0, "item_count": 0}
                }), 200
            
            return jsonify(cart_response_schema.dump(cart)), 200
        except Exception as e:
            self.logger.error(f"Error retrieving cart for user {user_id}: {e}")
            return jsonify({"error": "Failed to retrieve cart"}), 500

    @token_required  
    def post(self, user_id):
        """
        Create new cart for user - user can only create their own cart, admins can create any.
        
        Args:
            user_id (int): ID of the user for whom to create cart
            
        Returns:
            JSON response with created cart data or error message
        """
        # USER ACCESS - Users can only create their own cart, admins can create any
        try:
            if not is_admin_user() and g.current_user.id != user_id:
                return jsonify({"error": "Access denied"}), 403
            
            cart_data = cart_registration_schema.load(request.json)
            created_cart, error = self.cart_service.create_cart(cart_data)
            
            if error:
                return jsonify({"error": error}), 400
            
            return jsonify({
                "message": "Cart created successfully",
                "cart": cart_response_schema.dump(created_cart)
            }), 201
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error creating cart for user {user_id}: {e}")
            return jsonify({"error": "Failed to create cart"}), 500

    @token_required
    def put(self, user_id):
        """
        Update cart contents - user can only update their own cart, admins can update any.
        
        Args:
            user_id (int): ID of the user whose cart to update
            
        Returns:
            JSON response with updated cart data or error message
        """
        # USER ACCESS - Users can only update their own cart, admins can update any
        try:
            if not is_admin_user() and g.current_user.id != user_id:
                return jsonify({"error": "Access denied"}), 403
            
            cart_data = cart_update_schema.load(request.json)
            updated_cart, error = self.cart_service.update_cart(user_id, cart_data)
            
            if error:
                return jsonify({"error": error}), 400
            
            return jsonify({
                "message": "Cart updated successfully",
                "cart": cart_response_schema.dump(updated_cart)
            }), 200
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error updating cart for user {user_id}: {e}")
            return jsonify({"error": "Failed to update cart"}), 500

    @token_required
    def delete(self, user_id, product_id=None):
        """
        Clear entire cart or remove specific item - user can only modify their own cart.
        
        Args:
            user_id (int): ID of the user whose cart to modify
            product_id (int, optional): If provided, removes specific product; otherwise clears cart
            
        Returns:
            JSON response with success message or error
        """
        # USER ACCESS - Users can only modify their own cart, admins can modify any
        try:
            if not is_admin_user() and g.current_user.id != user_id:
                return jsonify({"error": "Access denied"}), 403
            
            if product_id:
                success, error = self.cart_service.remove_item_from_cart(user_id, product_id)
                message = "Item removed from cart successfully"
            else:
                success, error = self.cart_service.clear_cart(user_id)
                message = "Cart cleared successfully"
            
            if error:
                return jsonify({"error": error}), 400
            
            return jsonify({"message": message}), 200
        except Exception as e:
            self.logger.error(f"Error modifying cart for user {user_id}: {e}")
            return jsonify({"error": "Failed to update cart"}), 500

class AdminCartAPI(MethodView):
    """Admin-only cart operations - view all carts"""
    
    init_every_request = False

    def __init__(self):
        """Initialize the admin cart API with service dependency."""
        self.logger = logger
        self.cart_service = CartService(DB_PATH)

    @token_required
    @admin_required  
    def get(self):
        """
        Get all carts - admin only access.
        
        Returns:
            JSON response with all carts data or error message
        """
        # ADMIN ONLY - View all carts in system
        try:
            all_carts = self.cart_service.get_carts()
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
    """Register all cart routes with the sales blueprint."""
    # User cart operations
    sales_bp.add_url_rule('/cart/<int:user_id>', view_func=CartAPI.as_view('cart'))
    sales_bp.add_url_rule('/cart/<int:user_id>/items/<int:product_id>', 
                          methods=['DELETE'], view_func=CartAPI.as_view('cart_item'))
    
    # Admin cart operations
    sales_bp.add_url_rule('/admin/carts', view_func=AdminCartAPI.as_view('admin_carts'))

# Call the function to register routes
register_cart_routes()

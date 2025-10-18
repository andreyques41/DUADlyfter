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

# Common imports
from flask import Blueprint, request, jsonify, g
from flask.views import MethodView
from marshmallow import ValidationError
from config.logging import get_logger, EXC_INFO_LOG_ERRORS

# Auth imports (for decorators and utilities)
from app.core.middleware import token_required_with_repo, admin_required_with_repo

# Sales domain imports
from app.sales.schemas.cart_schema import (
    cart_registration_schema, 
    cart_response_schema, 
    cart_update_schema, 
    carts_response_schema
)

# Direct service import to avoid circular imports
from app.sales.services.cart_service import CartService

# Get logger for this module
logger = get_logger(__name__)

class CartAPI(MethodView):
    """CRUD operations for shopping carts - user authentication required"""
    
    init_every_request = False

    def __init__(self):
        """Initialize the cart API with service dependency."""
        self.logger = logger
        self.cart_service = CartService()

    @token_required_with_repo
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
            self.logger.debug(f"CartAPI.get called for user_id={user_id}")
            if not g.is_admin and g.current_user.id != user_id:
                self.logger.warning(f"Access denied for user {g.current_user.id} to cart {user_id}")
                return jsonify({"error": "Access denied"}), 403

            cart = self.cart_service.get_cart_by_user_id(user_id)
            if cart is None:
                self.logger.info(f"No cart found for user {user_id}")
                return jsonify({
                    "message": f"No cart found for user id {user_id}",
                }), 200

            try:
                serialized = cart_response_schema.dump(cart)
            except Exception as ser_e:
                self.logger.error(f"Serialization error for user {user_id}: {ser_e}", exc_info=EXC_INFO_LOG_ERRORS)
                raise
            self.logger.info(f"Cart retrieved for user {user_id}")
            return jsonify(serialized), 200
        except Exception as e:
            self.logger.error(f"Error retrieving cart for user {user_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to retrieve cart"}), 500

    @token_required_with_repo  
    def post(self):
        """
        Create new cart for user - user can only create their own cart, admins can create any.
        
        Args:
            
        Returns:
            JSON response with created cart data or error message
        """
        # USER ACCESS - Users can only create their own cart, admins can create any
        try:

            cart_data = cart_registration_schema.load(request.json)
            user_id = cart_data.get('user_id')

            if not g.is_admin and user_id != g.current_user.id:
                self.logger.warning(f"Access denied for user {g.current_user.id} to create cart {user_id}")
                return jsonify({"error": "Access denied"}), 403

            created_cart = self.cart_service.create_cart(**cart_data)

            if created_cart is None:
                self.logger.error(f"Cart creation failed for user {user_id}")
                return jsonify({"error": "Failed to create cart"}), 400

            try:
                serialized = cart_response_schema.dump(created_cart)
            except Exception as ser_e:
                self.logger.error(f"Serialization error for user {user_id}: {ser_e}", exc_info=EXC_INFO_LOG_ERRORS)
                raise
            self.logger.info(f"Cart created for user {user_id}")
            return jsonify({
                "message": "Cart created successfully",
                "cart": serialized
            }), 201
        except ValidationError as err:
            # user_id may be undefined if validation failed during load
            self.logger.warning(f"Cart creation validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error creating cart: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to create cart"}), 500

    @token_required_with_repo
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
            if not g.is_admin and g.current_user.id != user_id:
                self.logger.warning(f"Access denied for user {g.current_user.id} to update cart {user_id}")
                return jsonify({"error": "Access denied"}), 403

            cart_data = cart_update_schema.load(request.json)
            updated_cart = self.cart_service.update_cart(user_id, **cart_data)

            if updated_cart is None:
                self.logger.error(f"Cart update failed for user {user_id}")
                return jsonify({"error": "Failed to update cart"}), 400

            self.logger.info(f"Cart updated for user {user_id}")
            return jsonify({
                "message": "Cart updated successfully",
                "cart": cart_response_schema.dump(updated_cart)
            }), 200
        except ValidationError as err:
            self.logger.warning(f"Cart update validation error for user {user_id}: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error updating cart for user {user_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to update cart"}), 500

    @token_required_with_repo
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
            if not g.is_admin and g.current_user.id != user_id:
                self.logger.warning(f"Access denied for user {g.current_user.id} to modify cart {user_id}")
                return jsonify({"error": "Access denied"}), 403

            if product_id:
                success = self.cart_service.remove_item_from_cart(user_id, product_id)
                message = "Item removed from cart successfully"
                if success:
                    self.logger.info(f"Item {product_id} removed from cart for user {user_id}")
            else:
                success = self.cart_service.delete_cart(user_id)
                message = "Cart cleared successfully"
                if success:
                    self.logger.info(f"Cart cleared for user {user_id}")

            if not success:
                self.logger.error(f"Cart modification failed for user {user_id}")
                return jsonify({"error": "Failed to modify cart"}), 400

            return jsonify({"message": message}), 200
        except Exception as e:
            self.logger.error(f"Error modifying cart for user {user_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to update cart"}), 500

class CartItemAPI(MethodView):
    """Operations for cart items - add/update/remove items"""
    
    init_every_request = False

    def __init__(self):
        """Initialize cart item API with service dependency."""
        self.logger = logger
        self.cart_service = CartService()

    @token_required_with_repo
    def post(self, user_id, product_id):
        """
        Add item to cart or update quantity if already exists.
        
        Args:
            user_id (int): ID of the user whose cart to modify
            product_id (int): ID of the product to add
            
        Request Body:
            {"quantity": 2}
            
        Returns:
            JSON response with updated cart or error message
        """
        # USER ACCESS - Users can only add to their own cart, admins can add to any
        try:
            if not g.is_admin and g.current_user.id != user_id:
                self.logger.warning(f"Access denied for user {g.current_user.id} to add item to cart {user_id}")
                return jsonify({"error": "Access denied"}), 403

            # Get quantity from request (default: 1)
            data = request.json or {}
            quantity = data.get('quantity', 1)
            
            if not isinstance(quantity, int) or quantity < 1:
                self.logger.warning(f"Invalid quantity: {quantity}")
                return jsonify({"error": "Quantity must be a positive integer"}), 400

            # Add item to cart
            updated_cart = self.cart_service.add_item_to_cart(user_id, product_id, quantity)

            if updated_cart is None:
                self.logger.error(f"Failed to add item {product_id} to cart for user {user_id}")
                return jsonify({"error": "Failed to add item to cart"}), 400

            self.logger.info(f"Item {product_id} added to cart for user {user_id}")
            return jsonify({
                "message": "Item added to cart successfully",
                "cart": cart_response_schema.dump(updated_cart)
            }), 200

        except Exception as e:
            self.logger.error(f"Error adding item to cart: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to add item to cart"}), 500

    @token_required_with_repo
    def put(self, user_id, product_id):
        """
        Update quantity of an existing item in cart.
        
        Args:
            user_id (int): ID of the user whose cart to modify
            product_id (int): ID of the product to update
            
        Request Body:
            {"quantity": 5}
            
        Returns:
            JSON response with updated cart or error message
        """
        # USER ACCESS - Users can only update their own cart, admins can update any
        try:
            if not g.is_admin and g.current_user.id != user_id:
                self.logger.warning(f"Access denied for user {g.current_user.id} to update cart {user_id}")
                return jsonify({"error": "Access denied"}), 403

            # Get quantity from request
            data = request.json or {}
            quantity = data.get('quantity')
            
            if quantity is None or not isinstance(quantity, int) or quantity < 0:
                self.logger.warning(f"Invalid quantity: {quantity}")
                return jsonify({"error": "Quantity must be a non-negative integer"}), 400

            # Update item quantity
            updated_cart = self.cart_service.update_item_quantity(user_id, product_id, quantity)

            if updated_cart is None:
                self.logger.error(f"Failed to update item {product_id} in cart for user {user_id}")
                return jsonify({"error": "Failed to update item quantity"}), 400

            message = "Item removed from cart" if quantity == 0 else "Item quantity updated successfully"
            self.logger.info(f"Item {product_id} quantity updated to {quantity} in cart for user {user_id}")
            return jsonify({
                "message": message,
                "cart": cart_response_schema.dump(updated_cart)
            }), 200

        except Exception as e:
            self.logger.error(f"Error updating item quantity: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to update item quantity"}), 500

    @token_required_with_repo
    def delete(self, user_id, product_id):
        """
        Remove specific item from cart.
        
        Args:
            user_id (int): ID of the user whose cart to modify
            product_id (int): ID of the product to remove
            
        Returns:
            JSON response with success message or error
        """
        # USER ACCESS - Users can only modify their own cart, admins can modify any
        try:
            if not g.is_admin and g.current_user.id != user_id:
                self.logger.warning(f"Access denied for user {g.current_user.id} to modify cart {user_id}")
                return jsonify({"error": "Access denied"}), 403

            success = self.cart_service.remove_item_from_cart(user_id, product_id)

            if not success:
                self.logger.error(f"Failed to remove item {product_id} from cart for user {user_id}")
                return jsonify({"error": "Failed to remove item from cart"}), 400

            self.logger.info(f"Item {product_id} removed from cart for user {user_id}")
            return jsonify({"message": "Item removed from cart successfully"}), 200

        except Exception as e:
            self.logger.error(f"Error removing item: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to remove item"}), 500


class AdminCartAPI(MethodView):
    """Admin-only cart operations - view all carts"""
    
    init_every_request = False

    def __init__(self):
        """Initialize the admin cart API with service dependency."""
        self.logger = logger
        self.cart_service = CartService()

    @admin_required_with_repo  
    def get(self):
        """
        Get all carts - admin only access.
        
        Returns:
            JSON response with all carts data or error message
        """
        # ADMIN ONLY - View all carts in system
        try:
            all_carts = self.cart_service.get_all_carts()
            self.logger.info("All carts retrieved by admin.")
            return jsonify({
                "total_carts": len(all_carts),
                "carts": carts_response_schema.dump(all_carts)
            }), 200
        except Exception as e:
            self.logger.error(f"Error retrieving all carts: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to retrieve carts"}), 500

# Register routes when this module is imported by sales/__init__.py
def register_cart_routes(sales_bp):
    """Register all cart routes with the sales blueprint."""
    # User cart operations
    sales_bp.add_url_rule('/cart', methods=['POST'], view_func=CartAPI.as_view('cart_create'))
    sales_bp.add_url_rule('/cart/<int:user_id>', methods=['GET', 'PUT', 'DELETE'], view_func=CartAPI.as_view('cart'))

    # Cart item operations (add/update/remove items)
    sales_bp.add_url_rule('/cart/<int:user_id>/items/<int:product_id>', 
                          methods=['POST', 'PUT', 'DELETE'], 
                          view_func=CartItemAPI.as_view('cart_item'))

    # Admin cart operations
    sales_bp.add_url_rule('/admin/carts', view_func=AdminCartAPI.as_view('admin_carts'))

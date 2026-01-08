"""
Cart Controller Module

HTTP request processing layer for shopping cart operations.
Delegates to CartService for business logic.

Responsibilities:
- Request validation and deserialization
- HTTP response formatting
- Error handling and logging
- Access control verification
- Cache-aware data retrieval

Dependencies:
- CartService: Business logic and caching
- Flask request/g: Request context
- Marshmallow schemas: Validation
- Auth helpers: Access control

Usage:
    controller = CartController()
    response, status = controller.get(user_id=123)
"""
import logging
from flask import request, jsonify, g
from marshmallow import ValidationError
from typing import Tuple, Optional
from config.logging import get_logger, EXC_INFO_LOG_ERRORS
from app.core.lib.error_utils import error_response

# Service imports
from app.sales.services.cart_service import CartService

# Schema imports
from app.sales.schemas.cart_schema import (
    cart_registration_schema,
    cart_response_schema,
    cart_update_schema,
    carts_response_schema
)

# Auth imports
from app.core.lib.auth import is_admin_user, is_user_or_admin

logger = get_logger(__name__)


class CartController:
    """Controller for shopping cart HTTP operations."""
    
    def __init__(self):
        """Initialize cart controller with service dependency."""
        self.cart_service = CartService()
        self.logger = logger
    
    # ============================================
    # PRIVATE HELPER METHODS
    # ============================================
    
    def _check_cart_access(self, user_id: int) -> Optional[Tuple[dict, int]]:
        """
        Check if current user has access to the specified user's cart.
        Returns error response if access denied, None if access granted.
        
        Args:
            user_id: ID of the user whose cart is being accessed
            
        Returns:
            None if access granted, or (error_response, status_code) if denied
        """
        if not is_user_or_admin(user_id):
            self.logger.warning(f"Access denied for user {g.current_user.id} to cart {user_id}")
            return jsonify({"error": "Access denied"}), 403
        return None
    
    # ============================================
    # CART CRUD OPERATIONS
    # ============================================
    
    def get(self, user_id: Optional[int] = None) -> Tuple[dict, int]:
        """
        Retrieve cart(s):
        - No user_id: Admins see all carts, customers see own cart
        - With user_id: Get specific user's cart (admin or owner)
        
        Args:
            user_id: Optional user ID for specific cart lookup
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Case 1: GET /carts (no user_id) - List carts
            if user_id is None:
                if is_admin_user():
                    # Admin: Return all carts (cached) - already serialized
                    all_carts = self.cart_service.get_all_carts_cached()
                    self.logger.info(f"Admin retrieved all carts (total: {len(all_carts)})")
                    return jsonify({
                        "total_carts": len(all_carts),
                        "carts": all_carts
                    }), 200
                else:
                    # Customer: Return own cart (cached) - already serialized
                    cart = self.cart_service.get_cart_by_user_id_cached(g.current_user.id)
                    if cart is None:
                        self.logger.info(f"No cart found for user {g.current_user.id}")
                        return jsonify({
                            "message": "No cart found for your account"
                        }), 200
                    
                    self.logger.info(f"Cart retrieved for user {g.current_user.id}")
                    return jsonify(cart), 200
            
            # Case 2: GET /carts/<user_id> - Get specific user's cart
            self.logger.debug(f"CartController.get called for user_id={user_id}")
            
            # Check access: admin or owner
            if access_denied := self._check_cart_access(user_id):
                return access_denied
            
            # Get cart (cached) - already serialized
            cart = self.cart_service.get_cart_by_user_id_cached(user_id)
            if cart is None:
                self.logger.info(f"No cart found for user {user_id}")
                return jsonify({
                    "message": f"No cart found for user id {user_id}"
                }), 200
            
            self.logger.info(f"Cart retrieved for user {user_id}")
            return jsonify(cart), 200
            
        except Exception as e:
            self.logger.error(f"Error retrieving cart: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to retrieve cart", e)
    
    def post(self) -> Tuple[dict, int]:
        """
        Create new cart for user.
        Users can create own cart, admins can create any.
        
        Expected JSON:
            {"user_id": 123}
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Validate request data
            cart_data = cart_registration_schema.load(request.json)
            user_id = cart_data.get('user_id')
            
            # Check access: admin or owner
            if access_denied := self._check_cart_access(user_id):
                return access_denied
            
            # Create cart
            created_cart = self.cart_service.create_cart(**cart_data)
            
            if created_cart is None:
                self.logger.error(f"Cart creation failed for user {user_id}")
                return jsonify({"error": "Failed to create cart"}), 400
            
            self.logger.info(f"Cart created for user {user_id}")
            return jsonify({
                "message": "Cart created successfully",
                "cart": cart_response_schema.dump(created_cart)
            }), 201
            
        except ValidationError as err:
            self.logger.warning(f"Cart creation validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error creating cart: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to create cart", e)
    
    def put(self, user_id: int) -> Tuple[dict, int]:
        """
        Update cart contents.
        Users can update own cart, admins can update any.
        
        Args:
            user_id: ID of the user whose cart to update
            
        Expected JSON:
            Cart update fields
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Check access: admin or owner
            if access_denied := self._check_cart_access(user_id):
                return access_denied
            
            # Validate request data
            cart_data = cart_update_schema.load(request.json)
            
            # Update cart
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
            return error_response("Failed to update cart", e)
    
    def delete(self, user_id: int) -> Tuple[dict, int]:
        """
        Clear entire cart.
        Users can clear own cart, admins can clear any.
        
        Args:
            user_id: ID of the user whose cart to clear
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Check access: admin or owner
            if access_denied := self._check_cart_access(user_id):
                return access_denied
            
            # Delete cart
            success = self.cart_service.delete_cart(user_id)
            
            if not success:
                self.logger.error(f"Cart deletion failed for user {user_id}")
                return jsonify({"error": "Failed to clear cart"}), 400
            
            self.logger.info(f"Cart cleared for user {user_id}")
            return jsonify({"message": "Cart cleared successfully"}), 200
            
        except Exception as e:
            self.logger.error(f"Error clearing cart for user {user_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to clear cart", e)
    
    # ============================================
    # CART ITEM OPERATIONS
    # ============================================
    
    def add_item(self, user_id: int, product_id: int) -> Tuple[dict, int]:
        """
        Add item to cart or update quantity if exists.
        Users can add to own cart, admins can add to any.
        
        Args:
            user_id: ID of the user whose cart to modify
            product_id: ID of the product to add
            
        Expected JSON:
            {"quantity": 2}  (optional, default: 1)
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Check access: admin or owner
            if access_denied := self._check_cart_access(user_id):
                return access_denied
            
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
            return error_response("Failed to add item to cart", e)
    
    def update_item(self, user_id: int, product_id: int) -> Tuple[dict, int]:
        """
        Update quantity of existing item in cart.
        Users can update own cart, admins can update any.
        
        Args:
            user_id: ID of the user whose cart to modify
            product_id: ID of the product to update
            
        Expected JSON:
            {"quantity": 5}
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Check access: admin or owner
            if access_denied := self._check_cart_access(user_id):
                return access_denied
            
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
            return error_response("Failed to update item quantity", e)
    
    def remove_item(self, user_id: int, product_id: int) -> Tuple[dict, int]:
        """
        Remove specific item from cart.
        Users can remove from own cart, admins can remove from any.
        
        Args:
            user_id: ID of the user whose cart to modify
            product_id: ID of the product to remove
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Check access: admin or owner
            if access_denied := self._check_cart_access(user_id):
                return access_denied
            
            # Remove item from cart
            success = self.cart_service.remove_item_from_cart(user_id, product_id)
            
            if not success:
                self.logger.error(f"Failed to remove item {product_id} from cart for user {user_id}")
                return jsonify({"error": "Failed to remove item from cart"}), 400
            
            self.logger.info(f"Item {product_id} removed from cart for user {user_id}")
            return jsonify({"message": "Item removed from cart successfully"}), 200
            
        except Exception as e:
            self.logger.error(f"Error removing item: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to remove item", e)

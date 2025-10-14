"""
Cart Service Module

This module provides comprehensive cart management functionality including:
- CRUD operations for shopping carts (Create, Read, Update, Delete)
- Cart item management (add, update, remove items)
- Business logic for cart calculations and validation
- Data persistence and user-specific cart operations

Used by: Cart routes for API operations
Dependencies: Cart models, shared CRUD utilities
"""
from datetime import datetime
from typing import List, Optional, Tuple
import logging
from config.logging import EXC_INFO_LOG_ERRORS
from app.sales.imports import Cart, CartItem, save_models_to_json, load_models_from_json, load_single_model_by_field, generate_next_id, CARTS_DB_PATH

logger = logging.getLogger(__name__)


class CartService:
    """
    Service class for cart management operations.
    Handles all business logic for cart CRUD operations, item management,
    and data persistence. Provides a clean interface for routes.
    """

    def __init__(self, db_path=CARTS_DB_PATH):
        """
        Initialize cart service with database path.
        Args:
            db_path (str): Path to the JSON file for cart data storage
        """
        self.db_path = db_path
        self.logger = logger

    # ========== CART RETRIEVAL ==========
    def get_carts(self, user_id=None):
        """
        Retrieve all carts or a specific cart by user ID.
        Args:
            user_id (int, optional): If provided, returns single user's cart
        Returns:
            list[Cart] or Cart or None: All carts, single cart, or None if not found
        """
        if user_id:
            return load_single_model_by_field(self.db_path, Cart, 'user_id', user_id)
        return load_models_from_json(self.db_path, Cart)

    # ========== CART CREATION ==========
    def create_cart(self, cart_data) -> Tuple[Optional[Cart], Optional[str]]:
        """
        Create a new cart from validated Cart object (from schema).
        """
        try:
            existing_carts = load_models_from_json(self.db_path, Cart)
            user_id = cart_data.user_id

            # Prevent duplicate cart for user
            existing_cart = self.get_carts(user_id)
            if existing_cart:
                self.logger.warning(f"Attempt to create duplicate cart for user {user_id}")
                return None, f"User already has a cart"

            # Set id and created_at for new cart
            cart_data.id = generate_next_id(existing_carts)
            cart_data.created_at = datetime.now()

            existing_carts.append(cart_data)
            save_models_to_json(existing_carts, self.db_path)

            self.logger.info(f"Cart created successfully for user {user_id}")
            return cart_data, None
        except Exception as e:
            error_msg = f"Error creating cart: {e}"
            self.logger.error(error_msg, exc_info=EXC_INFO_LOG_ERRORS)
            return None, error_msg

    # ========== CART UPDATE ==========
    def update_cart(self, user_id: int, cart_data: dict) -> Tuple[Optional[Cart], Optional[str]]:
        """
        Update an existing cart with new item data.
        """
        try:
            existing_cart = self.get_carts(user_id)
            if not existing_cart:
                self.logger.warning(f"Attempt to update non-existent cart for user {user_id}")
                return None, "Cart not found"

            # Update items (already CartItem objects from schema)
            existing_cart.items = cart_data["items"]

            # Save updated cart
            all_carts = load_models_from_json(self.db_path, Cart)
            for i, cart in enumerate(all_carts):
                if cart.user_id == user_id:
                    all_carts[i] = existing_cart
                    break

            save_models_to_json(all_carts, self.db_path)
            self.logger.info(f"Cart updated successfully for user {user_id}")
            return existing_cart, None
        except Exception as e:
            error_msg = f"Error updating cart: {e}"
            self.logger.error(error_msg, exc_info=EXC_INFO_LOG_ERRORS)
            return None, error_msg

    # ========== CART ITEM BUILDING (HELPER) ==========
    # Note: Product lookup and CartItem creation now handled in schema layer

    # ========== CART CLEAR ==========
    def clear_cart(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Clear entire cart for a specific user.
        Args:
            user_id (int): ID of the user whose cart to clear
        Returns:
            tuple: (True, None) on success, (False, error_message) on failure
        """
        try:
            all_carts = load_models_from_json(self.db_path, Cart)
            updated_carts = [cart for cart in all_carts if cart.user_id != user_id]

            if len(updated_carts) == len(all_carts):
                self.logger.warning(f"Attempt to clear non-existent cart for user {user_id}")
                return False, "Cart not found"

            save_models_to_json(updated_carts, self.db_path)
            self.logger.info(f"Cart cleared successfully for user {user_id}")
            return True, None
        except Exception as e:
            error_msg = f"Error clearing cart: {e}"
            self.logger.error(error_msg, exc_info=EXC_INFO_LOG_ERRORS)
            return False, error_msg

    # ========== REMOVE ITEM FROM CART ==========
    def remove_item_from_cart(self, user_id: int, product_id: int) -> Tuple[bool, Optional[str]]:
        """
        Remove a specific item from user's cart.
        Args:
            user_id (int): ID of the user whose cart to modify
            product_id (int): ID of the product to remove from cart
        Returns:
            tuple: (True, None) on success, (False, error_message) on failure
        """
        try:
            cart = self.get_carts(user_id)
            if not cart:
                self.logger.warning(f"Attempt to remove item from non-existent cart for user {user_id}")
                return False, "Cart not found"

            original_count = len(cart.items)
            cart.items = [item for item in cart.items if item.product_id != product_id]

            if len(cart.items) == original_count:
                self.logger.warning(f"Attempt to remove non-existent product {product_id} from cart for user {user_id}")
                return False, "Product not found in cart"

            # Save updated cart
            all_carts = load_models_from_json(self.db_path, Cart)
            for i, c in enumerate(all_carts):
                if c.user_id == user_id:
                    all_carts[i] = cart
                    break

            save_models_to_json(all_carts, self.db_path)
            self.logger.info(f"Item {product_id} removed from cart for user {user_id}")
            return True, None
        except Exception as e:
            error_msg = f"Error removing item: {e}"
            self.logger.error(error_msg, exc_info=EXC_INFO_LOG_ERRORS)
            return False, error_msg

    # ========== USER ACCESS CHECK ==========
    def check_user_access(self, current_user, is_admin, user_id=None):
        """
        Check if current user has access to perform operations on specified user's cart.
        Args:
            current_user: Current authenticated user object
            is_admin (bool): Whether current user has admin privileges
            user_id (int, optional): ID of the user whose cart is being accessed
        Returns:
            bool: True if access is allowed, False otherwise
        """
        if is_admin:
            return True
        if user_id:
            return current_user.id == user_id
        return False

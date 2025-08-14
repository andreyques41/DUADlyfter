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
import json
import os
from datetime import datetime
from typing import List, Optional, Tuple
from app.sales.models.cart import Cart, CartItem
from app.shared.utils import read_json, write_json, save_models_to_json, load_models_from_json, load_single_model_by_field, generate_next_id
import logging

logger = logging.getLogger(__name__)

class CartService:
    """
    Service class for cart management operations.
    
    Handles all business logic for cart CRUD operations, item management,
    and data persistence. Provides a clean interface for routes.
    """
    
    def __init__(self, db_path='./carts.json'):
        """
        Initialize cart service with database path.
        
        Args:
            db_path (str): Path to the JSON file for cart data storage
        """
        self.db_path = db_path
        self.logger = logger

    def get_carts(self, user_id=None):
        """
        Unified method to get all carts or a specific cart by user ID.
        
        Args:
            user_id (int, optional): If provided, returns single user's cart
            
        Returns:
            list[Cart] or Cart or None: All carts, single cart, or None if not found
        """
        if user_id:
            return load_single_model_by_field(self.db_path, Cart, 'user_id', user_id)
        return load_models_from_json(self.db_path, Cart)

    def create_cart(self, cart_instance: Cart) -> Tuple[Optional[Cart], Optional[str]]:
        """
        Create a new cart with Cart instance from schema.
        
        Args:
            cart_instance (Cart): Cart instance from schema with @post_load
            
        Returns:
            tuple: (Cart, None) on success, (None, error_message) on failure
            
        Note:
            Automatically generates unique ID and handles duplicate user validation
        """
        try:
            existing_carts = load_models_from_json(self.db_path, Cart)

            # Check if user already has a cart
            existing_cart = self.get_carts(cart_instance.user_id)
            if existing_cart:
                return None, f"User already has a cart"
            
            cart_instance.id = generate_next_id(existing_carts)
            cart_instance.created_at = datetime.now()
            
            existing_carts.append(cart_instance)
            save_models_to_json(existing_carts, self.db_path)

            self.logger.info(f"Cart created successfully for user {cart_instance.user_id}")
            return cart_instance, None
            
        except Exception as e:
            error_msg = f"Error creating cart: {e}"
            self.logger.error(error_msg)
            return None, error_msg
    
    def update_cart(self, user_id: int, cart_data: dict) -> Tuple[Optional[Cart], Optional[str]]:
        """
        Update an existing cart with new item data.
        
        Args:
            user_id (int): ID of the user whose cart to update
            cart_data (dict): Dictionary containing new cart items data
            
        Returns:
            tuple: (Updated Cart, None) on success, (None, error_message) on failure
        """
        try:
            existing_cart = self.get_carts(user_id)
            if not existing_cart:
                return None, "Cart not found"
            
            # Update cart items
            existing_cart.items = [CartItem(**item) for item in cart_data['items']]
            
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
            self.logger.error(error_msg)
            return None, error_msg

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
                return False, "Cart not found"
            
            save_models_to_json(updated_carts, self.db_path)
            self.logger.info(f"Cart cleared successfully for user {user_id}")
            return True, None
            
        except Exception as e:
            error_msg = f"Error clearing cart: {e}"
            self.logger.error(error_msg)
            return False, error_msg

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
                return False, "Cart not found"
            
            original_count = len(cart.items)
            cart.items = [item for item in cart.items if item.product_id != product_id]
            
            if len(cart.items) == original_count:
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
            self.logger.error(error_msg)
            return False, error_msg

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

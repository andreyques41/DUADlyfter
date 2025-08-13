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
import logging
from app.shared.utils import read_json, write_json, save_models_to_json, load_models_from_json, load_single_model_by_field, generate_next_id

logger = logging.getLogger(__name__)

class CartService:
    """
    Service class for cart management operations.
    
    Handles all business logic for cart CRUD operations, item management,
    and data persistence. Provides a clean interface for routes.
    """
    
    def __init__(self, db_path='./carts.json'):
        """Initialize cart service with database path."""
        self.db_path = db_path
        self.logger = logger

    # ============ CART RETRIEVAL METHODS ============

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

    # ============ CART CRUD OPERATIONS ============

    def create_cart(self, cart_instance: Cart) -> Tuple[Optional[Cart], Optional[str]]:
        """
        Create a new cart with Cart instance from schema.
        
        Args:
            cart_instance (Cart): Cart instance from schema with @post_load
            
        Returns:
            tuple: (Cart, None) on success, (None, error_message) on failure
            
        Note:
            Automatically generates unique ID and handles duplicate items
        """
        try:
            # Load existing carts to generate next ID
            existing_carts = load_models_from_json(self.db_path, Cart)

            # Check if user already has a cart
            existing_cart = self.get_carts(cart_instance.user_id)
            if existing_cart:
                return None, f"User {cart_instance.user_id} already has an active cart"
            
            # Set the ID for the new cart instance
            cart_instance.id = generate_next_id(existing_carts)
            cart_instance.created_at = datetime.now()
            
            # Validate and merge duplicate items
            cart_instance.items = self._merge_duplicate_items(cart_instance.items)
            
            # Save cart to database
            existing_carts.append(cart_instance)
            save_models_to_json(existing_carts, self.db_path)

            self.logger.info(f"Cart created successfully for user {cart_instance.user_id}")
            return cart_instance, None
            
        except Exception as e:
            error_msg = f"Error creating cart: {e}"
            self.logger.error(error_msg)
            return None, error_msg
    
    def update_cart(self, user_id: int, cart_instance: Cart) -> Tuple[Optional[Cart], Optional[str]]:
        """
        Update an existing cart with Cart instance from schema.
        
        Args:
            user_id (int): ID of the user whose cart to update
            cart_instance (Cart): Updated cart instance from schema
            
        Returns:
            tuple: (Cart, None) on success, (None, error_message) on failure
            
        Note:
            Updates the entire cart with new instance data
        """
        try:
            existing_cart = self.get_carts(user_id)
            if not existing_cart:
                return None, f"No cart found for user {user_id}"
            
            # Preserve original cart ID and creation time
            cart_instance.id = existing_cart.id
            cart_instance.created_at = existing_cart.created_at
            
            # Validate and merge duplicate items
            cart_instance.items = self._merge_duplicate_items(cart_instance.items)
            
            # Load all carts, replace the specific one, and save
            all_carts = load_models_from_json(self.db_path, Cart)
            for i, cart in enumerate(all_carts):
                if cart.user_id == user_id:
                    all_carts[i] = cart_instance
                    break
            
            save_models_to_json(all_carts, self.db_path)
            
            self.logger.info(f"Cart updated for user {user_id}")
            return cart_instance, None
            
        except Exception as e:
            error_msg = f"Error updating cart: {e}"
            self.logger.error(error_msg)
            return None, error_msg

    def delete_cart(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete a cart by user ID.
        
        Args:
            user_id (int): ID of the user whose cart to delete
            
        Returns:
            tuple: (True, None) on success, (False, error_message) on failure
            
        Note:
            Permanently removes user's cart from database
        """
        try:
            cart = self.get_carts(user_id)
            if not cart:
                return False, f"No cart found for user {user_id}"
            
            # Remove cart from database
            all_carts = load_models_from_json(self.db_path, Cart)
            all_carts = [c for c in all_carts if c.user_id != user_id]
            save_models_to_json(all_carts, self.db_path)
            
            self.logger.info(f"Cart deleted for user {user_id}")
            return True, None
            
        except Exception as e:
            error_msg = f"Error deleting cart: {e}"
            self.logger.error(error_msg)
            return False, error_msg

    # ============ CART ITEM MANAGEMENT METHODS ============

    def add_item_to_cart(self, user_id: int, new_item: CartItem) -> Tuple[Optional[Cart], Optional[str]]:
        """
        Add an item to user's cart (create cart if doesn't exist).
        
        Args:
            user_id (int): ID of the user
            new_item (CartItem): Item to add to cart
            
        Returns:
            tuple: (Cart, None) on success, (None, error_message) on failure
            
        Note:
            Creates new cart if user doesn't have one
        """
        try:
            existing_cart = self.get_carts(user_id)
            
            if not existing_cart:
                # Create new cart with the item
                new_cart = Cart(
                    id=0,  # Will be set by create_cart
                    user_id=user_id,
                    items=[new_item]
                )
                return self.create_cart(new_cart)
            
            # Add item to existing cart
            existing_cart.items.append(new_item)
            return self.update_cart(user_id, existing_cart)
            
        except Exception as e:
            self.logger.error(f"Error adding item to cart for user {user_id}: {e}")
            return None, f"Failed to add item to cart: {str(e)}"

    def remove_item_from_cart(self, user_id: int, product_id: int) -> Tuple[Optional[Cart], Optional[str]]:
        """
        Remove a specific item from user's cart.
        
        Args:
            user_id (int): ID of the user
            product_id (int): ID of the product to remove
            
        Returns:
            tuple: (Cart, None) on success, (None, error_message) on failure
        """
        try:
            cart = self.get_carts(user_id)
            if not cart:
                return None, f"No cart found for user {user_id}"
            
            # Remove item with matching product_id
            original_count = len(cart.items)
            cart.items = [item for item in cart.items if item.product_id != product_id]
            
            if len(cart.items) == original_count:
                return None, f"Product {product_id} not found in cart"
            
            return self.update_cart(user_id, cart)
            
        except Exception as e:
            self.logger.error(f"Error removing item {product_id} from cart for user {user_id}: {e}")
            return None, f"Failed to remove item: {str(e)}"

    def clear_cart(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Clear/delete user's entire cart.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            tuple: (True, None) on success, (False, error_message) on failure
        """
        return self.delete_cart(user_id)

    # ============ PRIVATE HELPER METHODS ============

    def _merge_duplicate_items(self, items: List[CartItem]) -> List[CartItem]:
        """
        Merge items with same product_id by combining quantities.
        
        Args:
            items (list[CartItem]): List of cart items potentially with duplicates
            
        Returns:
            list[CartItem]: List with merged duplicate items
            
        Note:
            Enforces maximum quantity per item (50) as per business rules
        """
        merged_dict = {}
        
        for item in items:
            if item.product_id in merged_dict:
                # Combine quantities
                existing_item = merged_dict[item.product_id]
                existing_item.quantity += item.quantity
                
                # Validate maximum quantity per item (from schema: max 50)
                if existing_item.quantity > 50:
                    existing_item.quantity = 50
                    self.logger.warning(f"Product {item.product_id} quantity capped at 50")
            else:
                merged_dict[item.product_id] = item
        
        return list(merged_dict.values())

    def validate_cart_limits(self, cart: Cart) -> List[str]:
        """
        Validate cart against business rules.
        
        Args:
            cart (Cart): Cart to validate
            
        Returns:
            list[str]: List of validation error messages, empty if valid
            
        Note:
            Checks cart and item limits as defined in business requirements
        """
        errors = []
        
        # Check total items limit (from schema: max 100 items)
        if len(cart.items) > 100:
            errors.append("Cart cannot contain more than 100 different products")
        
        # Check individual item quantities
        for item in cart.items:
            if item.quantity > 50:
                errors.append(f"Product {item.product_name} quantity cannot exceed 50")
            if item.quantity < 1:
                errors.append(f"Product {item.product_name} must have quantity of at least 1")
            if item.price < 0:
                errors.append(f"Product {item.product_name} cannot have negative price")
        
        return errors

    # ============ PRIVATE HELPER METHODS ============
    # (Service layer uses shared utilities for data persistence)
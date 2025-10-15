"""
Cart Service Module

This module provides comprehensive cart management functionality including:
- CRUD operations for shopping carts (Create, Read, Update, Delete)
- Cart item management (add, update, remove items)
- Business logic for cart calculations and validation
- Uses CartRepository for data access layer

Used by: Cart routes for API operations
Dependencies: Cart models, CartRepository
"""
from datetime import datetime
from typing import List, Optional
import logging
from config.logging import EXC_INFO_LOG_ERRORS
from app.sales.repositories.cart_repository import CartRepository
from app.sales.models.cart import Cart, CartItem

logger = logging.getLogger(__name__)


class CartService:
    """
    Service class for cart management operations.
    Handles all business logic for cart CRUD operations, item management,
    and data validation. Provides a clean interface for routes.
    """

    def __init__(self):
        """Initialize cart service with CartRepository."""
        self.repository = CartRepository()
        self.logger = logger

    # ========== CART RETRIEVAL ==========
    def get_cart_by_id(self, cart_id: int) -> Optional[Cart]:
        """
        Retrieve cart by ID.
        
        Args:
            cart_id: Cart ID to retrieve
            
        Returns:
            Cart object or None if not found
        """
        return self.repository.get_by_id(cart_id)
    
    def get_cart_by_user_id(self, user_id: int) -> Optional[Cart]:
        """
        Retrieve cart by user ID.
        
        Args:
            user_id: User ID to retrieve cart for
            
        Returns:
            Cart object or None if not found
        """
        return self.repository.get_by_user_id(user_id)
    
    def get_all_carts(self) -> List[Cart]:
        """
        Retrieve all carts.
        
        Returns:
            List of all Cart objects
        """
        return self.repository.get_all()

    # ========== CART CREATION ==========
    def create_cart(self, **cart_data) -> Optional[Cart]:
        """
        Create a new cart with validation.
        
        Args:
            **cart_data: Cart fields (user_id, items, finalized, created_at)
            
        Returns:
            Created Cart object or None on error
        """
        try:
            user_id = cart_data.get('user_id')
            
            if not user_id:
                self.logger.error("Cannot create cart without user_id")
                return None
            
            # Prevent duplicate cart for user
            existing_cart = self.repository.get_by_user_id(user_id)
            if existing_cart:
                self.logger.warning(f"Attempt to create duplicate cart for user {user_id}")
                return None
            
            # Set defaults
            cart_data.setdefault('finalized', False)
            cart_data.setdefault('created_at', datetime.utcnow())
            
            # Create Cart instance
            cart = Cart(**cart_data)
            
            # Save to database
            created_cart = self.repository.create(cart)
            
            if created_cart:
                self.logger.info(f"Cart created successfully for user {user_id}")
            else:
                self.logger.error(f"Failed to create cart for user {user_id}")
            
            return created_cart
            
        except Exception as e:
            self.logger.error(f"Error creating cart: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return None

    # ========== CART UPDATE ==========
    def update_cart(self, user_id: int, **updates) -> Optional[Cart]:
        """
        Update an existing cart with new data.
        
        Args:
            user_id: User ID whose cart to update
            **updates: Fields to update (items, finalized, etc.)
            
        Returns:
            Updated Cart object or None on error
        """
        try:
            existing_cart = self.repository.get_by_user_id(user_id)
            if not existing_cart:
                self.logger.warning(f"Attempt to update non-existent cart for user {user_id}")
                return None
            
            # Update fields
            if 'items' in updates:
                existing_cart.items = updates['items']
            
            if 'finalized' in updates:
                existing_cart.finalized = updates['finalized']
            
            # Save updated cart
            updated_cart = self.repository.update(existing_cart)
            
            if updated_cart:
                self.logger.info(f"Cart updated successfully for user {user_id}")
            else:
                self.logger.error(f"Failed to update cart for user {user_id}")
            
            return updated_cart
            
        except Exception as e:
            self.logger.error(f"Error updating cart: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return None

    # ========== CART DELETION (CLEAR) ==========
    def delete_cart(self, user_id: int) -> bool:
        """
        Delete (clear) entire cart for a specific user.
        
        Args:
            user_id: ID of the user whose cart to delete
            
        Returns:
            True on success, False on failure
        """
        try:
            deleted = self.repository.delete_by_user_id(user_id)
            
            if deleted:
                self.logger.info(f"Cart deleted successfully for user {user_id}")
            else:
                self.logger.warning(f"Attempt to delete non-existent cart for user {user_id}")
            
            return deleted
            
        except Exception as e:
            self.logger.error(f"Error deleting cart: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return False

    # ========== REMOVE ITEM FROM CART ==========
    def remove_item_from_cart(self, user_id: int, product_id: int) -> bool:
        """
        Remove a specific item from user's cart.
        
        Args:
            user_id: ID of the user whose cart to modify
            product_id: ID of the product to remove from cart
            
        Returns:
            True on success, False on failure
        """
        try:
            cart = self.repository.get_by_user_id(user_id)
            if not cart:
                self.logger.warning(f"Attempt to remove item from non-existent cart for user {user_id}")
                return False
            
            original_count = len(cart.items)
            cart.items = [item for item in cart.items if item.product_id != product_id]
            
            if len(cart.items) == original_count:
                self.logger.warning(f"Attempt to remove non-existent product {product_id} from cart for user {user_id}")
                return False
            
            # Save updated cart
            updated_cart = self.repository.update(cart)
            
            if updated_cart:
                self.logger.info(f"Item {product_id} removed from cart for user {user_id}")
                return True
            else:
                self.logger.error(f"Failed to update cart after removing item for user {user_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing item: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return False

    # ========== CART FINALIZATION ==========
    def finalize_cart(self, cart_id: int) -> Optional[Cart]:
        """
        Mark a cart as finalized (ready for checkout).
        
        Args:
            cart_id: ID of cart to finalize
            
        Returns:
            Updated Cart object or None on error
        """
        try:
            finalized_cart = self.repository.finalize_cart(cart_id)
            
            if finalized_cart:
                self.logger.info(f"Cart {cart_id} finalized successfully")
            else:
                self.logger.warning(f"Failed to finalize cart {cart_id}")
            
            return finalized_cart
            
        except Exception as e:
            self.logger.error(f"Error finalizing cart: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return None

    # ========== VALIDATION HELPERS ==========
    def cart_exists_for_user(self, user_id: int) -> bool:
        """
        Check if a cart exists for a user.
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if exists, False otherwise
        """
        return self.repository.exists_by_user_id(user_id)
    
    def check_user_access(self, current_user, is_admin: bool, user_id: Optional[int] = None) -> bool:
        """
        Check if current user has access to perform operations on specified user's cart.
        
        Args:
            current_user: Current authenticated user object
            is_admin: Whether current user has admin privileges
            user_id: ID of the user whose cart is being accessed (optional)
            
        Returns:
            True if access is allowed, False otherwise
        """
        if is_admin:
            return True
        if user_id:
            return current_user.id == user_id
        return False

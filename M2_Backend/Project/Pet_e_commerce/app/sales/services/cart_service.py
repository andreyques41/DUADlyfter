"""
Cart Service Module

This module provides comprehensive cart management functionality including:
- CRUD operations for shopping carts (Create, Read, Update, Delete)
- Cart item management (add, update, remove items)
- Business logic for cart calculations and validation
- Caching support for improved performance
- Uses CartRepository for data access layer

Used by: CartController for API operations
Dependencies: Cart models, CartRepository, CacheHelper

Cache Strategy:
- Resource: "cart", Version: "v1"
- Keys: "cart:v1:{user_id}" for single carts, "cart:v1:all" for all carts
- TTL: 300s (5 min - carts change frequently)
- Invalidation: On create, update, delete, and item modifications
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
from config.logging import EXC_INFO_LOG_ERRORS
from app.sales.repositories.cart_repository import CartRepository
from app.sales.models.cart import Cart, CartItem
from app.sales.schemas.cart_schema import cart_response_schema, carts_response_schema
from app.core.middleware.cache_decorators import CacheHelper, cache_invalidate

logger = logging.getLogger(__name__)


class CartService:
    """
    Service class for cart management operations with caching support.
    Handles all business logic for cart CRUD operations, item management,
    and data validation. Provides a clean interface for controllers.
    """

    def __init__(self):
        """Initialize cart service with repository and cache helper."""
        self.repository = CartRepository()
        self.logger = logger
        self.cache = CacheHelper(resource_name="cart", version="v1")

    # ============================================
    # CACHED RETRIEVAL METHODS
    # ============================================
    
    def get_cart_by_user_id_cached(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve cart by user ID with caching.
        Returns Marshmallow-serialized dict for consistent caching.
        
        Args:
            user_id: User ID to retrieve cart for
            
        Returns:
            Serialized cart dict or None if not found
        """
        cache_key = f"{user_id}"
        
        # Try to get from cache
        cached_cart = self.cache.get(cache_key)
        if cached_cart is not None:
            self.logger.debug(f"Cache HIT for cart user_id={user_id}")
            return cached_cart
        
        self.logger.debug(f"Cache MISS for cart user_id={user_id}")
        
        # Get from database
        cart = self.repository.get_by_user_id(user_id)
        if cart is None:
            return None
        
        # Serialize and cache
        serialized_cart = cart_response_schema.dump(cart)
        self.cache.set(cache_key, serialized_cart, ttl=300)  # 5 min TTL
        
        return serialized_cart
    
    def get_all_carts_cached(self) -> List[Dict[str, Any]]:
        """
        Retrieve all carts with caching.
        Returns list of Marshmallow-serialized dicts.
        
        Returns:
            List of serialized cart dicts
        """
        cache_key = "all"
        
        # Try to get from cache
        cached_carts = self.cache.get(cache_key)
        if cached_carts is not None:
            self.logger.debug("Cache HIT for all carts")
            return cached_carts
        
        self.logger.debug("Cache MISS for all carts")
        
        # Get from database
        carts = self.repository.get_all()
        
        # Serialize and cache
        serialized_carts = carts_response_schema.dump(carts)
        self.cache.set(cache_key, serialized_carts, ttl=300)  # 5 min TTL
        
        return serialized_carts

    # ============================================
    # NON-CACHED ORM METHODS (for internal use)
    # ============================================
    
    def get_cart_by_id(self, cart_id: int) -> Optional[Cart]:
        """
        Retrieve cart by ID (non-cached ORM object).
        For internal use only.
        
        Args:
            cart_id: Cart ID to retrieve
            
        Returns:
            Cart object or None if not found
        """
        return self.repository.get_by_id(cart_id)
    
    def get_cart_by_user_id(self, user_id: int) -> Optional[Cart]:
        """
        Retrieve cart by user ID (non-cached ORM object).
        For internal use only.
        
        Args:
            user_id: User ID to retrieve cart for
            
        Returns:
            Cart object or None if not found
        """
        return self.repository.get_by_user_id(user_id)
    
    def get_all_carts(self) -> List[Cart]:
        """
        Retrieve all carts (non-cached ORM objects).
        For internal use only.
        
        Returns:
            List of all Cart objects
        """
        return self.repository.get_all()

    # ============================================
    # CART CRUD OPERATIONS (with cache invalidation)
    # ============================================
    
    @cache_invalidate(resource_name="cart", version="v1", key_suffix="{user_id}", additional_keys=["all"])
    def create_cart(self, force_create=False, **cart_data) -> Optional[Cart]:
        """
        Create a new cart with validation.
        
        Args:
            force_create: If True, skip duplicate check (used when creating cart for new order)
            **cart_data: Cart fields (user_id, items, finalized, created_at)
            
        Returns:
            Created Cart object or None on error
        """
        try:
            user_id = cart_data.get('user_id')
            
            if not user_id:
                self.logger.error("Cannot create cart without user_id")
                return None
            
            # Prevent duplicate cart for user (unless forced)
            if not force_create:
                existing_cart = self.repository.get_by_user_id(user_id)
                if existing_cart:
                    self.logger.warning(f"Attempt to create duplicate cart for user {user_id}")
                    return None
            
            # Extract and convert items from dicts to CartItem objects
            items_data = cart_data.pop('items', [])
            
            # Set defaults
            cart_data.setdefault('finalized', False)
            cart_data.setdefault('created_at', datetime.utcnow())
            
            # Create Cart instance
            cart = Cart(**cart_data)
            
            # Convert item dicts to CartItem objects and append to cart
            for item_data in items_data:
                cart_item = CartItem(
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    amount=item_data['amount']
                )
                cart.items.append(cart_item)
            
            # Save to database
            created_cart = self.repository.create(cart)
            
            if created_cart:
                self.logger.info(f"Cart created successfully for user {user_id} with {len(items_data)} items")
            else:
                self.logger.error(f"Failed to create cart for user {user_id}")
            
            return created_cart
            
        except Exception as e:
            self.logger.error(f"Error creating cart: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return None

    @cache_invalidate(resource_name="cart", version="v1", key_suffix="{user_id}", additional_keys=["all"])
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
            
            # Update items if provided
            if 'items' in updates:
                # Clear existing items
                existing_cart.items.clear()
                
                # Flush to ensure items are deleted before adding new ones
                # This prevents unique constraint violations
                from app.core.database import get_db
                db = get_db()
                db.flush()
                
                # Convert item dicts to CartItem objects and append to cart
                items_data = updates['items']
                for item_data in items_data:
                    cart_item = CartItem(
                        product_id=item_data['product_id'],
                        quantity=item_data['quantity'],
                        amount=item_data['amount']
                    )
                    existing_cart.items.append(cart_item)
                
                self.logger.info(f"Updated cart items for user {user_id}: {len(items_data)} items")
            
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

    @cache_invalidate(resource_name="cart", version="v1", key_suffix="{user_id}", additional_keys=["all"])
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

    @cache_invalidate(resource_name="cart", version="v1", key_suffix="{user_id}", additional_keys=["all"])
    def add_item_to_cart(self, user_id: int, product_id: int, quantity: int = 1) -> Optional[Cart]:
        """
        Add an item to user's cart or update quantity if already exists.
        Automatically fetches current product price.
        
        Args:
            user_id: ID of the user whose cart to modify
            product_id: ID of the product to add
            quantity: Quantity to add (default: 1)
            
        Returns:
            Updated Cart object or None on failure
        """
        try:
            from app.products.services import ProductService
            
            # Get or create cart for user
            cart = self.repository.get_by_user_id(user_id)
            if not cart:
                self.logger.info(f"Creating new cart for user {user_id}")
                cart_data = {'user_id': user_id, 'finalized': False, 'created_at': datetime.utcnow()}
                cart = Cart(**cart_data)
                cart = self.repository.create(cart)
                if not cart:
                    self.logger.error(f"Failed to create cart for user {user_id}")
                    return None
            
            # Check if cart is finalized
            if cart.finalized:
                self.logger.warning(f"Attempt to modify finalized cart for user {user_id}")
                return None
            
            # Get product and validate
            product_service = ProductService()
            product = product_service.get_product_by_id(product_id)
            
            if not product:
                self.logger.warning(f"Product {product_id} not found")
                return None
            
            if not product.is_active:
                self.logger.warning(f"Attempt to add inactive product {product_id}")
                return None
            
            if product.stock_quantity < quantity:
                self.logger.warning(f"Insufficient stock for product {product_id}. Requested: {quantity}, Available: {product.stock_quantity}")
                return None
            
            # Check if item already exists in cart
            from app.sales.models.cart import CartItem
            existing_item = None
            for item in cart.items:
                if item.product_id == product_id:
                    existing_item = item
                    break
            
            if existing_item:
                existing_item.quantity += quantity
                existing_item.amount = product.price * existing_item.quantity
                self.logger.info(f"Updated quantity for product {product_id} in cart for user {user_id}")
            else:
                new_item = CartItem(
                    product_id=product_id,
                    cart_id=cart.id,
                    amount=product.price * quantity,
                    quantity=quantity
                )
                cart.items.append(new_item)
                self.logger.info(f"Added product {product_id} to cart for user {user_id}")
            
            # Save updated cart
            updated_cart = self.repository.update(cart)
            
            if updated_cart:
                self.logger.info(f"Cart updated successfully for user {user_id}")
            else:
                self.logger.error(f"Failed to update cart for user {user_id}")
            
            return updated_cart
            
        except Exception as e:
            self.logger.error(f"Error adding item to cart: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return None

    @cache_invalidate(resource_name="cart", version="v1", key_suffix="{user_id}", additional_keys=["all"])
    def update_item_quantity(self, user_id: int, product_id: int, quantity: int) -> Optional[Cart]:
        """
        Update quantity of an existing item in cart.
        
        Args:
            user_id: ID of the user whose cart to modify
            product_id: ID of the product to update
            quantity: New quantity (must be > 0)
            
        Returns:
            Updated Cart object or None on failure
        """
        try:
            cart = self.repository.get_by_user_id(user_id)
            if not cart:
                self.logger.warning(f"Cart not found for user {user_id}")
                return None
            
            if cart.finalized:
                self.logger.warning(f"Attempt to modify finalized cart for user {user_id}")
                return None
            
            # Find the item
            item_found = False
            for item in cart.items:
                if item.product_id == product_id:
                    item_found = True
                    if quantity <= 0:
                        # Remove item if quantity is 0 or negative
                        cart.items.remove(item)
                        self.logger.info(f"Removed product {product_id} from cart (quantity <= 0)")
                    else:
                        from app.products.services.product_service import ProductService
                        prod_service = ProductService()
                        product = prod_service.get_product_by_id(product_id)
                        if product:
                            item.quantity = quantity
                            item.amount = product.price * quantity
                            self.logger.info(f"Updated quantity to {quantity} for product {product_id}")
                        else:
                            self.logger.error(f"Product {product_id} not found during quantity update")
                            return None
                    break
            
            if not item_found:
                self.logger.warning(f"Product {product_id} not found in cart for user {user_id}")
                return None
            
            # Save updated cart
            updated_cart = self.repository.update(cart)
            
            if updated_cart:
                self.logger.info(f"Cart updated successfully for user {user_id}")
            else:
                self.logger.error(f"Failed to update cart for user {user_id}")
            
            return updated_cart
            
        except Exception as e:
            self.logger.error(f"Error updating item quantity: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return None

    @cache_invalidate(resource_name="cart", version="v1", key_suffix="{user_id}", additional_keys=["all"])
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

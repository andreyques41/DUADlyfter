"""
Order Service Module

This module provides comprehensive order management functionality including:
- CRUD operations for orders (Create, Read, Update, Delete)
- Order status management and validation
- Business logic for order calculations and validation
- Uses OrderRepository for data access layer
- Cache support with CacheHelper for performance optimization

Key Changes:
- Converts status names to IDs before database operations
- Validates status using ReferenceData instead of enums
- Added caching for order retrieval operations (TTL: 600s / 10 min)
- Cache invalidation on mutations (create, update, delete, status change)

Used by: Order routes for API operations
Dependencies: Order models, OrderRepository, ReferenceData, CacheHelper
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
from config.logging import EXC_INFO_LOG_ERRORS
from app.sales.repositories.order_repository import OrderRepository
from app.sales.models.order import Order, OrderItem
from app.core.reference_data import ReferenceData
from app.core.middleware.cache_decorators import CacheHelper, cache_invalidate
from app.sales.schemas.order_schema import (
    order_response_schema, 
    orders_response_schema,
    OrderResponseSchema
)

logger = logging.getLogger(__name__)


class OrderService:
    """
    Service class for order management operations.
    Handles all business logic for order CRUD operations, status management,
    and data validation. Provides a clean interface for routes.
    
    Cache Strategy:
    - TTL: 600s (10 min - orders less volatile than carts)
    - Keys: order:v1:{id}, order:v1:user:{user_id}:all, order:v1:all
    - Invalidation: On create, update, delete, status change
    """

    def __init__(self):
        """Initialize order service with repository and cache helper."""
        self.repository = OrderRepository()
        self.logger = logger
        self.cache_helper = CacheHelper(resource_name="order", version="v1")

    # ============ ORDER RETRIEVAL METHODS ============
    
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """
        Retrieve order by ID.
        
        Args:
            order_id: Order ID to retrieve
            
        Returns:
            Order object or None if not found
        """
        return self.repository.get_by_id(order_id)
    
    def get_orders_by_user_id(self, user_id: int) -> List[Order]:
        """
        Retrieve all orders for a specific user.
        
        Args:
            user_id: User ID to retrieve orders for
            
        Returns:
            List of Order objects
        """
        return self.repository.get_by_user_id(user_id)
        
    def get_order_by_cart_id(self, cart_id: int) -> Optional[Order]:
        """
        Retrieve order by cart ID.
        
        Args:
            cart_id: Cart ID to retrieve order for
            
        Returns:
            Order object or None if not found
        """
        return self.repository.get_by_cart_id(cart_id)
    
    def get_all_orders(self) -> List[Order]:
        """
        Retrieve all orders.
        
        Returns:
            List of all Order objects
        """
        return self.repository.get_all()
    
    def get_orders_by_filters(self, filters: Dict[str, Any]) -> List[Order]:
        """
        Retrieve orders by filters.
        
        Args:
            filters: Dictionary with filter criteria
            
        Returns:
            List of filtered Order objects
        """
        return self.repository.get_by_filters(filters)

    # ============ CACHED ORDER RETRIEVAL METHODS ============
    
    def get_order_by_id_cached(self, order_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve order by ID with caching.
        
        Args:
            order_id: Order ID to retrieve
            
        Returns:
            Serialized order dict or None if not found
            
        Cache Key: order:v1:{order_id}
        """
        return self.cache_helper.get_or_set(
            cache_key=str(order_id),
            fetch_func=lambda: self.repository.get_by_id(order_id),
            schema_class=OrderResponseSchema,
            ttl=600  # 10 min TTL
        )
    
    def get_orders_by_user_id_cached(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Retrieve all orders for a specific user with caching.
        
        Args:
            user_id: User ID to retrieve orders for
            
        Returns:
            List of serialized order dicts
            
        Cache Key: order:v1:user:{user_id}:all
        """
        return self.cache_helper.get_or_set(
            cache_key=f"user:{user_id}:all",
            fetch_func=lambda: self.repository.get_by_user_id(user_id),
            schema_class=OrderResponseSchema,
            many=True,
            ttl=600  # 10 min TTL
        )
    
    def get_all_orders_cached(self) -> List[Dict[str, Any]]:
        """
        Retrieve all orders with caching.
        
        Returns:
            List of serialized order dicts
            
        Cache Key: order:v1:all
        """
        return self.cache_helper.get_or_set(
            cache_key="all",
            fetch_func=lambda: self.repository.get_all(),
            schema_class=OrderResponseSchema,
            many=True,
            ttl=600  # 10 min TTL
        )

    # ============ ORDER CREATION ============
    @cache_invalidate([
        lambda self, **order_data: f"order:v1:user:{order_data.get('user_id')}:all",
        lambda self, **order_data: "order:v1:all"
    ])
    def create_order(self, **order_data) -> Optional[Order]:
        """
        Create a new order with validation.
        Converts status name to ID if present.
        
        Args:
            **order_data: Order fields (user_id, items, total_amount, status, shipping_address, etc.)
                - status can be a string name (e.g., "pending") - will be converted to ID
                - items: list of dicts with product info (converted to OrderItem objects)
            
        Returns:
            Created Order object or None on error
        """
        try:
            # Convert status name to ID if present
            if 'status' in order_data:
                status_name = order_data.pop('status')
                status_id = ReferenceData.get_order_status_id(status_name)
                
                if status_id is None:
                    self.logger.error(f"Invalid order status: {status_name}")
                    return None
                
                order_data['order_status_id'] = status_id
                self.logger.debug(f"Converted status '{status_name}' to ID {status_id}")
            
            # Extract items before creating Order
            items_data = order_data.pop('items', [])
            
            if not order_data.get('user_id'):
                self.logger.error("Cannot create order without user_id")
                return None
            
            if not items_data:
                self.logger.error("Cannot create order without items")
                return None
            
            # Get or create cart for order if cart_id not provided
            # Each order needs its own unique cart (orders.cart_id is UNIQUE constraint)
            if 'cart_id' not in order_data:
                from app.sales.services.cart_service import CartService  # Lazy import to avoid circular import
                cart_service = CartService()
                
                # Check if user has an existing cart
                existing_cart = cart_service.get_cart_by_user_id(order_data['user_id'])
                
                if existing_cart:
                    # Check if cart already has an order
                    existing_order = self.repository.get_by_cart_id(existing_cart.id)
                    if existing_order:
                        # Cart already has an order, delete the order first (cascading), then delete cart
                        self.logger.debug(f"Cart {existing_cart.id} already has order {existing_order.id}, deleting both")
                        self.repository.delete(existing_order.id)  # Delete order first
                        cart_service.delete_cart(order_data['user_id'])  # Then delete cart
                        # Create new cart with force_create=True to bypass duplicate check
                        new_cart = cart_service.create_cart(force_create=True, user_id=order_data['user_id'], items=[])
                        if new_cart:
                            order_data['cart_id'] = new_cart.id
                            self.logger.debug(f"Created new cart {new_cart.id} for order")
                        else:
                            self.logger.error(f"Failed to create new cart for user {order_data['user_id']}")
                            return None
                    else:
                        # Cart doesn't have an order yet, use it
                        order_data['cart_id'] = existing_cart.id
                        self.logger.debug(f"Using existing cart {existing_cart.id} for order")
                else:
                    # No existing cart, create new one
                    new_cart = cart_service.create_cart(user_id=order_data['user_id'], items=[])
                    if new_cart:
                        order_data['cart_id'] = new_cart.id
                        self.logger.debug(f"Created new cart {new_cart.id} for order")
                    else:
                        self.logger.error(f"Failed to create cart for user {order_data['user_id']}")
                        return None
            
            # Calculate total from items
            total_amount = sum(item['amount'] for item in items_data)
            order_data['total_amount'] = total_amount
            
            # Set defaults
            order_data.setdefault('created_at', datetime.utcnow())
            
            # Create Order instance
            order = Order(**order_data)
            
            # Convert item dicts to OrderItem objects and append to order
            for item_data in items_data:
                order_item = OrderItem(
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    amount=item_data['amount']
                )
                order.items.append(order_item)
            
            # Validate order total integrity
            validation_errors = self._validate_total_integrity(order)
            if validation_errors:
                self.logger.error(f"Order total validation failed for user {order_data.get('user_id')}: {'; '.join(validation_errors)}")
                return None
            
            # Save to database
            created_order = self.repository.create(order)
            
            if created_order:
                # Mark the cart as finalized so user can create a new cart
                from app.sales.services.cart_service import CartService
                cart_service = CartService()
                finalized_cart = cart_service.finalize_cart(created_order.cart_id)
                if finalized_cart:
                    self.logger.debug(f"Cart {created_order.cart_id} marked as finalized")
                
                self.logger.info(f"Order created successfully: {created_order.id} with {len(items_data)} items")
            else:
                self.logger.error("Failed to create order")
            
            return created_order
            
        except Exception as e:
            self.logger.error(f"Error creating order: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return None

    # ============ ORDER UPDATE ============
    @cache_invalidate([
        lambda self, order_id, **updates: f"order:v1:{order_id}",
        lambda self, order_id, **updates: f"order:v1:user:{self.repository.get_by_id(order_id).user_id if self.repository.get_by_id(order_id) else 0}:all",
        lambda self, *args, **kwargs: "order:v1:all"
    ])
    def update_order(self, order_id: int, **updates) -> Optional[Order]:
        """
        Update an existing order with new data.
        Converts status name to ID if present.
        
        Args:
            order_id: Order ID to update
            **updates: Fields to update (items, status, shipping_address, etc.)
                - status can be a string name - will be converted to order_status_id
            
        Returns:
            Updated Order object or None on error
        """
        try:
            existing_order = self.repository.get_by_id(order_id)
            if not existing_order:
                self.logger.warning(f"Attempt to update non-existent order {order_id}")
                return None
            
            if 'status' in updates:
                status_name = updates.pop('status')
                status_id = ReferenceData.get_order_status_id(status_name)
                
                if status_id is None:
                    self.logger.error(f"Invalid order status: {status_name}")
                    return None
                
                updates['order_status_id'] = status_id
                self.logger.debug(f"Converted status '{status_name}' to ID {status_id}")
            
            if 'items' in updates:
                # Extract items before processing
                items_data = updates.pop('items')
                
                # Clear existing items
                existing_order.items.clear()
                
                # Flush to ensure items are deleted before adding new ones
                from app.core.database import get_db
                db = get_db()
                db.flush()
                
                # Convert item dicts to OrderItem objects and append to order
                for item_data in items_data:
                    order_item = OrderItem(
                        product_id=item_data['product_id'],
                        quantity=item_data['quantity'],
                        amount=item_data['amount']
                    )
                    existing_order.items.append(order_item)
                
                # Recalculate total from items (never trust input)
                existing_order.total_amount = sum(item_data['amount'] for item_data in items_data)
                self.logger.info(f"Updated order items for order {order_id}: {len(items_data)} items")
            
            if 'order_status_id' in updates:
                existing_order.order_status_id = updates['order_status_id']
            
            if 'shipping_address' in updates:
                existing_order.shipping_address = updates['shipping_address']
            
            
            validation_errors = self.validate_order_data(existing_order, require_cart_id=False)
            if validation_errors:
                self.logger.warning(f"Order validation failed: {'; '.join(validation_errors)}")
                return None
            
            integrity_errors = self._validate_total_integrity(existing_order)
            if integrity_errors:
                self.logger.error(f"Order total integrity check failed: {'; '.join(integrity_errors)}")
                return None
            
            updated_order = self.repository.update(existing_order)
            
            if updated_order:
                self.logger.info(f"Order updated successfully: {order_id}")
            else:
                self.logger.error(f"Failed to update order {order_id}")
            
            return updated_order
            
        except Exception as e:
            self.logger.error(f"Error updating order: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return None

    # ============ ORDER DELETION ============
    @cache_invalidate([
        lambda self, order_id: f"order:v1:{order_id}",
        lambda self, order_id: f"order:v1:user:{self.repository.get_by_id(order_id).user_id if self.repository.get_by_id(order_id) else 0}:all",
        lambda self, *args, **kwargs: "order:v1:all"
    ])
    def delete_order(self, order_id: int) -> bool:
        """
        Delete an order by ID (only if status allows).
        
        Args:
            order_id: ID of order to delete
            
        Returns:
            True on success, False on failure
        """
        try:
            order = self.repository.get_by_id(order_id)
            if not order:
                self.logger.warning(f"Attempt to delete non-existent order {order_id}")
                return False
            
            # Check if order can be deleted based on status
            # Only allow deletion of pending or cancelled orders
            deletable_statuses = ['pending', 'cancelled']
            if hasattr(order, 'status') and hasattr(order.status, 'status'):
                if order.status.status not in deletable_statuses:
                    self.logger.warning(f"Cannot delete order {order_id} with status {order.status.status}")
                    return False
            
            deleted = self.repository.delete(order_id)
            
            if deleted:
                self.logger.info(f"Order deleted successfully: {order_id}")
            else:
                self.logger.error(f"Failed to delete order {order_id}")
            
            return deleted
            
        except Exception as e:
            self.logger.error(f"Error deleting order: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return False

    # ============ ORDER STATUS MANAGEMENT ============
    def update_order_status(self, order_id: int, status: str) -> Optional[Order]:
        """
        Update order status using status name.
        Converts status name to ID before update.
        Validates that the status transition is allowed (e.g., can't cancel already cancelled order).
        
        Args:
            order_id: Order ID to update
            status: Status name (e.g., "pending", "shipped")
            
        Returns:
            Updated Order object or None on error
        """
        # Get current order to check current status
        current_order = self.repository.get_by_id(order_id)
        if not current_order:
            self.logger.error(f"Order not found: {order_id}")
            return None
        
        # Convert status name to ID
        status_id = ReferenceData.get_order_status_id(status)
        if status_id is None:
            self.logger.error(f"Invalid order status: {status}")
            return None
        
        # Get current status name
        current_status_name = ReferenceData.get_order_status_name(current_order.order_status_id)
        
        # Validate status transitions - prevent duplicate status changes
        if current_status_name == status:
            self.logger.warning(f"Order {order_id} is already in status '{status}'")
            return None
        
        # Additional validation: Cancelled orders cannot be changed
        if current_status_name == "cancelled":
            self.logger.warning(f"Cannot change status of cancelled order {order_id}")
            return None
        
        return self.update_order(order_id, order_status_id=status_id)
    
    def get_status_id_by_name(self, status_name: str) -> Optional[int]:
        """
        Get order status ID by name.
        
        Args:
            status_name: Status name to search for
            
        Returns:
            Status ID or None if not found
        """
        return ReferenceData.get_order_status_id(status_name)

    # ============ VALIDATION HELPERS ============
    def validate_order_data(self, order: Order, require_cart_id: bool = True) -> List[str]:
        """
        Validate order data.
        
        Args:
            order: Order object to validate
            require_cart_id: Whether cart_id is required (False for updates)
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate required fields
        # cart_id only required for new orders (create), not updates
        if require_cart_id:
            if not hasattr(order, 'cart_id') or order.cart_id is None:
                errors.append("cart_id is required")
        
        if not hasattr(order, 'user_id') or order.user_id is None:
            errors.append("user_id is required")
        
        if not hasattr(order, 'order_status_id') or order.order_status_id is None:
            errors.append("order_status_id is required")
        
        if not hasattr(order, 'total_amount') or order.total_amount is None:
            errors.append("total_amount is required")
        elif order.total_amount < 0:
            errors.append("total_amount must be non-negative")
        
        # Validate items if present
        if hasattr(order, 'items') and order.items:
            if len(order.items) == 0:
                errors.append("Order must have at least one item")
            
            for idx, item in enumerate(order.items):
                if not hasattr(item, 'product_id') or item.product_id is None:
                    errors.append(f"Item {idx}: product_id is required")
                
                if not hasattr(item, 'quantity') or item.quantity is None:
                    errors.append(f"Item {idx}: quantity is required")
                elif item.quantity <= 0:
                    errors.append(f"Item {idx}: quantity must be positive")
                
                if not hasattr(item, 'amount') or item.amount is None:
                    errors.append(f"Item {idx}: amount is required")
                elif item.amount < 0:
                    errors.append(f"Item {idx}: amount must be non-negative")
        
        return errors
    
    def _validate_total_integrity(self, order: Order) -> List[str]:
        """
        Validate that total_amount matches sum of item amounts.
        This is a critical security check to prevent financial discrepancies.
        
        Args:
            order: Order object to validate
            
        Returns:
            List of integrity error messages (empty if valid)
        """
        from app.sales.utils.validation_helpers import validate_total_integrity, calculate_items_total
        
        if not hasattr(order, 'items') or not order.items:
            return []
        
        calculated_total = calculate_items_total(order.items)
        return validate_total_integrity(order.total_amount, calculated_total, "Order")
    
    def order_exists_by_cart(self, cart_id: int) -> bool:
        """
        Check if an order exists for a cart.
        
        Args:
            cart_id: Cart ID to check
            
        Returns:
            True if exists, False otherwise
        """
        return self.repository.exists_by_cart_id(cart_id)

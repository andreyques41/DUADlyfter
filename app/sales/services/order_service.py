"""
Order Service Module

This module provides comprehensive order management functionality including:
- CRUD operations for orders (Create, Read, Update, Delete)
- Order status management and validation
- Business logic for order calculations and validation
- Uses OrderRepository for data access layer

Key Changes:
- Converts status names to IDs before database operations
- Validates status using ReferenceData instead of enums

Used by: Order routes for API operations
Dependencies: Order models, OrderRepository, ReferenceData
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
from config.logging import EXC_INFO_LOG_ERRORS
from app.sales.repositories.order_repository import OrderRepository
from app.sales.models.order import Order, OrderItem
from app.core.reference_data import ReferenceData

logger = logging.getLogger(__name__)


class OrderService:
    """
    Service class for order management operations.
    Handles all business logic for order CRUD operations, status management,
    and data validation. Provides a clean interface for routes.
    """

    def __init__(self):
        """Initialize order service with OrderRepository."""
        self.repository = OrderRepository()
        self.logger = logger

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

    # ============ ORDER CREATION ============
    def create_order(self, **order_data) -> Optional[Order]:
        """
        Create a new order with validation.
        Converts status name to ID if present.
        
        Args:
            **order_data: Order fields (cart_id, user_id, items, total_amount, status, etc.)
                - status can be a string name (e.g., "pending") - will be converted to ID
            
        Returns:
            Created Order object or None on error
        """
        try:
            # === CONVERT STATUS NAME TO ID ===
            if 'status' in order_data:
                status_name = order_data.pop('status')
                status_id = ReferenceData.get_order_status_id(status_name)
                
                if status_id is None:
                    self.logger.error(f"Invalid order status: {status_name}")
                    return None
                
                order_data['order_status_id'] = status_id
                self.logger.debug(f"Converted status '{status_name}' to ID {status_id}")
            
            # Validate required fields
            if not order_data.get('cart_id'):
                self.logger.error("Cannot create order without cart_id")
                return None
            
            if not order_data.get('user_id'):
                self.logger.error("Cannot create order without user_id")
                return None
            
            # Check if order already exists for this cart
            existing_order = self.repository.get_by_cart_id(order_data['cart_id'])
            if existing_order:
                self.logger.warning(f"Order already exists for cart {order_data['cart_id']}")
                return None
            
            # Set defaults
            order_data.setdefault('created_at', datetime.utcnow())
            
            # Create Order instance
            order = Order(**order_data)
            
            # Validate order data
            validation_errors = self.validate_order_data(order)
            if validation_errors:
                self.logger.warning(f"Order validation failed: {'; '.join(validation_errors)}")
                return None
            
            # Save to database
            created_order = self.repository.create(order)
            
            if created_order:
                self.logger.info(f"Order created successfully: {created_order.id}")
            else:
                self.logger.error("Failed to create order")
            
            return created_order
            
        except Exception as e:
            self.logger.error(f"Error creating order: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return None

    # ============ ORDER UPDATE ============
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
            
            # === CONVERT STATUS NAME TO ID ===
            if 'status' in updates:
                status_name = updates.pop('status')
                status_id = ReferenceData.get_order_status_id(status_name)
                
                if status_id is None:
                    self.logger.error(f"Invalid order status: {status_name}")
                    return None
                
                updates['order_status_id'] = status_id
                self.logger.debug(f"Converted status '{status_name}' to ID {status_id}")
            
            # Update fields
            if 'items' in updates:
                existing_order.items = updates['items']
                # Recalculate total if items changed
                if hasattr(updates['items'][0], 'amount') and hasattr(updates['items'][0], 'quantity'):
                    existing_order.total_amount = sum(
                        item.amount * item.quantity for item in updates['items']
                    )
            
            if 'order_status_id' in updates:
                existing_order.order_status_id = updates['order_status_id']
            
            if 'shipping_address' in updates:
                existing_order.shipping_address = updates['shipping_address']
            
            if 'total_amount' in updates:
                existing_order.total_amount = updates['total_amount']
            
            # Validate updated order
            validation_errors = self.validate_order_data(existing_order)
            if validation_errors:
                self.logger.warning(f"Order validation failed: {'; '.join(validation_errors)}")
                return None
            
            # Save updated order
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
            deletable_statuses = ['Pending', 'Cancelled']
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
        
        Args:
            order_id: Order ID to update
            status: Status name (e.g., "pending", "shipped")
            
        Returns:
            Updated Order object or None on error
        """
        # Convert status name to ID
        status_id = ReferenceData.get_order_status_id(status)
        if status_id is None:
            self.logger.error(f"Invalid order status: {status}")
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
    def validate_order_data(self, order: Order) -> List[str]:
        """
        Validate order data.
        
        Args:
            order: Order object to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate required fields
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
    
    def order_exists_by_cart(self, cart_id: int) -> bool:
        """
        Check if an order exists for a cart.
        
        Args:
            cart_id: Cart ID to check
            
        Returns:
            True if exists, False otherwise
        """
        return self.repository.exists_by_cart_id(cart_id)

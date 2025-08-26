"""
Orders Service Module

This module provides comprehensive orders management functionality including:
- CRUD operations for orders (Create, Read, Update, Delete)
- Order status management (pending, confirmed, processing, shipped, delivered, cancelled)
- Business logic for order calculations and validation
- Data persistence and user-specific order operations

Used by: Orders routes for API operations
Dependencies: Orders models, shared CRUD utilities
"""
from datetime import datetime
from typing import List, Optional, Tuple
import logging
from config.logging_config import EXC_INFO_LOG_ERRORS
from app.sales.imports import Order, OrderItem, OrderStatus, save_models_to_json, load_models_from_json, load_single_model_by_field, generate_next_id, ORDERS_DB_PATH

logger = logging.getLogger(__name__)

class OrdersService:
    """
    Service class for orders management operations.
    
    Handles all business logic for orders CRUD operations, status management,
    and data persistence. Provides a clean interface for routes.
    """
    
    def __init__(self, db_path=ORDERS_DB_PATH):
        """Initialize orders service with database path."""
        self.db_path = db_path
        self.logger = logger

    # ============ ORDERS RETRIEVAL METHODS ============

    def get_orders(self, order_id=None, user_id=None):
        """
        Unified method to get all orders, specific order by ID, or orders by user ID.
        
        Args:
            order_id (int, optional): If provided, returns single order by ID
            user_id (int, optional): If provided, returns orders for specific user
            
        Returns:
            list[Order] or Order or None: Orders collection, single order, or None if not found
        """
        if order_id:
            return load_single_model_by_field(self.db_path, Order, 'id', order_id)
        
        all_orders = load_models_from_json(self.db_path, Order)
        
        if user_id:
            return [order for order in all_orders if order.user_id == user_id]
            
        return all_orders

    # ============ ORDERS CRUD OPERATIONS ============

    def create_order(self, order_object) -> Tuple[Optional[Order], Optional[str]]:
        """
        Create a new order from validated Order object (from schema).
        """
        try:
            existing_orders = load_models_from_json(self.db_path, Order)
            
            # Set id and created_at for new order
            order_object.id = generate_next_id(existing_orders)
            order_object.created_at = datetime.now()
            
            validation_errors = self.validate_order_data(order_object)
            if validation_errors:
                self.logger.warning(f"Order validation failed for user {order_object.user_id}: {'; '.join(validation_errors)}")
                return None, "; ".join(validation_errors)
                
            existing_orders.append(order_object)
            save_models_to_json(existing_orders, self.db_path)
            
            self.logger.info(f"Order created successfully for user {order_object.user_id}")
            return order_object, None
        except Exception as e:
            error_msg = f"Error creating order: {e}"
            self.logger.error(error_msg, exc_info=EXC_INFO_LOG_ERRORS)
            return None, error_msg
    
    def update_order(self, order_id: int, update_obj: Order) -> Tuple[Optional[Order], Optional[str]]:
        """
        Update an existing order with new data from an Order object.
        """
        try:
            existing_order = self.get_orders(order_id)
            if not existing_order:
                self.logger.warning(f"Attempt to update non-existent order ID {order_id}")
                return None, f"No order found with ID {order_id}"

            # Only update allowed fields (items, status, shipping_address)
            if hasattr(update_obj, 'items') and update_obj.items is not None:
                existing_order.items = update_obj.items
                existing_order.total_amount = sum(item.subtotal() for item in update_obj.items)
            if hasattr(update_obj, 'status') and update_obj.status is not None:
                existing_order.status = update_obj.status
            if hasattr(update_obj, 'shipping_address') and update_obj.shipping_address is not None:
                existing_order.shipping_address = update_obj.shipping_address

            validation_errors = self.validate_order_data(existing_order)
            if validation_errors:
                return None, "; ".join(validation_errors)

            # Save updated order
            all_orders = load_models_from_json(self.db_path, Order)
            for i, order in enumerate(all_orders):
                if order.id == order_id:
                    all_orders[i] = existing_order
                    break

            save_models_to_json(all_orders, self.db_path)

            self.logger.info(f"Order updated: {order_id}")
            return existing_order, None
        except Exception as e:
            error_msg = f"Error updating order: {e}"
            self.logger.error(error_msg, exc_info=EXC_INFO_LOG_ERRORS)
            return None, error_msg
    # ============ ORDER ITEM BUILDING (HELPER) ============
    # Note: Product lookup and OrderItem creation now handled in schema layer

    def delete_order(self, order_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete an order by ID (only if status allows).
        
        Args:
            order_id (int): ID of the order to delete
            
        Returns:
            tuple: (True, None) on success, (False, error_message) on failure
            
        Note:
            Can only delete orders with PENDING or CANCELLED status
        """
        try:
            order = self.get_orders(order_id)
            if not order:
                self.logger.warning(f"Attempt to delete non-existent order ID {order_id}")
                return False, f"No order found with ID {order_id}"
            
            # Check if order can be deleted
            if order.status not in [OrderStatus.PENDING, OrderStatus.CANCELLED]:
                self.logger.warning(f"Attempt to delete order {order_id} with status {order.status.value}")
                return False, f"Cannot delete order with status: {order.status.value}"
            
            # Remove order from database
            all_orders = load_models_from_json(self.db_path, Order)
            all_orders = [o for o in all_orders if o.id != order_id]
            save_models_to_json(all_orders, self.db_path)
            
            self.logger.info(f"Order deleted: {order_id}")
            return True, None
        except Exception as e:
            error_msg = f"Error deleting order: {e}"
            self.logger.error(error_msg, exc_info=EXC_INFO_LOG_ERRORS)
            return False, error_msg

    # ============ ORDER STATUS MANAGEMENT METHODS ============

    def update_order_status(self, order_id: int, new_status: OrderStatus) -> Tuple[Optional[Order], Optional[str]]:
        """
        Update order status with validation.
        
        Args:
            order_id (int): ID of the order
            new_status (OrderStatus): New status to set
            
        Returns:
            tuple: (Order, None) on success, (None, error_message) on failure
        """
        try:
            order = self.get_orders(order_id)
            if not order:
                self.logger.warning(f"Attempt to update status of non-existent order ID {order_id}")
                return None, f"No order found with ID {order_id}"
            
            # Validate status transition
            if not self._is_valid_status_transition(order.status, new_status):
                self.logger.warning(f"Invalid status transition for order {order_id}: {order.status.value} -> {new_status.value}")
                return None, f"Invalid status transition from {order.status.value} to {new_status.value}"
            
            # Update status
            order.status = new_status
            
            # Update order in database
            all_orders = load_models_from_json(self.db_path, Order)
            for i, o in enumerate(all_orders):
                if o.id == order_id:
                    all_orders[i] = order
                    break
            
            save_models_to_json(all_orders, self.db_path)
            
            self.logger.info(f"Order {order_id} status updated to {new_status.value}")
            return order, None
        except Exception as e:
            self.logger.error(f"Error updating order status for {order_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return None, f"Failed to update order status: {str(e)}"

    def cancel_order(self, order_id: int) -> Tuple[Optional[Order], Optional[str]]:
        """
        Cancel an order if possible.
        
        Args:
            order_id (int): ID of the order to cancel
            
        Returns:
            tuple: (Order, None) on success, (None, error_message) on failure
        """
        try:
            order = self.get_orders(order_id)
            if not order:
                self.logger.warning(f"Attempt to cancel non-existent order ID {order_id}")
                return None, f"No order found with ID {order_id}"
            
            # Check if order can be cancelled
            if order.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
                self.logger.warning(f"Attempt to cancel order {order_id} with status {order.status.value}")
                return None, f"Cannot cancel order with status: {order.status.value}"
            
            return self.update_order_status(order_id, OrderStatus.CANCELLED)
            
        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return None, f"Failed to cancel order: {str(e)}"

    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        """
        Get all orders with specific status.
        
        Args:
            status (OrderStatus): Status to filter by
            
        Returns:
            list[Order]: List of orders with the specified status
        """
        try:
            all_orders = load_models_from_json(self.db_path, Order)
            return [order for order in all_orders if order.status == status]
            
        except Exception as e:
            self.logger.error(f"Error getting orders by status {status.value}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return []

    # ============ ACCESS CONTROL METHODS ============

    def check_user_access(self, current_user, is_admin, order_id=None, user_id=None):
        """
        Check if current user can access the specified order or user's orders
        
        Args:
            current_user: Current authenticated user object
            is_admin (bool): Whether current user is admin
            order_id (int, optional): Order ID to check access for
            user_id (int, optional): User ID to check access for
            
        Returns:
            bool: True if access allowed, False otherwise
        """
        # Admins can access any order, regular users only their own
        if is_admin:
            return True
        
        if order_id:
            # Check if order belongs to current user
            order = self.get_orders(order_id)
            if order:
                return current_user.id == order.user_id
            return False
        
        if user_id:
            return current_user.id == user_id
            
        return False

    # ============ PRIVATE HELPER METHODS ============

    def _is_valid_status_transition(self, current_status: OrderStatus, new_status: OrderStatus) -> bool:
        """
        Validate if status transition is allowed.
        
        Args:
            current_status (OrderStatus): Current order status
            new_status (OrderStatus): Proposed new status
            
        Returns:
            bool: True if transition is valid, False otherwise
        """
        # Define valid transitions
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
            OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED: [],  # Final state
            OrderStatus.CANCELLED: []   # Final state
        }
        
        return new_status in valid_transitions.get(current_status, [])

    def validate_order_data(self, order: Order) -> List[str]:
        """
        Validate order against business rules.
        
        Args:
            order (Order): Order to validate
            
        Returns:
            list[str]: List of validation error messages, empty if valid
        """
        errors = []
        
        # Check items
        if not order.items:
            errors.append("Order must contain at least one item")
        
        # Check total amount
        if order.total_amount <= 0:
            errors.append("Order total must be greater than 0")
        
        # Check individual items
        for item in order.items:
            if item.quantity <= 0:
                errors.append(f"Item {item.product_name} must have quantity greater than 0")
            if item.price < 0:
                errors.append(f"Item {item.product_name} cannot have negative price")
        
        return errors

    # ============ PRIVATE HELPER METHODS ============
    # (Service layer uses shared utilities for data persistence)
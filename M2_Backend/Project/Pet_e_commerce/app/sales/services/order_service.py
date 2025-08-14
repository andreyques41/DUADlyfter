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
import json
import os
from datetime import datetime
from typing import List, Optional, Tuple
from app.sales.models.order import Order, OrderItem, OrderStatus
import logging
from app.shared.utils import read_json, write_json, save_models_to_json, load_models_from_json, load_single_model_by_field, generate_next_id

logger = logging.getLogger(__name__)

class OrdersService:
    """
    Service class for orders management operations.
    
    Handles all business logic for orders CRUD operations, status management,
    and data persistence. Provides a clean interface for routes.
    """
    
    def __init__(self, db_path='./orders.json'):
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

    def create_order(self, order_instance: Order) -> Tuple[Optional[Order], Optional[str]]:
        """
        Create a new order with Order instance from schema.
        
        Args:
            order_instance (Order): Order instance from schema with @post_load
            
        Returns:
            tuple: (Order, None) on success, (None, error_message) on failure
            
        Note:
            Automatically generates unique ID and calculates total amount
        """
        try:
            # Load existing orders to generate next ID
            existing_orders = load_models_from_json(self.db_path, Order)
            
            # Set the ID for the new order instance
            order_instance.id = generate_next_id(existing_orders)
            order_instance.created_at = datetime.now()
            
            # Calculate total amount from items
            order_instance.total_amount = sum(item.subtotal() for item in order_instance.items)
            
            # Validate order items
            validation_errors = self.validate_order_data(order_instance)
            if validation_errors:
                return None, "; ".join(validation_errors)
            
            # Save order to database
            existing_orders.append(order_instance)
            save_models_to_json(existing_orders, self.db_path)

            self.logger.info(f"Order created successfully for user {order_instance.user_id}")
            return order_instance, None
            
        except Exception as e:
            error_msg = f"Error creating order: {e}"
            self.logger.error(error_msg)
            return None, error_msg
    
    def update_order(self, order_id: int, order_instance: Order) -> Tuple[Optional[Order], Optional[str]]:
        """
        Update an existing order with Order instance from schema.
        
        Args:
            order_id (int): ID of the order to update
            order_instance (Order): Updated order instance from schema
            
        Returns:
            tuple: (Order, None) on success, (None, error_message) on failure
            
        Note:
            Updates the entire order with new instance data
        """
        try:
            existing_order = self.get_orders(order_id)
            if not existing_order:
                return None, f"No order found with ID {order_id}"
            
            # Preserve original order ID and creation time
            order_instance.id = existing_order.id
            order_instance.created_at = existing_order.created_at
            
            # Recalculate total amount
            order_instance.total_amount = sum(item.subtotal() for item in order_instance.items)
            
            # Validate updated order
            validation_errors = self.validate_order_data(order_instance)
            if validation_errors:
                return None, "; ".join(validation_errors)
            
            # Load all orders, replace the specific one, and save
            all_orders = load_models_from_json(self.db_path, Order)
            for i, order in enumerate(all_orders):
                if order.id == order_id:
                    all_orders[i] = order_instance
                    break
            
            save_models_to_json(all_orders, self.db_path)
            
            self.logger.info(f"Order updated: {order_id}")
            return order_instance, None
            
        except Exception as e:
            error_msg = f"Error updating order: {e}"
            self.logger.error(error_msg)
            return None, error_msg

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
                return False, f"No order found with ID {order_id}"
            
            # Check if order can be deleted
            if order.status not in [OrderStatus.PENDING, OrderStatus.CANCELLED]:
                return False, f"Cannot delete order with status: {order.status.value}"
            
            # Remove order from database
            all_orders = load_models_from_json(self.db_path, Order)
            all_orders = [o for o in all_orders if o.id != order_id]
            save_models_to_json(all_orders, self.db_path)
            
            self.logger.info(f"Order deleted: {order_id}")
            return True, None
            
        except Exception as e:
            error_msg = f"Error deleting order: {e}"
            self.logger.error(error_msg)
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
                return None, f"No order found with ID {order_id}"
            
            # Validate status transition
            if not self._is_valid_status_transition(order.status, new_status):
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
            self.logger.error(f"Error updating order status for {order_id}: {e}")
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
                return None, f"No order found with ID {order_id}"
            
            # Check if order can be cancelled
            if order.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
                return None, f"Cannot cancel order with status: {order.status.value}"
            
            return self.update_order_status(order_id, OrderStatus.CANCELLED)
            
        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id}: {e}")
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
            self.logger.error(f"Error getting orders by status {status.value}: {e}")
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
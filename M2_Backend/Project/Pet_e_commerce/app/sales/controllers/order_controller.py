"""
Order Controller Module

HTTP request processing layer for order operations.
Delegates to OrderService for business logic.

Responsibilities:
- Request validation and deserialization
- HTTP response formatting
- Error handling and logging
- Access control verification
- Cache-aware data retrieval

Dependencies:
- OrderService: Business logic and caching
- Flask request/g: Request context
- Marshmallow schemas: Validation
- Auth helpers: Access control

Usage:
    controller = OrderController()
    response, status = controller.get_list()
    response, status = controller.get(order_id=123)
"""
import logging
from flask import request, jsonify, g
from marshmallow import ValidationError
from typing import Tuple, Optional
from config.logging import get_logger, EXC_INFO_LOG_ERRORS
from app.core.lib.error_utils import error_response

# Service imports
from app.sales.services.order_service import OrderService

# Schema imports
from app.sales.schemas.order_schema import (
    order_registration_schema,
    order_update_schema,
    order_status_update_schema,
    order_response_schema,
    orders_response_schema
)

# Auth imports
from app.core.lib.auth import is_admin_user, is_user_or_admin

# Model imports
from app.sales.models.order import OrderStatus

logger = get_logger(__name__)


class OrderController:
    """Controller for order HTTP operations."""
    
    def __init__(self):
        """Initialize order controller with service dependency."""
        self.order_service = OrderService()
        self.logger = logger
    
    # ============================================
    # PRIVATE HELPER METHODS
    # ============================================
    
    def _check_order_access(self, user_id: int) -> Optional[Tuple[dict, int]]:
        """
        Check if current user has access to the specified user's order.
        Returns error response if access denied, None if access granted.
        
        Args:
            user_id: ID of the user whose order is being accessed
            
        Returns:
            None if access granted, or (error_response, status_code) if denied
        """
        if not is_user_or_admin(user_id):
            self.logger.warning(f"Access denied for user {g.current_user.id} to order for user {user_id}")
            return jsonify({"error": "Access denied"}), 403
        return None
    
    # ============================================
    # ORDER CRUD OPERATIONS
    # ============================================
    
    def get_list(self) -> Tuple[dict, int]:
        """
        Get orders collection - auto-filtered based on user role.
        - Admins: See all orders
        - Users: See only their own orders
        
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            if is_admin_user():
                # Admin: Return all orders (cached) - already serialized
                orders = self.order_service.get_all_orders_cached()
                self.logger.info(f"Admin retrieved all orders (total: {len(orders)})")
            else:
                # Customer: Return own orders (cached) - already serialized
                orders = self.order_service.get_orders_by_user_id_cached(g.current_user.id)
                self.logger.info(f"Orders retrieved for user {g.current_user.id} (total: {len(orders)})")
            
            return jsonify({
                "total_orders": len(orders),
                "orders": orders
            }), 200
            
        except Exception as e:
            self.logger.error(f"Error retrieving orders: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to retrieve orders", e)
    
    def get(self, order_id: int) -> Tuple[dict, int]:
        """
        Get specific order by ID.
        Users can view own orders, admins can view any.
        
        Args:
            order_id: ID of the order to retrieve
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Get order (cached) - already serialized
            order = self.order_service.get_order_by_id_cached(order_id)
            if order is None:
                self.logger.warning(f"Order not found: {order_id}")
                return jsonify({"error": "Order not found"}), 404
            
            # Check access: admin or owner
            if access_denied := self._check_order_access(order['user_id']):
                return access_denied
            
            self.logger.info(f"Order retrieved: {order_id}")
            return jsonify(order), 200
            
        except Exception as e:
            self.logger.error(f"Error retrieving order {order_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to retrieve order", e)
    
    def post(self) -> Tuple[dict, int]:
        """
        Create new order.
        Users can create own orders, admins can create any.
        
        Expected JSON:
            {
                "user_id": 123,
                "items": [{"product_id": 1, "quantity": 2}],
                "shipping_address": "123 Main St",
                "status": "pending"  # optional
            }
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Validate request data
            order_data = order_registration_schema.load(request.json)
            user_id = order_data.get('user_id')
            
            # Check access: admin or owner
            if access_denied := self._check_order_access(user_id):
                return access_denied
            
            # Create order
            created_order = self.order_service.create_order(**order_data)
            
            if created_order is None:
                self.logger.error(f"Order creation failed for user {user_id}")
                return jsonify({"error": "Failed to create order"}), 400
            
            self.logger.info(f"Order created: {created_order.id if hasattr(created_order, 'id') else 'unknown'}")
            return jsonify({
                "message": "Order created successfully",
                "order": order_response_schema.dump(created_order)
            }), 201
            
        except ValidationError as err:
            self.logger.warning(f"Order creation validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error creating order: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to create order", e)
    
    def put(self, order_id: int) -> Tuple[dict, int]:
        """
        Update existing order (admin only).
        
        Args:
            order_id: ID of the order to update
            
        Expected JSON:
            Order update fields
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Validate request data
            order_data = order_update_schema.load(request.json)
            
            # Check if order exists
            existing_order = self.order_service.get_order_by_id(order_id)
            if not existing_order:
                self.logger.warning(f"Order update attempt for non-existent order: {order_id}")
                return jsonify({"error": "Order not found"}), 404
            
            # Update order
            updated_order = self.order_service.update_order(order_id, **order_data)
            
            if updated_order is None:
                self.logger.error(f"Order update failed for {order_id}")
                return jsonify({"error": "Failed to update order"}), 400
            
            self.logger.info(f"Order updated: {order_id}")
            return jsonify({
                "message": "Order updated successfully",
                "order": order_response_schema.dump(updated_order)
            }), 200
            
        except ValidationError as err:
            self.logger.warning(f"Order update validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error updating order {order_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to update order", e)
    
    def patch_status(self, order_id: int) -> Tuple[dict, int]:
        """
        Update order status (admin only).
        
        Args:
            order_id: ID of the order to update
            
        Expected JSON:
            {"status": "shipped"}
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Validate request data
            status_data = order_status_update_schema.load(request.json)
            new_status = status_data['status']
            
            # Update order status
            updated_order = self.order_service.update_order_status(order_id, new_status)
            
            if updated_order is None:
                self.logger.warning(f"Status update failed for order: {order_id}")
                return jsonify({"error": "Failed to update order status"}), 404
            
            self.logger.info(f"Order status updated for {order_id} to {new_status}")
            return jsonify({
                "message": f"Order status updated to {new_status}",
                "order": order_response_schema.dump(updated_order)
            }), 200
            
        except ValidationError as err:
            self.logger.warning(f"Order status update validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error updating order status for {order_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to update order status", e)
    
    def delete(self, order_id: int) -> Tuple[dict, int]:
        """
        Delete order (admin only, limited by status).
        
        Args:
            order_id: ID of the order to delete
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Delete order
            success = self.order_service.delete_order(order_id)
            
            if not success:
                self.logger.warning(f"Delete attempt failed for order: {order_id}")
                return jsonify({"error": "Failed to delete order"}), 404
            
            self.logger.info(f"Order deleted: {order_id}")
            return jsonify({"message": "Order deleted successfully"}), 200
            
        except Exception as e:
            self.logger.error(f"Error deleting order {order_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to delete order", e)
    
    def cancel(self, order_id: int) -> Tuple[dict, int]:
        """
        Cancel order (user access - owner or admin).
        Updates order status to CANCELLED.
        
        Args:
            order_id: ID of the order to cancel
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Get order first to check ownership
            order = self.order_service.get_order_by_id(order_id)
            if order is None:
                self.logger.warning(f"Cancel attempt for non-existent order: {order_id}")
                return jsonify({"error": "Order not found"}), 404
            
            # Check access: admin or owner
            if access_denied := self._check_order_access(order.user_id):
                return access_denied
            
            # Cancel by updating status to CANCELLED
            updated_order = self.order_service.update_order_status(order_id, OrderStatus.CANCELLED)
            
            if updated_order is None:
                self.logger.warning(f"Cancel attempt failed for order: {order_id}")
                return jsonify({"error": "Failed to cancel order"}), 404
            
            self.logger.info(f"Order cancelled: {order_id}")
            return jsonify({
                "message": "Order cancelled successfully",
                "order": order_response_schema.dump(updated_order)
            }), 200
            
        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to cancel order", e)

""""""

Order Service ModuleOrders Service Module



This module provides comprehensive order management functionality including:This module provides comprehensive orders management functionality including:

- CRUD operations for orders (Create, Read, Update, Delete)- CRUD operations for orders (Create, Read, Update, Delete)

- Order status management and validation- Order status management (pending, confirmed, processing, shipped, delivered, cancelled)

- Business logic for order calculations and validation- Business logic for order calculations and validation

- Uses OrderRepository for data access layer- Data persistence and user-specific order operations



Used by: Order routes for API operationsUsed by: Orders routes for API operations

Dependencies: Order models, OrderRepositoryDependencies: Orders models, shared CRUD utilities

""""""

from datetime import datetimefrom datetime import datetime

from typing import List, Optional, Dict, Anyfrom typing import List, Optional, Tuple

import loggingimport logging

from config.logging import EXC_INFO_LOG_ERRORSfrom config.logging import EXC_INFO_LOG_ERRORS

from app.sales.repositories.order_repository import OrderRepositoryfrom app.sales.imports import Order, OrderItem, OrderStatus, save_models_to_json, load_models_from_json, load_single_model_by_field, generate_next_id, ORDERS_DB_PATH

from app.sales.models.order import Order, OrderItem, OrderStatus

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

class OrdersService:

    """

class OrderService:    Service class for orders management operations.

    """    

    Service class for order management operations.    Handles all business logic for orders CRUD operations, status management,

    Handles all business logic for order CRUD operations, status management,    and data persistence. Provides a clean interface for routes.

    and data validation. Provides a clean interface for routes.    """

    """    

    def __init__(self, db_path=ORDERS_DB_PATH):

    def __init__(self):        """Initialize orders service with database path."""

        """Initialize order service with OrderRepository."""        self.db_path = db_path

        self.repository = OrderRepository()        self.logger = logger

        self.logger = logger

    # ============ ORDERS RETRIEVAL METHODS ============

    # ============ ORDER RETRIEVAL METHODS ============

    def get_order_by_id(self, order_id: int) -> Optional[Order]:    def get_orders(self, order_id=None, user_id=None):

        """        """

        Retrieve order by ID.        Unified method to get all orders, specific order by ID, or orders by user ID.

                

        Args:        Args:

            order_id: Order ID to retrieve            order_id (int, optional): If provided, returns single order by ID

                        user_id (int, optional): If provided, returns orders for specific user

        Returns:            

            Order object or None if not found        Returns:

        """            list[Order] or Order or None: Orders collection, single order, or None if not found

        return self.repository.get_by_id(order_id)        """

            if order_id:

    def get_orders_by_user_id(self, user_id: int) -> List[Order]:            return load_single_model_by_field(self.db_path, Order, 'id', order_id)

        """        

        Retrieve all orders for a specific user.        all_orders = load_models_from_json(self.db_path, Order)

                

        Args:        if user_id:

            user_id: User ID to retrieve orders for            return [order for order in all_orders if order.user_id == user_id]

                        

        Returns:        return all_orders

            List of Order objects

        """    # ============ ORDERS CRUD OPERATIONS ============

        return self.repository.get_by_user_id(user_id)

        def create_order(self, order_object) -> Tuple[Optional[Order], Optional[str]]:

    def get_order_by_cart_id(self, cart_id: int) -> Optional[Order]:        """

        """        Create a new order from validated Order object (from schema).

        Retrieve order by cart ID.        """

                try:

        Args:            existing_orders = load_models_from_json(self.db_path, Order)

            cart_id: Cart ID to retrieve order for            

                        # Set id and created_at for new order

        Returns:            order_object.id = generate_next_id(existing_orders)

            Order object or None if not found            order_object.created_at = datetime.now()

        """            

        return self.repository.get_by_cart_id(cart_id)            validation_errors = self.validate_order_data(order_object)

                if validation_errors:

    def get_all_orders(self) -> List[Order]:                self.logger.warning(f"Order validation failed for user {order_object.user_id}: {'; '.join(validation_errors)}")

        """                return None, "; ".join(validation_errors)

        Retrieve all orders.                

                    existing_orders.append(order_object)

        Returns:            save_models_to_json(existing_orders, self.db_path)

            List of all Order objects            

        """            self.logger.info(f"Order created successfully for user {order_object.user_id}")

        return self.repository.get_all()            return order_object, None

            except Exception as e:

    def get_orders_by_filters(self, filters: Dict[str, Any]) -> List[Order]:            error_msg = f"Error creating order: {e}"

        """            self.logger.error(error_msg, exc_info=EXC_INFO_LOG_ERRORS)

        Retrieve orders by filters.            return None, error_msg

            

        Args:    def update_order(self, order_id: int, update_obj: Order) -> Tuple[Optional[Order], Optional[str]]:

            filters: Dictionary with filter criteria        """

                    Update an existing order with new data from an Order object.

        Returns:        """

            List of filtered Order objects        try:

        """            existing_order = self.get_orders(order_id)

        return self.repository.get_by_filters(filters)            if not existing_order:

                self.logger.warning(f"Attempt to update non-existent order ID {order_id}")

    # ============ ORDER CREATION ============                return None, f"No order found with ID {order_id}"

    def create_order(self, **order_data) -> Optional[Order]:

        """            # Only update allowed fields (items, status, shipping_address)

        Create a new order with validation.            if hasattr(update_obj, 'items') and update_obj.items is not None:

                        existing_order.items = update_obj.items

        Args:                existing_order.total_amount = sum(item.subtotal() for item in update_obj.items)

            **order_data: Order fields (cart_id, user_id, items, total_amount, etc.)            if hasattr(update_obj, 'status') and update_obj.status is not None:

                            existing_order.status = update_obj.status

        Returns:            if hasattr(update_obj, 'shipping_address') and update_obj.shipping_address is not None:

            Created Order object or None on error                existing_order.shipping_address = update_obj.shipping_address

        """

        try:            validation_errors = self.validate_order_data(existing_order)

            # Validate required fields            if validation_errors:

            if not order_data.get('cart_id'):                return None, "; ".join(validation_errors)

                self.logger.error("Cannot create order without cart_id")

                return None            # Save updated order

                        all_orders = load_models_from_json(self.db_path, Order)

            if not order_data.get('user_id'):            for i, order in enumerate(all_orders):

                self.logger.error("Cannot create order without user_id")                if order.id == order_id:

                return None                    all_orders[i] = existing_order

                                break

            # Check if order already exists for this cart

            existing_order = self.repository.get_by_cart_id(order_data['cart_id'])            save_models_to_json(all_orders, self.db_path)

            if existing_order:

                self.logger.warning(f"Order already exists for cart {order_data['cart_id']}")            self.logger.info(f"Order updated: {order_id}")

                return None            return existing_order, None

                    except Exception as e:

            # Set defaults            error_msg = f"Error updating order: {e}"

            order_data.setdefault('created_at', datetime.utcnow())            self.logger.error(error_msg, exc_info=EXC_INFO_LOG_ERRORS)

                        return None, error_msg

            # Create Order instance    # ============ ORDER ITEM BUILDING (HELPER) ============

            order = Order(**order_data)    # Note: Product lookup and OrderItem creation now handled in schema layer

            

            # Validate order data    def delete_order(self, order_id: int) -> Tuple[bool, Optional[str]]:

            validation_errors = self.validate_order_data(order)        """

            if validation_errors:        Delete an order by ID (only if status allows).

                self.logger.warning(f"Order validation failed: {'; '.join(validation_errors)}")        

                return None        Args:

                        order_id (int): ID of the order to delete

            # Save to database            

            created_order = self.repository.create(order)        Returns:

                        tuple: (True, None) on success, (False, error_message) on failure

            if created_order:            

                self.logger.info(f"Order created successfully: {created_order.id}")        Note:

            else:            Can only delete orders with PENDING or CANCELLED status

                self.logger.error("Failed to create order")        """

                    try:

            return created_order            order = self.get_orders(order_id)

                        if not order:

        except Exception as e:                self.logger.warning(f"Attempt to delete non-existent order ID {order_id}")

            self.logger.error(f"Error creating order: {e}", exc_info=EXC_INFO_LOG_ERRORS)                return False, f"No order found with ID {order_id}"

            return None            

            # Check if order can be deleted

    # ============ ORDER UPDATE ============            if order.status not in [OrderStatus.PENDING, OrderStatus.CANCELLED]:

    def update_order(self, order_id: int, **updates) -> Optional[Order]:                self.logger.warning(f"Attempt to delete order {order_id} with status {order.status.value}")

        """                return False, f"Cannot delete order with status: {order.status.value}"

        Update an existing order with new data.            

                    # Remove order from database

        Args:            all_orders = load_models_from_json(self.db_path, Order)

            order_id: Order ID to update            all_orders = [o for o in all_orders if o.id != order_id]

            **updates: Fields to update (items, status, shipping_address, etc.)            save_models_to_json(all_orders, self.db_path)

                        

        Returns:            self.logger.info(f"Order deleted: {order_id}")

            Updated Order object or None on error            return True, None

        """        except Exception as e:

        try:            error_msg = f"Error deleting order: {e}"

            existing_order = self.repository.get_by_id(order_id)            self.logger.error(error_msg, exc_info=EXC_INFO_LOG_ERRORS)

            if not existing_order:            return False, error_msg

                self.logger.warning(f"Attempt to update non-existent order {order_id}")

                return None    # ============ ORDER STATUS MANAGEMENT METHODS ============

            

            # Update fields    def update_order_status(self, order_id: int, new_status: OrderStatus) -> Tuple[Optional[Order], Optional[str]]:

            if 'items' in updates:        """

                existing_order.items = updates['items']        Update order status with validation.

                # Recalculate total if items changed        

                if hasattr(updates['items'][0], 'amount') and hasattr(updates['items'][0], 'quantity'):        Args:

                    existing_order.total_amount = sum(            order_id (int): ID of the order

                        item.amount * item.quantity for item in updates['items']            new_status (OrderStatus): New status to set

                    )            

                    Returns:

            if 'order_status_id' in updates:            tuple: (Order, None) on success, (None, error_message) on failure

                existing_order.order_status_id = updates['order_status_id']        """

                    try:

            if 'shipping_address' in updates:            order = self.get_orders(order_id)

                existing_order.shipping_address = updates['shipping_address']            if not order:

                            self.logger.warning(f"Attempt to update status of non-existent order ID {order_id}")

            if 'total_amount' in updates:                return None, f"No order found with ID {order_id}"

                existing_order.total_amount = updates['total_amount']            

                        # Validate status transition

            # Validate updated order            if not self._is_valid_status_transition(order.status, new_status):

            validation_errors = self.validate_order_data(existing_order)                self.logger.warning(f"Invalid status transition for order {order_id}: {order.status.value} -> {new_status.value}")

            if validation_errors:                return None, f"Invalid status transition from {order.status.value} to {new_status.value}"

                self.logger.warning(f"Order validation failed: {'; '.join(validation_errors)}")            

                return None            # Update status

                        order.status = new_status

            # Save updated order            

            updated_order = self.repository.update(existing_order)            # Update order in database

                        all_orders = load_models_from_json(self.db_path, Order)

            if updated_order:            for i, o in enumerate(all_orders):

                self.logger.info(f"Order updated successfully: {order_id}")                if o.id == order_id:

            else:                    all_orders[i] = order

                self.logger.error(f"Failed to update order {order_id}")                    break

                        

            return updated_order            save_models_to_json(all_orders, self.db_path)

                        

        except Exception as e:            self.logger.info(f"Order {order_id} status updated to {new_status.value}")

            self.logger.error(f"Error updating order: {e}", exc_info=EXC_INFO_LOG_ERRORS)            return order, None

            return None        except Exception as e:

            self.logger.error(f"Error updating order status for {order_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)

    # ============ ORDER DELETION ============            return None, f"Failed to update order status: {str(e)}"

    def delete_order(self, order_id: int) -> bool:

        """    def cancel_order(self, order_id: int) -> Tuple[Optional[Order], Optional[str]]:

        Delete an order by ID (only if status allows).        """

                Cancel an order if possible.

        Args:        

            order_id: ID of order to delete        Args:

                        order_id (int): ID of the order to cancel

        Returns:            

            True on success, False on failure        Returns:

        """            tuple: (Order, None) on success, (None, error_message) on failure

        try:        """

            order = self.repository.get_by_id(order_id)        try:

            if not order:            order = self.get_orders(order_id)

                self.logger.warning(f"Attempt to delete non-existent order {order_id}")            if not order:

                return False                self.logger.warning(f"Attempt to cancel non-existent order ID {order_id}")

                            return None, f"No order found with ID {order_id}"

            # Check if order can be deleted based on status            

            # Only allow deletion of pending or cancelled orders            # Check if order can be cancelled

            deletable_statuses = ['Pending', 'Cancelled']            if order.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:

            if hasattr(order, 'status') and hasattr(order.status, 'status'):                self.logger.warning(f"Attempt to cancel order {order_id} with status {order.status.value}")

                if order.status.status not in deletable_statuses:                return None, f"Cannot cancel order with status: {order.status.value}"

                    self.logger.warning(f"Cannot delete order {order_id} with status {order.status.status}")            

                    return False            return self.update_order_status(order_id, OrderStatus.CANCELLED)

                        

            deleted = self.repository.delete(order_id)        except Exception as e:

                        self.logger.error(f"Error cancelling order {order_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)

            if deleted:            return None, f"Failed to cancel order: {str(e)}"

                self.logger.info(f"Order deleted successfully: {order_id}")

            else:    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:

                self.logger.error(f"Failed to delete order {order_id}")        """

                    Get all orders with specific status.

            return deleted        

                    Args:

        except Exception as e:            status (OrderStatus): Status to filter by

            self.logger.error(f"Error deleting order: {e}", exc_info=EXC_INFO_LOG_ERRORS)            

            return False        Returns:

            list[Order]: List of orders with the specified status

    # ============ ORDER STATUS MANAGEMENT ============        """

    def update_order_status(self, order_id: int, status_id: int) -> Optional[Order]:        try:

        """            all_orders = load_models_from_json(self.db_path, Order)

        Update order status.            return [order for order in all_orders if order.status == status]

                    

        Args:        except Exception as e:

            order_id: Order ID to update            self.logger.error(f"Error getting orders by status {status.value}: {e}", exc_info=EXC_INFO_LOG_ERRORS)

            status_id: New status ID            return []

            

        Returns:    # ============ ACCESS CONTROL METHODS ============

            Updated Order object or None on error

        """    def check_user_access(self, current_user, is_admin, order_id=None, user_id=None):

        return self.update_order(order_id, order_status_id=status_id)        """

            Check if current user can access the specified order or user's orders

    def get_status_by_name(self, status_name: str) -> Optional[OrderStatus]:        

        """        Args:

        Get order status by name.            current_user: Current authenticated user object

                    is_admin (bool): Whether current user is admin

        Args:            order_id (int, optional): Order ID to check access for

            status_name: Status name to search for            user_id (int, optional): User ID to check access for

                        

        Returns:        Returns:

            OrderStatus object or None if not found            bool: True if access allowed, False otherwise

        """        """

        return self.repository.get_status_by_name(status_name)        # Admins can access any order, regular users only their own

        if is_admin:

    # ============ VALIDATION HELPERS ============            return True

    def validate_order_data(self, order: Order) -> List[str]:        

        """        if order_id:

        Validate order data.            # Check if order belongs to current user

                    order = self.get_orders(order_id)

        Args:            if order:

            order: Order object to validate                return current_user.id == order.user_id

                        return False

        Returns:        

            List of validation error messages (empty if valid)        if user_id:

        """            return current_user.id == user_id

        errors = []            

                return False

        # Validate required fields

        if not hasattr(order, 'cart_id') or order.cart_id is None:    # ============ PRIVATE HELPER METHODS ============

            errors.append("cart_id is required")

            def _is_valid_status_transition(self, current_status: OrderStatus, new_status: OrderStatus) -> bool:

        if not hasattr(order, 'user_id') or order.user_id is None:        """

            errors.append("user_id is required")        Validate if status transition is allowed.

                

        if not hasattr(order, 'order_status_id') or order.order_status_id is None:        Args:

            errors.append("order_status_id is required")            current_status (OrderStatus): Current order status

                    new_status (OrderStatus): Proposed new status

        if not hasattr(order, 'total_amount') or order.total_amount is None:            

            errors.append("total_amount is required")        Returns:

        elif order.total_amount < 0:            bool: True if transition is valid, False otherwise

            errors.append("total_amount must be non-negative")        """

                # Define valid transitions

        # Validate items if present        valid_transitions = {

        if hasattr(order, 'items') and order.items:            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],

            if len(order.items) == 0:            OrderStatus.CONFIRMED: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],

                errors.append("Order must have at least one item")            OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],

                        OrderStatus.SHIPPED: [OrderStatus.DELIVERED],

            for idx, item in enumerate(order.items):            OrderStatus.DELIVERED: [],  # Final state

                if not hasattr(item, 'product_id') or item.product_id is None:            OrderStatus.CANCELLED: []   # Final state

                    errors.append(f"Item {idx}: product_id is required")        }

                        

                if not hasattr(item, 'quantity') or item.quantity is None:        return new_status in valid_transitions.get(current_status, [])

                    errors.append(f"Item {idx}: quantity is required")

                elif item.quantity <= 0:    def validate_order_data(self, order: Order) -> List[str]:

                    errors.append(f"Item {idx}: quantity must be positive")        """

                        Validate order against business rules.

                if not hasattr(item, 'amount') or item.amount is None:        

                    errors.append(f"Item {idx}: amount is required")        Args:

                elif item.amount < 0:            order (Order): Order to validate

                    errors.append(f"Item {idx}: amount must be non-negative")            

                Returns:

        return errors            list[str]: List of validation error messages, empty if valid

            """

    def order_exists_by_cart(self, cart_id: int) -> bool:        errors = []

        """        

        Check if an order exists for a cart.        # Check items

                if not order.items:

        Args:            errors.append("Order must contain at least one item")

            cart_id: Cart ID to check        

                    # Check total amount

        Returns:        if order.total_amount <= 0:

            True if exists, False otherwise            errors.append("Order total must be greater than 0")

        """        

        return self.repository.exists_by_cart_id(cart_id)        # Check individual items

        for item in order.items:
            if item.quantity <= 0:
                errors.append(f"Item {item.product_name} must have quantity greater than 0")
            if item.price < 0:
                errors.append(f"Item {item.product_name} cannot have negative price")
        
        return errors

    # ============ PRIVATE HELPER METHODS ============
    # (Service layer uses shared utilities for data persistence)
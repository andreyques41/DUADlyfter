"""
Order Repository Module

Handles all database operations for Order and OrderItem models using SQLAlchemy ORM.
Provides CRUD operations and query methods for order management.

Responsibilities:
- Database queries and operations (SELECT, INSERT, UPDATE, DELETE)
- Order lookups by different fields (id, user_id, cart_id)
- Advanced filtering capabilities (status, date range)
- Transaction management via session_scope

Usage:
    repo = OrderRepository()
    order = repo.get_by_id(1)
    user_orders = repo.get_by_user_id(1)
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from app.core.database import session_scope
from app.sales.models.order import Order, OrderItem, OrderStatus
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OrderRepository:
    """Repository for Order database operations."""
    
    def get_by_id(self, order_id: int) -> Optional[Order]:
        """
        Get order by ID.
        
        Args:
            order_id: Order ID to search for
            
        Returns:
            Order object or None if not found
        """
        try:
            with session_scope() as session:
                return session.query(Order).filter_by(id=order_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching order by id {order_id}: {e}")
            return None
    
    def get_by_user_id(self, user_id: int) -> List[Order]:
        """
        Get all orders for a specific user.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            List of Order objects
        """
        try:
            with session_scope() as session:
                return session.query(Order).filter_by(user_id=user_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching orders by user_id {user_id}: {e}")
            return []
    
    def get_by_cart_id(self, cart_id: int) -> Optional[Order]:
        """
        Get order by cart ID.
        
        Args:
            cart_id: Cart ID to search for
            
        Returns:
            Order object or None if not found
        """
        try:
            with session_scope() as session:
                return session.query(Order).filter_by(cart_id=cart_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching order by cart_id {cart_id}: {e}")
            return None
    
    def get_all(self) -> List[Order]:
        """
        Get all orders.
        
        Returns:
            List of all Order objects
        """
        try:
            with session_scope() as session:
                return session.query(Order).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching all orders: {e}")
            return []
    
    def get_by_filters(self, filters: Dict[str, Any]) -> List[Order]:
        """
        Get orders by filters.
        
        Args:
            filters: Dictionary with filter criteria
                - user_id: int
                - status_id: int
                - order_status_id: int (alias for status_id)
                - start_date: datetime
                - end_date: datetime
                - min_amount: float
                - max_amount: float
                
        Returns:
            List of filtered Order objects
        """
        try:
            with session_scope() as session:
                query = session.query(Order)
                
                # Apply filters
                if 'user_id' in filters:
                    query = query.filter(Order.user_id == filters['user_id'])
                
                if 'status_id' in filters:
                    query = query.filter(Order.order_status_id == filters['status_id'])
                
                if 'order_status_id' in filters:
                    query = query.filter(Order.order_status_id == filters['order_status_id'])
                
                if 'start_date' in filters:
                    query = query.filter(Order.created_at >= filters['start_date'])
                
                if 'end_date' in filters:
                    query = query.filter(Order.created_at <= filters['end_date'])
                
                if 'min_amount' in filters:
                    query = query.filter(Order.total_amount >= filters['min_amount'])
                
                if 'max_amount' in filters:
                    query = query.filter(Order.total_amount <= filters['max_amount'])
                
                return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching orders with filters: {e}")
            return []
    
    def create(self, order: Order) -> Optional[Order]:
        """
        Create a new order in the database.
        
        Args:
            order: Order object to create (without ID)
            
        Returns:
            Created Order object with ID, or None on error
        """
        try:
            with session_scope() as session:
                session.add(order)
                session.flush()  # Get the ID before commit
                session.refresh(order)  # Refresh to load relationships
                return order
        except SQLAlchemyError as e:
            logger.error(f"Error creating order for user {order.user_id}: {e}")
            return None
    
    def update(self, order: Order) -> Optional[Order]:
        """
        Update an existing order.
        
        Args:
            order: Order object with updated data
            
        Returns:
            Updated Order object or None on error
        """
        try:
            with session_scope() as session:
                # Merge the detached order object into the session
                updated_order = session.merge(order)
                session.flush()
                session.refresh(updated_order)
                return updated_order
        except SQLAlchemyError as e:
            logger.error(f"Error updating order {order.id}: {e}")
            return None
    
    def delete(self, order_id: int) -> bool:
        """
        Delete an order by ID.
        
        Args:
            order_id: ID of order to delete
            
        Returns:
            True if deleted, False on error or not found
        """
        try:
            with session_scope() as session:
                order = session.query(Order).filter_by(id=order_id).first()
                if order:
                    session.delete(order)
                    return True
                return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting order {order_id}: {e}")
            return False
    
    def get_status_by_name(self, status_name: str) -> Optional[OrderStatus]:
        """
        Get order status by name.
        
        Args:
            status_name: Status name to search for
            
        Returns:
            OrderStatus object or None if not found
        """
        try:
            with session_scope() as session:
                return session.query(OrderStatus).filter_by(status=status_name).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching order status {status_name}: {e}")
            return None
    
    def exists_by_cart_id(self, cart_id: int) -> bool:
        """
        Check if an order exists for a cart.
        
        Args:
            cart_id: Cart ID to check
            
        Returns:
            True if exists, False otherwise
        """
        try:
            with session_scope() as session:
                return session.query(Order).filter_by(cart_id=cart_id).first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking if order exists for cart {cart_id}: {e}")
            return False

"""
Return Repository Module

Handles all database operations for Return and ReturnItem models using SQLAlchemy ORM.
Provides CRUD operations and query methods for return management.

Responsibilities:
- Database queries and operations (SELECT, INSERT, UPDATE, DELETE)
- Return lookups by different fields (id, order_id, user_id)
- Advanced filtering capabilities (status)
- Transaction management via session_scope

Usage:
    repo = ReturnRepository()
    return_obj = repo.get_by_order_id(1)
    user_returns = repo.get_by_user_id(1)
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_db
from app.sales.models.returns import Return, ReturnItem, ReturnStatus
import logging

logger = logging.getLogger(__name__)


class ReturnRepository:
    """Repository for Return database operations."""
    
    def get_by_id(self, return_id: int) -> Optional[Return]:
        """
        Get return by ID.
        
        Args:
            return_id: Return ID to search for
            
        Returns:
            Return object or None if not found
        """
        try:
            db = get_db()
            return db.query(Return).filter_by(id=return_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching return by id {return_id}: {e}")
            return None
    
    def get_by_order_id(self, order_id: int) -> List[Return]:
        """
        Get all returns for a specific order.
        
        Args:
            order_id: Order ID to search for
            
        Returns:
            List of Return objects
        """
        try:
            db = get_db()
            return db.query(Return).filter_by(order_id=order_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching returns by order_id {order_id}: {e}")
            return []
    
    def get_by_user_id(self, user_id: int) -> List[Return]:
        """
        Get all returns for a specific user.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            List of Return objects
        """
        try:
            db = get_db()
            return db.query(Return).filter_by(user_id=user_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching returns by user_id {user_id}: {e}")
            return []
    
    def get_all(self) -> List[Return]:
        """
        Get all returns.
        
        Returns:
            List of all Return objects
        """
        try:
            db = get_db()
            return db.query(Return).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching all returns: {e}")
            return []
    
    def get_by_filters(self, filters: Dict[str, Any]) -> List[Return]:
        """
        Get returns by filters.
        
        Args:
            filters: Dictionary with filter criteria
                - user_id: int
                - order_id: int
                - status_id: int
                - return_status_id: int (alias for status_id)
                - start_date: datetime
                - end_date: datetime
                - min_amount: float
                - max_amount: float
                
        Returns:
            List of filtered Return objects
        """
        try:
            db = get_db()
            query = db.query(Return)
            
            # Apply filters
            if 'user_id' in filters:
                query = query.filter(Return.user_id == filters['user_id'])
            
            if 'order_id' in filters:
                query = query.filter(Return.order_id == filters['order_id'])
            
            if 'status_id' in filters:
                query = query.filter(Return.return_status_id == filters['status_id'])
            
            if 'return_status_id' in filters:
                query = query.filter(Return.return_status_id == filters['return_status_id'])
            
            if 'start_date' in filters:
                query = query.filter(Return.created_at >= filters['start_date'])
            
            if 'end_date' in filters:
                query = query.filter(Return.created_at <= filters['end_date'])
            
            if 'min_amount' in filters:
                query = query.filter(Return.total_amount >= filters['min_amount'])
            
            if 'max_amount' in filters:
                query = query.filter(Return.total_amount <= filters['max_amount'])
            
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching returns with filters: {e}")
            return []
    
    def create(self, return_obj: Return) -> Optional[Return]:
        """
        Create a new return in the database.
        
        Args:
            return_obj: Return object to create (without ID)
            
        Returns:
            Created Return object with ID, or None on error
        """
        try:
            db = get_db()
            db.add(return_obj)
            db.flush()  # Get the ID before commit
            db.refresh(return_obj)  # Refresh to load relationships
            return return_obj
        except SQLAlchemyError as e:
            logger.error(f"Error creating return for order {return_obj.order_id}: {e}")
            return None
    
    def update(self, return_obj: Return) -> Optional[Return]:
        """
        Update an existing return.
        
        Args:
            return_obj: Return object with updated data
            
        Returns:
            Updated Return object or None on error
        """
        try:
            db = get_db()
            # Merge the detached return object into the session
            updated_return = db.merge(return_obj)
            db.flush()
            db.refresh(updated_return)
            return updated_return
        except SQLAlchemyError as e:
            logger.error(f"Error updating return {return_obj.id}: {e}")
            return None
    
    def delete(self, return_id: int) -> bool:
        """
        Delete a return by ID.
        
        Args:
            return_id: ID of return to delete
            
        Returns:
            True if deleted, False on error or not found
        """
        try:
            db = get_db()
            return_obj = db.query(Return).filter_by(id=return_id).first()
            if return_obj:
                db.delete(return_obj)
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting return {return_id}: {e}")
            return False
    
    def get_status_by_name(self, status_name: str) -> Optional[ReturnStatus]:
        """
        Get return status by name.
        
        Args:
            status_name: Status name to search for
            
        Returns:
            ReturnStatus object or None if not found
        """
        try:
            db = get_db()
            return db.query(ReturnStatus).filter_by(status=status_name).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching return status {status_name}: {e}")
            return None


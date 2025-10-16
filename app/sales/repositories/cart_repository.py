"""
Cart Repository Module

Handles all database operations for Cart and CartItem models using SQLAlchemy ORM.
Provides CRUD operations and query methods for cart management.

Responsibilities:
- Database queries and operations (SELECT, INSERT, UPDATE, DELETE)
- Cart lookups by different fields (id, user_id)
- Cart item management
- Transaction management via session_scope

Usage:
    repo = CartRepository()
    cart = repo.get_by_user_id(1)
    all_carts = repo.get_all()
"""
from typing import Optional, List
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_db
from app.sales.models.cart import Cart, CartItem
import logging

logger = logging.getLogger(__name__)


class CartRepository:
    """Repository for Cart database operations."""
    
    def get_by_id(self, cart_id: int) -> Optional[Cart]:
        """
        Get cart by ID.
        
        Args:
            cart_id: Cart ID to search for
            
        Returns:
            Cart object or None if not found
        """
        try:
            db = get_db()
            return db.query(Cart).filter_by(id=cart_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching cart by id {cart_id}: {e}")
            return None
    
    def get_by_user_id(self, user_id: int) -> Optional[Cart]:
        """
        Get cart by user ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            Cart object or None if not found
        """
        try:
            db = get_db()
            return db.query(Cart).filter_by(user_id=user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching cart by user_id {user_id}: {e}")
            return None
    
    def get_all(self) -> List[Cart]:
        """
        Get all carts.
        
        Returns:
            List of all Cart objects
        """
        try:
            db = get_db()
            return db.query(Cart).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching all carts: {e}")
            return []
    
    def create(self, cart: Cart) -> Optional[Cart]:
        """
        Create a new cart in the database.
        
        Args:
            cart: Cart object to create (without ID)
            
        Returns:
            Created Cart object with ID, or None on error
        """
        try:
            db = get_db()
            db.add(cart)
            db.flush()  # Get the ID before commit
            db.refresh(cart)  # Refresh to load relationships
            return cart
        except SQLAlchemyError as e:
            logger.error(f"Error creating cart for user {cart.user_id}: {e}")
            return None
    
    def update(self, cart: Cart) -> Optional[Cart]:
        """
        Update an existing cart.
        
        Args:
            cart: Cart object with updated data
            
        Returns:
            Updated Cart object or None on error
        """
        try:
            db = get_db()
            # Merge the detached cart object into the session
            updated_cart = db.merge(cart)
            db.flush()
            db.refresh(updated_cart)
            return updated_cart
        except SQLAlchemyError as e:
            logger.error(f"Error updating cart {cart.id}: {e}")
            return None
    
    def delete(self, cart_id: int) -> bool:
        """
        Delete a cart by ID.
        
        Args:
            cart_id: ID of cart to delete
            
        Returns:
            True if deleted, False on error or not found
        """
        try:
            db = get_db()
            cart = db.query(Cart).filter_by(id=cart_id).first()
            if cart:
                db.delete(cart)
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting cart {cart_id}: {e}")
            return False
    
    def delete_by_user_id(self, user_id: int) -> bool:
        """
        Delete a cart by user ID.
        
        Args:
            user_id: User ID whose cart to delete
            
        Returns:
            True if deleted, False on error or not found
        """
        try:
            db = get_db()
            cart = db.query(Cart).filter_by(user_id=user_id).first()
            if cart:
                db.delete(cart)
                return True
            return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting cart for user {user_id}: {e}")
            return False
    
    def finalize_cart(self, cart_id: int) -> Optional[Cart]:
        """
        Mark a cart as finalized (ready for checkout).
        
        Args:
            cart_id: ID of cart to finalize
            
        Returns:
            Updated Cart object or None on error
        """
        try:
            db = get_db()
            cart = db.query(Cart).filter_by(id=cart_id).first()
            if cart:
                cart.finalized = True
                db.flush()
                db.refresh(cart)
                return cart
            return None
        except SQLAlchemyError as e:
            logger.error(f"Error finalizing cart {cart_id}: {e}")
            return None
    
    def exists_by_user_id(self, user_id: int) -> bool:
        """
        Check if a cart exists for a user.
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if exists, False otherwise
        """
        try:
            db = get_db()
            return db.query(Cart).filter_by(user_id=user_id).first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking if cart exists for user {user_id}: {e}")
            return False


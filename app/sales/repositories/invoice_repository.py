"""
Invoice Repository Module

Handles all database operations for Invoice model using SQLAlchemy ORM.
Provides CRUD operations and query methods for invoice management.

Responsibilities:
- Database queries and operations (SELECT, INSERT, UPDATE, DELETE)
- Invoice lookups by different fields (id, order_id, user_id)
- Advanced filtering capabilities (status)
- Transaction management via session_scope

Usage:
    repo = InvoiceRepository()
    invoice = repo.get_by_order_id(1)
    user_invoices = repo.get_by_user_id(1)
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import session_scope
from app.sales.models.invoice import Invoice, InvoiceStatus
import logging

logger = logging.getLogger(__name__)


class InvoiceRepository:
    """Repository for Invoice database operations."""
    
    def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
        """
        Get invoice by ID.
        
        Args:
            invoice_id: Invoice ID to search for
            
        Returns:
            Invoice object or None if not found
        """
        try:
            with session_scope() as session:
                return session.query(Invoice).filter_by(id=invoice_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching invoice by id {invoice_id}: {e}")
            return None
    
    def get_by_order_id(self, order_id: int) -> Optional[Invoice]:
        """
        Get invoice by order ID.
        
        Args:
            order_id: Order ID to search for
            
        Returns:
            Invoice object or None if not found
        """
        try:
            with session_scope() as session:
                return session.query(Invoice).filter_by(order_id=order_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching invoice by order_id {order_id}: {e}")
            return None
    
    def get_by_user_id(self, user_id: int) -> List[Invoice]:
        """
        Get all invoices for a specific user.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            List of Invoice objects
        """
        try:
            with session_scope() as session:
                return session.query(Invoice).filter_by(user_id=user_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching invoices by user_id {user_id}: {e}")
            return []
    
    def get_all(self) -> List[Invoice]:
        """
        Get all invoices.
        
        Returns:
            List of all Invoice objects
        """
        try:
            with session_scope() as session:
                return session.query(Invoice).all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching all invoices: {e}")
            return []
    
    def get_by_filters(self, filters: Dict[str, Any]) -> List[Invoice]:
        """
        Get invoices by filters.
        
        Args:
            filters: Dictionary with filter criteria
                - user_id: int
                - status_id: int
                - invoice_status_id: int (alias for status_id)
                - start_date: datetime
                - end_date: datetime
                - min_amount: float
                - max_amount: float
                - overdue: bool (due_date < now and status != paid)
                
        Returns:
            List of filtered Invoice objects
        """
        try:
            with session_scope() as session:
                query = session.query(Invoice)
                
                # Apply filters
                if 'user_id' in filters:
                    query = query.filter(Invoice.user_id == filters['user_id'])
                
                if 'status_id' in filters:
                    query = query.filter(Invoice.invoice_status_id == filters['status_id'])
                
                if 'invoice_status_id' in filters:
                    query = query.filter(Invoice.invoice_status_id == filters['invoice_status_id'])
                
                if 'start_date' in filters:
                    query = query.filter(Invoice.created_at >= filters['start_date'])
                
                if 'end_date' in filters:
                    query = query.filter(Invoice.created_at <= filters['end_date'])
                
                if 'min_amount' in filters:
                    query = query.filter(Invoice.total_amount >= filters['min_amount'])
                
                if 'max_amount' in filters:
                    query = query.filter(Invoice.total_amount <= filters['max_amount'])
                
                if 'overdue' in filters and filters['overdue']:
                    from datetime import datetime
                    # Assuming 'Paid' status has specific name - adjust as needed
                    query = query.filter(Invoice.due_date < datetime.utcnow())
                
                return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching invoices with filters: {e}")
            return []
    
    def create(self, invoice: Invoice) -> Optional[Invoice]:
        """
        Create a new invoice in the database.
        
        Args:
            invoice: Invoice object to create (without ID)
            
        Returns:
            Created Invoice object with ID, or None on error
        """
        try:
            with session_scope() as session:
                session.add(invoice)
                session.flush()  # Get the ID before commit
                session.refresh(invoice)  # Refresh to load relationships
                return invoice
        except SQLAlchemyError as e:
            logger.error(f"Error creating invoice for order {invoice.order_id}: {e}")
            return None
    
    def update(self, invoice: Invoice) -> Optional[Invoice]:
        """
        Update an existing invoice.
        
        Args:
            invoice: Invoice object with updated data
            
        Returns:
            Updated Invoice object or None on error
        """
        try:
            with session_scope() as session:
                # Merge the detached invoice object into the session
                updated_invoice = session.merge(invoice)
                session.flush()
                session.refresh(updated_invoice)
                return updated_invoice
        except SQLAlchemyError as e:
            logger.error(f"Error updating invoice {invoice.id}: {e}")
            return None
    
    def delete(self, invoice_id: int) -> bool:
        """
        Delete an invoice by ID.
        
        Args:
            invoice_id: ID of invoice to delete
            
        Returns:
            True if deleted, False on error or not found
        """
        try:
            with session_scope() as session:
                invoice = session.query(Invoice).filter_by(id=invoice_id).first()
                if invoice:
                    session.delete(invoice)
                    return True
                return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting invoice {invoice_id}: {e}")
            return False
    
    def get_status_by_name(self, status_name: str) -> Optional[InvoiceStatus]:
        """
        Get invoice status by name.
        
        Args:
            status_name: Status name to search for
            
        Returns:
            InvoiceStatus object or None if not found
        """
        try:
            with session_scope() as session:
                return session.query(InvoiceStatus).filter_by(name=status_name).first()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching invoice status {status_name}: {e}")
            return None
    
    def exists_by_order_id(self, order_id: int) -> bool:
        """
        Check if an invoice exists for an order.
        
        Args:
            order_id: Order ID to check
            
        Returns:
            True if exists, False otherwise
        """
        try:
            with session_scope() as session:
                return session.query(Invoice).filter_by(order_id=order_id).first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking if invoice exists for order {order_id}: {e}")
            return False

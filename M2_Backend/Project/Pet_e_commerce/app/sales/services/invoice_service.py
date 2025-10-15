"""
Invoice Service Module

This module provides comprehensive invoice management functionality including:
- CRUD operations for invoices (Create, Read, Update, Delete)
- Invoice status management and validation
- Business logic for invoice calculations and due dates
- Uses InvoiceRepository for data access layer

Used by: Invoice routes for API operations
Dependencies: Invoice models, InvoiceRepository
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
from config.logging import EXC_INFO_LOG_ERRORS
from app.sales.repositories.invoice_repository import InvoiceRepository
from app.sales.models.invoice import Invoice, InvoiceStatus

logger = logging.getLogger(__name__)


class InvoiceService:
    """
    Service class for invoice management operations.
    Handles all business logic for invoice CRUD operations, status management,
    and data validation. Provides a clean interface for routes.
    """

    def __init__(self):
        """Initialize invoice service with InvoiceRepository."""
        self.repository = InvoiceRepository()
        self.logger = logger

    # ============ INVOICE RETRIEVAL METHODS ============
    def get_invoice_by_id(self, invoice_id: int) -> Optional[Invoice]:
        """
        Retrieve invoice by ID.
        
        Args:
            invoice_id: Invoice ID to retrieve
            
        Returns:
            Invoice object or None if not found
        """
        return self.repository.get_by_id(invoice_id)
    
    def get_invoice_by_order_id(self, order_id: int) -> Optional[Invoice]:
        """
        Retrieve invoice by order ID.
        
        Args:
            order_id: Order ID to retrieve invoice for
            
        Returns:
            Invoice object or None if not found
        """
        return self.repository.get_by_order_id(order_id)
    
    def get_invoices_by_user_id(self, user_id: int) -> List[Invoice]:
        """
        Retrieve all invoices for a specific user.
        
        Args:
            user_id: User ID to retrieve invoices for
            
        Returns:
            List of Invoice objects
        """
        return self.repository.get_by_user_id(user_id)
    
    def get_all_invoices(self) -> List[Invoice]:
        """
        Retrieve all invoices.
        
        Returns:
            List of all Invoice objects
        """
        return self.repository.get_all()
    
    def get_invoices_by_filters(self, filters: Dict[str, Any]) -> List[Invoice]:
        """
        Retrieve invoices by filters.
        
        Args:
            filters: Dictionary with filter criteria
            
        Returns:
            List of filtered Invoice objects
        """
        return self.repository.get_by_filters(filters)

    # ============ INVOICE CREATION ============
    def create_invoice(self, **invoice_data) -> Optional[Invoice]:
        """
        Create a new invoice with validation.
        
        Args:
            **invoice_data: Invoice fields (order_id, user_id, total_amount, etc.)
            
        Returns:
            Created Invoice object or None on error
        """
        try:
            # Validate required fields
            if not invoice_data.get('order_id'):
                self.logger.error("Cannot create invoice without order_id")
                return None
            
            if not invoice_data.get('user_id'):
                self.logger.error("Cannot create invoice without user_id")
                return None
            
            # Check if invoice already exists for this order
            existing_invoice = self.repository.get_by_order_id(invoice_data['order_id'])
            if existing_invoice:
                self.logger.warning(f"Invoice already exists for order {invoice_data['order_id']}")
                return None
            
            # Set defaults
            invoice_data.setdefault('created_at', datetime.utcnow())
            
            # Set due date if not provided (default 30 days)
            if 'due_date' not in invoice_data or invoice_data['due_date'] is None:
                invoice_data['due_date'] = invoice_data['created_at'] + timedelta(days=30)
            
            # Create Invoice instance
            invoice = Invoice(**invoice_data)
            
            # Validate invoice data
            validation_errors = self.validate_invoice_data(invoice)
            if validation_errors:
                self.logger.warning(f"Invoice validation failed: {'; '.join(validation_errors)}")
                return None
            
            # Save to database
            created_invoice = self.repository.create(invoice)
            
            if created_invoice:
                self.logger.info(f"Invoice created successfully: {created_invoice.id}")
            else:
                self.logger.error("Failed to create invoice")
            
            return created_invoice
            
        except Exception as e:
            self.logger.error(f"Error creating invoice: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return None

    # ============ INVOICE UPDATE ============
    def update_invoice(self, invoice_id: int, **updates) -> Optional[Invoice]:
        """
        Update an existing invoice with new data.
        
        Args:
            invoice_id: Invoice ID to update
            **updates: Fields to update (total_amount, status, due_date, etc.)
            
        Returns:
            Updated Invoice object or None on error
        """
        try:
            existing_invoice = self.repository.get_by_id(invoice_id)
            if not existing_invoice:
                self.logger.warning(f"Attempt to update non-existent invoice {invoice_id}")
                return None
            
            # Update fields
            if 'total_amount' in updates:
                existing_invoice.total_amount = updates['total_amount']
            
            if 'invoice_status_id' in updates:
                existing_invoice.invoice_status_id = updates['invoice_status_id']
            
            if 'due_date' in updates:
                existing_invoice.due_date = updates['due_date']
            
            # Validate updated invoice
            validation_errors = self.validate_invoice_data(existing_invoice)
            if validation_errors:
                self.logger.warning(f"Invoice validation failed: {'; '.join(validation_errors)}")
                return None
            
            # Save updated invoice
            updated_invoice = self.repository.update(existing_invoice)
            
            if updated_invoice:
                self.logger.info(f"Invoice updated successfully: {invoice_id}")
            else:
                self.logger.error(f"Failed to update invoice {invoice_id}")
            
            return updated_invoice
            
        except Exception as e:
            self.logger.error(f"Error updating invoice: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return None

    # ============ INVOICE DELETION ============
    def delete_invoice(self, invoice_id: int) -> bool:
        """
        Delete an invoice by ID.
        
        Args:
            invoice_id: ID of invoice to delete
            
        Returns:
            True on success, False on failure
        """
        try:
            invoice = self.repository.get_by_id(invoice_id)
            if not invoice:
                self.logger.warning(f"Attempt to delete non-existent invoice {invoice_id}")
                return False
            
            deleted = self.repository.delete(invoice_id)
            
            if deleted:
                self.logger.info(f"Invoice deleted successfully: {invoice_id}")
            else:
                self.logger.error(f"Failed to delete invoice {invoice_id}")
            
            return deleted
            
        except Exception as e:
            self.logger.error(f"Error deleting invoice: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return False

    # ============ INVOICE STATUS MANAGEMENT ============
    def update_invoice_status(self, invoice_id: int, status_id: int) -> Optional[Invoice]:
        """
        Update invoice status.
        
        Args:
            invoice_id: Invoice ID to update
            status_id: New status ID
            
        Returns:
            Updated Invoice object or None on error
        """
        return self.update_invoice(invoice_id, invoice_status_id=status_id)
    
    def get_status_by_name(self, status_name: str) -> Optional[InvoiceStatus]:
        """
        Get invoice status by name.
        
        Args:
            status_name: Status name to search for
            
        Returns:
            InvoiceStatus object or None if not found
        """
        return self.repository.get_status_by_name(status_name)

    # ============ VALIDATION HELPERS ============
    def validate_invoice_data(self, invoice: Invoice) -> List[str]:
        """
        Validate invoice data.
        
        Args:
            invoice: Invoice object to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate required fields
        if not hasattr(invoice, 'order_id') or invoice.order_id is None:
            errors.append("order_id is required")
        
        if not hasattr(invoice, 'user_id') or invoice.user_id is None:
            errors.append("user_id is required")
        
        if not hasattr(invoice, 'invoice_status_id') or invoice.invoice_status_id is None:
            errors.append("invoice_status_id is required")
        
        if not hasattr(invoice, 'total_amount') or invoice.total_amount is None:
            errors.append("total_amount is required")
        elif invoice.total_amount < 0:
            errors.append("total_amount must be non-negative")
        
        # Validate dates
        if hasattr(invoice, 'due_date') and hasattr(invoice, 'created_at'):
            if invoice.due_date and invoice.created_at:
                if invoice.due_date < invoice.created_at:
                    errors.append("due_date cannot be before created_at")
        
        return errors
    
    def invoice_exists_by_order(self, order_id: int) -> bool:
        """
        Check if an invoice exists for an order.
        
        Args:
            order_id: Order ID to check
            
        Returns:
            True if exists, False otherwise
        """
        return self.repository.exists_by_order_id(order_id)

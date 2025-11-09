"""
Invoice Controller Module

HTTP request processing layer for invoice operations.
Delegates to InvoiceService for business logic.

Responsibilities:
- Request validation and deserialization
- HTTP response formatting
- Error handling and logging
- Access control verification
- Cache-aware data retrieval

Dependencies:
- InvoiceService: Business logic and caching
- Flask request/g: Request context
- Marshmallow schemas: Validation
- Auth helpers: Access control

Usage:
    controller = InvoiceController()
    response, status = controller.get_list()
    response, status = controller.get(invoice_id=123)
"""
import logging
from flask import request, jsonify, g
from marshmallow import ValidationError
from typing import Tuple, Optional
from config.logging import get_logger, EXC_INFO_LOG_ERRORS
from app.core.lib.error_utils import error_response

# Service imports
from app.sales.services.invoice_service import InvoiceService

# Schema imports
from app.sales.schemas.invoice_schema import (
    invoice_registration_schema,
    invoice_update_schema,
    invoice_status_update_schema,
    invoice_response_schema,
    invoices_response_schema
)

# Auth imports
from app.core.lib.auth import is_admin_user, is_user_or_admin

# Model imports
from app.sales.models.invoice import InvoiceStatus

logger = get_logger(__name__)


class InvoiceController:
    """Controller for invoice HTTP operations."""
    
    def __init__(self):
        """Initialize invoice controller with service dependency."""
        self.invoice_service = InvoiceService()
        self.logger = logger
    
    # ============================================
    # PRIVATE HELPER METHODS
    # ============================================
    
    def _check_invoice_access(self, user_id: int) -> Optional[Tuple[dict, int]]:
        """
        Check if current user has access to the specified user's invoice.
        Returns error response if access denied, None if access granted.
        
        Args:
            user_id: ID of the user whose invoice is being accessed
            
        Returns:
            None if access granted, or (error_response, status_code) if denied
        """
        if not is_user_or_admin(user_id):
            self.logger.warning(f"Access denied for user {g.current_user.id} to invoice for user {user_id}")
            return jsonify({"error": "Access denied"}), 403
        return None
    
    # ============================================
    # INVOICE CRUD OPERATIONS
    # ============================================
    
    def get_list(self) -> Tuple[dict, int]:
        """
        Get invoices collection - auto-filtered based on user role.
        - Admins: See all invoices
        - Users: See only their own invoices
        
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            if is_admin_user():
                # Admin: Return all invoices (cached) - already serialized
                invoices = self.invoice_service.get_all_invoices_cached()
                self.logger.info(f"Admin retrieved all invoices (total: {len(invoices)})")
            else:
                # Customer: Return own invoices (cached) - already serialized
                invoices = self.invoice_service.get_invoices_by_user_id_cached(g.current_user.id)
                self.logger.info(f"Invoices retrieved for user {g.current_user.id} (total: {len(invoices)})")
            
            return jsonify({
                "total_invoices": len(invoices),
                "invoices": invoices
            }), 200
            
        except Exception as e:
            self.logger.error(f"Error retrieving invoices: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to retrieve invoices", e)
    
    def get(self, invoice_id: int) -> Tuple[dict, int]:
        """
        Get specific invoice by ID.
        Users can view own invoices, admins can view any.
        
        Args:
            invoice_id: ID of the invoice to retrieve
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Get invoice (cached) - already serialized
            invoice = self.invoice_service.get_invoice_by_id_cached(invoice_id)
            if invoice is None:
                self.logger.warning(f"Invoice not found: {invoice_id}")
                return jsonify({"error": "Invoice not found"}), 404
            
            # Check access: admin or owner
            if access_denied := self._check_invoice_access(invoice['user_id']):
                return access_denied
            
            self.logger.info(f"Invoice retrieved: {invoice_id}")
            return jsonify(invoice), 200
            
        except Exception as e:
            self.logger.error(f"Error retrieving invoice {invoice_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to retrieve invoice", e)
    
    def post(self) -> Tuple[dict, int]:
        """
        Create new invoice (admin only).
        
        Expected JSON:
            {
                "user_id": 123,
                "order_id": 456,
                "total_amount": 99.99,
                "status": "pending"  # optional
            }
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Validate request data
            invoice_data = invoice_registration_schema.load(request.json)
            
            # Create invoice
            created_invoice = self.invoice_service.create_invoice(**invoice_data)
            
            if created_invoice is None:
                self.logger.error(f"Invoice creation failed")
                return jsonify({"error": "Failed to create invoice"}), 400
            
            self.logger.info(f"Invoice created: {created_invoice.id if hasattr(created_invoice, 'id') else 'unknown'}")
            return jsonify({
                "message": "Invoice created successfully",
                "invoice": invoice_response_schema.dump(created_invoice)
            }), 201
            
        except ValidationError as err:
            self.logger.warning(f"Invoice creation validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error creating invoice: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to create invoice", e)
    
    def put(self, invoice_id: int) -> Tuple[dict, int]:
        """
        Update existing invoice (admin only).
        
        Args:
            invoice_id: ID of the invoice to update
            
        Expected JSON:
            Invoice update fields
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Validate request data
            invoice_data = invoice_update_schema.load(request.json)
            
            # Check if invoice exists
            existing_invoice = self.invoice_service.get_invoice_by_id(invoice_id)
            if not existing_invoice:
                self.logger.warning(f"Invoice update attempt for non-existent invoice: {invoice_id}")
                return jsonify({"error": "Invoice not found"}), 404
            
            # Convert status string to enum if present
            if 'status' in invoice_data:
                invoice_data['status'] = InvoiceStatus(invoice_data['status'])
            
            # Update invoice
            updated_invoice = self.invoice_service.update_invoice(invoice_id, **invoice_data)
            
            if updated_invoice is None:
                self.logger.error(f"Invoice update failed for {invoice_id}")
                return jsonify({"error": "Failed to update invoice"}), 400
            
            self.logger.info(f"Invoice updated: {invoice_id}")
            return jsonify({
                "message": "Invoice updated successfully",
                "invoice": invoice_response_schema.dump(updated_invoice)
            }), 200
            
        except ValidationError as err:
            self.logger.warning(f"Invoice update validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error updating invoice {invoice_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to update invoice", e)
    
    def patch_status(self, invoice_id: int) -> Tuple[dict, int]:
        """
        Update invoice status (admin only).
        
        Args:
            invoice_id: ID of the invoice to update
            
        Expected JSON:
            {"status": "paid"}
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Validate request data
            status_data = invoice_status_update_schema.load(request.json)
            new_status = status_data['status']
            
            # Update invoice status
            updated_invoice = self.invoice_service.update_invoice_status(invoice_id, new_status)
            
            if updated_invoice is None:
                self.logger.warning(f"Status update failed for invoice: {invoice_id}")
                return jsonify({"error": "Failed to update invoice status"}), 404
            
            self.logger.info(f"Invoice status updated for {invoice_id} to {new_status}")
            return jsonify({
                "message": f"Invoice status updated to {new_status}",
                "invoice": invoice_response_schema.dump(updated_invoice)
            }), 200
            
        except ValidationError as err:
            self.logger.warning(f"Invoice status update validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error updating invoice status for {invoice_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to update invoice status", e)
    
    def delete(self, invoice_id: int) -> Tuple[dict, int]:
        """
        Delete invoice (admin only).
        
        Args:
            invoice_id: ID of the invoice to delete
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Delete invoice
            success = self.invoice_service.delete_invoice(invoice_id)
            
            if not success:
                self.logger.warning(f"Delete attempt failed for invoice: {invoice_id}")
                return jsonify({"error": "Failed to delete invoice"}), 404
            
            self.logger.info(f"Invoice deleted: {invoice_id}")
            return jsonify({"message": "Invoice deleted successfully"}), 200
            
        except Exception as e:
            self.logger.error(f"Error deleting invoice {invoice_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to delete invoice", e)

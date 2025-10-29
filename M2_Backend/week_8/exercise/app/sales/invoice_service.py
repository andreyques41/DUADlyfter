"""
InvoiceService: Handles business logic for invoice CRUD operations and permission checks.
Delegates data access to InvoiceRepository.
"""
from app.sales.invoice_repository import InvoiceRepository

class InvoiceService:
    """
    Service layer for invoice management. Implements business rules and permissions.
    """
    def __init__(self, invoice_repository):
        """
        Initialize InvoiceService.
        :param invoice_repository: Data access layer for invoices
        """
        self.invoice_repository = invoice_repository

    def get_invoice(self, invoice_id, user_id, is_admin):
        """
        Retrieve a single invoice by ID. Admins can view any invoice, clients only their own.
        Returns (invoice, error, status_code).
        """
        invoice = self.invoice_repository.get_by_id(invoice_id)
        if invoice is False:
            return None, "Database error", 500
        if invoice is None:
            return None, "Invoice not found", 404
        if not is_admin and invoice['user_id'] != user_id:
            return None, "Forbidden", 403
        return invoice, None, 200

    def get_invoices(self, user_id, is_admin):
        """
        Retrieve invoices. Admins get all, clients get their own.
        Returns (invoices, error, status_code).
        """
        if is_admin:
            invoices = self.invoice_repository.get_all()
        else:
            invoices = self.invoice_repository.get_by_user(user_id)
        if invoices is False:
            return None, "Database error", 500
        return invoices, None, 200

    def create_invoice(self, user_id, items):
        """
        Create a new invoice for the user with the given items.
        Returns (invoice_id, error, status_code).
        """
        if not items or not isinstance(items, list):
            return None, "Items array required", 400
        if len(items) == 0:
            return None, "At least one item required", 400
        for item in items:
            if "product_id" not in item or "quantity" not in item:
                return None, "Each item must have product_id and quantity", 400
        invoice_id, error = self.invoice_repository.create_invoice(user_id, items)
        if invoice_id is False:
            return None, error or "Invoice creation failed", 500
        return invoice_id, None, 201

    def delete_invoice(self, invoice_id):
        """
        Delete an invoice by ID. Returns (success, error, status_code).
        """
        success, error = self.invoice_repository.delete_invoice(invoice_id)
        if not success:
            if error == "Invoice not found":
                return False, error, 404
            return False, error or "Invoice deletion failed", 500
        return True, None, 200

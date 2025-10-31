"""
InvoiceController: Handles HTTP responses for invoice CRUD endpoints.
Delegates business logic to InvoiceService.
"""
from flask import jsonify, request, g

class InvoiceController:
    """
    Controller layer for invoice management. Handles HTTP responses and delegates to InvoiceService.
    """
    def __init__(self, invoice_service):
        """
        Initialize InvoiceController.
        :param invoice_service: Service layer for invoices
        """
        self.invoice_service = invoice_service

    def get(self, invoice_id=None):
        """
        GET endpoint dispatcher. Calls get_invoice or get_invoices.
        """
        user_id = g.user_data['user_id']
        is_admin = g.is_admin
        if invoice_id:
            invoice, error, status = self.invoice_service.get_invoice(invoice_id, user_id, is_admin)
            if error:
                return jsonify({"error": error}), status
            return jsonify({"invoice": invoice}), status
        invoices, error, status = self.invoice_service.get_invoices(user_id, is_admin)
        if error:
            return jsonify({"error": error}), status
        return jsonify({"invoices": invoices}), status

    def post(self):
        """
        POST endpoint. Calls service to create invoice.
        """
        user_id = g.user_data['user_id']
        data = request.get_json()
        items = data.get("items") if data else None
        invoice_id, error, status = self.invoice_service.create_invoice(user_id, items)
        if error:
            return jsonify({"error": error}), status
        return jsonify({
            "message": "Invoice created successfully",
            "invoice_id": invoice_id
        }), status

    def delete(self, invoice_id):
        """
        DELETE endpoint. Calls service to delete invoice.
        """
        success, error, status = self.invoice_service.delete_invoice(invoice_id)
        if not success:
            return jsonify({"error": error}), status
        return jsonify({"message": "Invoice deleted successfully"}), status

"""
Invoice Routes Module

Provides RESTful API endpoints for invoice management:
- GET /invoices/<invoice_id> - Get specific invoice (user access)
- GET /invoices/user/<user_id> - Get user's invoices (user access)
- POST /invoices - Create new invoice (admin only)
- PUT /invoices/<invoice_id> - Update invoice (admin only)
- PATCH /invoices/<invoice_id>/status - Update invoice status (admin only)
- DELETE /invoices/<invoice_id> - Delete invoice (admin only)
- GET /admin/invoices - Get all invoices (admin only)

Features:
- User authentication required for all operations
- Users can only access their own invoices (or admins can access any)
- Comprehensive invoice business logic through service layer
- Input validation using schemas
- Detailed error handling and logging
"""
# Common imports
from flask import Blueprint, request, jsonify, g
from flask.views import MethodView
from marshmallow import ValidationError
from config.logging import get_logger, EXC_INFO_LOG_ERRORS

# Auth imports (for decorators)
from app.core.middleware import token_required_with_repo, admin_required_with_repo

# Sales domain imports
from app.sales.models.invoice import InvoiceStatus
from app.sales.schemas.invoice_schema import (
    invoice_registration_schema,
    invoice_update_schema,
    invoice_status_update_schema,
    invoice_response_schema,
    invoices_response_schema
)

# Direct service import
from app.sales.services.invoice_service import InvoiceService

# Get logger for this module
logger = get_logger(__name__)

class InvoiceAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.invoice_service = InvoiceService()

    @token_required_with_repo
    def get(self, invoice_id):
        try:
            if not self.invoice_service.check_user_access(g.current_user, g.is_admin, invoice_id=invoice_id):
                logger.warning(f"Access denied for user {g.current_user.id} to invoice {invoice_id}")
                return jsonify({"error": "Access denied"}), 403

            invoice = self.invoice_service.get_invoice_by_id(invoice_id)
            if invoice is None:
                logger.warning(f"Invoice not found: {invoice_id}")
                return jsonify({"error": "Invoice not found"}), 404

            logger.info(f"Invoice retrieved: {invoice_id}")
            return jsonify(invoice_response_schema.dump(invoice)), 200
        except Exception as e:
            logger.error(f"Failed to retrieve invoice {invoice_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to retrieve invoice"}), 500

    @admin_required_with_repo
    def post(self):
        try:
            invoice_data = invoice_registration_schema.load(request.json)
            created_invoice = self.invoice_service.create_invoice(**invoice_data)

            if created_invoice is None:
                logger.error(f"Invoice creation failed")
                return jsonify({"error": "Failed to create invoice"}), 400

            logger.info(f"Invoice created: {created_invoice.id if created_invoice else 'unknown'}")
            return jsonify({
                "message": "Invoice created successfully",
                "invoice": invoice_response_schema.dump(created_invoice)
            }), 201
        except ValidationError as err:
            logger.warning(f"Invoice creation validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            logger.error(f"Failed to create invoice: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to create invoice"}), 500

    @admin_required_with_repo
    def put(self, invoice_id):
        try:
            invoice_data = invoice_update_schema.load(request.json)

            existing_invoice = self.invoice_service.get_invoice_by_id(invoice_id)
            if not existing_invoice:
                logger.warning(f"Invoice update attempt for non-existent invoice: {invoice_id}")
                return jsonify({"error": "Invoice not found"}), 404

            # Convert status string to enum if present
            if 'status' in invoice_data:
                invoice_data['status'] = InvoiceStatus(invoice_data['status'])

            updated_invoice = self.invoice_service.update_invoice(invoice_id, **invoice_data)
            if updated_invoice is None:
                logger.error(f"Invoice update failed for {invoice_id}")
                return jsonify({"error": "Failed to update invoice"}), 400

            logger.info(f"Invoice updated: {invoice_id}")
            return jsonify({
                "message": "Invoice updated successfully",
                "invoice": invoice_response_schema.dump(updated_invoice)
            }), 200
        except ValidationError as err:
            logger.warning(f"Invoice update validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            logger.error(f"Failed to update invoice {invoice_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to update invoice"}), 500

    @admin_required_with_repo
    def delete(self, invoice_id):
        try:
            success = self.invoice_service.delete_invoice(invoice_id)
            if not success:
                logger.warning(f"Delete attempt failed for invoice: {invoice_id}")
                return jsonify({"error": "Failed to delete invoice"}), 404

            logger.info(f"Invoice deleted: {invoice_id}")
            return jsonify({"message": "Invoice deleted successfully"}), 200
        except Exception as e:
            logger.error(f"Failed to delete invoice {invoice_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to delete invoice"}), 500

class UserInvoicesAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.invoice_service = InvoiceService()

    @token_required_with_repo
    def get(self, user_id):
        try:
            if not self.invoice_service.check_user_access(g.current_user, g.is_admin, user_id=user_id):
                logger.warning(f"Access denied for user {g.current_user.id} to invoices of user {user_id}")
                return jsonify({"error": "Access denied"}), 403

            user_invoices = self.invoice_service.get_invoices_by_user_id(user_id)
            logger.info(f"Invoices retrieved for user {user_id}")
            return jsonify({
                "total_invoices": len(user_invoices),
                "invoices": invoices_response_schema.dump(user_invoices)
            }), 200
        except Exception as e:
            logger.error(f"Failed to retrieve invoices for user {user_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to retrieve invoices"}), 500

class InvoiceStatusAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.invoice_service = InvoiceService()

    @admin_required_with_repo
    def patch(self, invoice_id):
        try:
            status_data = invoice_status_update_schema.load(request.json)
            new_status = InvoiceStatus(status_data['status'])

            updated_invoice = self.invoice_service.update_invoice_status(invoice_id, new_status)
            if updated_invoice is None:
                logger.warning(f"Status update failed for invoice: {invoice_id}")
                return jsonify({"error": "Failed to update invoice status"}), 404

            logger.info(f"Invoice status updated for {invoice_id} to {new_status.value}")
            return jsonify({
                "message": f"Invoice status updated to {new_status.value}",
                "invoice": invoice_response_schema.dump(updated_invoice)
            }), 200
        except ValidationError as err:
            logger.warning(f"Invoice status update validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            logger.error(f"Failed to update invoice status for {invoice_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to update invoice status"}), 500

class AdminInvoicesAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.invoice_service = InvoiceService()

    @admin_required_with_repo
    def get(self):
        try:
            all_invoices = self.invoice_service.get_all_invoices()
            logger.info("All invoices retrieved by admin.")
            return jsonify({
                "total_invoices": len(all_invoices),
                "invoices": invoices_response_schema.dump(all_invoices)
            }), 200
        except Exception as e:
            logger.error(f"Failed to retrieve all invoices: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to retrieve invoices"}), 500

# Import blueprint from sales module
from app.sales import sales_bp

# Register routes when this module is imported by sales/__init__.py
def register_invoice_routes(sales_bp):
    # Individual invoice operations
    sales_bp.add_url_rule('/invoices', methods=['POST'], view_func=InvoiceAPI.as_view('invoice_create'))
    sales_bp.add_url_rule('/invoices/<int:invoice_id>', view_func=InvoiceAPI.as_view('invoice'))
    
    # User invoices operations
    sales_bp.add_url_rule('/invoices/user/<int:user_id>', view_func=UserInvoicesAPI.as_view('user_invoices'))
    
    # Invoice status operations
    sales_bp.add_url_rule('/invoices/<int:invoice_id>/status', view_func=InvoiceStatusAPI.as_view('invoice_status'))
    
    # Admin invoice operations
    sales_bp.add_url_rule('/admin/invoices', view_func=AdminInvoicesAPI.as_view('admin_invoices'))

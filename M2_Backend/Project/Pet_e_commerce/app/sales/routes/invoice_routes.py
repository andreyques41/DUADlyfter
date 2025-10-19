"""
Invoice Routes Module

Provides RESTful API endpoints for invoice management:
- GET /invoices - List invoices (REST standard: auto-filtered by user role)
- GET /invoices/<invoice_id> - Get specific invoice (user access)
- POST /invoices - Create new invoice (admin only)
- PUT /invoices/<invoice_id> - Update invoice (admin only)
- PATCH /invoices/<invoice_id>/status - Update invoice status (admin only)
- DELETE /invoices/<invoice_id> - Delete invoice (admin only)

Features:
- REST standard: GET /invoices auto-filters based on user role
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

# Auth imports (for decorators and utilities)
from app.core.middleware import token_required_with_repo, admin_required_with_repo
from app.core.lib.auth import is_admin_user, is_user_or_admin

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

class InvoiceListAPI(MethodView):
    """
    REST standard GET /invoices endpoint.
    
    Behavior:
    - Regular users: See only their own invoices (auto-filtered by user_id)
    - Admins: See all invoices in the system
    """
    init_every_request = False

    def __init__(self):
        self.invoice_service = InvoiceService()

    @token_required_with_repo
    def get(self):
        """
        Get invoices collection - auto-filtered based on user role.
        
        Returns:
            JSON response with invoices list (filtered by role)
        """
        try:
            if is_admin_user():
                # Admin sees all invoices
                invoices = self.invoice_service.get_all_invoices()
                logger.info(f"All invoices retrieved by admin user {g.current_user.id}")
            else:
                # Regular user sees only their invoices
                invoices = self.invoice_service.get_invoices_by_user_id(g.current_user.id)
                logger.info(f"Invoices retrieved for user {g.current_user.id}")
            
            return jsonify({
                "total_invoices": len(invoices),
                "invoices": invoices_response_schema.dump(invoices)
            }), 200
        except Exception as e:
            logger.error(f"Failed to retrieve invoices: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to retrieve invoices"}), 500

class InvoiceAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.invoice_service = InvoiceService()

    @token_required_with_repo
    def get(self, invoice_id):
        try:
            invoice = self.invoice_service.get_invoice_by_id(invoice_id)
            if invoice is None:
                logger.warning(f"Invoice not found: {invoice_id}")
                return jsonify({"error": "Invoice not found"}), 404
            
            # Check access: admin or owner
            if not is_user_or_admin(invoice.user_id):
                logger.warning(f"Access denied for user {g.current_user.id} to invoice {invoice_id}")
                return jsonify({"error": "Access denied"}), 403

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

class InvoiceStatusAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.invoice_service = InvoiceService()

    @admin_required_with_repo
    def patch(self, invoice_id):
        try:
            status_data = invoice_status_update_schema.load(request.json)
            new_status = status_data['status']

            updated_invoice = self.invoice_service.update_invoice_status(invoice_id, new_status)
            if updated_invoice is None:
                logger.warning(f"Status update failed for invoice: {invoice_id}")
                return jsonify({"error": "Failed to update invoice status"}), 404

            logger.info(f"Invoice status updated for {invoice_id} to {new_status}")
            return jsonify({
                "message": f"Invoice status updated to {new_status}",
                "invoice": invoice_response_schema.dump(updated_invoice)
            }), 200
        except ValidationError as err:
            logger.warning(f"Invoice status update validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            logger.error(f"Failed to update invoice status for {invoice_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to update invoice status"}), 500

# Import blueprint from sales module
from app.sales import sales_bp

# Register routes when this module is imported by sales/__init__.py
def register_invoice_routes(sales_bp):
    # REST standard: Collection endpoint (auto-filtered by role)
    sales_bp.add_url_rule('/invoices', methods=['GET'], view_func=InvoiceListAPI.as_view('invoice_list'))
    
    # REST standard: Create and individual operations
    sales_bp.add_url_rule('/invoices', methods=['POST'], view_func=InvoiceAPI.as_view('invoice_create'))
    sales_bp.add_url_rule('/invoices/<int:invoice_id>', view_func=InvoiceAPI.as_view('invoice'))
    
    # Invoice status operations
    sales_bp.add_url_rule('/invoices/<int:invoice_id>/status', view_func=InvoiceStatusAPI.as_view('invoice_status'))

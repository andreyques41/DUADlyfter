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
- Comprehensive invoice business logic delegated to InvoiceController
- Input validation handled by controller layer
- Detailed error handling and logging in controller
"""
# Common imports
from flask import Blueprint
from flask.views import MethodView

# Auth imports (for decorators)
from app.core.middleware import token_required_with_repo, admin_required_with_repo

# Controller imports
from app.sales.controllers.invoice_controller import InvoiceController

class InvoiceListAPI(MethodView):
    """
    REST standard GET /invoices endpoint.
    
    Behavior:
    - Regular users: See only their own invoices (auto-filtered by user_id)
    - Admins: See all invoices in the system
    """
    init_every_request = False

    def __init__(self):
        self.controller = InvoiceController()

    @token_required_with_repo
    def get(self):
        """Get invoices collection - auto-filtered based on user role."""
        return self.controller.get_list()

class InvoiceAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.controller = InvoiceController()

    @token_required_with_repo
    def get(self, invoice_id):
        """Get specific invoice by ID."""
        return self.controller.get(invoice_id)

    @admin_required_with_repo
    def post(self):
        """Create new invoice (admin only)."""
        return self.controller.post()

    @admin_required_with_repo
    def put(self, invoice_id):
        """Update existing invoice (admin only)."""
        return self.controller.put(invoice_id)

    @admin_required_with_repo
    def delete(self, invoice_id):
        """Delete invoice (admin only)."""
        return self.controller.delete(invoice_id)

class InvoiceStatusAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.controller = InvoiceController()

    @admin_required_with_repo
    def patch(self, invoice_id):
        """Update invoice status (admin only)."""
        return self.controller.patch_status(invoice_id)

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

from flask import request, jsonify, g
from flask.views import MethodView

from app.sales.invoice_repository import InvoiceRepository
from app.sales.invoice_service import InvoiceService
from app.sales.invoice_controller import InvoiceController
from app.auth.user_repository import UserRepository
from app.utilities.decorators import require_auth_with_repo, require_admin_with_repo


class InvoiceAPI(MethodView):
    """
    InvoiceAPI: Flask route class for invoice CRUD operations.
    Delegates all logic to InvoiceController.
    """

    def __init__(self, db_manager):
        """
        Initialize InvoiceAPI with database manager and controller.
        """
        self.invoice_repository = InvoiceRepository(db_manager)
        self.invoice_service = InvoiceService(self.invoice_repository)
        self.controller = InvoiceController(self.invoice_service)

    @require_auth_with_repo('user_repository')
    def get(self, invoice_id=None):
        """
        GET endpoint. Calls controller to get invoice(s).
        """
        return self.controller.get(invoice_id)
    
    @require_auth_with_repo('user_repository')
    def post(self):
        """
        POST endpoint. Calls controller to create invoice.
        """
        return self.controller.post()
    
    @require_admin_with_repo('user_repository')
    def delete(self, invoice_id):
        """
        DELETE endpoint. Calls controller to delete invoice.
        """
        return self.controller.delete(invoice_id)

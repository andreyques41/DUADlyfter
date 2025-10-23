from flask import request, jsonify, g
from flask.views import MethodView
from app.sales.invoice_repository import InvoiceRepository
from app.auth.user_repository import UserRepository
from app.utilities.decorators import require_auth_with_repo, require_admin_with_repo


class InvoiceAPI(MethodView):
    """CRUD operations for invoices with role-based access control."""
    
    def __init__(self, db_manager):
        self.invoice_repository = InvoiceRepository(db_manager)
        self.user_repository = UserRepository(db_manager)
    
    @require_auth_with_repo('user_repository')
    def get(self, invoice_id=None):
        """
        Get invoices.
        - Admin: Can see all invoices
        - Cliente: Can only see their own invoices
        """
        try:
            user_id = g.user_data['user_id']
            is_admin = g.is_admin
            
            # Get specific invoice
            if invoice_id:
                result = self.invoice_repository.get_by_id(invoice_id)
                if result is False:
                    return jsonify({"error": "Database error"}), 500
                if result is None:
                    return jsonify({"error": "Invoice not found"}), 404
                
                # Check permission: admin or owner
                if not is_admin and result['user_id'] != user_id:
                    return jsonify({"error": "Forbidden"}), 403
                
                return jsonify({"invoice": result}), 200
            
            # Get all invoices (filtered by role)
            if is_admin:
                result = self.invoice_repository.get_all()
            else:
                result = self.invoice_repository.get_by_user(user_id)
            
            if result is False:
                return jsonify({"error": "Database error"}), 500
            
            return jsonify({"invoices": result}), 200
            
        except Exception as e:
            print(f"[ERROR] Get invoice error: {e}")
            return jsonify({"error": "Failed to retrieve invoices"}), 500
    
    @require_auth_with_repo('user_repository')
    def post(self):
        """
        Create new invoice.
        Required: items array with {product_id, quantity}
        """
        try:
            user_id = g.user_data['user_id']
            
            data = request.get_json()
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400
            
            if not data.get("items") or not isinstance(data["items"], list):
                return jsonify({"error": "Items array required"}), 400
            
            if len(data["items"]) == 0:
                return jsonify({"error": "At least one item required"}), 400
            
            # Validate items structure
            for item in data["items"]:
                if "product_id" not in item or "quantity" not in item:
                    return jsonify({"error": "Each item must have product_id and quantity"}), 400
            
            # Create invoice
            invoice_id, error = self.invoice_repository.create_invoice(user_id, data["items"])
            
            if invoice_id is False:
                return jsonify({"error": error or "Invoice creation failed"}), 500
            
            return jsonify({
                "message": "Invoice created successfully",
                "invoice_id": invoice_id
            }), 201
            
        except Exception as e:
            print(f"[ERROR] Create invoice error: {e}")
            return jsonify({"error": "Invoice creation failed"}), 500
    
    @require_admin_with_repo('user_repository')
    def delete(self, invoice_id):
        """
        Delete invoice.
        Only admin can delete invoices.
        """
        try:
            success, error = self.invoice_repository.delete_invoice(invoice_id)
            
            if not success:
                if error == "Invoice not found":
                    return jsonify({"error": error}), 404
                return jsonify({"error": error}), 500
            
            return jsonify({"message": "Invoice deleted successfully"}), 200
            
        except Exception as e:
            print(f"[ERROR] Delete invoice error: {e}")
            return jsonify({"error": "Invoice deletion failed"}), 500

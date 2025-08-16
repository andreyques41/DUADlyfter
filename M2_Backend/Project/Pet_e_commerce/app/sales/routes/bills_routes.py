"""
Bills Routes Module

Provides RESTful API endpoints for bills management:
- GET /bills/<bill_id> - Get specific bill (user access)
- GET /bills/user/<user_id> - Get user's bills (user access)
- POST /bills - Create new bill (admin only)
- PUT /bills/<bill_id> - Update bill (admin only)
- PATCH /bills/<bill_id>/status - Update bill status (admin only)
- DELETE /bills/<bill_id> - Delete bill (admin only)
- GET /admin/bills - Get all bills (admin only)

Features:
- User authentication required for all operations
- Users can only access their own bills (or admins can access any)
- Comprehensive bill business logic through service layer
- Input validation using schemas
- Detailed error handling and logging
"""
# Common imports
from app.shared.common_imports import *

# Auth imports (for decorators)
from app.auth.imports import token_required, admin_required, is_admin_user

# Sales domain imports
from app.sales.imports import (
    Bill,
    BillStatus,
    bill_registration_schema, bill_update_schema, 
    bill_status_update_schema, bill_response_schema,
    bills_response_schema, BILLS_DB_PATH
)

# Direct service import to avoid circular imports
from app.sales.services.bills_services import BillsService


# Get logger for this module
logger = get_logger(__name__)

class BillAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.bills_service = BillsService(BILLS_DB_PATH)

    @token_required
    def get(self, bill_id):
        try:
            if not self.bills_service.check_user_access(g.current_user, is_admin_user(), bill_id=bill_id):
                logger.warning(f"Access denied for user {g.current_user.id} to bill {bill_id}")
                return jsonify({"error": "Access denied"}), 403

            bill = self.bills_service.get_bills(bill_id)
            if bill is None:
                logger.warning(f"Bill not found: {bill_id}")
                return jsonify({"error": "Bill not found"}), 404

            logger.info(f"Bill retrieved: {bill_id}")
            return jsonify(bill_response_schema.dump(bill)), 200
        except Exception as e:
            logger.error(f"Failed to retrieve bill {bill_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to retrieve bill"}), 500

    @token_required
    @admin_required
    def post(self):
        try:
            bill_data = bill_registration_schema.load(request.json)
            created_bill, error = self.bills_service.create_bill(bill_data)

            if error:
                logger.error(f"Bill creation failed: {error}")
                return jsonify({"error": error}), 400

            logger.info(f"Bill created: {created_bill.id if created_bill else 'unknown'}")
            return jsonify({
                "message": "Bill created successfully",
                "bill": bill_response_schema.dump(created_bill)
            }), 201
        except ValidationError as err:
            logger.warning(f"Bill creation validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            logger.error(f"Failed to create bill: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to create bill"}), 500

    @token_required
    @admin_required
    def put(self, bill_id):
        try:
            bill_data = bill_update_schema.load(request.json)

            existing_bill = self.bills_service.get_bills(bill_id)
            if not existing_bill:
                logger.warning(f"Bill update attempt for non-existent bill: {bill_id}")
                return jsonify({"error": "Bill not found"}), 404

            for key, value in bill_data.items():
                if key == 'status':
                    value = BillStatus(value)
                setattr(existing_bill, key, value)

            updated_bill, error = self.bills_service.update_bill(bill_id, existing_bill)
            if error:
                logger.error(f"Bill update failed for {bill_id}: {error}")
                return jsonify({"error": error}), 400

            logger.info(f"Bill updated: {bill_id}")
            return jsonify({
                "message": "Bill updated successfully",
                "bill": bill_response_schema.dump(updated_bill)
            }), 200
        except ValidationError as err:
            logger.warning(f"Bill update validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            logger.error(f"Failed to update bill {bill_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to update bill"}), 500

    @token_required
    @admin_required
    def delete(self, bill_id):
        try:
            success, error = self.bills_service.delete_bill(bill_id)
            if error:
                if "No bill found" in error:
                    logger.warning(f"Delete attempt for non-existent bill: {bill_id}")
                    return jsonify({"error": error}), 404
                logger.error(f"Bill deletion failed for {bill_id}: {error}")
                return jsonify({"error": error}), 400

            logger.info(f"Bill deleted: {bill_id}")
            return jsonify({"message": "Bill deleted successfully"}), 200
        except Exception as e:
            logger.error(f"Failed to delete bill {bill_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to delete bill"}), 500

class UserBillsAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.bills_service = BillsService(BILLS_DB_PATH)

    @token_required
    def get(self, user_id):
        try:
            if not self.bills_service.check_user_access(g.current_user, is_admin_user(), user_id=user_id):
                logger.warning(f"Access denied for user {g.current_user.id} to bills of user {user_id}")
                return jsonify({"error": "Access denied"}), 403

            user_bills = self.bills_service.get_bills(user_id=user_id)
            logger.info(f"Bills retrieved for user {user_id}")
            return jsonify({
                "total_bills": len(user_bills),
                "bills": bills_response_schema.dump(user_bills)
            }), 200
        except Exception as e:
            logger.error(f"Failed to retrieve bills for user {user_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to retrieve bills"}), 500

class BillStatusAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.bills_service = BillsService(BILLS_DB_PATH)

    @token_required
    @admin_required
    def patch(self, bill_id):
        try:
            status_data = bill_status_update_schema.load(request.json)
            new_status = BillStatus(status_data['status'])

            updated_bill, error = self.bills_service.update_bill_status(bill_id, new_status)
            if error:
                if "No bill found" in error:
                    logger.warning(f"Status update attempt for non-existent bill: {bill_id}")
                    return jsonify({"error": error}), 404
                logger.error(f"Bill status update failed for {bill_id}: {error}")
                return jsonify({"error": error}), 400

            logger.info(f"Bill status updated for {bill_id} to {new_status.value}")
            return jsonify({
                "message": f"Bill status updated to {new_status.value}",
                "bill": bill_response_schema.dump(updated_bill)
            }), 200
        except ValidationError as err:
            logger.warning(f"Bill status update validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            logger.error(f"Failed to update bill status for {bill_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to update bill status"}), 500

class AdminBillsAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.bills_service = BillsService(BILLS_DB_PATH)

    @token_required
    @admin_required  
    def get(self):
        try:
            all_bills = self.bills_service.get_bills()
            logger.info("All bills retrieved by admin.")
            return jsonify({
                "total_bills": len(all_bills),
                "bills": bills_response_schema.dump(all_bills)
            }), 200
        except Exception as e:
            logger.error(f"Failed to retrieve all bills: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to retrieve bills"}), 500

# Import blueprint from sales module
from app.sales import sales_bp

# Register routes when this module is imported by sales/__init__.py
def register_bills_routes(sales_bp):
    # Individual bill operations
    sales_bp.add_url_rule('/bills', methods=['POST'], view_func=BillAPI.as_view('bill_create'))
    sales_bp.add_url_rule('/bills/<int:bill_id>', view_func=BillAPI.as_view('bill'))
    
    # User bills operations
    sales_bp.add_url_rule('/bills/user/<int:user_id>', view_func=UserBillsAPI.as_view('user_bills'))
    
    # Bill status operations
    sales_bp.add_url_rule('/bills/<int:bill_id>/status', view_func=BillStatusAPI.as_view('bill_status'))
    
    # Admin bill operations
    sales_bp.add_url_rule('/admin/bills', view_func=AdminBillsAPI.as_view('admin_bills'))

"""
Returns Routes Module

Provides RESTful API endpoints for returns management:
- GET /returns/<return_id> - Get specific return (user access)
- GET /returns/user/<user_id> - Get user's returns (user access)
- POST /returns - Create new return request (user access)
- PUT /returns/<return_id> - Update return (admin only)
- PATCH /returns/<return_id>/status - Update return status (admin only)
- DELETE /returns/<return_id> - Delete return (admin only, limited status)
- GET /admin/returns - Get all returns (admin only)

Features:
- User authentication required for all operations
- Users can only access their own returns (or admins can access any)
- Comprehensive return business logic through service layer
- Input validation using schemas
- Detailed error handling and logging
"""
from flask import request, jsonify, g
from flask.views import MethodView
from marshmallow import ValidationError
from app.sales.services.returns_service import ReturnsService
from app.sales.schemas.returns_schema import (
    return_registration_schema,
    return_update_schema,
    return_status_update_schema,
    return_response_schema,
    returns_response_schema
)
from app.sales.models.returns import ReturnStatus
from app.auth.services import token_required, admin_required
from app.shared.utils import is_admin_user
from config.logging_config import get_logger, EXC_INFO_LOG_ERRORS

# Get logger for this module
logger = get_logger(__name__)

DB_PATH = './app/shared/json_db/returns.json'

class ReturnAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.returns_service = ReturnsService(DB_PATH)

    @token_required
    def get(self, return_id):
        try:
            if not self.returns_service.check_user_access(g.current_user, is_admin_user(), return_id=return_id):
                logger.warning(f"Access denied for user {g.current_user.id} to return {return_id}")
                return jsonify({"error": "Access denied"}), 403

            ret = self.returns_service.get_returns(return_id)
            if ret is None:
                logger.warning(f"Return not found: {return_id}")
                return jsonify({"error": "Return not found"}), 404

            logger.info(f"Return retrieved: {return_id}")
            return jsonify(return_response_schema.dump(ret)), 200
        except Exception as e:
            logger.error(f"Failed to retrieve return {return_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to retrieve return"}), 500

    @token_required
    def post(self):
        try:
            return_data = return_registration_schema.load(request.json)

            if not is_admin_user() and return_data.user_id != g.current_user.id:
                logger.warning(f"Access denied for user {g.current_user.id} to create return for user {return_data.user_id}")
                return jsonify({"error": "Access denied"}), 403

            created_return, error = self.returns_service.create_return(return_data)
            if error:
                logger.error(f"Return creation failed: {error}")
                return jsonify({"error": error}), 400

            logger.info(f"Return created: {created_return.id if created_return else 'unknown'}")
            return jsonify({
                "message": "Return request created successfully",
                "return": return_response_schema.dump(created_return)
            }), 201
        except ValidationError as err:
            logger.warning(f"Return creation validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            logger.error(f"Failed to create return: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to create return"}), 500

    @token_required
    @admin_required
    def put(self, return_id):
        try:
            return_data = return_update_schema.load(request.json)

            existing_return = self.returns_service.get_returns(return_id)
            if not existing_return:
                logger.warning(f"Return update attempt for non-existent return: {return_id}")
                return jsonify({"error": "Return not found"}), 404

            for key, value in return_data.items():
                if key == 'status':
                    value = ReturnStatus(value)
                setattr(existing_return, key, value)

            updated_return, error = self.returns_service.update_return(return_id, existing_return)
            if error:
                logger.error(f"Return update failed for {return_id}: {error}")
                return jsonify({"error": error}), 400

            logger.info(f"Return updated: {return_id}")
            return jsonify({
                "message": "Return updated successfully",
                "return": return_response_schema.dump(updated_return)
            }), 200
        except ValidationError as err:
            logger.warning(f"Return update validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            logger.error(f"Failed to update return {return_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to update return"}), 500

    @token_required
    @admin_required
    def delete(self, return_id):
        try:
            success, error = self.returns_service.delete_return(return_id)
            if error:
                if "No return found" in error:
                    logger.warning(f"Delete attempt for non-existent return: {return_id}")
                    return jsonify({"error": error}), 404
                logger.error(f"Return deletion failed for {return_id}: {error}")
                return jsonify({"error": error}), 400

            logger.info(f"Return deleted: {return_id}")
            return jsonify({"message": "Return deleted successfully"}), 200
        except Exception as e:
            logger.error(f"Failed to delete return {return_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to delete return"}), 500

class UserReturnsAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.returns_service = ReturnsService(DB_PATH)

    @token_required
    def get(self, user_id):
        try:
            if not self.returns_service.check_user_access(g.current_user, is_admin_user(), user_id=user_id):
                logger.warning(f"Access denied for user {g.current_user.id} to returns of user {user_id}")
                return jsonify({"error": "Access denied"}), 403

            user_returns = self.returns_service.get_returns(user_id=user_id)
            logger.info(f"Returns retrieved for user {user_id}")
            return jsonify({
                "total_returns": len(user_returns),
                "returns": returns_response_schema.dump(user_returns)
            }), 200
        except Exception as e:
            logger.error(f"Failed to retrieve returns for user {user_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to retrieve returns"}), 500

class ReturnStatusAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.returns_service = ReturnsService(DB_PATH)

    @token_required
    @admin_required
    def patch(self, return_id):
        try:
            status_data = return_status_update_schema.load(request.json)
            new_status = ReturnStatus(status_data['status'])

            updated_return, error = self.returns_service.update_return_status(return_id, new_status)
            if error:
                if "No return found" in error:
                    logger.warning(f"Status update attempt for non-existent return: {return_id}")
                    return jsonify({"error": error}), 404
                logger.error(f"Return status update failed for {return_id}: {error}")
                return jsonify({"error": error}), 400

            logger.info(f"Return status updated for {return_id} to {new_status.value}")
            return jsonify({
                "message": f"Return status updated to {new_status.value}",
                "return": return_response_schema.dump(updated_return)
            }), 200
        except ValidationError as err:
            logger.warning(f"Return status update validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            logger.error(f"Failed to update return status for {return_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to update return status"}), 500

class AdminReturnsAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.returns_service = ReturnsService(DB_PATH)

    @token_required
    @admin_required  
    def get(self):
        try:
            all_returns = self.returns_service.get_returns()
            logger.info("All returns retrieved by admin.")
            return jsonify({
                "total_returns": len(all_returns),
                "returns": returns_response_schema.dump(all_returns)
            }), 200
        except Exception as e:
            logger.error(f"Failed to retrieve all returns: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to retrieve returns"}), 500

# Import blueprint from sales module
from app.sales import sales_bp

def register_returns_routes():
    # Individual return operations
    sales_bp.add_url_rule('/returns', methods=['POST'], view_func=ReturnAPI.as_view('return_create'))
    sales_bp.add_url_rule('/returns/<int:return_id>', view_func=ReturnAPI.as_view('return'))
    
    # User returns operations
    sales_bp.add_url_rule('/returns/user/<int:user_id>', view_func=UserReturnsAPI.as_view('user_returns'))
    
    # Return status operations
    sales_bp.add_url_rule('/returns/<int:return_id>/status', view_func=ReturnStatusAPI.as_view('return_status'))
    
    # Admin return operations
    sales_bp.add_url_rule('/admin/returns', view_func=AdminReturnsAPI.as_view('admin_returns'))

register_returns_routes()

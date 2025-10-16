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

# Common imports
from flask import Blueprint, request, jsonify, g
from flask.views import MethodView
from marshmallow import ValidationError
from config.logging import get_logger, EXC_INFO_LOG_ERRORS

# Auth imports (for decorators and utilities)
from app.core.middleware import token_required, admin_required, token_required_with_repo, admin_required_with_repo
from app.core.lib.auth import is_admin_user

# Sales domain imports
from app.sales.models.returns import Return, ReturnStatus, ReturnItem
from app.sales.schemas.returns_schema import (
    return_registration_schema,
    return_update_schema,
    return_status_update_schema,
    return_response_schema,
    returns_response_schema
)

# Direct service import to avoid circular imports
from app.sales.services.returns_service import ReturnService

# Get logger for this module
logger = get_logger(__name__)

class ReturnAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.returns_service = ReturnService()

    @token_required_with_repo
    def get(self, return_id):
        try:
            if not self.returns_service.check_user_access(g.current_user, g.is_admin, return_id=return_id):
                logger.warning(f"Access denied for user {g.current_user.id} to return {return_id}")
                return jsonify({"error": "Access denied"}), 403

            ret = self.returns_service.get_return_by_id(return_id)
            if ret is None:
                logger.warning(f"Return not found: {return_id}")
                return jsonify({"error": "Return not found"}), 404

            logger.info(f"Return retrieved: {return_id}")
            return jsonify(return_response_schema.dump(ret)), 200
        except Exception as e:
            logger.error(f"Failed to retrieve return {return_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to retrieve return"}), 500

    @token_required_with_repo
    def post(self):
        try:
            return_data = return_registration_schema.load(request.json)

            if not g.is_admin and return_data.get('user_id') != g.current_user.id:
                logger.warning(f"Access denied for user {g.current_user.id} to create return for user {return_data.get('user_id')}")
                return jsonify({"error": "Access denied"}), 403

            created_return = self.returns_service.create_return(**return_data)
            if created_return is None:
                logger.error(f"Return creation failed")
                return jsonify({"error": "Failed to create return"}), 400

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

    @admin_required_with_repo
    def put(self, return_id):
        try:
            return_data = return_update_schema.load(request.json)

            existing_return = self.returns_service.get_return_by_id(return_id)
            if not existing_return:
                logger.warning(f"Return update attempt for non-existent return: {return_id}")
                return jsonify({"error": "Return not found"}), 404

            # Convert status string to enum if present
            if 'status' in return_data:
                return_data['status'] = ReturnStatus(return_data['status'])

            updated_return = self.returns_service.update_return(return_id, **return_data)
            if updated_return is None:
                logger.error(f"Return update failed for {return_id}")
                return jsonify({"error": "Failed to update return"}), 400

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

    @admin_required_with_repo
    def delete(self, return_id):
        try:
            success = self.returns_service.delete_return(return_id)
            if not success:
                logger.warning(f"Delete attempt failed for return: {return_id}")
                return jsonify({"error": "Failed to delete return"}), 404

            logger.info(f"Return deleted: {return_id}")
            return jsonify({"message": "Return deleted successfully"}), 200
        except Exception as e:
            logger.error(f"Failed to delete return {return_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to delete return"}), 500

class UserReturnsAPI(MethodView):
    init_every_request = False

    def __init__(self):
        self.returns_service = ReturnService()

    @token_required_with_repo
    def get(self, user_id):
        try:
            if not self.returns_service.check_user_access(g.current_user, g.is_admin, user_id=user_id):
                logger.warning(f"Access denied for user {g.current_user.id} to returns of user {user_id}")
                return jsonify({"error": "Access denied"}), 403

            user_returns = self.returns_service.get_returns_by_user_id(user_id)
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
        self.returns_service = ReturnService()

    @admin_required_with_repo
    def patch(self, return_id):
        try:
            status_data = return_status_update_schema.load(request.json)
            new_status = ReturnStatus(status_data['status'])

            updated_return = self.returns_service.update_return_status(return_id, new_status)
            if updated_return is None:
                logger.warning(f"Status update failed for return: {return_id}")
                return jsonify({"error": "Failed to update return status"}), 404

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
        self.returns_service = ReturnService()

    @admin_required_with_repo  
    def get(self):
        try:
            all_returns = self.returns_service.get_all_returns()
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

# Register routes when this module is imported by sales/__init__.py
def register_returns_routes(sales_bp):
    # Individual return operations
    sales_bp.add_url_rule('/returns', methods=['POST'], view_func=ReturnAPI.as_view('return_create'))
    sales_bp.add_url_rule('/returns/<int:return_id>', view_func=ReturnAPI.as_view('return'))
    
    # User returns operations
    sales_bp.add_url_rule('/returns/user/<int:user_id>', view_func=UserReturnsAPI.as_view('user_returns'))
    
    # Return status operations
    sales_bp.add_url_rule('/returns/<int:return_id>/status', view_func=ReturnStatusAPI.as_view('return_status'))
    
    # Admin return operations
    sales_bp.add_url_rule('/admin/returns', view_func=AdminReturnsAPI.as_view('admin_returns'))

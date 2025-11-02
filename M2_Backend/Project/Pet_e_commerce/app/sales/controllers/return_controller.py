"""
Return Controller Module

HTTP request processing layer for return operations.
Delegates to ReturnService for business logic.

Responsibilities:
- Request validation and deserialization
- HTTP response formatting
- Error handling and logging
- Access control verification
- Cache-aware data retrieval

Dependencies:
- ReturnService: Business logic and caching
- Flask request/g: Request context
- Marshmallow schemas: Validation
- Auth helpers: Access control

Usage:
    controller = ReturnController()
    response, status = controller.get_list()
    response, status = controller.get(return_id=123)
"""
import logging
from flask import request, jsonify, g
from marshmallow import ValidationError
from typing import Tuple, Optional
from config.logging import get_logger, EXC_INFO_LOG_ERRORS

# Service imports
from app.sales.services.returns_service import ReturnService

# Schema imports
from app.sales.schemas.returns_schema import (
    return_registration_schema,
    return_update_schema,
    return_status_update_schema,
    return_response_schema,
    returns_response_schema
)

# Auth imports
from app.core.lib.auth import is_admin_user, is_user_or_admin

# Model imports
from app.sales.models.returns import ReturnStatus

logger = get_logger(__name__)


class ReturnController:
    """Controller for return HTTP operations."""
    
    def __init__(self):
        """Initialize return controller with service dependency."""
        self.returns_service = ReturnService()
        self.logger = logger
    
    # ============================================
    # PRIVATE HELPER METHODS
    # ============================================
    
    def _check_return_access(self, user_id: int) -> Optional[Tuple[dict, int]]:
        """
        Check if current user has access to the specified user's return.
        Returns error response if access denied, None if access granted.
        
        Args:
            user_id: ID of the user whose return is being accessed
            
        Returns:
            None if access granted, or (error_response, status_code) if denied
        """
        if not is_user_or_admin(user_id):
            self.logger.warning(f"Access denied for user {g.current_user.id} to return for user {user_id}")
            return jsonify({"error": "Access denied"}), 403
        return None
    
    # ============================================
    # RETURN CRUD OPERATIONS
    # ============================================
    
    def get_list(self) -> Tuple[dict, int]:
        """
        Get returns collection - auto-filtered based on user role.
        - Admins: See all returns
        - Users: See only their own returns
        
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            if is_admin_user():
                # Admin: Return all returns (cached)
                returns = self.returns_service.get_all_returns_cached()
                self.logger.info(f"Admin retrieved all returns (total: {len(returns)})")
            else:
                # Customer: Return own returns (cached)
                returns = self.returns_service.get_returns_by_user_id_cached(g.current_user.id)
                self.logger.info(f"Returns retrieved for user {g.current_user.id} (total: {len(returns)})")
            
            return jsonify({
                "total_returns": len(returns),
                "returns": returns_response_schema.dump(returns)
            }), 200
            
        except Exception as e:
            self.logger.error(f"Error retrieving returns: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to retrieve returns"}), 500
    
    def get(self, return_id: int) -> Tuple[dict, int]:
        """
        Get specific return by ID.
        Users can view own returns, admins can view any.
        
        Args:
            return_id: ID of the return to retrieve
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Get return (cached)
            ret = self.returns_service.get_return_by_id_cached(return_id)
            if ret is None:
                self.logger.warning(f"Return not found: {return_id}")
                return jsonify({"error": "Return not found"}), 404
            
            # Check access: admin or owner
            if access_denied := self._check_return_access(ret['user_id']):
                return access_denied
            
            self.logger.info(f"Return retrieved: {return_id}")
            return jsonify(return_response_schema.dump(ret)), 200
            
        except Exception as e:
            self.logger.error(f"Error retrieving return {return_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to retrieve return"}), 500
    
    def post(self) -> Tuple[dict, int]:
        """
        Create new return request.
        Users can create own returns, admins can create any.
        
        Expected JSON:
            {
                "user_id": 123,
                "order_id": 456,
                "reason": "Product damaged",
                "status": "pending"  # optional
            }
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Validate request data
            return_data = return_registration_schema.load(request.json)
            user_id = return_data.get('user_id')
            
            # Check access: admin or owner
            if access_denied := self._check_return_access(user_id):
                return access_denied
            
            # Create return
            created_return = self.returns_service.create_return(**return_data)
            
            if created_return is None:
                self.logger.error(f"Return creation failed for user {user_id}")
                return jsonify({"error": "Failed to create return"}), 400
            
            self.logger.info(f"Return created: {created_return.id if hasattr(created_return, 'id') else 'unknown'}")
            return jsonify({
                "message": "Return request created successfully",
                "return": return_response_schema.dump(created_return)
            }), 201
            
        except ValidationError as err:
            self.logger.warning(f"Return creation validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error creating return: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to create return"}), 500
    
    def put(self, return_id: int) -> Tuple[dict, int]:
        """
        Update existing return (admin only).
        
        Args:
            return_id: ID of the return to update
            
        Expected JSON:
            Return update fields
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Validate request data
            return_data = return_update_schema.load(request.json)
            
            # Check if return exists
            existing_return = self.returns_service.get_return_by_id(return_id)
            if not existing_return:
                self.logger.warning(f"Return update attempt for non-existent return: {return_id}")
                return jsonify({"error": "Return not found"}), 404
            
            # Convert status string to enum if present
            if 'status' in return_data:
                return_data['status'] = ReturnStatus(return_data['status'])
            
            # Update return
            updated_return = self.returns_service.update_return(return_id, **return_data)
            
            if updated_return is None:
                self.logger.error(f"Return update failed for {return_id}")
                return jsonify({"error": "Failed to update return"}), 400
            
            self.logger.info(f"Return updated: {return_id}")
            return jsonify({
                "message": "Return updated successfully",
                "return": return_response_schema.dump(updated_return)
            }), 200
            
        except ValidationError as err:
            self.logger.warning(f"Return update validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error updating return {return_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to update return"}), 500
    
    def patch_status(self, return_id: int) -> Tuple[dict, int]:
        """
        Update return status (admin only).
        
        Args:
            return_id: ID of the return to update
            
        Expected JSON:
            {"status": "approved"}
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Validate request data
            status_data = return_status_update_schema.load(request.json)
            new_status = status_data['status']
            
            # Update return status
            updated_return = self.returns_service.update_return_status(return_id, new_status)
            
            if updated_return is None:
                self.logger.warning(f"Status update failed for return: {return_id}")
                return jsonify({"error": "Failed to update return status"}), 404
            
            self.logger.info(f"Return status updated for {return_id} to {new_status}")
            return jsonify({
                "message": f"Return status updated to {new_status}",
                "return": return_response_schema.dump(updated_return)
            }), 200
            
        except ValidationError as err:
            self.logger.warning(f"Return status update validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error updating return status for {return_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to update return status"}), 500
    
    def delete(self, return_id: int) -> Tuple[dict, int]:
        """
        Delete return (admin only, limited by status).
        
        Args:
            return_id: ID of the return to delete
            
        Returns:
            Tuple of (JSON response, HTTP status code)
        """
        try:
            # Delete return
            success = self.returns_service.delete_return(return_id)
            
            if not success:
                self.logger.warning(f"Delete attempt failed for return: {return_id}")
                return jsonify({"error": "Failed to delete return"}), 404
            
            self.logger.info(f"Return deleted: {return_id}")
            return jsonify({"message": "Return deleted successfully"}), 200
            
        except Exception as e:
            self.logger.error(f"Error deleting return {return_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to delete return"}), 500

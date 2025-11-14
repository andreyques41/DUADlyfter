"""
UserController: Handles HTTP responses for user management endpoints.
Delegates business logic to UserService.

Features:
- User CRUD operations
- Role-based access control
- User role management (admin only)
- Password change functionality
- Comprehensive error handling and logging
"""
from flask import request, jsonify, g
from marshmallow import ValidationError
from config.logging import get_logger, EXC_INFO_LOG_ERRORS
from app.core.lib.error_utils import error_response

# Auth services
from app.auth.services.security_service import hash_password, verify_password
from app.core.lib.auth import is_admin_user, is_user_or_admin

# Schemas
from app.auth.schemas import (
    user_update_schema,
    user_response_schema,
    users_response_schema,
    user_password_change_schema,
    role_assignment_schema
)

# Get logger for this module
logger = get_logger(__name__)


class UserController:
    """
    Controller layer for user management operations.
    Handles HTTP responses, authorization, and delegates to UserService.
    """
    
    def __init__(self):
        self.logger = logger
        # Import here to avoid circular dependency
        from app.auth.services.user_service import UserService
        self.user_service = UserService()
    
    def get(self, user_id=None):
        """
        GET /auth/users or /auth/users/<id>
        Retrieve user profile(s) - specific user by ID or all users.
        
        Access control:
        - All users list: Admin only
        - Specific user: User themselves or admin
        
        Authentication required (via decorator in routes).
        """
        try:
            # Authorization check based on whether getting single user or all users
            if user_id is None:
                # Only admins can see all users
                if not is_admin_user():
                    self.logger.warning(f"Non-admin user {g.current_user.id} attempted to list all users.")
                    return jsonify({"error": "Admin access required"}), 403
                
                # Get all users (cached)
                result = self.user_service.get_all_users_cached(include_sensitive=True)
                self.logger.info("All users retrieved")
                return jsonify(result), 200
            else:
                # Users can only see their own profile, admins can see any
                if not is_user_or_admin(user_id):
                    self.logger.warning(f"User {g.current_user.id} attempted to access user {user_id} profile.")
                    return jsonify({"error": "Access denied"}), 403
                
                # Determine if sensitive data should be included
                include_sensitive = is_admin_user() or g.current_user.id == user_id
                
                # Get specific user (cached)
                result = self.user_service.get_user_by_id_cached(user_id, include_sensitive=include_sensitive)
                
                if result is None:
                    self.logger.warning(f"User not found: {user_id}")
                    return jsonify({"error": "User not found"}), 404

                self.logger.info(f"User retrieved: {user_id}")
                return jsonify(result), 200

        except Exception as e:
            self.logger.error(f"Error retrieving user(s): {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to retrieve user data", e)
    
    def put(self, user_id):
        """
        PUT /auth/users/<id>
        Update user profile or password based on request content.
        
        Access control:
        - User can update their own profile/password
        - Admin can update any user's profile/password
        
        Authentication required (via decorator in routes).
        """
        try:
            # Authorization: Users can only update their own profile, admins can update any
            if not is_user_or_admin(user_id):
                self.logger.warning(f"User {g.current_user.id} attempted to update user {user_id}")
                return jsonify({"error": "Access denied"}), 403

            # Check if this is a password change request
            if request.json and 'current_password' in request.json:
                return self._change_password(user_id)
            else:
                return self._update_profile(user_id)
        except Exception as e:
            self.logger.error(f"Error updating user: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("User update failed", e)
    
    def delete(self, user_id):
        """
        DELETE /auth/users/<id>
        Delete user account by ID.
        
        Access control:
        - User can delete their own account
        - Admin can delete any user account
        
        Authentication required (via decorator in routes).
        """
        try:
            # Authorization: Users can only delete their own account, admins can delete any
            if not is_user_or_admin(user_id):
                self.logger.warning(f"User {g.current_user.id} attempted to delete user {user_id}")
                return jsonify({"error": "Access denied"}), 403

            # Delete user
            success, error = self.user_service.delete_user(user_id)

            if error:
                if error == "User not found":
                    self.logger.warning(f"Delete attempt for non-existent user: {user_id}")
                    return jsonify({"error": error}), 404
                self.logger.error(f"User deletion failed for user {user_id}: {error}")
                return jsonify({"error": error}), 500

            self.logger.info(f"User deleted: {user_id}")
            return jsonify({"message": "User deleted successfully"}), 200

        except Exception as e:
            self.logger.error(f"Error deleting user: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("User deletion failed", e)
    
    # ============ USER ROLES MANAGEMENT ============
    
    def get_roles(self, user_id):
        """
        GET /auth/users/<user_id>/roles
        Get all roles assigned to a user.
        
        Access: Admin only (enforced by decorator in routes)
        """
        try:
            # Get user roles
            roles, error = self.user_service.get_user_roles(user_id)
            
            if error:
                if error == "User not found":
                    self.logger.warning(f"Get roles attempt for non-existent user: {user_id}")
                    return jsonify({"error": error}), 404
                self.logger.error(f"Failed to get roles for user {user_id}: {error}")
                return jsonify({"error": error}), 500
            
            # Get user for username (non-cached, role queries are infrequent)
            user = self.user_service.get_user_by_id(user_id)
            
            response = {
                "user_id": user_id,
                "username": user.username if user else "Unknown",
                "roles": roles
            }
            
            self.logger.debug(f"Retrieved roles for user {user_id}: {roles}")
            return jsonify(response), 200
            
        except Exception as e:
            self.logger.error(f"Error getting user roles: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to retrieve user roles", e)
    
    def assign_role(self, user_id):
        """
        POST /auth/users/<user_id>/roles
        Assign a role to a user.
        
        Access: Admin only (enforced by decorator in routes)
        
        Request Body:
        {
            "role": "admin"  // or "user"
        }
        """
        try:
            # Validate request data
            try:
                validated_data = role_assignment_schema.load(request.json)
            except ValidationError as err:
                self.logger.warning(f"Role assignment validation failed: {err.messages}")
                return jsonify({"error": "Validation failed", "details": err.messages}), 400
            
            role_name = validated_data['role']
            
            # Assign role
            success, error = self.user_service.assign_role_to_user(user_id, role_name)
            
            if error:
                if error == "User not found":
                    self.logger.warning(f"Role assignment attempt for non-existent user: {user_id}")
                    return jsonify({"error": error}), 404
                elif "already has role" in error:
                    self.logger.warning(f"Duplicate role assignment attempt: {error}")
                    return jsonify({"error": error}), 409
                elif "Invalid role" in error:
                    self.logger.warning(f"Invalid role assignment attempt: {error}")
                    return jsonify({"error": error}), 400
                self.logger.error(f"Failed to assign role to user {user_id}: {error}")
                return jsonify({"error": error}), 500
            
            self.logger.info(f"Role '{role_name}' assigned to user {user_id} by admin {g.current_user.id}")
            
            # Get updated roles
            roles, _ = self.user_service.get_user_roles(user_id)
            user = self.user_service.get_user_by_id(user_id)
            
            response = {
                "message": f"Role '{role_name}' assigned successfully",
                "user_id": user_id,
                "username": user.username if user else "Unknown",
                "roles": roles
            }
            
            return jsonify(response), 200
            
        except Exception as e:
            self.logger.error(f"Error assigning role: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to assign role", e)
    
    def remove_role(self, user_id):
        """
        DELETE /auth/users/<user_id>/roles
        Remove a role from a user.
        
        Access: Admin only (enforced by decorator in routes)
        
        Request Body:
        {
            "role": "admin"  // or "user"
        }
        """
        try:
            # Validate request data
            try:
                validated_data = role_assignment_schema.load(request.json)
            except ValidationError as err:
                self.logger.warning(f"Role removal validation failed: {err.messages}")
                return jsonify({"error": "Validation failed", "details": err.messages}), 400
            
            role_name = validated_data['role']
            
            # Remove role
            success, error = self.user_service.remove_role_from_user(user_id, role_name)
            
            if error:
                if error == "User not found":
                    self.logger.warning(f"Role removal attempt for non-existent user: {user_id}")
                    return jsonify({"error": error}), 404
                elif "does not have role" in error:
                    self.logger.warning(f"Role removal attempt for unassigned role: {error}")
                    return jsonify({"error": error}), 404
                elif "Cannot remove the last role" in error:
                    self.logger.warning(f"Attempt to remove last role from user {user_id}")
                    return jsonify({"error": error}), 400
                elif "Invalid role" in error:
                    self.logger.warning(f"Invalid role removal attempt: {error}")
                    return jsonify({"error": error}), 400
                self.logger.error(f"Failed to remove role from user {user_id}: {error}")
                return jsonify({"error": error}), 500
            
            self.logger.info(f"Role '{role_name}' removed from user {user_id} by admin {g.current_user.id}")
            
            # Get updated roles
            roles, _ = self.user_service.get_user_roles(user_id)
            user = self.user_service.get_user_by_id(user_id)
            
            response = {
                "message": f"Role '{role_name}' removed successfully",
                "user_id": user_id,
                "username": user.username if user else "Unknown",
                "roles": roles
            }
            
            return jsonify(response), 200
            
        except Exception as e:
            self.logger.error(f"Error removing role: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to remove role", e)
    
    # ============ PRIVATE HELPER METHODS ============
    
    def _change_password(self, user_id):
        """Handle password change requests. Requires current_password and new_password."""
        try:
            # Validate password change data
            validated_data = user_password_change_schema.load(request.json)
            
            # Get user (non-cached for security)
            user = self.user_service.get_user_by_id(user_id)
            if not user:
                self.logger.warning(f"Password change attempt for non-existent user: {user_id}")
                return jsonify({"error": "User not found"}), 404

            # Verify current password
            if not verify_password(validated_data['current_password'], user.password_hash):
                self.logger.warning(f"Incorrect current password for user: {user.username}")
                return jsonify({"error": "Current password is incorrect"}), 401

            # Update password using service
            new_password_hash = hash_password(validated_data['new_password'])
            updated_user, error = self.user_service.update_user_password(user_id, new_password_hash)

            if error:
                self.logger.error(f"Password update failed for user {user_id}: {error}")
                return jsonify({"error": error}), 500

            self.logger.info(f"Password updated for user {user_id}")
            return jsonify({"message": "Password updated successfully"}), 200

        except ValidationError as err:
            self.logger.warning(f"Password change validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
    
    def _update_profile(self, user_id):
        """Handle profile updates (non-password fields)."""
        try:
            # Validate profile update data
            validated_data = user_update_schema.load(request.json)
            
            # Update user using service
            updated_user, error = self.user_service.update_user_profile(user_id, **validated_data)
            
            if error:
                if error == "User not found":
                    self.logger.warning(f"Profile update attempt for non-existent user: {user_id}")
                    return jsonify({"error": error}), 404
                self.logger.error(f"Profile update failed for user {user_id}: {error}")
                return jsonify({"error": error}), 500

            self.logger.info(f"Profile updated for user {user_id}")
            return jsonify({
                "message": "User profile updated successfully",
                "user": user_response_schema.dump(updated_user)
            }), 200

        except ValidationError as err:
            self.logger.warning(f"Profile update validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400

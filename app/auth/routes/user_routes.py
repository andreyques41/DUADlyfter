"""
User Management Routes Module

HTTP routing for user management endpoints (CRUD, roles).
Delegates to UserController for request processing.

Endpoints:
- GET /users - List all users (admin only)
- GET /users/<id> - Get user details
- PUT /users/<id> - Update user profile/password
- DELETE /users/<id> - Delete user account
- GET /users/<id>/roles - Get user roles (admin only)
- POST /users/<id>/roles - Assign role to user (admin only)
- DELETE /users/<id>/roles - Remove role from user (admin only)

Dependencies:
- UserController: Request processing
- Flask MethodView: RESTful routing
- Blueprint: Modular routing
- JWT: Authentication required

Usage:
    from app.auth.routes.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix='/auth')
"""
from flask import Blueprint
from flask.views import MethodView
from app.auth.controllers.user_controller import UserController

# Blueprint for user management routes
user_bp = Blueprint('users', __name__)


class UserAPI(MethodView):
    """
    User CRUD endpoints.
    
    Endpoints:
        GET /users - Get all users (admin only)
        GET /users/<id> - Get specific user
        PUT /users/<id> - Update user profile or password
        DELETE /users/<id> - Delete user account
    """
    
    def __init__(self):
        self.controller = UserController()
    
    def get(self, user_id=None):
        """
        Handle user retrieval requests.
        
        Args:
            user_id: Optional user ID for specific user lookup
        
        Query Parameters:
            include_sensitive: "true" to include sensitive data (admin only)
        
        Returns:
            200: {"user": {...}} or {"users": [...]}
            401: {"error": "Unauthorized"}
            403: {"error": "Forbidden"}
            404: {"error": "User not found"}
            500: {"error": "Internal server error"}
        """
        return self.controller.get(user_id)
    
    def put(self, user_id):
        """
        Handle user update requests (profile or password).
        
        Expected JSON payload for profile update:
            {
                "username": "string" (optional),
                "email": "string" (optional),
                "first_name": "string" (optional),
                "last_name": "string" (optional),
                "phone": "string" (optional)
            }
        
        Expected JSON payload for password update:
            {
                "old_password": "string",
                "new_password": "string"
            }
        
        Returns:
            200: {"message": "User updated successfully", "user": {...}}
            400: {"error": "Validation error"}
            401: {"error": "Unauthorized"}
            403: {"error": "Forbidden"}
            404: {"error": "User not found"}
            500: {"error": "Internal server error"}
        """
        return self.controller.put(user_id)
    
    def delete(self, user_id):
        """
        Handle user deletion requests.
        
        Returns:
            200: {"message": "User deleted successfully"}
            401: {"error": "Unauthorized"}
            403: {"error": "Forbidden"}
            404: {"error": "User not found"}
            500: {"error": "Internal server error"}
        """
        return self.controller.delete(user_id)


class UserRolesAPI(MethodView):
    """
    User role management endpoints (admin only).
    
    Endpoints:
        GET /users/<id>/roles - Get user's roles
        POST /users/<id>/roles - Assign role to user
        DELETE /users/<id>/roles - Remove role from user
    """
    
    def __init__(self):
        self.controller = UserController()
    
    def get(self, user_id):
        """
        Get all roles assigned to a user.
        
        Returns:
            200: {"roles": ["role1", "role2"]}
            401: {"error": "Unauthorized"}
            403: {"error": "Forbidden - Admin access required"}
            404: {"error": "User not found"}
            500: {"error": "Internal server error"}
        """
        return self.controller.get_roles(user_id)
    
    def post(self, user_id):
        """
        Assign a role to a user.
        
        Expected JSON payload:
            {
                "role_name": "string"
            }
        
        Returns:
            200: {"message": "Role assigned successfully", "roles": [...]}
            400: {"error": "Validation error"}
            401: {"error": "Unauthorized"}
            403: {"error": "Forbidden - Admin access required"}
            404: {"error": "User not found"}
            409: {"error": "User already has this role"}
            500: {"error": "Internal server error"}
        """
        return self.controller.assign_role(user_id)
    
    def delete(self, user_id):
        """
        Remove a role from a user.
        
        Expected JSON payload:
            {
                "role_name": "string"
            }
        
        Returns:
            200: {"message": "Role removed successfully", "roles": [...]}
            400: {"error": "Validation error"}
            401: {"error": "Unauthorized"}
            403: {"error": "Forbidden - Admin access required"}
            404: {"error": "User not found"}
            500: {"error": "Internal server error"}
        """
        return self.controller.remove_role(user_id)


# Register route views
user_view = UserAPI.as_view('user_api')
user_roles_view = UserRolesAPI.as_view('user_roles_api')

# Map routes to views
user_bp.add_url_rule('/users', view_func=user_view, methods=['GET'], defaults={'user_id': None})
user_bp.add_url_rule('/users/<int:user_id>', view_func=user_view, methods=['GET', 'PUT', 'DELETE'])
user_bp.add_url_rule('/users/<int:user_id>/roles', view_func=user_roles_view, methods=['GET', 'POST', 'DELETE'])

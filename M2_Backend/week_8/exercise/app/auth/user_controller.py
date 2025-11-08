
"""
UserController: Handles HTTP responses for user CRUD endpoints.
Delegates business logic to UserService.
"""
from flask import jsonify, g, request

class UserController:
    """
    Controller layer for user management. Handles HTTP responses and delegates to UserService.
    """
    def __init__(self, user_service, logger):
        """
        Initialize UserController.
        :param user_service: Service layer for users
        :param logger: Logger for error reporting
        """
        self.user_service = user_service
        self.logger = logger

    def get(self, user_id=None):
        """
        GET endpoint dispatcher. Calls get_user or get_all_users.
        """
        if user_id:
            return self.get_user(user_id)
        return self.get_all_users()

    def get_user(self, user_id):
        """
        Get a single user by ID. Admins can get any user, clients only their own profile.
        """
        current_user_id = g.user_data['user_id']
        is_admin = g.is_admin
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        if not is_admin and current_user_id != user_id:
            return jsonify({"error": "Forbidden"}), 403
        user.pop('password', None)
        return jsonify({"user": user}), 200

    def get_all_users(self):
        """
        Get all users (admin only).
        """
        is_admin = g.is_admin
        if not is_admin:
            return jsonify({"error": "Forbidden: Admin access required"}), 403
        users = self.user_service.get_all_users()
        return jsonify({"users": users}), 200

    def post(self):
        """
        Create a new user. Admin only.
        """
        data = request.get_json()
        if not data or not data.get("username") or not data.get("password"):
            return jsonify({"error": "Username and password required"}), 400
        user_id, error = self.user_service.create_user(
            username=data.get("username"),
            password=data.get("password"),
            role_id=data.get("role_id", 2)
        )
        if error:
            status = 409 if error == "Username already exists" else 400
            return jsonify({"error": error}), status
        return jsonify({
            "message": "User created successfully",
            "user_id": user_id,
            "role_id": data.get("role_id", 2)
        }), 201

    def put(self, user_id):
        """
        Update user. Admin: all fields, Client: password only.
        """
        current_user_id = g.user_data['user_id']
        is_admin = g.is_admin
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        success, error = self.user_service.update_user(user_id, data, is_admin, current_user_id)
        if not success:
            status = 403 if error == "Forbidden" else 400
            return jsonify({"error": error}), status
        return jsonify({"message": "User updated successfully"}), 200

    def delete(self, user_id):
        """
        Delete user. Admin only, cannot delete own account.
        """
        current_user_id = g.user_data['user_id']
        is_admin = g.is_admin
        success, error = self.user_service.delete_user(user_id, is_admin, current_user_id)
        if not success:
            status = 400 if error == "Cannot delete your own account" else 404 if error == "User not found" else 500
            return jsonify({"error": error}), status
        return jsonify({"message": "User deleted successfully"}), 200

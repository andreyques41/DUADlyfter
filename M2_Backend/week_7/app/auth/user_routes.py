from flask import request, jsonify
from flask.views import MethodView
from app.auth.user_repository import UserRepository
from app.utilities.jwt_manager import JWT_Manager

jwt_manager = JWT_Manager()


class UserAPI(MethodView):
    """CRUD operations for user management."""
    
    def __init__(self, db_manager):
        self.user_repository = UserRepository(db_manager)
    
    def get(self, user_id=None):
        """Get users. Admin: all users, Client: own profile only."""
        user_data = jwt_manager.get_user_from_request()
        if not user_data:
            return jsonify({"error": "Unauthorized"}), 401
        
        current_user_id = user_data.get('user_id')
        is_admin = jwt_manager.is_admin(self.user_repository, current_user_id)
        
        if user_id:
            # Check permission
            if not is_admin and current_user_id != user_id:
                return jsonify({"error": "Forbidden"}), 403
            
            result = self.user_repository.get_by_id(user_id)
            if not result:
                return jsonify({"error": "User not found"}), 404
            
            result.pop('password', None)
            return jsonify({"user": result}), 200
        
        # Get all users (admin only)
        if not is_admin:
            return jsonify({"error": "Forbidden: Admin access required"}), 403
        
        users = self.user_repository.get_all()
        return jsonify({"users": users}), 200
    
    def post(self):
        """Create new user. Admin only."""
        user_data = jwt_manager.get_user_from_request()
        if not user_data:
            return jsonify({"error": "Unauthorized"}), 401
        
        if not jwt_manager.is_admin(self.user_repository, user_data.get('user_id')):
            return jsonify({"error": "Forbidden: Admin access required"}), 403
        
        data = request.get_json()
        if not data or not data.get("username") or not data.get("password"):
            return jsonify({"error": "Username and password required"}), 400
        
        # Check if username exists
        if self.user_repository.get_by_username(data.get("username")):
            return jsonify({"error": "Username already exists"}), 409
        
        role_id = data.get("role_id", 2)
        if role_id not in [1, 2]:
            return jsonify({"error": "Invalid role_id. Must be 1 or 2"}), 400
        
        user_id = self.user_repository.create_user(
            username=data.get("username"),
            password=data.get("password"),
            role_id=role_id
        )
        
        if not user_id:
            return jsonify({"error": "User creation failed"}), 500
        
        return jsonify({
            "message": "User created successfully",
            "user_id": user_id,
            "role_id": role_id
        }), 201
    
    def put(self, user_id):
        """Update user. Admin: all fields, Client: password only."""
        user_data = jwt_manager.get_user_from_request()
        if not user_data:
            return jsonify({"error": "Unauthorized"}), 401
        
        current_user_id = user_data.get('user_id')
        is_admin = jwt_manager.is_admin(self.user_repository, current_user_id)
        
        # Check permission
        if not is_admin and current_user_id != user_id:
            return jsonify({"error": "Forbidden"}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Check if user exists
        existing = self.user_repository.get_by_id(user_id)
        if not existing:
            return jsonify({"error": "User not found"}), 404
        
        # Client can only update password
        if not is_admin:
            invalid_fields = [f for f in data.keys() if f != "password"]
            if invalid_fields:
                return jsonify({"error": "Clients can only update password"}), 403
        else:
            # Admin validations
            if "role_id" in data and data["role_id"] not in [1, 2]:
                return jsonify({"error": "Invalid role_id"}), 400
            
            if "username" in data and data["username"] != existing["username"]:
                if self.user_repository.get_by_username(data["username"]):
                    return jsonify({"error": "Username already exists"}), 409
        
        if not self.user_repository.update_user(user_id, **data):
            return jsonify({"error": "Update failed"}), 500
        
        return jsonify({"message": "User updated successfully"}), 200
    
    def delete(self, user_id):
        """Delete user. Admin only, cannot delete self."""
        user_data = jwt_manager.get_user_from_request()
        if not user_data:
            return jsonify({"error": "Unauthorized"}), 401
        
        current_user_id = user_data.get('user_id')
        if not jwt_manager.is_admin(self.user_repository, current_user_id):
            return jsonify({"error": "Forbidden: Admin access required"}), 403
        
        if current_user_id == user_id:
            return jsonify({"error": "Cannot delete your own account"}), 400
        
        success, error = self.user_repository.delete_user(user_id)
        if not success:
            status_code = 404 if error == "User not found" else 500
            return jsonify({"error": error}), status_code
        
        return jsonify({"message": "User deleted successfully"}), 200

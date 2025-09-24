import logging
from flask import request, jsonify
from flask.views import MethodView
from exercise2.user_repository import UserRepository

logger = logging.getLogger(__name__)


class UserAPI(MethodView):
    """CRUD operations for users - Complete user management functionality"""

    init_every_request = False

    def __init__(self, db_manager):
        self.logger = logger
        self.user_repository = UserRepository(db_manager)

    def get(self, user_id=None):
        """Retrieve all users or specific user."""
        try:
            # Get user(s) using repository method with optional filters
            result = self.user_repository.get_users(
                user_id, request_args=request.args if user_id is None else None
            )

            # Handle not found case for single user
            if user_id is not None and result is None:
                self.logger.warning(f"User not found: {user_id}")
                return jsonify({"error": "User not found"}), 404

            # Handle database errors
            if result is False:
                self.logger.error("Database error occurred while retrieving users")
                return jsonify({"error": "Database error occurred"}), 500

            self.logger.info(
                f"User(s) retrieved: {'all' if user_id is None else user_id}"
            )
            return jsonify({"users": result if isinstance(result, list) else [result]})

        except Exception as e:
            self.logger.error(f"Error retrieving user(s): {e}")
            return jsonify({"error": "Failed to retrieve user data"}), 500

    def post(self):
        """Create new user with validation."""
        try:
            # Get JSON data from request
            data = request.get_json()

            if not data:
                return jsonify({"error": "No JSON data provided"}), 400

            # Basic validation for required fields
            required_fields = [
                "full_name",
                "email",
                "username",
                "password",
                "birthday",
                "account_status_id",
            ]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                return (
                    jsonify(
                        {
                            "error": f"Missing required fields: {', '.join(missing_fields)}"
                        }
                    ),
                    400,
                )

            # Create user using repository
            result = self.user_repository.insert_new_user(
                full_name=data["full_name"],
                email=data["email"],
                username=data["username"],
                password=data["password"],  # In production, hash this password
                birthday=data["birthday"],
                account_status_id=data["account_status_id"],
            )

            if result is False:
                self.logger.error("User creation failed in database")
                return jsonify({"error": "User creation failed"}), 500

            self.logger.info(f"User created: {data['username']}")
            return jsonify({"message": "User created successfully"}), 201

        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            return jsonify({"error": "User creation failed"}), 500

    def put(self, user_id):
        """Update user data - only provided fields are updated, existing values are kept for missing fields."""
        try:
            # Get JSON data from request
            data = request.get_json()

            if not data:
                return jsonify({"error": "No JSON data provided"}), 400

            # Check if user exists first and get existing data
            existing_user = self.user_repository.get_by_id(user_id)
            if existing_user is None:
                self.logger.warning(
                    f"User update attempt for non-existent user: {user_id}"
                )
                return jsonify({"error": "User not found"}), 404

            if existing_user is False:
                return jsonify({"error": "Database error occurred"}), 500

            # Merge request data with existing user data (request data takes priority)
            updated_data = {
                "full_name": data.get("full_name", existing_user["full_name"]),
                "email": data.get("email", existing_user["email"]),
                "username": data.get("username", existing_user["username"]),
                "password": data.get(
                    "password", existing_user["password"]
                ),  # In production, hash this password
                "birthday": data.get("birthday", existing_user["birthday"]),
                "account_status_id": data.get(
                    "account_status_id", existing_user["account_status_id"]
                ),
            }

            # Update user using repository
            result = self.user_repository.update_user(
                _id=user_id,
                full_name=updated_data["full_name"],
                email=updated_data["email"],
                username=updated_data["username"],
                password=updated_data["password"],
                birthday=updated_data["birthday"],
                account_status_id=updated_data["account_status_id"],
            )

            if result is False:
                self.logger.error(f"User update failed for {user_id}")
                return jsonify({"error": "User update failed"}), 500

            self.logger.info(f"User updated: {user_id}")
            return jsonify({"message": "User updated successfully"}), 200

        except Exception as e:
            self.logger.error(f"Error updating user: {e}")
            return jsonify({"error": "User update failed"}), 500

    def delete(self, user_id):
        """Delete user by ID."""
        try:
            success, error = self.user_repository.delete_user(user_id)

            if not success:
                if error == "User not found":
                    self.logger.warning(
                        f"Delete attempt for non-existent user: {user_id}"
                    )
                    return jsonify({"error": error}), 404
                self.logger.error(f"User deletion failed for {user_id}: {error}")
                return jsonify({"error": error}), 500

            self.logger.info(f"User deleted: {user_id}")
            return jsonify({"message": "User deleted successfully"}), 200

        except Exception as e:
            self.logger.error(f"Error deleting user: {e}")
            return jsonify({"error": "User deletion failed"}), 500

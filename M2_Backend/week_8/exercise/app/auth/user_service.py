
"""
UserService: Handles business logic and permission checks for user CRUD operations.
Delegates data access to UserRepository.
"""

class UserService:
    """
    Service layer for user management. Implements business rules and permissions.
    """
    def __init__(self, user_repository, logger):
        """
        Initialize UserService.
        :param user_repository: Data access layer for users
        :param logger: Logger for error reporting
        """
        self.user_repository = user_repository
        self.logger = logger

    def get_user_by_id(self, user_id):
        """
        Retrieve a user by ID.
        """
        return self.user_repository.get_by_id(user_id)

    def get_all_users(self):
        """
        Retrieve all users.
        """
        return self.user_repository.get_all()

    def create_user(self, username, password, role_id=2):
        """
        Create a new user. Returns (user_id, error).
        """
        if self.user_repository.get_by_username(username):
            return None, "Username already exists"
        if role_id not in [1, 2]:
            return None, "Invalid role_id. Must be 1 or 2"
        user_id = self.user_repository.create_user(username, password, role_id)
        if not user_id:
            return None, "User creation failed"
        return user_id, None

    def update_user(self, user_id, data, is_admin, current_user_id):
        """
        Update user fields. Admins can update all fields, clients only password.
        Returns (success, error).
        """
        existing = self.user_repository.get_by_id(user_id)
        if not existing:
            return False, "User not found"
        if not is_admin and current_user_id != user_id:
            return False, "Forbidden"
        # Client can only update password
        if not is_admin:
            invalid_fields = [f for f in data.keys() if f != "password"]
            if invalid_fields:
                return False, "Clients can only update password"
        else:
            if "role_id" in data and data["role_id"] not in [1, 2]:
                return False, "Invalid role_id"
            if "username" in data and data["username"] != existing["username"]:
                if self.user_repository.get_by_username(data["username"]):
                    return False, "Username already exists"
        success = self.user_repository.update_user(user_id, **data)
        if not success:
            return False, "Update failed"
        return True, None

    def delete_user(self, user_id, is_admin, current_user_id):
        """
        Delete a user. Admin only, cannot delete own account.
        Returns (success, error).
        """
        if not is_admin:
            return False, "Forbidden"
        if current_user_id == user_id:
            return False, "Cannot delete your own account"
        success, error = self.user_repository.delete_user(user_id)
        if not success:
            return False, error
        return True, None

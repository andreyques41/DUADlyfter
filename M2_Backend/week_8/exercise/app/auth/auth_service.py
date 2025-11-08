"""
AuthService: Handles business logic for user registration and login.
Uses UserRepository for data access and JWT_Manager for token generation.
"""
from app.auth.user_repository import UserRepository
from app.utilities.jwt_manager import JWT_Manager

class AuthService:
    """
    Service layer for authentication (register, login).
    """
    def __init__(self, user_repository: UserRepository, jwt_manager: JWT_Manager):
        """
        Initialize AuthService.
        :param user_repository: Data access layer for users
        :param jwt_manager: JWT token manager
        """
        self.user_repository = user_repository
        self.jwt_manager = jwt_manager

    def register_user(self, data):
        """
        Register a new user. Returns (result_dict, error, status_code).
        """
        if not data:
            return None, "No JSON data provided", 400
        if not data.get("username") or not data.get("password"):
            return None, "Username and password required", 400
        if self.user_repository.get_by_username(data.get("username")):
            return None, "Username already exists", 409
        user_id = self.user_repository.create_user(
            username=data.get("username"),
            password=data.get("password"),
            role_id=2
        )
        if not user_id:
            return None, "User registration failed", 500
        token = self.jwt_manager.generate_jwt_token({
            "id": user_id,
            "username": data.get("username"),
            "role_id": 2
        })
        result = {
            "message": "User registered successfully",
            "token": token,
            "user_id": user_id
        }
        return result, None, 201

    def login_user(self, data):
        """
        Login a user. Returns (result_dict, error, status_code).
        """
        if not data:
            return None, "No JSON data provided", 400
        if not data.get("username") or not data.get("password"):
            return None, "Username and password required", 400
        user = self.user_repository.get_by_username(data.get("username"))
        if not user or user["password"] != data.get("password"):
            return None, "Invalid credentials", 401
        token = self.jwt_manager.generate_jwt_token({
            "id": user["id"],
            "username": user["username"],
            "role_id": user["role_id"],
            "is_admin": user["role_id"] == 1
        })
        result = {
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "role": user["role_name"],
                "is_admin": user["role_id"] == 1
            }
        }
        return result, None, 200

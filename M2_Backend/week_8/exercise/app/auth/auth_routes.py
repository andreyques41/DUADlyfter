from flask import request, jsonify
from flask.views import MethodView
from app.utilities.jwt_manager import JWT_Manager
from app.auth.user_repository import UserRepository

jwt_manager = JWT_Manager()


class RegisterAPI(MethodView):
    def __init__(self, db_manager):
        self.user_repository = UserRepository(db_manager)
    
    def post(self):
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        if not data.get("username") or not data.get("password"):
            return jsonify({"error": "Username and password required"}), 400
        existing_user = self.user_repository.get_by_username(data.get("username"))
        if existing_user:
            return jsonify({"error": "Username already exists"}), 409
        user_id = self.user_repository.create_user(
            username=data.get("username"), 
            password=data.get("password"), 
            role_id=2
        )
        if not user_id:
            return jsonify({"error": "User registration failed"}), 500
        token = jwt_manager.generate_jwt_token({
            "id": user_id, 
            "username": data.get("username"), 
            "role_id": 2
        })
        return jsonify({
            "message": "User registered successfully", 
            "token": token, 
            "user_id": user_id
        }), 201


class LoginAPI(MethodView):
    def __init__(self, db_manager):
        self.user_repository = UserRepository(db_manager)
    
    def post(self):
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        if not data.get("username") or not data.get("password"):
            return jsonify({"error": "Username and password required"}), 400
        user = self.user_repository.get_by_username(data.get("username"))
        if not user or user["password"] != data.get("password"):
            return jsonify({"error": "Invalid credentials"}), 401
        token = jwt_manager.generate_jwt_token({
            "id": user["id"], 
            "username": user["username"], 
            "role_id": user["role_id"], 
            "is_admin": user["role_id"] == 1
        })
        return jsonify({
            "message": "Login successful", 
            "token": token, 
            "user": {
                "id": user["id"], 
                "username": user["username"], 
                "role": user["role_name"], 
                "is_admin": user["role_id"] == 1
            }
        }), 200
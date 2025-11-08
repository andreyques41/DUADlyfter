"""
AuthController: Handles HTTP responses for registration and login endpoints.
Delegates business logic to AuthService.
"""
from flask import jsonify, request

class AuthController:
    """
    Controller layer for authentication (register, login).
    """
    def __init__(self, auth_service):
        """
        Initialize AuthController.
        :param auth_service: Service layer for authentication
        """
        self.auth_service = auth_service

    def register(self):
        """
        Handle user registration. Returns HTTP response.
        """
        data = request.get_json()
        result, error, status = self.auth_service.register_user(data)
        if error:
            return jsonify({"error": error}), status
        return jsonify(result), status

    def login(self):
        """
        Handle user login. Returns HTTP response.
        """
        data = request.get_json()
        result, error, status = self.auth_service.login_user(data)
        if error:
            return jsonify({"error": error}), status
        return jsonify(result), status

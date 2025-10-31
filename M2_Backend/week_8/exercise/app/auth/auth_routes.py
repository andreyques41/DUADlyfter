from flask import request, jsonify
from flask.views import MethodView

from app.utilities.jwt_manager import JWT_Manager
from app.auth.user_repository import UserRepository
from app.auth.auth_service import AuthService
from app.auth.auth_controller import AuthController

jwt_manager = JWT_Manager()


class RegisterAPI(MethodView):
    """
    API endpoint for user registration. Delegates to AuthController.
    """
    def __init__(self, db_manager):
        self.user_repository = UserRepository(db_manager)
        self.auth_service = AuthService(self.user_repository, jwt_manager)
        self.controller = AuthController(self.auth_service)

    def post(self):
        """
        POST endpoint for user registration.
        """
        return self.controller.register()


class LoginAPI(MethodView):
    """
    API endpoint for user login. Delegates to AuthController.
    """
    def __init__(self, db_manager):
        self.user_repository = UserRepository(db_manager)
        self.auth_service = AuthService(self.user_repository, jwt_manager)
        self.controller = AuthController(self.auth_service)

    def post(self):
        """
        POST endpoint for user login.
        """
        return self.controller.login()
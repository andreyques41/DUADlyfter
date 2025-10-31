from flask import request, jsonify, g
from flask.views import MethodView
import logging
from app.auth.user_repository import UserRepository
from app.auth.user_service import UserService
from app.auth.user_controller import UserController
from app.utilities.decorators import require_auth_with_repo, require_admin_with_repo


class UserAPI(MethodView):
    """
    UserAPI: Flask route class for user CRUD operations.
    Delegates all logic to UserController.
    """
    
    def __init__(self, db_manager):
        """
        Initialize UserAPI with database manager and controller.
        """
        self.logger = logging.getLogger(__name__)
        self.user_repository = UserRepository(db_manager)
        self.user_service = UserService(self.user_repository, self.logger)
        self.controller = UserController(self.user_service, self.logger)
    
    @require_auth_with_repo('user_repository')
    def get(self, user_id=None):
        """
        GET endpoint. Calls controller to get user(s).
        """
        return self.controller.get(user_id)
    
    @require_admin_with_repo('user_repository')
    def post(self):
        """
        POST endpoint. Calls controller to create user.
        """
        return self.controller.post()
    
    @require_auth_with_repo('user_repository')
    def put(self, user_id):
        """
        PUT endpoint. Calls controller to update user.
        """
        return self.controller.put(user_id)
    
    @require_admin_with_repo('user_repository')
    def delete(self, user_id):
        """
        DELETE endpoint. Calls controller to delete user.
        """
        return self.controller.delete(user_id)

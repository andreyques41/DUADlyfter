"""
Auth Routes
Blueprint registration for authentication endpoints.
"""

from flask import Blueprint
from app.auth.controllers import AuthController
from app.core.middleware.auth_middleware import jwt_required

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    POST /auth/register
    Register a new user.
    """
    return AuthController.register()


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    POST /auth/login
    Authenticate user and receive JWT token.
    """
    return AuthController.login()


@auth_bp.route('/me', methods=['GET'])
@jwt_required
def get_current_user():
    """
    GET /auth/me
    Get current authenticated user information.
    Requires: Authorization header with Bearer token
    """
    return AuthController.get_current_user()

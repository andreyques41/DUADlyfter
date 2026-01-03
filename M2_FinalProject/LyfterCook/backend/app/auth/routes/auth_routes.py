"""
Auth Routes
Blueprint registration for authentication endpoints.
"""

from flask import Blueprint
from app.auth.controllers import AuthController
from app.core.middleware.auth_middleware import jwt_required
from app.core.limiter import limiter

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Initialize controller
auth_controller = AuthController()


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("3 per minute")
def register():
    """
    POST /auth/register
    Register a new user.
    """
    return auth_controller.register()


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """
    POST /auth/login
    Authenticate user and receive JWT token.
    """
    return auth_controller.login()


@auth_bp.route('/me', methods=['GET'])
@limiter.limit("60 per minute")
@jwt_required
def get_current_user():
    """
    GET /auth/me
    Get current authenticated user information.
    Requires: Authorization header with Bearer token
    """
    return auth_controller.get_current_user()

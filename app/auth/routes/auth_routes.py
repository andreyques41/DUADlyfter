"""
Authentication Routes Module

HTTP routing for authentication endpoints (login, register).
Delegates to AuthController for request processing.

Endpoints:
- POST /auth/login - User login with credentials
- POST /auth/register - New user registration

Dependencies:
- AuthController: Request processing
- Flask MethodView: RESTful routing
- Blueprint: Modular routing

Usage:
    from app.auth.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
"""
from flask import Blueprint
from flask.views import MethodView
from app.auth.controllers.auth_controller import AuthController

# Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)


class AuthAPI(MethodView):
    """
    Authentication endpoint for user login.
    
    Endpoints:
        POST /auth/login - Authenticate user and generate JWT token
    """
    
    def __init__(self):
        self.controller = AuthController()
    
    def post(self):
        """
        Handle user login requests.
        
        Expected JSON payload:
            {
                "username": "string",
                "password": "string"
            }
        
        Returns:
            200: {"token": "jwt_token", "user": {...}}
            400: {"error": "Validation error"}
            401: {"error": "Invalid credentials"}
            500: {"error": "Internal server error"}
        """
        return self.controller.login()


class RegisterAPI(MethodView):
    """
    User registration endpoint.
    
    Endpoints:
        POST /auth/register - Create new user account
    """
    
    def __init__(self):
        self.controller = AuthController()
    
    def post(self):
        """
        Handle user registration requests.
        
        Expected JSON payload:
            {
                "username": "string",
                "email": "string",
                "password": "string",
                "first_name": "string" (optional),
                "last_name": "string" (optional),
                "phone": "string" (optional)
            }
        
        Returns:
            201: {"message": "User created successfully", "user": {...}}
            400: {"error": "Validation error"}
            409: {"error": "Username/email already exists"}
            500: {"error": "Internal server error"}
        """
        return self.controller.register()


# Register route views
auth_view = AuthAPI.as_view('auth_api')
register_view = RegisterAPI.as_view('register_api')

# Map routes to views
auth_bp.add_url_rule('/login', view_func=auth_view, methods=['POST'])
auth_bp.add_url_rule('/register', view_func=register_view, methods=['POST'])

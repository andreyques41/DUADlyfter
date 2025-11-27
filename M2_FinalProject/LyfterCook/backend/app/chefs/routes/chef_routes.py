"""
Chef Routes
Blueprint registration for chef profile endpoints
"""
from flask import Blueprint
from app.chefs.controllers import ChefController
from app.core.middleware.auth_middleware import jwt_required

# Create blueprint
chef_bp = Blueprint('chefs', __name__, url_prefix='/chefs')

# Initialize controller
chef_controller = ChefController()


@chef_bp.route('/profile', methods=['POST'])
@jwt_required
def create_profile():
    """
    POST /chefs/profile
    Create chef profile for authenticated user
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return chef_controller.create_profile(g.current_user)


@chef_bp.route('/profile', methods=['GET'])
@jwt_required
def get_my_profile():
    """
    GET /chefs/profile
    Get current user's chef profile
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return chef_controller.get_my_profile(g.current_user)


@chef_bp.route('/profile', methods=['PUT'])
@jwt_required
def update_my_profile():
    """
    PUT /chefs/profile
    Update current user's chef profile
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return chef_controller.update_my_profile(g.current_user)


@chef_bp.route('', methods=['GET'])
def get_all_chefs():
    """
    GET /chefs
    Get all active chef profiles (public endpoint)
    Query params: include_inactive=true (optional)
    """
    return chef_controller.get_all_chefs()


@chef_bp.route('/<int:chef_id>', methods=['GET'])
def get_chef_by_id(chef_id):
    """
    GET /chefs/:id
    Get chef profile by ID (public endpoint)
    """
    return chef_controller.get_chef_by_id(chef_id)

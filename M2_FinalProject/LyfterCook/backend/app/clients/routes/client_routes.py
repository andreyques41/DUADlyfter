"""
Client Routes
Blueprint registration for client endpoints
"""
from flask import Blueprint
from app.clients.controllers import ClientController
from app.core.middleware.auth_middleware import jwt_required

# Create blueprint
client_bp = Blueprint('clients', __name__, url_prefix='/clients')

# Initialize controller
client_controller = ClientController()


@client_bp.route('', methods=['POST'])
@jwt_required
def create_client():
    """
    POST /clients
    Create a new client
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return client_controller.create_client(g.current_user)


@client_bp.route('', methods=['GET'])
@jwt_required
def get_all_clients():
    """
    GET /clients
    Get all clients for the current chef
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return client_controller.get_all_clients(g.current_user)


@client_bp.route('/<int:client_id>', methods=['GET'])
@jwt_required
def get_client_by_id(client_id):
    """
    GET /clients/:id
    Get client by ID
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return client_controller.get_client_by_id(client_id, g.current_user)


@client_bp.route('/<int:client_id>', methods=['PUT'])
@jwt_required
def update_client(client_id):
    """
    PUT /clients/:id
    Update client
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return client_controller.update_client(client_id, g.current_user)


@client_bp.route('/<int:client_id>', methods=['DELETE'])
@jwt_required
def delete_client(client_id):
    """
    DELETE /clients/:id
    Delete client
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return client_controller.delete_client(client_id, g.current_user)

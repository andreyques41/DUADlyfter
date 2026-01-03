"""
Quotation Routes
Blueprint registration for quotation endpoints
"""
from flask import Blueprint
from app.quotations.controllers import QuotationController
from app.core.middleware.auth_middleware import jwt_required

# Create blueprint
quotation_bp = Blueprint('quotations', __name__, url_prefix='/quotations')

# Initialize controller
quotation_controller = QuotationController()


@quotation_bp.route('', methods=['POST'])
@jwt_required
def create_quotation():
    """
    POST /quotations
    Create a new quotation with items
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return quotation_controller.create_quotation(g.current_user)


@quotation_bp.route('', methods=['GET'])
@jwt_required
def get_all_quotations():
    """
    GET /quotations
    Get all quotations for the current chef
    Query params: status=draft|sent|accepted|rejected|expired (optional)
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return quotation_controller.get_all_quotations(g.current_user)


@quotation_bp.route('/<int:quotation_id>', methods=['GET'])
@jwt_required
def get_quotation_by_id(quotation_id):
    """
    GET /quotations/:id
    Get quotation by ID with items
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return quotation_controller.get_quotation_by_id(quotation_id, g.current_user)


@quotation_bp.route('/<int:quotation_id>', methods=['PUT'])
@jwt_required
def update_quotation(quotation_id):
    """
    PUT /quotations/:id
    Update quotation (only draft status)
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return quotation_controller.update_quotation(quotation_id, g.current_user)


@quotation_bp.route('/<int:quotation_id>/status', methods=['PATCH'])
@jwt_required
def update_quotation_status(quotation_id):
    """
    PATCH /quotations/:id/status
    Update quotation status
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return quotation_controller.update_quotation_status(quotation_id, g.current_user)


@quotation_bp.route('/<int:quotation_id>', methods=['DELETE'])
@jwt_required
def delete_quotation(quotation_id):
    """
    DELETE /quotations/:id
    Delete quotation (only draft status)
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return quotation_controller.delete_quotation(quotation_id, g.current_user)


@quotation_bp.route('/<int:quotation_id>/pdf', methods=['GET'])
@jwt_required
def download_quotation_pdf(quotation_id):
    """GET /quotations/:id/pdf - Download quotation as PDF."""
    from flask import g
    return quotation_controller.download_quotation_pdf(quotation_id, g.current_user)


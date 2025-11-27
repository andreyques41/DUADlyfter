"""
Appointment Routes
Blueprint registration for appointment endpoints
"""
from flask import Blueprint
from app.appointments.controllers import AppointmentController
from app.core.middleware.auth_middleware import jwt_required

# Create blueprint
appointment_bp = Blueprint('appointments', __name__, url_prefix='/appointments')

# Initialize controller
appointment_controller = AppointmentController()


@appointment_bp.route('', methods=['POST'])
@jwt_required
def create_appointment():
    """
    POST /appointments
    Create a new appointment
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return appointment_controller.create_appointment(g.current_user)


@appointment_bp.route('', methods=['GET'])
@jwt_required
def get_all_appointments():
    """
    GET /appointments
    Get all appointments for the current chef
    Query params: 
        - status: str (optional)
        - start_date: ISO datetime (optional)
        - end_date: ISO datetime (optional)
        - upcoming: bool (optional) - Get only upcoming appointments
        - days: int (optional, default: 7) - Days to look ahead for upcoming
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return appointment_controller.get_all_appointments(g.current_user)


@appointment_bp.route('/<int:appointment_id>', methods=['GET'])
@jwt_required
def get_appointment_by_id(appointment_id):
    """
    GET /appointments/:id
    Get appointment by ID
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return appointment_controller.get_appointment_by_id(appointment_id, g.current_user)


@appointment_bp.route('/<int:appointment_id>', methods=['PUT'])
@jwt_required
def update_appointment(appointment_id):
    """
    PUT /appointments/:id
    Update appointment
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return appointment_controller.update_appointment(appointment_id, g.current_user)


@appointment_bp.route('/<int:appointment_id>/status', methods=['PATCH'])
@jwt_required
def update_appointment_status(appointment_id):
    """
    PATCH /appointments/:id/status
    Update appointment status
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return appointment_controller.update_appointment_status(appointment_id, g.current_user)


@appointment_bp.route('/<int:appointment_id>', methods=['DELETE'])
@jwt_required
def delete_appointment(appointment_id):
    """
    DELETE /appointments/:id
    Delete appointment
    Requires: Authorization header with Bearer token
    """
    from flask import g
    return appointment_controller.delete_appointment(appointment_id, g.current_user)

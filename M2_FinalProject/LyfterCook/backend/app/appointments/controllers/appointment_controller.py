"""
Appointment Controller - HTTP request/response handling for appointment endpoints
"""
from flask import request, jsonify, g
from datetime import datetime
from app.appointments.schemas import (
    AppointmentCreateSchema,
    AppointmentUpdateSchema,
    AppointmentResponseSchema,
    AppointmentStatusUpdateSchema
)
from app.appointments.services import AppointmentService
from app.appointments.repositories import AppointmentRepository
from app.chefs.repositories import ChefRepository
from app.clients.repositories import ClientRepository
from app.core.lib.error_utils import error_response, success_response
from app.core.database import get_db
from app.core.middleware.request_decorators import validate_json
from config.logging import get_logger

logger = get_logger(__name__)


class AppointmentController:
    """Controller for appointment operations"""
    
    def __init__(self):
        """Initialize controller with logger"""
        self.logger = logger
    
    def _get_service(self):
        """
        Get appointment service with database session.
        Creates new instances per request using Flask's g.db.
        """
        db = get_db()
        appointment_repo = AppointmentRepository(db)
        chef_repo = ChefRepository(db)
        client_repo = ClientRepository(db)
        return AppointmentService(appointment_repo, chef_repo, client_repo)
    
    @validate_json(AppointmentCreateSchema)
    def create_appointment(self, current_user):
        """
        Create a new appointment
        
        Request body:
            {
                "client_id": 1,  // Optional
                "title": "Menu Tasting Session",
                "description": "Discuss requirements for wedding reception",
                "scheduled_at": "2025-12-15T14:00:00",
                "duration_minutes": 90,
                "location": "Chef's Kitchen, 123 Main St",
                "meeting_url": "https://zoom.us/j/123456789",  // Optional
                "notes": "Client prefers vegetarian options"
            }
        
        Returns:
            201: Appointment created successfully
            400: Validation error
            500: Server error
        """
        try:
            service = self._get_service()
            appointment_data = request.validated_data
            
            appointment = service.create_appointment(current_user['id'], appointment_data)
            
            # Serialize response
            schema = AppointmentResponseSchema()
            result = schema.dump(appointment)
            
            self.logger.info(f"Appointment created for user {current_user['id']}")
            return success_response(
                data=result,
                message="Appointment created successfully",
                status=201
            )
            
        except ValueError as e:
            self.logger.warning(f"Appointment creation failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Error creating appointment: {e}", exc_info=True)
            return error_response("Failed to create appointment", 500)
    
    def get_all_appointments(self, current_user):
        """
        Get all appointments for the current chef
        
        Query params:
            status: str (optional) - Filter by status
            start_date: ISO datetime (optional) - Filter from date
            end_date: ISO datetime (optional) - Filter to date
            upcoming: bool (optional) - Get only upcoming appointments (next 7 days)
        
        Returns:
            200: List of appointments
            400: Chef profile not found or invalid dates
            500: Server error
        """
        try:
            service = self._get_service()
            
            # Check for upcoming flag
            upcoming = request.args.get('upcoming', 'false').lower() == 'true'
            
            if upcoming:
                days = int(request.args.get('days', '7'))
                appointments = service.get_upcoming_appointments(current_user['id'], days=days)
            else:
                # Get filters from query params
                status = request.args.get('status')
                start_date = request.args.get('start_date')
                end_date = request.args.get('end_date')
                
                # Parse dates if provided
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00')) if start_date else None
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00')) if end_date else None
                
                appointments = service.get_all_appointments(
                    current_user['id'],
                    status=status,
                    start_date=start_dt,
                    end_date=end_dt
                )
            
            # Serialize response
            schema = AppointmentResponseSchema(many=True)
            result = schema.dump(appointments)
            
            return success_response(
                data=result,
                message=f"Retrieved {len(result)} appointments"
            )
            
        except ValueError as e:
            self.logger.warning(f"Get appointments failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Error retrieving appointments: {e}", exc_info=True)
            return error_response("Failed to retrieve appointments", 500)
    
    def get_appointment_by_id(self, appointment_id: int, current_user):
        """
        Get appointment by ID
        
        Args:
            appointment_id: Appointment ID from URL parameter
        
        Returns:
            200: Appointment data
            404: Appointment not found or access denied
            500: Server error
        """
        try:
            service = self._get_service()
            appointment = service.get_appointment_by_id(appointment_id, current_user['id'])
            
            if not appointment:
                return error_response("Appointment not found or access denied", 404)
            
            # Serialize response
            schema = AppointmentResponseSchema()
            result = schema.dump(appointment)
            
            return success_response(data=result)
            
        except ValueError as e:
            self.logger.warning(f"Get appointment failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            self.logger.error(f"Error retrieving appointment {appointment_id}: {e}", exc_info=True)
            return error_response("Failed to retrieve appointment", 500)
    
    @validate_json(AppointmentUpdateSchema)
    def update_appointment(self, appointment_id: int, current_user):
        """
        Update appointment
        
        Args:
            appointment_id: Appointment ID from URL parameter
        
        Request body (all fields optional):
            {
                "title": "Updated Title",
                "scheduled_at": "2025-12-20T15:00:00",
                "duration_minutes": 120,
                "notes": "Updated notes"
            }
        
        Returns:
            200: Appointment updated successfully
            400: Validation error or appointment already completed/cancelled
            404: Appointment not found or access denied
            500: Server error
        """
        try:
            service = self._get_service()
            update_data = request.validated_data
            
            appointment = service.update_appointment(appointment_id, current_user['id'], update_data)
            
            # Serialize response
            schema = AppointmentResponseSchema()
            result = schema.dump(appointment)
            
            self.logger.info(f"Appointment {appointment_id} updated")
            return success_response(
                data=result,
                message="Appointment updated successfully"
            )
            
        except ValueError as e:
            self.logger.warning(f"Appointment update failed: {str(e)}")
            status_code = 404 if "not found" in str(e).lower() else 400
            return error_response(str(e), status_code)
        except Exception as e:
            self.logger.error(f"Error updating appointment {appointment_id}: {e}", exc_info=True)
            return error_response("Failed to update appointment", 500)
    
    @validate_json(AppointmentStatusUpdateSchema)
    def update_appointment_status(self, appointment_id: int, current_user):
        """
        Update appointment status
        
        Args:
            appointment_id: Appointment ID from URL parameter
        
        Request body:
            {
                "status": "confirmed",  // scheduled, confirmed, cancelled, completed, no_show
                "cancellation_reason": "Client requested reschedule"  // Optional, for cancelled status
            }
        
        Returns:
            200: Status updated successfully
            400: Invalid status transition
            404: Appointment not found or access denied
            500: Server error
        """
        try:
            service = self._get_service()
            data = request.validated_data
            status = data['status']
            cancellation_reason = data.get('cancellation_reason')
            
            appointment = service.update_appointment_status(
                appointment_id, 
                current_user['id'], 
                status,
                cancellation_reason
            )
            
            # Serialize response
            schema = AppointmentResponseSchema()
            result = schema.dump(appointment)
            
            self.logger.info(f"Appointment {appointment_id} status updated to {status}")
            return success_response(
                data=result,
                message=f"Appointment status updated to '{status}'"
            )
            
        except ValueError as e:
            self.logger.warning(f"Status update failed: {str(e)}")
            status_code = 404 if "not found" in str(e).lower() else 400
            return error_response(str(e), status_code)
        except Exception as e:
            self.logger.error(f"Error updating appointment status {appointment_id}: {e}", exc_info=True)
            return error_response("Failed to update appointment status", 500)
    
    def delete_appointment(self, appointment_id: int, current_user):
        """
        Delete appointment
        
        Args:
            appointment_id: Appointment ID from URL parameter
        
        Returns:
            200: Appointment deleted successfully
            400: Cannot delete completed appointment
            404: Appointment not found or access denied
            500: Server error
        """
        try:
            service = self._get_service()
            service.delete_appointment(appointment_id, current_user['id'])
            
            self.logger.info(f"Appointment {appointment_id} deleted")
            return success_response(
                message="Appointment deleted successfully"
            )
            
        except ValueError as e:
            self.logger.warning(f"Appointment deletion failed: {str(e)}")
            status_code = 404 if "not found" in str(e).lower() else 400
            return error_response(str(e), status_code)
        except Exception as e:
            self.logger.error(f"Error deleting appointment {appointment_id}: {e}", exc_info=True)
            return error_response("Failed to delete appointment", 500)

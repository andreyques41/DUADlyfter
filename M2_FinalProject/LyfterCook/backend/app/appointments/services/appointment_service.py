"""
Appointment Service - Business logic for appointment management
"""
from typing import Optional, List
from datetime import datetime, timedelta
from app.appointments.repositories.appointment_repository import AppointmentRepository
from app.appointments.models.appointment_model import Appointment
from app.chefs.repositories.chef_repository import ChefRepository
from app.clients.repositories.client_repository import ClientRepository
from config.logging import get_logger

logger = get_logger(__name__)


class AppointmentService:
    """Service for appointment business logic"""
    
    def __init__(
        self,
        appointment_repository: AppointmentRepository,
        chef_repository: ChefRepository,
        client_repository: ClientRepository
    ):
        self.appointment_repository = appointment_repository
        self.chef_repository = chef_repository
        self.client_repository = client_repository
    
    def create_appointment(self, user_id: int, appointment_data: dict) -> Appointment:
        """
        Create a new appointment for a chef
        
        Args:
            user_id: User ID of the chef
            appointment_data: Dictionary with appointment information
            
        Returns:
            Created Appointment instance
            
        Raises:
            ValueError: If chef profile not found or validation fails
        """
        # Get chef profile
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            logger.warning(f"Attempted to create appointment for user {user_id} without chef profile")
            raise ValueError("Chef profile not found. Please create your chef profile first.")
        
        # Validate client if provided
        if appointment_data.get('client_id'):
            client = self.client_repository.get_by_id(appointment_data['client_id'])
            if not client or client.chef_id != chef.id:
                raise ValueError("Client not found or does not belong to you")
        
        # Add chef_id and set default status
        appointment_data['chef_id'] = chef.id
        appointment_data['status'] = 'scheduled'
        
        appointment = self.appointment_repository.create(appointment_data)
        logger.info(f"Created appointment {appointment.id} for chef {chef.id}")
        return appointment
    
    def get_appointment_by_id(self, appointment_id: int, user_id: int) -> Optional[Appointment]:
        """
        Get appointment by ID (only if owned by the chef)
        
        Args:
            appointment_id: Appointment ID
            user_id: User ID of the chef
            
        Returns:
            Appointment instance or None if not found or not owned
            
        Raises:
            ValueError: If chef profile not found
        """
        # Get chef profile
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            raise ValueError("Chef profile not found")
        
        # Get appointment
        appointment = self.appointment_repository.get_by_id(appointment_id)
        
        # Verify ownership
        if appointment and appointment.chef_id != chef.id:
            logger.warning(f"User {user_id} attempted to access appointment {appointment_id} owned by chef {appointment.chef_id}")
            return None
        
        return appointment
    
    def get_all_appointments(
        self, 
        user_id: int, 
        status: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Appointment]:
        """
        Get all appointments for a chef
        
        Args:
            user_id: User ID of the chef
            status: Optional status filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of Appointment instances
            
        Raises:
            ValueError: If chef profile not found
        """
        # Get chef profile
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            raise ValueError("Chef profile not found")
        
        return self.appointment_repository.get_by_chef_id(
            chef.id, 
            status=status,
            start_date=start_date,
            end_date=end_date
        )
    
    def get_upcoming_appointments(self, user_id: int, days: int = 7) -> List[Appointment]:
        """
        Get upcoming appointments for a chef
        
        Args:
            user_id: User ID of the chef
            days: Number of days to look ahead (default: 7)
            
        Returns:
            List of upcoming Appointment instances
            
        Raises:
            ValueError: If chef profile not found
        """
        # Get chef profile
        chef = self.chef_repository.get_by_user_id(user_id)
        if not chef:
            raise ValueError("Chef profile not found")
        
        return self.appointment_repository.get_upcoming_appointments(chef.id, days=days)
    
    def update_appointment(self, appointment_id: int, user_id: int, update_data: dict) -> Appointment:
        """
        Update appointment (only if owned by the chef)
        
        Args:
            appointment_id: Appointment ID
            user_id: User ID of the chef
            update_data: Dictionary with fields to update
            
        Returns:
            Updated Appointment instance
            
        Raises:
            ValueError: If appointment not found, not owned, or already completed/cancelled
        """
        # Get appointment with ownership check
        appointment = self.get_appointment_by_id(appointment_id, user_id)
        if not appointment:
            raise ValueError("Appointment not found or access denied")
        
        # Don't allow updates to completed or cancelled appointments
        if appointment.status in ['completed', 'cancelled']:
            raise ValueError(f"Cannot update appointment with status '{appointment.status}'")
        
        # Get chef for validations
        chef = self.chef_repository.get_by_user_id(user_id)
        
        # Validate client if being updated
        if 'client_id' in update_data and update_data['client_id']:
            client = self.client_repository.get_by_id(update_data['client_id'])
            if not client or client.chef_id != chef.id:
                raise ValueError("Client not found or does not belong to you")
        
        # Filter allowed fields
        allowed_fields = ['client_id', 'title', 'description', 'scheduled_at', 
                         'duration_minutes', 'location', 'meeting_url', 'notes']
        filtered_data = {
            k: v for k, v in update_data.items() 
            if k in allowed_fields
        }
        
        updated_appointment = self.appointment_repository.update(appointment, filtered_data)
        logger.info(f"Updated appointment {appointment_id}")
        return updated_appointment
    
    def update_appointment_status(
        self, 
        appointment_id: int, 
        user_id: int, 
        status: str,
        cancellation_reason: str = None
    ) -> Appointment:
        """
        Update appointment status
        
        Args:
            appointment_id: Appointment ID
            user_id: User ID of the chef
            status: New status
            cancellation_reason: Reason for cancellation (if applicable)
            
        Returns:
            Updated Appointment instance
            
        Raises:
            ValueError: If appointment not found or invalid status transition
        """
        # Get appointment with ownership check
        appointment = self.get_appointment_by_id(appointment_id, user_id)
        if not appointment:
            raise ValueError("Appointment not found or access denied")
        
        # Validate status transitions
        current_status = appointment.status
        valid_transitions = {
            'scheduled': ['confirmed', 'cancelled'],
            'confirmed': ['completed', 'cancelled', 'no_show'],
            'cancelled': [],
            'completed': [],
            'no_show': []
        }
        
        if status not in valid_transitions.get(current_status, []):
            raise ValueError(f"Cannot transition from '{current_status}' to '{status}'")
        
        updated_appointment = self.appointment_repository.update_status(
            appointment, 
            status, 
            cancellation_reason
        )
        logger.info(f"Appointment {appointment_id} status updated to {status}")
        return updated_appointment
    
    def delete_appointment(self, appointment_id: int, user_id: int) -> None:
        """
        Delete appointment (only if owned by the chef and not completed)
        
        Args:
            appointment_id: Appointment ID
            user_id: User ID of the chef
            
        Raises:
            ValueError: If appointment not found, not owned, or already completed
        """
        # Get appointment with ownership check
        appointment = self.get_appointment_by_id(appointment_id, user_id)
        if not appointment:
            raise ValueError("Appointment not found or access denied")
        
        # Don't allow deletion of completed appointments
        if appointment.status == 'completed':
            raise ValueError("Cannot delete completed appointments. Consider cancelling instead.")
        
        self.appointment_repository.delete(appointment)
        logger.info(f"Deleted appointment {appointment_id}")
    
    def sync_from_external_calendar(self, external_calendar_id: str, calendar_data: dict) -> Appointment:
        """
        Sync appointment from external calendar (Calendly, Google Calendar)
        Placeholder for future calendar integration
        
        Args:
            external_calendar_id: External calendar event ID
            calendar_data: Event data from external calendar
            
        Returns:
            Created or updated Appointment instance
            
        Raises:
            NotImplementedError: Feature not yet implemented
        """
        # TODO: Implement calendar integration
        raise NotImplementedError("External calendar integration not yet implemented")

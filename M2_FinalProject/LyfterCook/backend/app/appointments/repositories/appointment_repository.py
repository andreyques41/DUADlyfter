"""
Appointment Repository - Data access layer for Appointment model
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, and_
from datetime import datetime, timedelta
from app.appointments.models.appointment_model import Appointment
from config.logging import get_logger

logger = get_logger(__name__)


class AppointmentRepository:
    """Repository for Appointment database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, appointment_data: dict) -> Appointment:
        """
        Create a new appointment
        
        Args:
            appointment_data: Dictionary with appointment information
            
        Returns:
            Created Appointment instance
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            appointment = Appointment(**appointment_data)
            self.db.add(appointment)
            self.db.flush()
            logger.info(f"Appointment created with ID: {appointment.id}")
            return appointment
        except SQLAlchemyError as e:
            logger.error(f"Error creating appointment: {e}", exc_info=True)
            raise
    
    def get_by_id(self, appointment_id: int) -> Optional[Appointment]:
        """
        Get appointment by ID with client
        
        Args:
            appointment_id: Appointment ID
            
        Returns:
            Appointment instance or None if not found
        """
        try:
            appointment = self.db.query(Appointment).options(
                joinedload(Appointment.client)
            ).filter(Appointment.id == appointment_id).first()
            
            if appointment:
                logger.debug(f"Retrieved appointment ID: {appointment_id}")
            return appointment
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving appointment by ID {appointment_id}: {e}", exc_info=True)
            raise
    
    def get_by_chef_id(
        self, 
        chef_id: int, 
        status: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Appointment]:
        """
        Get all appointments for a specific chef
        
        Args:
            chef_id: Chef ID
            status: Optional status filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of Appointment instances with client
        """
        try:
            query = self.db.query(Appointment).options(
                joinedload(Appointment.client)
            ).filter(Appointment.chef_id == chef_id)
            
            if status:
                query = query.filter(Appointment.status == status)
            
            if start_date:
                query = query.filter(Appointment.scheduled_at >= start_date)
            
            if end_date:
                query = query.filter(Appointment.scheduled_at <= end_date)
            
            appointments = query.order_by(Appointment.scheduled_at).all()
            logger.debug(f"Retrieved {len(appointments)} appointments for chef {chef_id}")
            return appointments
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving appointments for chef {chef_id}: {e}", exc_info=True)
            raise
    
    def get_upcoming_appointments(self, chef_id: int, days: int = 7) -> List[Appointment]:
        """
        Get upcoming appointments for a chef
        
        Args:
            chef_id: Chef ID
            days: Number of days to look ahead (default: 7)
            
        Returns:
            List of upcoming Appointment instances
        """
        try:
            now = datetime.utcnow()
            end_date = now + timedelta(days=days)
            
            appointments = self.db.query(Appointment).filter(
                and_(
                    Appointment.chef_id == chef_id,
                    Appointment.scheduled_at >= now,
                    Appointment.scheduled_at <= end_date,
                    Appointment.status.in_(['scheduled', 'confirmed'])
                )
            ).order_by(Appointment.scheduled_at).all()
            
            logger.debug(f"Retrieved {len(appointments)} upcoming appointments for chef {chef_id}")
            return appointments
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving upcoming appointments: {e}", exc_info=True)
            raise
    
    def update(self, appointment: Appointment, update_data: dict) -> Appointment:
        """
        Update appointment
        
        Args:
            appointment: Appointment instance to update
            update_data: Dictionary with fields to update
            
        Returns:
            Updated Appointment instance
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            for key, value in update_data.items():
                if hasattr(appointment, key):
                    setattr(appointment, key, value)
            
            self.db.flush()
            logger.info(f"Updated appointment ID: {appointment.id}")
            return appointment
        except SQLAlchemyError as e:
            logger.error(f"Error updating appointment ID {appointment.id}: {e}", exc_info=True)
            raise
    
    def update_status(self, appointment: Appointment, status: str, cancellation_reason: str = None) -> Appointment:
        """
        Update appointment status
        
        Args:
            appointment: Appointment instance
            status: New status
            cancellation_reason: Reason for cancellation (if applicable)
            
        Returns:
            Updated Appointment instance
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            appointment.status = status
            
            # Update timestamps based on status
            if status == 'cancelled' and not appointment.cancelled_at:
                appointment.cancelled_at = datetime.utcnow()
                if cancellation_reason:
                    appointment.cancellation_reason = cancellation_reason
            elif status == 'completed' and not appointment.completed_at:
                appointment.completed_at = datetime.utcnow()
            
            self.db.flush()
            logger.info(f"Appointment {appointment.id} status updated to {status}")
            return appointment
        except SQLAlchemyError as e:
            logger.error(f"Error updating appointment status: {e}", exc_info=True)
            raise
    
    def delete(self, appointment: Appointment) -> None:
        """
        Delete appointment
        
        Args:
            appointment: Appointment instance to delete
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            self.db.delete(appointment)
            self.db.flush()
            logger.info(f"Deleted appointment ID: {appointment.id}")
        except SQLAlchemyError as e:
            logger.error(f"Error deleting appointment ID {appointment.id}: {e}", exc_info=True)
            raise
    
    def get_by_external_calendar_id(self, external_calendar_id: str) -> Optional[Appointment]:
        """
        Get appointment by external calendar ID
        
        Args:
            external_calendar_id: External calendar event ID
            
        Returns:
            Appointment instance or None if not found
        """
        try:
            appointment = self.db.query(Appointment).filter(
                Appointment.external_calendar_id == external_calendar_id
            ).first()
            
            if appointment:
                logger.debug(f"Retrieved appointment by external ID: {external_calendar_id}")
            return appointment
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving appointment by external ID: {e}", exc_info=True)
            raise

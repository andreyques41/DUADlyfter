"""
Appointment Model
Appointment/booking system with Calendly integration.
"""

from app.core.lib.time_utils import utcnow_naive
from sqlalchemy import Column, Integer, String, Text, DateTime, Time, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class AppointmentStatus(enum.Enum):
    """Appointment status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Appointment(Base):
    """
    Appointment model for chef scheduling.
    
    Attributes:
        id: Primary key
        chef_id: Foreign key to Chef
        client_id: Foreign key to Client (nullable for public bookings)
        client_name, client_email, client_phone: Guest booking info
        appointment_date: Date of appointment
        appointment_time: Time of appointment
        duration_minutes: Duration in minutes
        status: Appointment status
        calendly_event_id: Calendly event identifier
        google_event_id: Google Calendar event identifier
        notes: Additional notes
        created_at, updated_at: Timestamps
    """
    __tablename__ = 'appointments'
    __table_args__ = {'schema': 'integrations'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chef_id = Column(Integer, ForeignKey('core.chefs.id', ondelete='CASCADE'), nullable=False)
    client_id = Column(Integer, ForeignKey('core.clients.id', ondelete='SET NULL'), nullable=True)
    
    # Guest booking information (if client_id is null)
    client_name = Column(String(100), nullable=True)
    client_email = Column(String(120), nullable=True)
    client_phone = Column(String(20), nullable=True)
    
    appointment_date = Column(DateTime, nullable=False)
    appointment_time = Column(Time, nullable=True)
    duration_minutes = Column(Integer, nullable=False, default=60)
    status = Column(SQLEnum(AppointmentStatus), nullable=False, default=AppointmentStatus.PENDING)
    
    # External calendar integrations
    calendly_event_id = Column(String(255), nullable=True)
    google_event_id = Column(String(255), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, nullable=False, default=utcnow_naive)
    updated_at = Column(DateTime, nullable=False, default=utcnow_naive, onupdate=utcnow_naive)
    
    # Relationships
    chef = relationship("Chef", backref="appointments")
    client = relationship("Client", backref="appointments")
    
    def __repr__(self):
        return f"<Appointment {self.id} - Chef {self.chef_id} on {self.appointment_date}>"
    
    def to_dict(self):
        """Convert appointment to dictionary."""
        return {
            'id': self.id,
            'chef_id': self.chef_id,
            'client_id': self.client_id,
            'client_name': self.client_name,
            'client_email': self.client_email,
            'client_phone': self.client_phone,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time.isoformat() if self.appointment_time else None,
            'duration_minutes': self.duration_minutes,
            'status': self.status.value,
            'calendly_event_id': self.calendly_event_id,
            'google_event_id': self.google_event_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

from sqlalchemy import Column, Integer, String, Text, DateTime, Time, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Appointment(Base):
    """
    Appointment model - Scheduled meetings/consultations
    Schema: integrations
    Supports external calendar integration (Calendly, Google Calendar)
    """
    __tablename__ = 'appointments'
    __table_args__ = {'schema': 'integrations'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    chef_id = Column(Integer, ForeignKey('core.chefs.id', ondelete='CASCADE'), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey('core.clients.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # Client information (denormalized for flexibility)
    client_name = Column(String(200), nullable=True)
    client_email = Column(String(200), nullable=True)
    client_phone = Column(String(50), nullable=True)
    
    # Appointment details
    appointment_date = Column(DateTime, nullable=False, index=True)  # Date and time combined
    appointment_time = Column(Time, nullable=True)  # Separate time field
    duration_minutes = Column(Integer, nullable=False, default=60)
    
    # Status
    status = Column(String(20), default='scheduled', nullable=False)  # 'scheduled', 'confirmed', 'cancelled', 'completed'
    
    # External calendar integration
    calendly_event_id = Column(String(255), nullable=True, unique=True, index=True)
    google_event_id = Column(String(255), nullable=True, unique=True, index=True)
    
    # Additional info
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    chef = relationship("Chef", backref="appointments")
    client = relationship("Client", backref="appointments")
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, client='{self.client_name}', date={self.appointment_date}, status='{self.status}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
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
            'status': self.status,
            'calendly_event_id': self.calendly_event_id,
            'google_event_id': self.google_event_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

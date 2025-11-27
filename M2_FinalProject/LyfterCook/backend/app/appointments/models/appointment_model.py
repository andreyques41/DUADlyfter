from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
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
    
    # Appointment details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    scheduled_at = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False, default=60)
    location = Column(String(500), nullable=True)  # Physical address or "Online"
    
    # External calendar integration
    external_calendar_id = Column(String(255), nullable=True, unique=True, index=True)  # Calendly/Google Calendar event ID
    external_calendar_provider = Column(String(50), nullable=True)  # 'calendly', 'google_calendar', null for manual
    meeting_url = Column(String(500), nullable=True)  # Video call link (Zoom, Meet, etc.)
    
    # Status
    status = Column(String(20), default='scheduled', nullable=False)  # 'scheduled', 'confirmed', 'cancelled', 'completed', 'no_show'
    
    # Additional info
    notes = Column(Text, nullable=True)  # Chef's private notes
    cancellation_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    cancelled_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    chef = relationship("Chef", backref="appointments")
    client = relationship("Client", backref="appointments")
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, title='{self.title}', scheduled_at={self.scheduled_at}, status='{self.status}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'chef_id': self.chef_id,
            'client_id': self.client_id,
            'title': self.title,
            'description': self.description,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'duration_minutes': self.duration_minutes,
            'location': self.location,
            'external_calendar_id': self.external_calendar_id,
            'external_calendar_provider': self.external_calendar_provider,
            'meeting_url': self.meeting_url,
            'status': self.status,
            'notes': self.notes,
            'cancellation_reason': self.cancellation_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

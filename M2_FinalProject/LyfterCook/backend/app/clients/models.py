"""
Client Model
Client management for chefs.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Client(Base):
    """
    Client model for chef's customer management.
    
    Attributes:
        id: Primary key
        chef_id: Foreign key to Chef
        name: Client full name
        email: Client email address
        phone: Client phone number
        company: Client company/organization (optional)
        notes: Additional notes about client
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    __tablename__ = 'clients'
    __table_args__ = {'schema': 'core'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chef_id = Column(Integer, ForeignKey('core.chefs.id', ondelete='CASCADE'), nullable=False)
    
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    phone = Column(String(20), nullable=True)
    company = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chef = relationship("Chef", backref="clients")
    
    def __repr__(self):
        return f"<Client {self.name} - Chef {self.chef_id}>"
    
    def to_dict(self):
        """Convert client to dictionary."""
        return {
            'id': self.id,
            'chef_id': self.chef_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company': self.company,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

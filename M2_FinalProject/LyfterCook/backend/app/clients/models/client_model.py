from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Client(Base):
    """
    Client model - Stores chef's client information
    Schema: core
    """
    __tablename__ = 'clients'
    __table_args__ = {'schema': 'core'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    chef_id = Column(Integer, ForeignKey('core.chefs.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=True)
    phone = Column(String(20), nullable=True)
    company = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    chef = relationship("Chef", backref="clients")
    
    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}', chef_id={self.chef_id})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
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

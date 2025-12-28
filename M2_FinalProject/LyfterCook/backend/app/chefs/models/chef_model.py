from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.lib.time_utils import utcnow_naive
from app.core.database import Base


class Chef(Base):
    """
    Chef profile model - Extends user account with professional information
    Schema: core
    """
    __tablename__ = 'chefs'
    __table_args__ = {'schema': 'core'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('auth.users.id', ondelete='CASCADE'), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    specialty = Column(String(100), nullable=True)  # e.g., "Italian Cuisine", "Pastry", "Vegan"
    phone = Column(String(20), nullable=True)
    location = Column(String(200), nullable=True)  # City or address
    profile_photo_url = Column(String(500), nullable=True)  # Cloudinary or other CDN URL
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utcnow_naive, nullable=False)
    updated_at = Column(DateTime, default=utcnow_naive, onupdate=utcnow_naive, nullable=False)

    # Relationships
    user = relationship("User", back_populates="chef", uselist=False)
    
    def __repr__(self):
        return f"<Chef(id={self.id}, user_id={self.user_id}, specialty='{self.specialty}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'bio': self.bio,
            'specialty': self.specialty,
            'phone': self.phone,
            'location': self.location,
            'profile_photo_url': self.profile_photo_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

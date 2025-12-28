"""
Chef Model
Chef profile model with relationship to User.
"""

from app.core.lib.time_utils import utcnow_naive
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Chef(Base):
    """
    Chef profile model.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User (1:1 relationship)
        bio: Chef biography/description
        specialty: Chef's culinary specialty
        phone: Contact phone number
        location: Chef's location/city
        profile_photo_url: Cloudinary URL for profile photo
        is_active: Profile active status (visible to public)
        created_at: Timestamp of profile creation
        updated_at: Timestamp of last update
    """
    __tablename__ = 'chefs'
    __table_args__ = {'schema': 'core'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('auth.users.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    bio = Column(Text, nullable=True)
    specialty = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    location = Column(String(100), nullable=True)
    profile_photo_url = Column(String(500), nullable=True)
    is_active = Column(Integer, nullable=False, default=1)
    
    created_at = Column(DateTime, nullable=False, default=utcnow_naive)
    updated_at = Column(DateTime, nullable=False, default=utcnow_naive, onupdate=utcnow_naive)
    
    # Relationships
    user = relationship("User", backref="chef_profile", uselist=False)
    
    def __repr__(self):
        return f"<Chef {self.id} - User {self.user_id}>"
    
    def to_dict(self, include_user=False):
        """Convert chef to dictionary."""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'bio': self.bio,
            'specialty': self.specialty,
            'phone': self.phone,
            'location': self.location,
            'profile_photo_url': self.profile_photo_url,
            'is_active': bool(self.is_active),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_user and self.user:
            data['user'] = self.user.to_dict()
        
        return data

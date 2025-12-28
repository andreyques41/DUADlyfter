from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.core.lib.time_utils import utcnow_naive
from app.core.database import Base
import enum


class MenuStatus(enum.Enum):
    """Enum for menu status values"""
    DRAFT = 'draft'              # Menu under construction, not visible
    PUBLISHED = 'published'      # Publicly available, active menu
    ARCHIVED = 'archived'        # Historical, no longer active
    SEASONAL = 'seasonal'        # Available only during specific dates/seasons


class Menu(Base):
    """
    Menu model - Collection of dishes for an event/service
    Schema: core
    """
    __tablename__ = 'menus'
    __table_args__ = {'schema': 'core'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    chef_id = Column(Integer, ForeignKey('core.chefs.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(MenuStatus, name='menustatus', create_type=False), default=MenuStatus.DRAFT, nullable=False)
    created_at = Column(DateTime, default=utcnow_naive, nullable=False)
    updated_at = Column(DateTime, default=utcnow_naive, onupdate=utcnow_naive, nullable=False)

    # Relationships
    chef = relationship("Chef", backref="menus")
    menu_dishes = relationship("MenuDish", back_populates="menu", cascade="all, delete-orphan", order_by="MenuDish.order_position")
    
    def __repr__(self):
        return f"<Menu(id={self.id}, name='{self.name}', chef_id={self.chef_id})>"
    
    def to_dict(self, include_dishes=True):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'chef_id': self.chef_id,
            'name': self.name,
            'description': self.description,
            'status': self.status.value if isinstance(self.status, MenuStatus) else self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_dishes and self.menu_dishes:
            data['dishes'] = [
                {
                    'dish_id': md.dish_id,
                    'order_position': md.order_position,
                    'dish': md.dish.to_dict(include_ingredients=False) if md.dish else None
                }
                for md in self.menu_dishes
            ]
        
        return data

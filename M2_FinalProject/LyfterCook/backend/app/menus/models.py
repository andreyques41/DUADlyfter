"""
Menu Models
Menu management with many-to-many relationship to dishes.
"""

from app.core.lib.time_utils import utcnow_naive
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class MenuStatus(enum.Enum):
    """Menu status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"


class Menu(Base):
    """
    Menu model for chef's curated dish collections.
    
    Attributes:
        id: Primary key
        chef_id: Foreign key to Chef
        name: Menu name
        description: Menu description
        status: Menu status (active/inactive)
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    __tablename__ = 'menus'
    __table_args__ = {'schema': 'core'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chef_id = Column(Integer, ForeignKey('core.chefs.id', ondelete='CASCADE'), nullable=False)
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(MenuStatus), nullable=False, default=MenuStatus.ACTIVE)
    
    created_at = Column(DateTime, nullable=False, default=utcnow_naive)
    updated_at = Column(DateTime, nullable=False, default=utcnow_naive, onupdate=utcnow_naive)
    
    # Relationships
    chef = relationship("Chef", backref="menus")
    menu_dishes = relationship("MenuDish", back_populates="menu", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Menu {self.name} - Chef {self.chef_id}>"
    
    def to_dict(self, include_dishes=False):
        """Convert menu to dictionary."""
        data = {
            'id': self.id,
            'chef_id': self.chef_id,
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_dishes:
            data['dishes'] = [md.to_dict() for md in self.menu_dishes]
        
        return data


class MenuDish(Base):
    """
    Many-to-many relationship table between Menu and Dish.
    
    Attributes:
        menu_id: Foreign key to Menu
        dish_id: Foreign key to Dish
        order_position: Display order in menu
    """
    __tablename__ = 'menu_dishes'
    __table_args__ = {'schema': 'core'}
    
    menu_id = Column(Integer, ForeignKey('core.menus.id', ondelete='CASCADE'), primary_key=True)
    dish_id = Column(Integer, ForeignKey('core.dishes.id', ondelete='CASCADE'), primary_key=True)
    order_position = Column(Integer, nullable=False, default=0)
    
    # Relationships
    menu = relationship("Menu", back_populates="menu_dishes")
    dish = relationship("Dish", backref="menu_dishes")
    
    def __repr__(self):
        return f"<MenuDish Menu:{self.menu_id} Dish:{self.dish_id}>"
    
    def to_dict(self):
        """Convert menu_dish to dictionary."""
        return {
            'menu_id': self.menu_id,
            'dish_id': self.dish_id,
            'order_position': self.order_position,
            'dish': self.dish.to_dict() if self.dish else None
        }

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class MenuDish(Base):
    """
    MenuDish model - Many-to-many relationship between menus and dishes
    Schema: core
    """
    __tablename__ = 'menu_dishes'
    __table_args__ = (
        UniqueConstraint('menu_id', 'dish_id', name='unique_menu_dish'),
        {'schema': 'core'}
    )

    menu_id = Column(Integer, ForeignKey('core.menus.id', ondelete='CASCADE'), primary_key=True)
    dish_id = Column(Integer, ForeignKey('core.dishes.id', ondelete='CASCADE'), primary_key=True)
    order_position = Column(Integer, nullable=False, default=0)  # Order in menu

    # Relationships
    menu = relationship("Menu", back_populates="menu_dishes")
    dish = relationship("Dish")
    
    def __repr__(self):
        return f"<MenuDish(menu_id={self.menu_id}, dish_id={self.dish_id}, position={self.order_position})>"

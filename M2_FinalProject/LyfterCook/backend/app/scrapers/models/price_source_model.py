from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class PriceSource(Base):
    """
    Model for configurable price sources (supermarkets, websites).
    Each source has custom CSS selectors for scraping.
    """
    __tablename__ = "price_sources"
    __table_args__ = {"schema": "integrations"}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)  # e.g., "Walmart", "Carrefour"
    base_url = Column(String(255), nullable=False)
    search_url_template = Column(String(500), nullable=False)  # URL with {ingredient} placeholder
    
    # CSS Selectors for scraping
    product_name_selector = Column(String(200), nullable=False)
    price_selector = Column(String(200), nullable=False)
    image_selector = Column(String(200), nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<PriceSource {self.name}>"

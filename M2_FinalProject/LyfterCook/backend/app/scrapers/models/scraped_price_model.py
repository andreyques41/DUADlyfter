from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base


class ScrapedPrice(Base):
    """
    Model for storing scraped price data from different sources.
    Cached results to avoid excessive scraping.
    """
    __tablename__ = "scraped_prices"
    __table_args__ = {"schema": "integrations"}

    id = Column(Integer, primary_key=True)
    price_source_id = Column(Integer, ForeignKey("integrations.price_sources.id", ondelete="CASCADE"), nullable=False)
    
    ingredient_name = Column(String(200), nullable=False)  # Searched ingredient
    product_name = Column(String(300), nullable=False)     # Actual product found
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    product_url = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
    
    unit = Column(String(50), nullable=True)  # e.g., "per kg", "per unit"
    notes = Column(Text, nullable=True)
    
    scraped_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<ScrapedPrice {self.product_name} - ${self.price}>"

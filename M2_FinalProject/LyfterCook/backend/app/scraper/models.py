"""
Scraper Models
Web scraping results in 'integrations' schema.
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime
from datetime import datetime, timezone
from app.core.database import Base


class ScrapedProduct(Base):
    """
    ScrapedProduct model - cached product prices from supermarkets.
    Stored in integrations.scraped_products table.
    """
    __tablename__ = 'scraped_products'
    __table_args__ = {'schema': 'integrations'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Product information
    ingredient_name = Column(String(100), nullable=False, index=True)
    store_name = Column(String(100), nullable=False)
    product_name = Column(String(200), nullable=False)
    price = Column(Numeric(10, 2), nullable=True)
    url = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
    
    # Timestamps
    last_scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __repr__(self):
        return f"<ScrapedProduct(id={self.id}, ingredient='{self.ingredient_name}', store='{self.store_name}', price={self.price})>"

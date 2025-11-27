from typing import List, Optional
from datetime import datetime, timedelta
from flask import g
from config.logging import get_logger
from app.scrapers.models import PriceSource, ScrapedPrice

logger = get_logger(__name__)


class ScraperRepository:
    """Repository for price sources and scraped prices data access"""

    # ==================== Price Sources ====================

    @staticmethod
    def create_price_source(data: dict) -> PriceSource:
        """Create a new price source"""
        price_source = PriceSource(**data)
        g.db.add(price_source)
        g.db.flush()
        logger.info(f"Created price source: {price_source.name}")
        return price_source

    @staticmethod
    def get_all_price_sources(active_only: bool = False) -> List[PriceSource]:
        """Get all price sources, optionally filter by active status"""
        query = g.db.query(PriceSource)
        
        if active_only:
            query = query.filter(PriceSource.is_active == True)
        
        return query.order_by(PriceSource.name).all()

    @staticmethod
    def get_price_source_by_id(source_id: int) -> Optional[PriceSource]:
        """Get price source by ID"""
        return g.db.query(PriceSource).filter(PriceSource.id == source_id).first()

    @staticmethod
    def get_price_source_by_name(name: str) -> Optional[PriceSource]:
        """Get price source by name"""
        return g.db.query(PriceSource).filter(PriceSource.name == name).first()

    @staticmethod
    def update_price_source(price_source: PriceSource, data: dict) -> PriceSource:
        """Update price source with new data"""
        for key, value in data.items():
            if hasattr(price_source, key):
                setattr(price_source, key, value)
        
        g.db.flush()
        logger.info(f"Updated price source: {price_source.name}")
        return price_source

    @staticmethod
    def delete_price_source(price_source: PriceSource) -> None:
        """Delete a price source (cascade deletes scraped prices)"""
        name = price_source.name
        g.db.delete(price_source)
        g.db.flush()
        logger.info(f"Deleted price source: {name}")

    # ==================== Scraped Prices ====================

    @staticmethod
    def create_scraped_price(data: dict) -> ScrapedPrice:
        """Create a new scraped price record"""
        scraped_price = ScrapedPrice(**data)
        g.db.add(scraped_price)
        g.db.flush()
        logger.info(f"Saved scraped price: {scraped_price.product_name} - ${scraped_price.price}")
        return scraped_price

    @staticmethod
    def get_scraped_prices(
        ingredient_name: Optional[str] = None,
        price_source_id: Optional[int] = None,
        max_age_hours: Optional[int] = 24
    ) -> List[ScrapedPrice]:
        """
        Get scraped prices with optional filters
        
        Args:
            ingredient_name: Filter by ingredient name
            price_source_id: Filter by price source
            max_age_hours: Only return prices scraped within this many hours (default: 24)
        """
        query = g.db.query(ScrapedPrice)
        
        if ingredient_name:
            query = query.filter(ScrapedPrice.ingredient_name.ilike(f"%{ingredient_name}%"))
        
        if price_source_id:
            query = query.filter(ScrapedPrice.price_source_id == price_source_id)
        
        if max_age_hours:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            query = query.filter(ScrapedPrice.scraped_at >= cutoff_time)
        
        return query.order_by(ScrapedPrice.scraped_at.desc()).all()

    @staticmethod
    def get_latest_price(ingredient_name: str, price_source_id: int) -> Optional[ScrapedPrice]:
        """Get the most recent scraped price for an ingredient from a specific source"""
        return (
            g.db.query(ScrapedPrice)
            .filter(
                ScrapedPrice.ingredient_name == ingredient_name,
                ScrapedPrice.price_source_id == price_source_id
            )
            .order_by(ScrapedPrice.scraped_at.desc())
            .first()
        )

    @staticmethod
    def delete_old_scraped_prices(days_old: int = 30) -> int:
        """Delete scraped prices older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        deleted_count = (
            g.db.query(ScrapedPrice)
            .filter(ScrapedPrice.scraped_at < cutoff_date)
            .delete()
        )
        g.db.flush()
        logger.info(f"Deleted {deleted_count} old scraped prices")
        return deleted_count

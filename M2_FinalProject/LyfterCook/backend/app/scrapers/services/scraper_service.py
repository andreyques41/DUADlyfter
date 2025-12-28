from typing import List, Dict, Optional
from datetime import timedelta
import requests
from bs4 import BeautifulSoup
import re
from config.logging import get_logger
from app.scrapers.repositories import ScraperRepository
from app.scrapers.models import PriceSource, ScrapedPrice
from app.core.lib.time_utils import utcnow_aware

logger = get_logger(__name__)


class ScraperService:
    """Service layer for web scraping and price management"""

    def __init__(self):
        self.repository = ScraperRepository()

    # ==================== Price Source Management ====================

    def create_price_source(self, data: dict) -> PriceSource:
        """Create a new price source configuration"""
        # Check if name already exists
        existing = self.repository.get_price_source_by_name(data.get("name"))
        if existing:
            raise ValueError(f"Price source with name '{data.get('name')}' already exists")
        
        return self.repository.create_price_source(data)

    def get_all_price_sources(self, active_only: bool = False) -> List[PriceSource]:
        """Get all price sources"""
        return self.repository.get_all_price_sources(active_only=active_only)

    def get_price_source(self, source_id: int) -> PriceSource:
        """Get price source by ID"""
        price_source = self.repository.get_price_source_by_id(source_id)
        if not price_source:
            raise ValueError(f"Price source with ID {source_id} not found")
        return price_source

    def update_price_source(self, source_id: int, data: dict) -> PriceSource:
        """Update price source"""
        price_source = self.get_price_source(source_id)
        
        # Check name uniqueness if changing name
        if "name" in data and data["name"] != price_source.name:
            existing = self.repository.get_price_source_by_name(data["name"])
            if existing:
                raise ValueError(f"Price source with name '{data['name']}' already exists")
        
        return self.repository.update_price_source(price_source, data)

    def delete_price_source(self, source_id: int) -> None:
        """Delete price source"""
        price_source = self.get_price_source(source_id)
        self.repository.delete_price_source(price_source)

    # ==================== Web Scraping ====================

    def scrape_ingredient_prices(
        self,
        ingredient_name: str,
        price_source_ids: Optional[List[int]] = None,
        force_refresh: bool = False
    ) -> List[ScrapedPrice]:
        """
        Scrape prices for an ingredient from specified sources.
        Uses cache unless force_refresh is True.
        
        Args:
            ingredient_name: Name of ingredient to search
            price_source_ids: List of source IDs to scrape (None = all active)
            force_refresh: Bypass cache and scrape fresh data
        
        Returns:
            List of ScrapedPrice objects
        """
        # Get active price sources
        if price_source_ids:
            sources = [self.get_price_source(sid) for sid in price_source_ids]
            sources = [s for s in sources if s.is_active]
        else:
            sources = self.repository.get_all_price_sources(active_only=True)

        if not sources:
            raise ValueError("No active price sources available")

        results = []

        for source in sources:
            try:
                # Check cache first (24 hour freshness)
                if not force_refresh:
                    cached = self._get_cached_price(ingredient_name, source.id, max_age_hours=24)
                    if cached:
                        logger.info(f"Using cached price for '{ingredient_name}' from {source.name}")
                        results.append(cached)
                        continue

                # Scrape fresh data
                scraped = self._scrape_from_source(ingredient_name, source)
                if scraped:
                    results.append(scraped)
                    logger.info(f"Scraped new price for '{ingredient_name}' from {source.name}")

            except Exception as e:
                logger.error(f"Error scraping {source.name} for '{ingredient_name}': {str(e)}")
                continue

        return results

    def _get_cached_price(
        self,
        ingredient_name: str,
        price_source_id: int,
        max_age_hours: int = 24
    ) -> Optional[ScrapedPrice]:
        """Check if we have a recent cached price"""
        cached = self.repository.get_latest_price(ingredient_name, price_source_id)
        
        if not cached:
            return None
        
        age = utcnow_aware() - cached.scraped_at
        if age > timedelta(hours=max_age_hours):
            return None
        
        return cached

    def _scrape_from_source(self, ingredient_name: str, source: PriceSource) -> Optional[ScrapedPrice]:
        """
        Perform actual web scraping from a price source.
        
        Args:
            ingredient_name: Ingredient to search for
            source: PriceSource configuration object
        
        Returns:
            ScrapedPrice object or None if scraping failed
        """
        try:
            # Build search URL
            search_url = source.search_url_template.replace("{ingredient}", ingredient_name)
            search_url = search_url.replace("{query}", ingredient_name)
            
            # Make HTTP request with timeout and headers
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract product name
            product_elem = soup.select_one(source.product_name_selector)
            if not product_elem:
                logger.warning(f"No product found at {source.name} for '{ingredient_name}'")
                return None
            
            product_name = product_elem.get_text(strip=True)
            
            # Extract price
            price_elem = soup.select_one(source.price_selector)
            if not price_elem:
                logger.warning(f"No price found at {source.name} for '{ingredient_name}'")
                return None
            
            price_text = price_elem.get_text(strip=True)
            price = self._extract_price(price_text)
            
            if not price:
                logger.warning(f"Could not parse price '{price_text}' from {source.name}")
                return None
            
            # Extract image URL (optional)
            image_url = None
            if source.image_selector:
                image_elem = soup.select_one(source.image_selector)
                if image_elem:
                    image_url = image_elem.get("src") or image_elem.get("data-src")
            
            # Save scraped price
            scraped_data = {
                "price_source_id": source.id,
                "ingredient_name": ingredient_name,
                "product_name": product_name,
                "price": price,
                "currency": "USD",  # TODO: Make configurable
                "product_url": search_url,
                "image_url": image_url,
                "scraped_at": utcnow_aware()
            }
            
            return self.repository.create_scraped_price(scraped_data)
            
        except requests.RequestException as e:
            logger.error(f"HTTP request failed for {source.name}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Scraping error for {source.name}: {str(e)}")
            return None

    def _extract_price(self, price_text: str) -> Optional[float]:
        """
        Extract numeric price from text.
        Handles formats like: $12.99, 12,99€, 12.99, etc.
        """
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[^\d,.]', '', price_text)
        
        # Handle European format (12,99) vs US format (12.99)
        if ',' in cleaned and '.' in cleaned:
            # Both present: assume , is thousands separator
            cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            # Only comma: might be decimal separator
            cleaned = cleaned.replace(',', '.')
        
        try:
            return float(cleaned)
        except ValueError:
            return None

    # ==================== Price History ====================

    def get_scraped_prices(
        self,
        ingredient_name: Optional[str] = None,
        price_source_id: Optional[int] = None,
        max_age_hours: int = 24
    ) -> List[ScrapedPrice]:
        """Get scraped price history with filters"""
        return self.repository.get_scraped_prices(
            ingredient_name=ingredient_name,
            price_source_id=price_source_id,
            max_age_hours=max_age_hours
        )

    def cleanup_old_prices(self, days_old: int = 30) -> int:
        """Delete scraped prices older than specified days"""
        return self.repository.delete_old_scraped_prices(days_old)

    def get_price_comparison(self, ingredient_name: str) -> Dict:
        """
        Get price comparison across all sources for an ingredient.
        Returns summary statistics and source breakdown.
        """
        prices = self.get_scraped_prices(ingredient_name=ingredient_name, max_age_hours=24)
        
        if not prices:
            return {
                "ingredient_name": ingredient_name,
                "found": False,
                "message": "No recent prices found. Try scraping first."
            }
        
        price_values = [float(p.price) for p in prices]
        
        return {
            "ingredient_name": ingredient_name,
            "found": True,
            "total_sources": len(prices),
            "min_price": min(price_values),
            "max_price": max(price_values),
            "avg_price": sum(price_values) / len(price_values),
            "prices": [
                {
                    "source_id": p.price_source_id,
                    "product_name": p.product_name,
                    "price": float(p.price),
                    "url": p.product_url,
                    "scraped_at": p.scraped_at.isoformat()
                }
                for p in prices
            ]
        }

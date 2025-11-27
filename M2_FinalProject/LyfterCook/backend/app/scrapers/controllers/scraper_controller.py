from flask import request
from config.logging import get_logger
from app.core.lib.error_utils import success_response, error_response
from app.scrapers.services import ScraperService
from app.scrapers.schemas import (
    price_source_create_schema,
    price_source_update_schema,
    price_source_response_schema,
    price_sources_response_schema,
    scraped_prices_response_schema,
    scrape_request_schema
)

logger = get_logger(__name__)


class ScraperController:
    """Controller for scraper endpoints"""

    @staticmethod
    def _get_service() -> ScraperService:
        """Helper to create service instance"""
        return ScraperService()

    # ==================== Price Source Endpoints ====================

    @staticmethod
    def create_price_source():
        """Create a new price source configuration"""
        try:
            service = ScraperController._get_service()
            price_source = service.create_price_source(request.validated_data)
            result = price_source_response_schema.dump(price_source)
            
            return success_response(result, "Price source created successfully", 201)
            
        except ValueError as e:
            logger.warning(f"Price source creation failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"Error creating price source: {str(e)}")
            return error_response("Failed to create price source", 500)

    @staticmethod
    def get_price_sources():
        """Get all price sources"""
        try:
            active_only = request.args.get("active_only", "false").lower() == "true"
            
            service = ScraperController._get_service()
            price_sources = service.get_all_price_sources(active_only=active_only)
            result = price_sources_response_schema.dump(price_sources)
            
            return success_response(result)
            
        except Exception as e:
            logger.error(f"Error fetching price sources: {str(e)}")
            return error_response("Failed to fetch price sources", 500)

    @staticmethod
    def get_price_source(source_id: int):
        """Get a specific price source"""
        try:
            service = ScraperController._get_service()
            price_source = service.get_price_source(source_id)
            result = price_source_response_schema.dump(price_source)
            
            return success_response(result)
            
        except ValueError as e:
            logger.warning(f"Price source not found: {str(e)}")
            return error_response(str(e), 404)
        except Exception as e:
            logger.error(f"Error fetching price source: {str(e)}")
            return error_response("Failed to fetch price source", 500)

    @staticmethod
    def update_price_source(source_id: int):
        """Update a price source"""
        try:
            service = ScraperController._get_service()
            price_source = service.update_price_source(source_id, request.validated_data)
            result = price_source_response_schema.dump(price_source)
            
            return success_response(result, "Price source updated successfully")
            
        except ValueError as e:
            logger.warning(f"Price source update failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"Error updating price source: {str(e)}")
            return error_response("Failed to update price source", 500)

    @staticmethod
    def delete_price_source(source_id: int):
        """Delete a price source"""
        try:
            service = ScraperController._get_service()
            service.delete_price_source(source_id)
            
            return success_response(None, "Price source deleted successfully")
            
        except ValueError as e:
            logger.warning(f"Price source deletion failed: {str(e)}")
            return error_response(str(e), 404)
        except Exception as e:
            logger.error(f"Error deleting price source: {str(e)}")
            return error_response("Failed to delete price source", 500)

    # ==================== Scraping Endpoints ====================

    @staticmethod
    def scrape_prices():
        """Scrape prices for an ingredient"""
        try:
            data = request.validated_data
            service = ScraperController._get_service()
            
            scraped_prices = service.scrape_ingredient_prices(
                ingredient_name=data["ingredient_name"],
                price_source_ids=data.get("price_source_ids"),
                force_refresh=data.get("force_refresh", False)
            )
            
            result = scraped_prices_response_schema.dump(scraped_prices)
            
            if not result:
                return success_response(
                    [],
                    "No prices found. Check if price sources are configured correctly.",
                    200
                )
            
            return success_response(
                result,
                f"Found {len(result)} price(s) for '{data['ingredient_name']}'",
                200
            )
            
        except ValueError as e:
            logger.warning(f"Scraping failed: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"Error scraping prices: {str(e)}")
            return error_response("Failed to scrape prices", 500)

    @staticmethod
    def get_scraped_prices():
        """Get scraped price history"""
        try:
            ingredient_name = request.args.get("ingredient_name")
            price_source_id = request.args.get("price_source_id", type=int)
            max_age_hours = request.args.get("max_age_hours", default=24, type=int)
            
            service = ScraperController._get_service()
            prices = service.get_scraped_prices(
                ingredient_name=ingredient_name,
                price_source_id=price_source_id,
                max_age_hours=max_age_hours
            )
            
            result = scraped_prices_response_schema.dump(prices)
            return success_response(result)
            
        except Exception as e:
            logger.error(f"Error fetching scraped prices: {str(e)}")
            return error_response("Failed to fetch scraped prices", 500)

    @staticmethod
    def get_price_comparison():
        """Get price comparison for an ingredient"""
        try:
            ingredient_name = request.args.get("ingredient_name")
            
            if not ingredient_name:
                return error_response("ingredient_name query parameter is required", 400)
            
            service = ScraperController._get_service()
            comparison = service.get_price_comparison(ingredient_name)
            
            return success_response(comparison)
            
        except Exception as e:
            logger.error(f"Error getting price comparison: {str(e)}")
            return error_response("Failed to get price comparison", 500)

    @staticmethod
    def cleanup_old_prices():
        """Clean up old scraped prices"""
        try:
            days_old = request.args.get("days_old", default=30, type=int)
            
            service = ScraperController._get_service()
            deleted_count = service.cleanup_old_prices(days_old)
            
            return success_response(
                {"deleted_count": deleted_count},
                f"Deleted {deleted_count} old price records"
            )
            
        except Exception as e:
            logger.error(f"Error cleaning up prices: {str(e)}")
            return error_response("Failed to cleanup prices", 500)

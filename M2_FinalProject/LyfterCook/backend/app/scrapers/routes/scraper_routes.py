from flask import Blueprint
from app.scrapers.controllers import ScraperController
from app.core.middleware.auth_middleware import jwt_required
from app.core.middleware.request_decorators import validate_json
from app.scrapers.schemas import (
    PriceSourceCreateSchema,
    PriceSourceUpdateSchema,
    ScrapeRequestSchema
)

scraper_bp = Blueprint("scrapers", __name__, url_prefix="/scrapers")


# ==================== Price Source Routes ====================

@scraper_bp.route("/sources", methods=["POST"])
@jwt_required
@validate_json(PriceSourceCreateSchema)
def create_price_source():
    """
    Create a new price source configuration
    ---
    Protected: Yes (JWT required)
    """
    return ScraperController.create_price_source()


@scraper_bp.route("/sources", methods=["GET"])
@jwt_required
def get_price_sources():
    """
    Get all price sources
    Query params: active_only (boolean)
    ---
    Protected: Yes (JWT required)
    """
    return ScraperController.get_price_sources()


@scraper_bp.route("/sources/<int:source_id>", methods=["GET"])
@jwt_required
def get_price_source(source_id: int):
    """
    Get a specific price source
    ---
    Protected: Yes (JWT required)
    """
    return ScraperController.get_price_source(source_id)


@scraper_bp.route("/sources/<int:source_id>", methods=["PUT"])
@jwt_required
@validate_json(PriceSourceUpdateSchema)
def update_price_source(source_id: int):
    """
    Update a price source
    ---
    Protected: Yes (JWT required)
    """
    return ScraperController.update_price_source(source_id)


@scraper_bp.route("/sources/<int:source_id>", methods=["DELETE"])
@jwt_required
def delete_price_source(source_id: int):
    """
    Delete a price source
    ---
    Protected: Yes (JWT required)
    """
    return ScraperController.delete_price_source(source_id)


# ==================== Scraping Routes ====================

@scraper_bp.route("/scrape", methods=["POST"])
@jwt_required
@validate_json(ScrapeRequestSchema)
def scrape_prices():
    """
    Scrape prices for an ingredient
    Body: {ingredient_name, price_source_ids (optional), force_refresh (optional)}
    ---
    Protected: Yes (JWT required)
    """
    return ScraperController.scrape_prices()


@scraper_bp.route("/prices", methods=["GET"])
@jwt_required
def get_scraped_prices():
    """
    Get scraped price history
    Query params: ingredient_name, price_source_id, max_age_hours
    ---
    Protected: Yes (JWT required)
    """
    return ScraperController.get_scraped_prices()


@scraper_bp.route("/prices/compare", methods=["GET"])
@jwt_required
def get_price_comparison():
    """
    Get price comparison for an ingredient
    Query params: ingredient_name (required)
    ---
    Protected: Yes (JWT required)
    """
    return ScraperController.get_price_comparison()


@scraper_bp.route("/prices/cleanup", methods=["DELETE"])
@jwt_required
def cleanup_old_prices():
    """
    Clean up old scraped prices
    Query params: days_old (default: 30)
    ---
    Protected: Yes (JWT required)
    """
    return ScraperController.cleanup_old_prices()

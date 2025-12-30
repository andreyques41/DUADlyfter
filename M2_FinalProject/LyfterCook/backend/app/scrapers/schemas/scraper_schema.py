from marshmallow import Schema, fields, validate, validates, ValidationError


class PriceSourceCreateSchema(Schema):
    """Schema for creating a new price source"""
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    base_url = fields.Url(required=True)
    search_url_template = fields.Str(required=True, validate=validate.Length(min=10, max=500))
    
    product_name_selector = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    price_selector = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    image_selector = fields.Str(allow_none=True, validate=validate.Length(max=200))
    
    is_active = fields.Bool(load_default=True)
    notes = fields.Str(allow_none=True)

    @validates("search_url_template")
    def validate_template(self, value, **kwargs):
        """Ensure search_url_template contains placeholder"""
        if "{ingredient}" not in value and "{query}" not in value:
            raise ValidationError("search_url_template must contain {ingredient} or {query} placeholder")


class PriceSourceUpdateSchema(Schema):
    """Schema for updating a price source"""
    name = fields.Str(validate=validate.Length(min=2, max=100))
    base_url = fields.Url()
    search_url_template = fields.Str(validate=validate.Length(min=10, max=500))
    
    product_name_selector = fields.Str(validate=validate.Length(min=1, max=200))
    price_selector = fields.Str(validate=validate.Length(min=1, max=200))
    image_selector = fields.Str(allow_none=True, validate=validate.Length(max=200))
    
    is_active = fields.Bool()
    notes = fields.Str(allow_none=True)


class PriceSourceResponseSchema(Schema):
    """Schema for price source response"""
    id = fields.Int(dump_only=True)
    name = fields.Str()
    base_url = fields.Str()
    search_url_template = fields.Str()
    
    product_name_selector = fields.Str()
    price_selector = fields.Str()
    image_selector = fields.Str()
    
    is_active = fields.Bool()
    notes = fields.Str()
    
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ScrapedPriceResponseSchema(Schema):
    """Schema for scraped price response"""
    id = fields.Int(dump_only=True)
    price_source_id = fields.Int()
    
    ingredient_name = fields.Str()
    product_name = fields.Str()
    price = fields.Decimal(as_string=True)
    currency = fields.Str()
    
    product_url = fields.Str()
    image_url = fields.Str()
    unit = fields.Str()
    notes = fields.Str()
    
    scraped_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class ScrapeRequestSchema(Schema):
    """Schema for requesting price scraping"""
    ingredient_name = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    price_source_ids = fields.List(fields.Int(), load_default=None)  # If None, use all active sources
    force_refresh = fields.Bool(load_default=False)  # Ignore cache


# Schema instances
price_source_create_schema = PriceSourceCreateSchema()
price_source_update_schema = PriceSourceUpdateSchema()
price_source_response_schema = PriceSourceResponseSchema()
price_sources_response_schema = PriceSourceResponseSchema(many=True)

scraped_price_response_schema = ScrapedPriceResponseSchema()
scraped_prices_response_schema = ScrapedPriceResponseSchema(many=True)

scrape_request_schema = ScrapeRequestSchema()

"""
Product Routes Module

Provides RESTful API endpoints for product management:
- GET /products - List all products with filtering (public access)
- GET /products/<id> - Get specific product (public access)  
- POST /products - Create new product (admin only)
- PUT /products/<id> - Update product (admin only)
- DELETE /products/<id> - Delete product (admin only)

Features:
- Public access for product browsing (e-commerce)
- Advanced filtering (category, price, brand, search, etc.)
- Admin-only access for product management
- Role-based response data (admins see more details)
- Comprehensive input validation
"""

# Common imports
from flask import Blueprint, request, jsonify, g
from flask.views import MethodView
from marshmallow import ValidationError
from config.logging import get_logger, EXC_INFO_LOG_ERRORS

# Auth imports (for decorators)
from app.core.middleware import admin_required_with_repo
from app.core.lib.auth import is_admin_user
from app.core.lib.jwt import verify_jwt_token
from app.core.lib.users import get_user_by_id

# Products domain imports
from app.products.services import ProductService
from app.products.schemas import (
    product_registration_schema,
    ProductResponseSchema
)

# Get logger for this module
logger = get_logger(__name__)

class ProductAPI(MethodView):
    """CRUD operations for products - GET: public access, POST/PUT/DELETE: admin only"""

    init_every_request = False

    def get(self, product_id=None):
        from app.products.controllers.product_controller import ProductController
        controller = ProductController()
        return controller.get(product_id)
        
    @admin_required_with_repo
    def post(self):
        from app.products.controllers.product_controller import ProductController
        controller = ProductController()
        return controller.post()

    @admin_required_with_repo
    def put(self, product_id):
        from app.products.controllers.product_controller import ProductController
        controller = ProductController()
        return controller.put(product_id)

    @admin_required_with_repo
    def delete(self, product_id):
        from app.products.controllers.product_controller import ProductController
        controller = ProductController()
        return controller.delete(product_id)

# Register routes when this module is imported by products/__init__.py
def register_product_routes(products_bp):
    """Register all product routes with the products blueprint"""
    # List all products (GET), create new product (POST)
    products_bp.add_url_rule(
        '/',
        view_func=ProductAPI.as_view('products'),
        methods=['GET', 'POST']
    )
    # Get, update, or delete a specific product by ID
    products_bp.add_url_rule(
        '/<int:product_id>',
        view_func=ProductAPI.as_view('product'),
        methods=['GET', 'PUT', 'DELETE']
    )

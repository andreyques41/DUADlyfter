from flask import request, jsonify
import logging
import os
from flask.views import MethodView
from app.products.models.product import Product, ProductCategory, PetType

# Configure logging at module level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = './products.json'

class ProductAPI(MethodView):
    """Main CRUD operations for products - admin use"""

    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.db_path = DB_PATH

    def get(self, product_id=None):
        # GET: Retrieve all products or specific product
        pass

    def post(self):
        # POST: Create new product
        pass

    def put(self, product_id):
        # PUT: Update existing product
        pass

    def delete(self, product_id):
        # DELETE: Remove product
        pass

class ProductSearchAPI(MethodView):
    """Advanced product search with filters - customer use"""

    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.db_path = DB_PATH

    def get(self):
        # GET: Search products by category, pet_type, etc.
        pass

# Import blueprint from products module
from app.products import products_bp

def register_product_routes():
    """Register all product routes with the products blueprint"""
    products_bp.add_url_rule('/', view_func=ProductAPI.as_view('products'))
    products_bp.add_url_rule('/<int:product_id>', view_func=ProductAPI.as_view('product'))
    products_bp.add_url_rule('/search', view_func=ProductSearchAPI.as_view('product_search'))

# Call the function to register routes
register_product_routes()
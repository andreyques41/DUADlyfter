from flask import request, jsonify
import logging
import os
from flask.views import MethodView
from app.sales.models.cart import Cart, CartItem

# Configure logging at module level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = './carts.json'

class CartAPI(MethodView):
    """Manage shopping cart - add items, update quantities, view cart"""
    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.db_path = DB_PATH

    def get(self, user_id):
        # GET: Retrieve user's cart
        pass

    def post(self, user_id):
        # POST: Add item to cart
        pass

    def put(self, user_id):
        # PUT: Update item quantity in cart
        pass

    def delete(self, user_id):
        # DELETE: Clear entire cart
        pass

class CartItemAPI(MethodView):
    """Remove individual items from cart"""
    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.db_path = DB_PATH

    def delete(self, user_id, product_id):
        # DELETE: Remove specific item from cart
        pass

# Import blueprint from sales module
from app.sales import sales_bp

def register_cart_routes():
    """Register all cart routes with the sales blueprint"""
    sales_bp.add_url_rule('/cart/<int:user_id>', view_func=CartAPI.as_view('cart'))
    sales_bp.add_url_rule('/cart/<int:user_id>/items/<int:product_id>', view_func=CartItemAPI.as_view('cart_item'))

# Call the function to register routes
register_cart_routes()
from flask import request, jsonify
import logging
import os
from flask.views import MethodView
from app.sales.models.order import Order, OrderItem, OrderStatus

# Configure logging at module level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = './orders.json'

class OrderAPI(MethodView):
    """Order management - view orders, update status (admin/customer)"""

    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.db_path = DB_PATH

    def get(self, order_id=None):
        # GET: Retrieve user's orders or specific order
        pass

    def post(self):
        # POST: Create order from cart (checkout)
        pass

    def put(self, order_id):
        # PUT: Update order status
        pass

class CheckoutAPI(MethodView):
    """Convert cart to confirmed order - main purchase flow"""

    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.db_path = DB_PATH

    def post(self):
        # POST: Convert cart to order (checkout process)
        pass

# Import blueprint from sales module
from app.sales import sales_bp

def register_order_routes():
    """Register all order routes with the sales blueprint"""
    sales_bp.add_url_rule('/orders', view_func=OrderAPI.as_view('orders'))
    sales_bp.add_url_rule('/orders/<int:order_id>', view_func=OrderAPI.as_view('order'))
    sales_bp.add_url_rule('/checkout', view_func=CheckoutAPI.as_view('checkout'))

# Call the function to register routes
register_order_routes()

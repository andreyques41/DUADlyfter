from flask import request, jsonify
import logging
import os
from flask.views import MethodView
from app.sales.models.bills import Bill, BillStatus

# Configure logging at module level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = './bills.json'

class BillAPI(MethodView):
    """View and manage bills/invoices for orders"""
    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.db_path = DB_PATH

    def get(self, bill_id=None):
        # GET: Retrieve user's bills or specific bill
        pass

    def put(self, bill_id):
        # PUT: Update bill status (mark as paid/overdue)
        pass

class OrderBillAPI(MethodView):
    """Get bill information for specific order"""
    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.db_path = DB_PATH

    def get(self, order_id):
        # GET: Get bill details for specific order
        pass

# Import blueprint from sales module
from app.sales import sales_bp

def register_bill_routes():
    """Register all bill routes with the sales blueprint"""
    sales_bp.add_url_rule('/bills', view_func=BillAPI.as_view('bills'))
    sales_bp.add_url_rule('/bills/<int:bill_id>', view_func=BillAPI.as_view('bill'))
    sales_bp.add_url_rule('/orders/<int:order_id>/bill', view_func=OrderBillAPI.as_view('order_bill'))

# Call the function to register routes
register_bill_routes()

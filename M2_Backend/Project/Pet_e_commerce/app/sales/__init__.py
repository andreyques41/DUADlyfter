from flask import Blueprint

sales_bp = Blueprint('sales', __name__)

# Import routes after blueprint creation to avoid circular imports
from app.sales.routes import cart_routes, order_routes, bills_routes, returns_routes

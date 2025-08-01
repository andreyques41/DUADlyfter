from flask import Blueprint

products_bp = Blueprint('products', __name__)

# Import routes after blueprint creation to avoid circular imports
from app.products.routes import product_routes

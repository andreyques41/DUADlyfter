from flask import Flask
import logging
from app.utilities.db_manager import DBManager
from app.auth.auth_routes import RegisterAPI, LoginAPI
from app.auth.user_routes import UserAPI
from app.products.product_routes import ProductAPI
from app.sales.invoice_routes import InvoiceAPI
from app.utilities.cache_manager import CacheManager


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
)

# Initialize Flask app
app = Flask("fruit-store-api")

# Initialize DB Manager
db_manager = DBManager()

# Initialize Cache Manager
cache_manager = CacheManager(
    host="placeholder",
    port=14684,
    password="placeholder",
)

# ============================================
# REGISTER ROUTES
# ============================================

# Authentication routes
app.add_url_rule(
    '/register',
    view_func=RegisterAPI.as_view('register', db_manager=db_manager),
    methods=['POST']
)

app.add_url_rule(
    '/login',
    view_func=LoginAPI.as_view('login', db_manager=db_manager),
    methods=['POST']
)

# User management routes (admin only, except viewing own profile)
user_view = UserAPI.as_view('users', db_manager=db_manager)
app.add_url_rule('/users', view_func=user_view, methods=['GET', 'POST'])
app.add_url_rule('/users/<int:user_id>', view_func=user_view, methods=['GET', 'PUT', 'DELETE'])

# Product routes
product_view = ProductAPI.as_view('products', db_manager=db_manager, cache_manager=cache_manager)
app.add_url_rule('/products', view_func=product_view, methods=['GET', 'POST'])
app.add_url_rule('/products/<int:product_id>', view_func=product_view, methods=['GET', 'PUT', 'DELETE'])

# Invoice routes  
invoice_view = InvoiceAPI.as_view('invoices', db_manager=db_manager)
app.add_url_rule('/invoices', view_func=invoice_view, methods=['GET', 'POST'])
app.add_url_rule('/invoices/<int:invoice_id>', view_func=invoice_view, methods=['GET', 'DELETE'])


# Health check
@app.route("/health")
def health():
    return {"status": "OK", "service": "fruit-store-api"}


if __name__ == "__main__":
    app.run(debug=True, port=5000)
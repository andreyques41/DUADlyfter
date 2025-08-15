from flask import Blueprint
from app.auth.routes.auth_routes import auth_bp
from app.products.routes.product_routes import products_bp
from app.sales import sales_bp

# Each tuple: (blueprint, url_prefix)
blueprints = [
    (auth_bp, '/auth'),
    (products_bp, '/products'),
    (sales_bp, '/sales')
]

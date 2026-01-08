from flask import Blueprint
from app.auth import auth_bp, user_bp
from app.products import products_bp
from app.sales import sales_bp

# Each tuple: (blueprint, url_prefix)
blueprints = [
    (auth_bp, '/auth'),
    (user_bp, '/auth'),  # User management routes under same /auth prefix
    (products_bp, '/products'),
    (sales_bp, '/sales')
]

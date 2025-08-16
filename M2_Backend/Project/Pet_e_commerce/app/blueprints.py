from flask import Blueprint
from app.auth import auth_bp
from app.products import products_bp
from app.sales import sales_bp

# Each tuple: (blueprint, url_prefix)
blueprints = [
    (auth_bp, '/auth'),
    (products_bp, '/products'),
    (sales_bp, '/sales')
]

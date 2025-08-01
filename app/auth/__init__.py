from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

# Import routes after blueprint creation to avoid circular imports
from app.auth.routes import auth_routes

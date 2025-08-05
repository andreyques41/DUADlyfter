from flask import jsonify
import logging
from app.shared.utils.json_handler import read_json, write_json
from app.auth.models.user import User, UserRole

logger = logging.getLogger(__name__)

class ProdService:
    """Service class for authentication and user management operations"""
    
    def __init__(self, db_path='./products.json'):
        self.db_path = db_path
        self.logger = logger

    def generate_new_id(self):
        pass
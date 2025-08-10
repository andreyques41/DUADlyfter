from flask import jsonify
import logging
from app.shared.utils import read_json, write_json
from app.products.models import Product, ProductCategory, PetType

logger = logging.getLogger(__name__)

class ProdService:
    """Service class for authentication and product management operations"""
    
    def __init__(self, db_path='./products.json'):
        self.db_path = db_path
        self.logger = logger

    # ============ PRODUCT RETRIEVAL METHODS ============

    def get_products(self, product_id=None):
        """
        Unified method to get all products or a specific product by ID.
        
        Args:
            product_id (int, optional): If provided, returns single product. 
            If None, returns all products.
        
        Returns:
            list[Product] or Product or None: List of products, single product, or None if not found
        """
        return _get_product(self.db_path, Product, id=product_id)

    def create_product(self):
        pass
    def update_product(self):
        pass
    def delete_product(self):
        pass

    # ============ PRIVATE INSTANCE METHODS ============

    def _generate_new_product_id(self):
        """Generate a new unique product ID based on existing products."""
        try:
            products = self.get_all_products()
            if not products:
                return 1
            return max(product.id for product in products) + 1
        except:
            return 1
        
# ============ MODULE-LEVEL UTILITY FUNCTIONS ============

def _save_products(products, db_path):
    """Save list of Product objects to JSON file.
    
    Reusable utility function for saving products that can be used by other services.
    Uses to_dict_with_password() for complete internal storage including password hashes.
    """
    product_dicts = [product.to_dict_with_password() for product in products]
    write_json(product_dicts, db_path)

def _get_product(db_path, model, id=None):
    """Load product(s) from JSON file and return as Product object(s).
    
    Reusable utility function for loading products that can be used by other services.
    """
    try:
        raw_data = read_json(db_path)
        
        if id is None:
            return [model.from_dict_with_password(product_data) for product_data in raw_data]
        else:
            for product_data in raw_data:
                if product_data.get('id') == id:
                    return model.from_dict_with_password(product_data)
            return None
                
    except Exception as e:
        logger.error(f"Error loading product(s): {e}")
        return [] if id is None else None

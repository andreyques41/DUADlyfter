from flask import jsonify
import logging
from app.shared.utils import read_json, write_json
from app.products.models import Product, ProductCategory, PetType

logger = logging.getLogger(__name__)

class ProdService:
    """Service class for product management operations"""
    
    def __init__(self, db_path='./products.json'):
        self.db_path = db_path
        self.logger = logger

    # ============ PUBLIC CRUD METHODS ============

    def get_products(self, product_id=None, filters=None):
        """
        Unified method to get all products or a specific product by ID with optional filtering.
        
        Args:
            product_id (int, optional): If provided, returns single product. 
            filters (dict, optional): Filter parameters for product search
            
        Returns:
            list[Product] or Product or None: Filtered products, single product, or None if not found
        """
        products = _get_product(self.db_path, Product, id=product_id)

        if product_id is None and filters:
            return _apply_filters(products, filters)
        return products

    def create_product(self):
        pass
    
    def update_product(self):
        pass
    
    def delete_product(self):
        pass

    # ============ STATIC UTILITY METHODS ============
    
    @staticmethod
    def process_filters(raw_filters):
        """Clean and validate filter parameters"""
        processed = {}    

        for key, value in raw_filters.items():
            if value is None:
                continue

            # Type conversion and validation
            if key in ['min_price', 'max_price', 'min_weight', 'max_weight']:
                try:
                    processed[key] = float(value)
                except ValueError:
                    continue    # Skip invalid numeric values

            elif key in ['available_only', 'is_active', 'low_stock']:
                processed[key] = value.lower() in ['true', '1', 'yes']

            elif key == 'category':
                # Validate against ProductCategory enum
                try:
                    ProductCategory(value.lower())
                    processed[key] = value.lower()
                except ValueError:
                        continue  # Skip invalid category
                
            elif key == 'pet_type':
                # Validate against PetType enum
                try:
                    PetType(value.lower())
                    processed[key] = value.lower()
                except ValueError:
                    continue  # Skip invalid pet type
                
            else:
                # String filters (brand, search)
                processed[key] = value.strip()
        
        return processed

    # ============ PRIVATE HELPER METHODS ============

    def _generate_new_product_id(self):
        """Generate a new unique product ID based on existing products."""
        try:
            products = self.get_products()  # Get all products
            if not products:
                return 1
            return max(product.id for product in products) + 1
        except:
            return 1
        
# ============ MODULE-LEVEL UTILITY FUNCTIONS ============

# --- Data Persistence Functions ---

def _save_products(products, db_path):
    """Save list of Product objects to JSON file.
    
    Reusable utility function for saving products that can be used by other services.
    """
    product_dicts = [product.to_dict() for product in products]
    write_json(product_dicts, db_path)

def _get_product(db_path, model, id=None):
    """Load product(s) from JSON file and return as Product object(s).
    
    Reusable utility function for loading products that can be used by other services.
    """
    try:
        raw_data = read_json(db_path)
        
        if id is None:
            return [model.from_dict(product_data) for product_data in raw_data]
        else:
            for product_data in raw_data:
                if product_data.get('id') == id:
                    return model.from_dict(product_data)
            return None
                
    except Exception as e:
        logger.error(f"Error loading product(s): {e}")
        return [] if id is None else None

# --- Filtering Functions ---

def _apply_filters(products, filters):
    """Apply filters to product list"""
    filtered_products = products

    for filter_key, filter_value in filters.items():
        if filter_key == 'category':
            filtered_products = [p for p in filtered_products if p.category.value == filter_value]
        elif filter_key == 'pet_type':
            filtered_products = [p for p in filtered_products if p.pet_type.value == filter_value]
        elif filter_key == 'min_price':
            filtered_products = [p for p in filtered_products if p.price >= filter_value]
        elif filter_key == 'max_price':
            filtered_products = [p for p in filtered_products if p.price <= filter_value]
        elif filter_key == 'min_weight':
            filtered_products = [p for p in filtered_products if p.weight and p.weight >= filter_value]
        elif filter_key == 'max_weight':
            filtered_products = [p for p in filtered_products if p.weight and p.weight <= filter_value]
        elif filter_key == 'available_only' and filter_value:
            filtered_products = [p for p in filtered_products if p.is_available()]
        elif filter_key == 'is_active':
            filtered_products = [p for p in filtered_products if p.is_active == filter_value]
        elif filter_key == 'low_stock' and filter_value:
            filtered_products = [p for p in filtered_products if p.stock_quantity <= 10]
        elif filter_key == 'brand' and filter_value:
            filtered_products = [p for p in filtered_products if p.brand and filter_value.lower() in p.brand.lower()]
        elif filter_key == 'search' and filter_value:
            filtered_products = [p for p in filtered_products if _matches_search(p, filter_value)]

    return filtered_products

def _matches_search(product, search_term):
    """Check if product matches search term"""
    search_term = search_term.lower()
    searchable_text = f"{product.name} {product.description} {product.brand or ''}".lower()
    return search_term in searchable_text
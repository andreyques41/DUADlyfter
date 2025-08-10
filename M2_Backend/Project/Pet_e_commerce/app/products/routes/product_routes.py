from flask import request, jsonify
import logging
from flask.views import MethodView
from marshmallow import ValidationError
from flask import g
from app.products.services import ProdService
from app.products.schemas import (
    product_registration_schema, 
    product_response_schema, 
    products_response_schema,
    ProductResponseSchema
)
from app.auth.services import token_required, admin_required
from app.shared.utils import require_admin_access, require_user_or_admin_access, is_admin_user
from config.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)

DB_PATH = './products.json'

class ProductAPI(MethodView):
    """CRUD operations for products - GET: public access, POST/PUT/DELETE: admin only"""

    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.prod_service = ProdService(DB_PATH)

    def get(self, product_id=None):
        """GET: Retrieve all products or specific product - Public access for e-commerce"""
        try:
            # Get product(s) using unified service method
            result = self.prod_service.get_products(product_id)
            
            # Handle not found case for single product
            if product_id is not None and result is None:
                return jsonify({"error": "Product not found"}), 404
            
            # Determine schema configuration based on user role
            include_admin_data = hasattr(g, 'current_user') and is_admin_user()
            show_exact_stock = include_admin_data
            many = product_id is None  # True for all products, False for single product
            
            # Create response schema with appropriate settings
            schema = ProductResponseSchema(
                include_admin_data=include_admin_data, 
                show_exact_stock=show_exact_stock, 
                many=many
            )
            
            return jsonify(schema.dump(result))
                
        except Exception as e:
            self.logger.error(f"Error retrieving product(s): {e}")
            return jsonify({"error": "Failed to retrieve product data"}), 500
        
    @token_required
    @admin_required
    def post(self):
        """Create new product with validation. Includes all fields since only admins can create products."""
        try:
            # Use product registration schema - since only admins can create products
            validated_data = product_registration_schema.load(request.json)
            
            # Create product using service
            new_product, error = self.prod_service.create_product(validated_data)
            if error:
                return jsonify({"error": error}), 500
            
            schema = ProductResponseSchema(include_admin_data=True, show_exact_stock=True)
            # Return success response
            return jsonify({
                "message": "Product created successfully",
                "product": schema.dump(new_product)
            }), 201
            
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error creating product: {e}")
            return jsonify({"error": "Product creation failed"}), 500

    @token_required
    @admin_required
    def put(self, product_id):
        """Update user profile or password based on request content."""
        try:   
            # Validate profile update data
            validated_data = product_registration_schema.load(request.json)
            
            # Update user using service (using path parameter, not g.current_user)
            updated_user, error = self.prod_service.update_product(product_id, validated_data)
            
            if error:
                if error == "product not found":
                    return jsonify({"error": error}), 404
                return jsonify({"error": error}), 500
            
            schema = ProductResponseSchema(include_admin_data=True, show_exact_stock=True)
            return jsonify({
                "message": "User profile updated successfully",
                "user": schema.dump(updated_user)
            }), 200
        except Exception as e:
            self.logger.error(f"Error updating user: {e}")
            return jsonify({"error": "User update failed"}), 500

    @token_required
    @admin_required
    def delete(self, product_id):
        """Delete user account by ID."""
        try:
            
            success, error = self.prod_service.delete_product(product_id)
            
            if error:
                if error == "Product not found":
                    return jsonify({"error": error}), 404
                return jsonify({"error": error}), 500
            
            return jsonify({"message": "Product deleted successfully"}), 200
            
        except Exception as e:
            self.logger.error(f"Error deleting user: {e}")
            return jsonify({"error": "Product deletion failed"}), 500

# Import blueprint from products module
from app.products import products_bp

def register_product_routes():
    """Register all product routes with the products blueprint"""
    products_bp.add_url_rule('/', view_func=ProductAPI.as_view('products'))
    products_bp.add_url_rule('/<int:product_id>', view_func=ProductAPI.as_view('product'))

# Call the function to register routes
register_product_routes()
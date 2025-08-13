"""
Product Routes Module

Provides RESTful API endpoints for product management:
- GET /products - List all products with filtering (public access)
- GET /products/<id> - Get specific product (public access)  
- POST /products - Create new product (admin only)
- PUT /products/<id> - Update product (admin only)
- DELETE /products/<id> - Delete product (admin only)

Features:
- Public access for product browsing (e-commerce)
- Advanced filtering (category, price, brand, search, etc.)
- Admin-only access for product management
- Role-based response data (admins see more details)
- Comprehensive input validation
"""
from flask import request, jsonify, g
from flask.views import MethodView
from marshmallow import ValidationError
from app.products.services import ProdService
from app.products.schemas import (
    product_registration_schema, 
    ProductResponseSchema
)
from app.auth.services import token_required, admin_required
from app.shared.utils import is_admin_user
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
        """Retrieve all products or specific product - public access for e-commerce."""
        # NO AUTHENTICATION REQUIRED - Public access for e-commerce browsing
        try:
            # Get product(s) using unified service method (service extracts filters internally)
            result = self.prod_service.get_products(product_id, request_args=request.args if product_id is None else None)
            
            # Handle not found case for single product
            if product_id is not None and result is None:
                return jsonify({"error": "Product not found"}), 404
            
            # Determine schema configuration based on user role
            # If user is authenticated AND is admin, show admin data
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
        
    @token_required  # Step 1: Validates JWT token, sets g.current_user
    @admin_required  # Step 2: Verifies g.current_user.role == ADMIN
    def post(self):
        """Create new product with validation. Admin access required."""
        # ADMIN ONLY ACCESS - Only administrators can create products
        try:
            # Schema now returns Product instance thanks to @post_load
            product_instance = product_registration_schema.load(request.json)
            
            # Create product using service - pass the Product instance directly
            new_product, error = self.prod_service.create_product(product_instance)
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

    @token_required  # Step 1: Validates JWT token, sets g.current_user
    @admin_required  # Step 2: Verifies g.current_user.role == ADMIN
    def put(self, product_id):
        """Update product data. Admin access required."""
        # ADMIN ONLY ACCESS - Only administrators can update products
        try:   
            # Schema now returns Product instance thanks to @post_load
            product_instance = product_registration_schema.load(request.json)
            
            # Update product using service - pass the Product instance directly
            updated_product, error = self.prod_service.update_product(product_id, product_instance)
            
            if error:
                if error == "Product not found":
                    return jsonify({"error": error}), 404
                return jsonify({"error": error}), 500
            
            schema = ProductResponseSchema(include_admin_data=True, show_exact_stock=True)
            return jsonify({
                "message": "Product updated successfully",
                "product": schema.dump(updated_product)
            }), 200
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error updating product: {e}")
            return jsonify({"error": "Product update failed"}), 500

    @token_required  # Step 1: Validates JWT token, sets g.current_user  
    @admin_required  # Step 2: Verifies g.current_user.role == ADMIN
    def delete(self, product_id):
        """Delete product by ID. Admin access required."""
        # ADMIN ONLY ACCESS - Only administrators can delete products
        try:
            success, error = self.prod_service.delete_product(product_id)
            
            if error:
                if error == "Product not found":
                    return jsonify({"error": error}), 404
                return jsonify({"error": error}), 500
            
            return jsonify({"message": "Product deleted successfully"}), 200
            
        except Exception as e:
            self.logger.error(f"Error deleting product: {e}")
            return jsonify({"error": "Product deletion failed"}), 500

# Import blueprint from products module
from app.products import products_bp

def register_product_routes():
    """Register all product routes with the products blueprint"""
    products_bp.add_url_rule('/', view_func=ProductAPI.as_view('products'))
    products_bp.add_url_rule('/<int:product_id>', view_func=ProductAPI.as_view('product'))

# Call the function to register routes
register_product_routes()
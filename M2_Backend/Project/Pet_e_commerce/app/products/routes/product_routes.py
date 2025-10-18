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

# Common imports
from flask import Blueprint, request, jsonify, g
from flask.views import MethodView
from marshmallow import ValidationError
from config.logging import get_logger, EXC_INFO_LOG_ERRORS

# Auth imports (for decorators)
from app.core.middleware import admin_required_with_repo
from app.core.lib.auth import is_admin_user

# Products domain imports
from app.products.services import ProductService
from app.products.schemas import (
    product_registration_schema,
    ProductResponseSchema
)

# Get logger for this module
logger = get_logger(__name__)

class ProductAPI(MethodView):
    """CRUD operations for products - GET: public access, POST/PUT/DELETE: admin only"""

    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.product_service = ProductService()

    def get(self, product_id=None):
        """Retrieve all products or specific product - public access for e-commerce."""
        # NO AUTHENTICATION REQUIRED - Public access for e-commerce browsing
        try:
            # Get product(s)
            if product_id:
                result = self.product_service.get_product_by_id(product_id)
                if result is None:
                    self.logger.warning(f"Product not found: {product_id}")
                    return jsonify({"error": "Product not found"}), 404
                many = False
            else:
                # Extract filters from query parameters
                filters = {}
                
                # Category filter (e.g., ?category=food)
                if 'category' in request.args:
                    filters['category'] = request.args.get('category')
                
                # Pet type filter (e.g., ?pet_type=dog)
                if 'pet_type' in request.args:
                    filters['pet_type'] = request.args.get('pet_type')
                
                # Brand filter (e.g., ?brand=PetNutrition)
                if 'brand' in request.args:
                    filters['brand'] = request.args.get('brand')
                
                # Active status filter (e.g., ?is_active=true)
                if 'is_active' in request.args:
                    filters['is_active'] = request.args.get('is_active').lower() == 'true'
                
                # Search filter (e.g., ?search=premium)
                if 'search' in request.args:
                    filters['search'] = request.args.get('search')
                
                # Min stock filter (e.g., ?min_stock=10)
                if 'min_stock' in request.args:
                    try:
                        filters['min_stock'] = int(request.args.get('min_stock'))
                    except ValueError:
                        self.logger.warning(f"Invalid min_stock value: {request.args.get('min_stock')}")
                
                # Get products with filters (or all if no filters)
                if filters:
                    self.logger.debug(f"Applying filters: {filters}")
                    result = self.product_service.get_products_by_filters(filters)
                else:
                    result = self.product_service.get_all_products()
                
                many = True

            # Determine schema configuration based on user role
            # If user is authenticated AND is admin, show admin data
            include_admin_data = hasattr(g, 'current_user') and is_admin_user()
            show_exact_stock = include_admin_data

            # Create response schema with appropriate settings
            schema = ProductResponseSchema(
                include_admin_data=include_admin_data, 
                show_exact_stock=show_exact_stock, 
                many=many
            )

            self.logger.info(f"Product(s) retrieved: {'all' if product_id is None else product_id}")
            return jsonify(schema.dump(result))

        except Exception as e:
            self.logger.error(f"Error retrieving product(s): {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Failed to retrieve product data"}), 500
        
    @admin_required_with_repo  # Validates JWT token + verifies admin in DB
    def post(self):
        """Create new product with validation. Admin access required."""
        # ADMIN ONLY ACCESS - Only administrators can create products
        try:
            # Validate request data
            product_data = product_registration_schema.load(request.json)
            self.logger.debug(f"Product data validated from request")

            # Add creator info
            product_data['created_by'] = g.current_user.username
            
            # Create product using service
            new_product = self.product_service.create_product(**product_data)
            
            if not new_product:
                self.logger.error("Product creation failed")
                return jsonify({"error": "Product creation failed"}), 500

            schema = ProductResponseSchema(include_admin_data=True, show_exact_stock=True)
            self.logger.info(f"Product created: {new_product.id}")
            # Return success response
            return jsonify({
                "message": "Product created successfully",
                "product": schema.dump(new_product)
            }), 201

        except ValidationError as err:
            self.logger.warning(f"Product creation validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error creating product: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Product creation failed"}), 500

    @admin_required_with_repo  # Validates JWT token + verifies admin in DB
    def put(self, product_id):
        """Update product data. Admin access required."""
        # ADMIN ONLY ACCESS - Only administrators can update products
        try:   
            # Validate request data
            product_data = product_registration_schema.load(request.json)

            # Update product using service
            updated_product = self.product_service.update_product(product_id, **product_data)

            if not updated_product:
                self.logger.warning(f"Product update attempt for non-existent product: {product_id}")
                return jsonify({"error": "Product not found"}), 404

            schema = ProductResponseSchema(include_admin_data=True, show_exact_stock=True)
            self.logger.info(f"Product updated: {product_id}")
            return jsonify({
                "message": "Product updated successfully",
                "product": schema.dump(updated_product)
            }), 200
        except ValidationError as err:
            self.logger.warning(f"Product update validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error updating product: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Product update failed"}), 500

    @admin_required_with_repo  # Validates JWT token + verifies admin in DB
    def delete(self, product_id):
        """Delete product by ID. Admin access required."""
        # ADMIN ONLY ACCESS - Only administrators can delete products
        try:
            success = self.product_service.delete_product(product_id)

            if not success:
                self.logger.warning(f"Delete attempt for non-existent product: {product_id}")
                return jsonify({"error": "Product not found"}), 404

            self.logger.info(f"Product deleted: {product_id}")
            return jsonify({"message": "Product deleted successfully"}), 200

        except Exception as e:
            self.logger.error(f"Error deleting product: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return jsonify({"error": "Product deletion failed"}), 500

# Register routes when this module is imported by products/__init__.py
def register_product_routes(products_bp):
    """Register all product routes with the products blueprint"""
    # List all products (GET), create new product (POST)
    products_bp.add_url_rule(
        '/',
        view_func=ProductAPI.as_view('products'),
        methods=['GET', 'POST']
    )
    # Get, update, or delete a specific product by ID
    products_bp.add_url_rule(
        '/<int:product_id>',
        view_func=ProductAPI.as_view('product'),
        methods=['GET', 'PUT', 'DELETE']
    )

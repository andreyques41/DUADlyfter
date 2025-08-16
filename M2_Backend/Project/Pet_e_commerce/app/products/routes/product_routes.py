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
from app.shared.common_imports import *

# Auth imports (for decorators)
from app.auth.imports import token_required, admin_required, is_admin_user

# Products domain imports
from app.products.imports import (
    ProdService, ProductResponseSchema,
    product_registration_schema, product_response_schema, 
    product_update_schema, products_response_schema,
    PRODUCTS_DB_PATH, ProductCategory, PetType
)

# Get logger for this module
logger = get_logger(__name__)

class ProductAPI(MethodView):
    """CRUD operations for products - GET: public access, POST/PUT/DELETE: admin only"""

    init_every_request = False

    def __init__(self):
        self.logger = logger
        self.prod_service = ProdService(PRODUCTS_DB_PATH)

    def get(self, product_id=None):
        """Retrieve all products or specific product - public access for e-commerce."""
        # NO AUTHENTICATION REQUIRED - Public access for e-commerce browsing
        try:
            # Get product(s) using unified service method (service extracts filters internally)
            result = self.prod_service.get_products(product_id, request_args=request.args if product_id is None else None)

            # Handle not found case for single product
            if product_id is not None and result is None:
                self.logger.warning(f"Product not found: {product_id}")
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

            self.logger.info(f"Product(s) retrieved: {'all' if product_id is None else product_id}")
            return jsonify(schema.dump(result))

        except Exception as e:
            self.logger.error(f"Error retrieving product(s): {e}", exc_info=EXC_INFO_LOG_ERRORS)
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
                self.logger.error(f"Product creation failed: {error}")
                return jsonify({"error": error}), 500

            schema = ProductResponseSchema(include_admin_data=True, show_exact_stock=True)
            self.logger.info(f"Product created: {new_product.id if new_product else 'unknown'}")
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
                    self.logger.warning(f"Product update attempt for non-existent product: {product_id}")
                    return jsonify({"error": error}), 404
                self.logger.error(f"Product update failed for {product_id}: {error}")
                return jsonify({"error": error}), 500

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

    @token_required  # Step 1: Validates JWT token, sets g.current_user  
    @admin_required  # Step 2: Verifies g.current_user.role == ADMIN
    def delete(self, product_id):
        """Delete product by ID. Admin access required."""
        # ADMIN ONLY ACCESS - Only administrators can delete products
        try:
            success, error = self.prod_service.delete_product(product_id)

            if error:
                if error == "Product not found":
                    self.logger.warning(f"Delete attempt for non-existent product: {product_id}")
                    return jsonify({"error": error}), 404
                self.logger.error(f"Product deletion failed for {product_id}: {error}")
                return jsonify({"error": error}), 500

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

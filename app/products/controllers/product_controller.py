"""
ProductController: Handles HTTP responses and error formatting for product endpoints.
Delegates business logic to ProductService.

Features:
- Optional authentication for role-based responses
- Advanced filtering support (category, pet_type, brand, search, etc.)
- Role-based schema configuration (admin users see more data)
- Centralized error handling and logging
"""
from flask import jsonify, request, g
from marshmallow import ValidationError
from config.logging import get_logger, EXC_INFO_LOG_ERRORS
from app.core.lib.error_utils import error_response

# Auth imports
from app.core.lib.auth import is_admin_user
from app.core.lib.jwt import verify_jwt_token
from app.core.lib.users import get_user_by_id

# Products domain imports
from app.products.services.product_service import ProductService
from app.products.schemas.product_schema import ProductRegistrationSchema, ProductResponseSchema

# Get logger for this module
logger = get_logger(__name__)


class ProductController:
    """
    Controller layer for product management. 
    Handles HTTP responses, authentication, filtering, and delegates to ProductService.
    """
    def __init__(self):
        self.product_service = ProductService()
        self.product_schema = ProductRegistrationSchema()
        self.logger = logger
    
    def _try_authenticate_user(self):
        """
        Optional authentication: Attempts to authenticate user from Authorization header.
        Does NOT fail if no token is present - just sets g.current_user if available.
        This allows public access while still recognizing authenticated admin users.
        """
        token = None
        
        # Try to get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # "Bearer <token>" → "<token>"
            except Exception:
                # Invalid format, but don't fail - just treat as unauthenticated
                return
        else:
            # No token provided, treat as public access
            return
        
        try:
            # Verify JWT token
            data = verify_jwt_token(token)
            if not data:
                return  # Invalid token, but don't fail
            
            # Get user from database
            current_user = get_user_by_id(data['user_id'])
            if not current_user:
                return  # User not found, but don't fail
            
            # Store user in Flask's g object
            g.current_user = current_user
            self.logger.info(f"Authenticated user {current_user.username} for optional auth")
        except Exception as e:
            # Token validation failed, but don't fail the request
            self.logger.debug(f"Optional auth failed (expected for public access): {e}")
            return
    
    def _extract_filters_from_request(self):
        """
        Extract and parse filter parameters from query string.
        
        Returns:
            Dictionary with filter criteria for ProductService
        """
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
        
        return filters

    def get(self, product_id=None):
        """
        GET endpoint dispatcher. Delegates to get_by_id or get_all.
        Supports optional authentication for role-based responses.
        """
        # Optional authentication: Try to authenticate user if token is present
        self._try_authenticate_user()
        
        if product_id:
            return self.get_by_id(product_id)
        return self.get_all()

    def get_all(self):
        """
        Return a list of all products with optional filtering.
        Public access - but admins see more data if authenticated.
        Uses schema-based caching for improved performance.
        """
        try:
            # Determine if admin for cache key
            include_admin_data = hasattr(g, 'current_user') and is_admin_user()
            show_exact_stock = include_admin_data
            
            # Extract filters from query parameters
            filters = self._extract_filters_from_request()
            
            # If filters are applied, bypass cache (dynamic queries)
            if filters:
                self.logger.debug(f"Applying filters (cache bypassed): {filters}")
                products = self.product_service.get_products_by_filters(filters)
                
                # Serialize with schema
                schema = ProductResponseSchema(
                    include_admin_data=include_admin_data,
                    show_exact_stock=show_exact_stock,
                    many=True
                )
                serialized = schema.dump(products)
                
                self.logger.info(f"Retrieved {len(products)} filtered product(s)")
                return jsonify(serialized), 200
            else:
                # No filters - use cached method
                products_data = self.product_service.get_all_products_cached(
                    include_admin_data=include_admin_data,
                    show_exact_stock=show_exact_stock
                )
                
                self.logger.info(f"Retrieved {len(products_data)} product(s) from service")
                return jsonify(products_data), 200
            
        except Exception as e:
            self.logger.error(f"Error retrieving products: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to retrieve product data", e)

    def get_by_id(self, product_id):
        """
        Return a product by its ID.
        Public access - but admins see more data if authenticated.
        Uses schema-based caching for improved performance.
        """
        try:
            # Determine if admin for cache key
            include_admin_data = hasattr(g, 'current_user') and is_admin_user()
            show_exact_stock = include_admin_data
            
            # Use cached method (returns serialized dict)
            product_data = self.product_service.get_product_by_id_cached(
                product_id,
                include_admin_data=include_admin_data,
                show_exact_stock=show_exact_stock
            )
            
            if product_data is None:
                self.logger.warning(f"Product not found: {product_id}")
                return jsonify({"error": "Product not found"}), 404
            
            self.logger.info(f"Product retrieved: {product_id}")
            return jsonify(product_data), 200
            
        except Exception as e:
            self.logger.error(f"Error retrieving product {product_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Failed to retrieve product data", e)

    def post(self):
        """
        POST endpoint. Validates input, adds creator info, and creates product.
        Admin access required (enforced by decorator in routes).
        """
        try:
            # Validate request data
            data = request.get_json()
            validated = self.product_schema.load(data)
            self.logger.debug(f"Product data validated from request")
            
            # Add creator info from authenticated user
            if hasattr(g, 'current_user'):
                validated['created_by'] = g.current_user.username
            
            # Create product using service
            product = self.product_service.create_product(**validated)
            
            if not product:
                self.logger.error("Product creation failed in service layer")
                return jsonify({"error": "Product creation failed"}), 500
            
            # Create response schema with admin data (since this is admin-only endpoint)
            schema = ProductResponseSchema(include_admin_data=True, show_exact_stock=True)
            self.logger.info(f"Product created: {product.id}")
            
            return jsonify({
                "message": "Product created successfully",
                "product": schema.dump(product)
            }), 201
            
        except ValidationError as err:
            self.logger.warning(f"Product creation validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error creating product: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Product creation failed", e)

    def put(self, product_id):
        """
        PUT endpoint. Validates input and updates product.
        Admin access required (enforced by decorator in routes).
        """
        try:
            # Validate request data (partial update allowed)
            data = request.get_json()
            validated = self.product_schema.load(data, partial=True)
            
            # Update product using service
            product = self.product_service.update_product(product_id, **validated)
            
            if not product:
                self.logger.warning(f"Product update attempt for non-existent product: {product_id}")
                return jsonify({"error": "Product not found"}), 404
            
            # Create response schema with admin data (since this is admin-only endpoint)
            schema = ProductResponseSchema(include_admin_data=True, show_exact_stock=True)
            self.logger.info(f"Product updated: {product_id}")
            
            return jsonify({
                "message": "Product updated successfully",
                "product": schema.dump(product)
            }), 200
            
        except ValidationError as err:
            self.logger.warning(f"Product update validation error: {err.messages}")
            return jsonify({"errors": err.messages}), 400
        except Exception as e:
            self.logger.error(f"Error updating product {product_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Product update failed", e)

    def delete(self, product_id):
        """
        DELETE endpoint. Deletes product by ID.
        Admin access required (enforced by decorator in routes).
        """
        try:
            success = self.product_service.delete_product(product_id)
            
            if not success:
                self.logger.warning(f"Delete attempt for non-existent product: {product_id}")
                return jsonify({"error": "Product not found"}), 404
            
            self.logger.info(f"Product deleted: {product_id}")
            return jsonify({"message": "Product deleted successfully"}), 200
            
        except Exception as e:
            self.logger.error(f"Error deleting product {product_id}: {e}", exc_info=EXC_INFO_LOG_ERRORS)
            return error_response("Product deletion failed", e)

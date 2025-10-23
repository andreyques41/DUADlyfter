from flask import request, jsonify, g
import logging
from flask.views import MethodView
from app.products.product_repository import ProductRepository
from app.auth.user_repository import UserRepository
from app.utilities.decorators import require_admin_with_repo
from datetime import date
import json

class ProductAPI(MethodView):
    """CRUD operations for products."""
    
    def __init__(self, db_manager, cache_manager):
        self.logger = logging.getLogger(__name__)
        self.product_repository = ProductRepository(db_manager)
        self.user_repository = UserRepository(db_manager)
        self.cache_manager = cache_manager
    
    def get(self, product_id=None):
        """Get all products or specific product by ID. Cache is per product and for full list."""
        if product_id:
            product = self._get_product_from_cache(product_id)
            if product is not None:
                return jsonify({"product": product}), 200
            # Fallback to DB
            try:
                result = self.product_repository.get_by_id(product_id)
                if result is False:
                    self.logger.error("Database error on get_by_id")
                    return jsonify({"error": "Database error"}), 500
                if result is None:
                    self.logger.warning(f"Product not found: {product_id}")
                    return jsonify({"error": "Product not found"}), 404
                # Store in cache for future requests
                self._set_product_in_cache(product_id, result)
                return jsonify({"product": result}), 200
            except Exception as e:
                self.logger.error(f"Get product error: {e}")
                return jsonify({"error": "Failed to retrieve product"}), 500
        else:
            # GET all: check cache first
            products = self._get_products_list_from_cache()
            if products is not None:
                return jsonify({"products": products}), 200
            try:
                products = self.product_repository.get_all()
                if products is False:
                    self.logger.error("Database error on get_all")
                    return jsonify({"error": "Database error"}), 500
                self._set_products_list_in_cache(products)
                return jsonify({"products": products}), 200
            except Exception as e:
                self.logger.error(f"Get products error: {e}")
                return jsonify({"error": "Failed to retrieve products"}), 500

    @require_admin_with_repo('user_repository')
    def post(self):
        """Create new product. Only admin can create products."""
        try:
            data = request.get_json()
            if not data:
                self.logger.warning("No JSON data provided in product creation")
                return jsonify({"error": "No JSON data provided"}), 400
            required_fields = ["name", "price", "quantity"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                self.logger.warning(f"Missing fields in product creation: {missing_fields}")
                return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400
            if data.get("entry_date"):
                try:
                    entry_date = date.fromisoformat(data["entry_date"])
                except ValueError:
                    self.logger.warning("Invalid date format in product creation")
                    return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
            else:
                entry_date = date.today()
            product_id = self.product_repository.create_product(
                name=data["name"],
                price=data["price"],
                quantity=data["quantity"],
                entry_date=entry_date
            )
            if product_id is False:
                self.logger.error("Product creation failed in repository")
                return jsonify({"error": "Product creation failed"}), 500
            self._invalidate_product_cache(product_id)
            self._invalidate_products_list_cache()
            return jsonify({"message": "Product created successfully", "product_id": product_id}), 201
        except Exception as e:
            self.logger.error(f"Create product error: {e}")
            return jsonify({"error": "Product creation failed"}), 500

    @require_admin_with_repo('user_repository')
    def put(self, product_id):
        """Update product. Only admin can update products."""
        try:
            data = request.get_json()
            if not data:
                self.logger.warning("No JSON data provided in product update")
                return jsonify({"error": "No JSON data provided"}), 400
            existing = self.product_repository.get_by_id(product_id)
            if existing is False:
                self.logger.error("Database error on get_by_id in update")
                return jsonify({"error": "Database error"}), 500
            if existing is None:
                self.logger.warning(f"Product not found for update: {product_id}")
                return jsonify({"error": "Product not found"}), 404
            if data.get("entry_date"):
                try:
                    data["entry_date"] = date.fromisoformat(data["entry_date"])
                except ValueError:
                    self.logger.warning("Invalid date format in product update")
                    return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
            else:
                data["entry_date"] = date.today()
            result = self.product_repository.update_product(product_id, **data)
            if result is False:
                self.logger.error("Product update failed in repository")
                return jsonify({"error": "Product update failed"}), 500
            self._invalidate_product_cache(product_id)
            self._invalidate_products_list_cache()
            return jsonify({"message": "Product updated successfully"}), 200
        except Exception as e:
            self.logger.error(f"Update product error: {e}")
            return jsonify({"error": "Product update failed"}), 500

    @require_admin_with_repo('user_repository')
    def delete(self, product_id):
        """Delete product. Only admin can delete products."""
        try:
            success, error = self.product_repository.delete_product(product_id)
            if not success:
                if error == "Product not found":
                    self.logger.warning(f"Product not found for delete: {product_id}")
                    return jsonify({"error": error}), 404
                self.logger.error(f"Product delete failed: {error}")
                return jsonify({"error": error}), 500
            self._invalidate_product_cache(product_id)
            self._invalidate_products_list_cache()
            return jsonify({"message": "Product deleted successfully"}), 200
        except Exception as e:
            self.logger.error(f"Delete product error: {e}")
            return jsonify({"error": "Product deletion failed"}), 500

    # --- Helpers for cache logic ---
    def _get_products_list_cache_key(self):
        return "products:all"

    def _get_products_list_from_cache(self):
        cache_key = self._get_products_list_cache_key()
        cache_exists, _ = self.cache_manager.check_key(cache_key)
        if cache_exists:
            cached = self.cache_manager.get_data(cache_key)
            try:
                return json.loads(cached)
            except Exception as e:
                self.logger.error(f"Cache decode error for '{cache_key}': {e}")
        return None

    def _set_products_list_in_cache(self, products):
        cache_key = self._get_products_list_cache_key()
        try:
            self.cache_manager.store_data(cache_key, json.dumps(products))
            self.logger.info(f"Products list cached in Redis under '{cache_key}'.")
        except Exception as e:
            self.logger.error(f"Failed to cache products list: {e}")

    def _invalidate_products_list_cache(self):
        cache_key = self._get_products_list_cache_key()
        try:
            self.cache_manager.delete_data(cache_key)
            self.logger.info(f"Cache for {cache_key} invalidated.")
        except Exception as e:
            self.logger.error(f"Failed to invalidate cache for {cache_key}: {e}")

    def _get_cache_key(self, product_id):
        return f"product:{product_id}"

    def _invalidate_product_cache(self, product_id):
        cache_key = self._get_cache_key(product_id)
        try:
            self.cache_manager.delete_data(cache_key)
            self.logger.info(f"Cache for {cache_key} invalidated.")
        except Exception as e:
            self.logger.error(f"Failed to invalidate cache for {cache_key}: {e}")

    def _get_product_from_cache(self, product_id):
        cache_key = self._get_cache_key(product_id)
        cache_exists, _ = self.cache_manager.check_key(cache_key)
        if cache_exists:
            cached = self.cache_manager.get_data(cache_key)
            try:
                return json.loads(cached)
            except Exception as e:
                self.logger.error(f"Cache decode error for '{cache_key}': {e}")
        return None

    def _set_product_in_cache(self, product_id, product_data):
        cache_key = self._get_cache_key(product_id)
        try:
            self.cache_manager.store_data(cache_key, json.dumps(product_data), time_to_live=600)
            self.logger.info(f"Product {product_id} cached in Redis under '{cache_key}'.")
        except Exception as e:
            self.logger.error(f"Failed to cache product {product_id}: {e}")


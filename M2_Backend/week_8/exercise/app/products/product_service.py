import json

class ProductService:
    def __init__(self, product_repository, cache_manager, logger):
        self.product_repository = product_repository
        self.cache_manager = cache_manager
        self.logger = logger

    def get_product_by_id(self, product_id):
        """
        Return a product by its ID, using cache if available.
        """
        product = self._get_product_from_cache(product_id)
        if product is not None:
            return product
        result = self.product_repository.get_by_id(product_id)
        if result:
            self._set_product_in_cache(product_id, result)
        return result

    def get_all_products(self):
        """
        Return a list of all products, using cache if available.
        """
        products = self._get_products_list_from_cache()
        if products is not None:
            return products
        products = self.product_repository.get_all()
        if products:
            self._set_products_list_in_cache(products)
        return products

    def create_product(self, name, price, quantity, entry_date):
        """
        Create a new product and update cache.
        """
        product_id = self.product_repository.create_product(
            name=name,
            price=price,
            quantity=quantity,
            entry_date=entry_date
        )
        if product_id:
            self._invalidate_product_cache(product_id)
            self._invalidate_products_list_cache()
        return product_id

    def update_product(self, product_id, **data):
        """
        Update an existing product and update cache.
        """
        result = self.product_repository.update_product(product_id, **data)
        if result:
            self._invalidate_product_cache(product_id)
            self._invalidate_products_list_cache()
        return result

    def delete_product(self, product_id):
        """
        Delete a product and update cache.
        """
        success, error = self.product_repository.delete_product(product_id)
        if success:
            self._invalidate_product_cache(product_id)
            self._invalidate_products_list_cache()
        return success, error

    # --- Cache helpers ---
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
        """
        Store product list in cache.
        """
        cache_key = self._get_products_list_cache_key()
        try:
            self.cache_manager.store_data(cache_key, json.dumps(products))
            self.logger.info(f"Products list cached in Redis under '{cache_key}'.")
        except Exception as e:
            self.logger.error(f"Failed to cache products list: {e}")

    def _invalidate_products_list_cache(self):
        """
        Remove product list from cache.
        """
        cache_key = self._get_products_list_cache_key()
        try:
            self.cache_manager.delete_data(cache_key)
            self.logger.info(f"Cache for {cache_key} invalidated.")
        except Exception as e:
            self.logger.error(f"Failed to invalidate cache for {cache_key}: {e}")

    def _get_cache_key(self, product_id):
        return f"product:{product_id}"

    def _invalidate_product_cache(self, product_id):
        """
        Remove a specific product from cache.
        """
        cache_key = self._get_cache_key(product_id)
        try:
            self.cache_manager.delete_data(cache_key)
            self.logger.info(f"Cache for {cache_key} invalidated.")
        except Exception as e:
            self.logger.error(f"Failed to invalidate cache for {cache_key}: {e}")

    def _get_product_from_cache(self, product_id):
        """
        Get a product from cache if exists.
        """
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
        """
        Store a product in cache.
        """
        cache_key = self._get_cache_key(product_id)
        try:
            self.cache_manager.store_data(cache_key, json.dumps(product_data), time_to_live=600)
            self.logger.info(f"Product {product_id} cached in Redis under '{cache_key}'.")
        except Exception as e:
            self.logger.error(f"Failed to cache product {product_id}: {e}")

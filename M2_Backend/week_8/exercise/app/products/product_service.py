
import json
from app.utilities.cache_decorators import cache_get, cache_invalidate

class ProductService:
    def __init__(self, product_repository, cache_manager, logger):
        self.product_repository = product_repository
        self.cache_manager = cache_manager
        self.logger = logger

    # --- Cache key helpers ---
    def _product_cache_key(self, product_id, *args, **kwargs):
        return f"product:{product_id}"

    def _products_list_cache_key(self, *args, **kwargs):
        return "products:all"

    # --- CRUD methods ---
    @cache_get(_product_cache_key)
    def get_product_by_id(self, product_id):
        """
        Return a product by its ID, using cache if available.
        """
        return self.product_repository.get_by_id(product_id)

    @cache_get(_products_list_cache_key)
    def get_all_products(self):
        """
        Return a list of all products, using cache if available.
        """
        return self.product_repository.get_all()

    @cache_invalidate([_product_cache_key, _products_list_cache_key])
    def create_product(self, name, price, quantity, entry_date):
        """
        Create a new product and update cache.
        """
        return self.product_repository.create_product(
            name=name,
            price=price,
            quantity=quantity,
            entry_date=entry_date
        )

    @cache_invalidate([_product_cache_key, _products_list_cache_key])
    def update_product(self, product_id, **data):
        """
        Update an existing product and update cache.
        """
        return self.product_repository.update_product(product_id, **data)

    @cache_invalidate([_product_cache_key, _products_list_cache_key])
    def delete_product(self, product_id):
        """
        Delete a product and update cache.
        """
        return self.product_repository.delete_product(product_id)

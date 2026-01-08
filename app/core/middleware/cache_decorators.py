"""
Cache decorators and utilities for get/set/invalidate cache logic.
Reusable for all modules (products, auth, sales, etc.).

Key Components:
- CacheHelper: Reusable class for schema-based caching (DRY principle)
- cache_invalidate: Decorator for automatic cache invalidation after mutations

Usage:
    from app.core.middleware.cache_decorators import CacheHelper, cache_invalidate
    
    class ProductService:
        def __init__(self):
            self.cache_helper = CacheHelper(resource_name="product", version="v1")
        
        def get_product_cached(self, product_id: int):
            return self.cache_helper.get_or_set(...)
        
        @cache_invalidate([lambda self, id, **kw: f"product:v1:{id}:admin=True"])
        def update_product(self, product_id: int, **updates):
            return self.product_repo.update(...)
"""
import json
import logging
from functools import wraps
from typing import Any, Callable, List, Optional
from app.core.cache_manager import get_cache

logger = logging.getLogger(__name__)


class CacheHelper:
    """
    Reusable helper for schema-based caching.
    Encapsulates the cache-fetch-serialize-store pattern to eliminate code duplication.
    
    Usage:
        from app.core.middleware.cache_decorators import CacheHelper
        
        class ProductService:
            def __init__(self):
                self.cache_helper = CacheHelper(
                    resource_name="product",
                    version="v1"
                )
            
            def get_product_cached(self, product_id: int, admin: bool = False):
                from app.products.schemas.product_schema import ProductResponseSchema
                
                return self.cache_helper.get_or_set(
                    cache_key=f"{product_id}:admin={admin}",
                    fetch_func=lambda: self.product_repo.get_by_id(product_id),
                    schema_class=ProductResponseSchema,
                    schema_kwargs={'include_admin_data': admin},
                    ttl=300
                )
    """
    
    def __init__(self, resource_name: str, version: str = "v1"):
        """
        Initialize cache helper for a specific resource type.
        
        Args:
            resource_name: Name of resource (e.g., "product", "user", "order")
            version: Cache version for schema compatibility (default: "v1")
        """
        self.resource_name = resource_name
        self.version = version
        self.cache = get_cache()
        self.logger = logging.getLogger(__name__)
    
    def _build_cache_key(self, key_suffix: str) -> str:
        """
        Build full cache key with resource name and version.
        
        Args:
            key_suffix: Unique identifier (e.g., "123:admin=True", "all:admin=False")
        
        Returns:
            Full cache key (e.g., "product:v1:123:admin=True")
        """
        return f"{self.resource_name}:{self.version}:{key_suffix}"
    
    def get_or_set(
        self,
        cache_key: str,
        fetch_func: Callable,
        schema_class: type,
        schema_kwargs: Optional[dict] = None,
        ttl: int = 300,
        many: bool = False
    ) -> Optional[Any]:
        """
        Get data from cache or fetch, serialize, and store.
        This is the core DRY method that replaces repetitive caching logic.
        
        Args:
            cache_key: Cache key suffix (will be prefixed with resource:version:)
            fetch_func: Function to fetch data from database (e.g., lambda: repo.get_by_id(1))
            schema_class: Marshmallow schema class for serialization
            schema_kwargs: Additional kwargs for schema instantiation (e.g., {'include_admin_data': True})
            ttl: Time to live in seconds (default: 300)
            many: Whether serializing list of objects (default: False)
        
        Returns:
            Serialized data dict or None if not found
        """
        # Build full cache key
        full_key = self._build_cache_key(cache_key)
        
        # Try cache first
        cached = self.cache.get_data(full_key)
        if cached:
            try:
                self.logger.info(f"Cache HIT: {full_key}")
                return json.loads(cached)
            except Exception as e:
                self.logger.error(f"Cache deserialization error for '{full_key}': {e}")
        
        # Cache miss - fetch from database
        self.logger.info(f"Cache MISS: {full_key}")
        data = fetch_func()
        
        if data is None:
            return None
        
        # Serialize with Marshmallow schema
        schema_kwargs = schema_kwargs or {}
        schema = schema_class(many=many, **schema_kwargs)
        serialized = schema.dump(data)
        
        # Cache the serialized data
        try:
            self.cache.store_data(
                full_key,
                json.dumps(serialized),
                time_to_live=ttl
            )
            count = len(serialized) if many else 1
            self.logger.info(f"Cached {count} item(s) under '{full_key}' (TTL: {ttl}s)")
        except Exception as e:
            self.logger.error(f"Failed to cache result for '{full_key}': {e}")
        
        return serialized
    
    def invalidate(self, *key_suffixes: str) -> None:
        """
        Invalidate multiple cache keys.
        
        Args:
            *key_suffixes: Cache key suffixes to invalidate
        
        Example:
            helper.invalidate("123:admin=True", "123:admin=False", "all:admin=True")
        """
        for suffix in key_suffixes:
            full_key = self._build_cache_key(suffix)
            try:
                deleted = self.cache.delete_data(full_key)
                if deleted:
                    self.logger.info(f"Cache invalidated: {full_key}")
                else:
                    self.logger.debug(f"Cache key not found: {full_key}")
            except Exception as e:
                self.logger.error(f"Failed to invalidate cache key '{full_key}': {e}")


# ============ CACHE INVALIDATION DECORATOR ============

def cache_invalidate(cache_key_funcs: List[Callable]):
    """
    Decorator to invalidate cache keys after a mutation method.
    
    This decorator clears specific cache entries after data modifications.
    Works properly even when caching is disabled in cache_get.
    
    Args:
        cache_key_funcs: List of functions to generate cache keys from args/kwargs
        
    Example:
        @cache_invalidate([
            lambda self, product_id, **kwargs: f"product:{product_id}",
            lambda self, product_id, **kwargs: "products:all"
        ])
        def update_product(self, product_id, **updates):
            return self.product_repo.update(product_id, updates)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            result = func(self, *args, **kwargs)
            
            # Invalidate all specified cache keys
            for key_func in cache_key_funcs:
                try:
                    cache_key = key_func(self, *args, **kwargs)
                    if hasattr(self, 'cache_manager') and self.cache_manager:
                        deleted = self.cache_manager.delete_data(cache_key)
                        if deleted:
                            self.logger.info(f"Cache invalidated: {cache_key}")
                        else:
                            self.logger.debug(f"Cache key not found or already deleted: {cache_key}")
                except Exception as e:
                    self.logger.error(f"Failed to invalidate cache: {e}")
            
            
            return result
        return wrapper
    return decorator

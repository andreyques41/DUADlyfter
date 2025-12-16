"""
Cache Helper - Reusable caching utility for schema-based caching

Eliminates code duplication and provides consistent caching behavior.
Adapted from Pet E-commerce project pattern.

Usage:
    from app.core.middleware.cache_helper import CacheHelper
    
    class ChefService:
        def __init__(self):
            self.cache_helper = CacheHelper(resource_name="chef", version="v1")
        
        def get_profile_by_id_cached(self, chef_id: int) -> Optional[dict]:
            return self.cache_helper.get_or_set(
                cache_key=f"{chef_id}",
                fetch_func=lambda: self.chef_repository.get_by_id(chef_id),
                schema_class=ChefResponseSchema,
                ttl=600
            )
"""

import json
from typing import Any, Callable, Optional, List
from app.core.cache_manager import get_cache
from config.logging import get_logger

logger = get_logger(__name__)


class CacheHelper:
    """
    Reusable helper for schema-based caching.
    
    Encapsulates the cache-fetch-serialize-store pattern to:
    - Eliminate code duplication
    - Ensure consistent caching behavior
    - Return serialized dict (not SQLAlchemy objects)
    - Prevent AttributeError when accessing cached data
    """
    
    def __init__(self, resource_name: str, version: str = "v1"):
        """
        Initialize cache helper for a specific resource type.
        
        Args:
            resource_name: Name of resource (e.g., "chef", "dish", "menu")
            version: Cache version for schema compatibility (default: "v1")
        """
        self.resource_name = resource_name
        self.version = version
        self.cache = get_cache()
    
    def _build_cache_key(self, key_suffix: str) -> str:
        """
        Build full cache key with resource name and version.
        
        Args:
            key_suffix: Unique identifier (e.g., "123", "all", "user:456")
        
        Returns:
            Full cache key (e.g., "chef:v1:123")
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
        Get data from cache or fetch, serialize with schema, and store.
        
        This is the core method that:
        1. Checks cache first
        2. On miss: fetches data, serializes with Marshmallow schema
        3. Stores serialized dict in cache
        4. Always returns dict (never SQLAlchemy objects)
        
        Args:
            cache_key: Cache key suffix (will be prefixed with resource:version:)
            fetch_func: Function to fetch data from database
                       Example: lambda: self.chef_repo.get_by_id(chef_id)
            schema_class: Marshmallow schema class for serialization
            schema_kwargs: Additional kwargs for schema instantiation
                          Example: {'include_admin_data': True}
            ttl: Time to live in seconds (default: 300)
            many: Whether serializing list of objects (default: False)
        
        Returns:
            Serialized data dict/list or None if not found
        """
        # Build full cache key
        full_key = self._build_cache_key(cache_key)
        
        # Try cache first
        cached = self.cache.get(full_key)
        if cached is not None:
            logger.debug(f"Cache HIT: {full_key}")
            return cached
        
        # Cache miss - fetch from database
        logger.debug(f"Cache MISS: {full_key}")
        data = fetch_func()
        
        if data is None:
            logger.debug(f"Data not found for key: {full_key}")
            return None
        
        # Serialize with Marshmallow schema
        schema_kwargs = schema_kwargs or {}
        schema = schema_class(many=many, **schema_kwargs)
        
        try:
            serialized = schema.dump(data)
        except Exception as e:
            logger.error(f"Schema serialization error for '{full_key}': {e}")
            return None
        
        # Cache the serialized data
        try:
            self.cache.set(full_key, serialized, ttl=ttl)
            count = len(serialized) if many else 1
            logger.info(f"Cached {count} item(s) under '{full_key}' (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Failed to cache result for '{full_key}': {e}")
        
        return serialized
    
    def invalidate(self, *key_suffixes: str) -> None:
        """
        Invalidate multiple cache keys.
        
        Args:
            *key_suffixes: Cache key suffixes to invalidate
        
        Example:
            helper.invalidate("123", "all", "user:456:all")
        """
        for suffix in key_suffixes:
            full_key = self._build_cache_key(suffix)
            try:
                deleted = self.cache.delete(full_key)
                if deleted:
                    logger.info(f"Cache invalidated: {full_key}")
                else:
                    logger.debug(f"Cache key not found: {full_key}")
            except Exception as e:
                logger.error(f"Failed to invalidate cache key '{full_key}': {e}")
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all cache keys matching a pattern.
        
        Args:
            pattern: Pattern suffix (e.g., "*", "user:*")
        
        Returns:
            Number of keys deleted
        
        Example:
            helper.invalidate_pattern("*")  # Clear all for this resource
        """
        full_pattern = self._build_cache_key(pattern)
        try:
            deleted = self.cache.delete_pattern(full_pattern)
            logger.info(f"Cache pattern invalidated: {full_pattern} ({deleted} keys)")
            return deleted
        except Exception as e:
            logger.error(f"Failed to invalidate pattern '{full_pattern}': {e}")
            return 0

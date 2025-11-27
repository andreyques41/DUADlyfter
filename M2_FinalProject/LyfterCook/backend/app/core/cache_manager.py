"""
Cache Manager using Redis

Provides centralized cache management with Redis backend.
Supports TTL, JSON serialization, and key namespacing.
"""

import json
import redis
from functools import wraps
from typing import Any, Optional, Callable
from config.settings import settings
from config.logging import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Redis-based cache manager with JSON serialization support"""
    
    def __init__(self):
        """Initialize Redis connection"""
        self.redis_client = None
        self.enabled = False
        self._connect()
    
    def _connect(self):
        """Establish connection to Redis server"""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True,  # Automatically decode bytes to strings
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            logger.info("Redis connection established successfully")
        except Exception as e:
            self.enabled = False
            logger.warning(f"Redis connection failed: {e}. Cache disabled.")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value (deserialized from JSON) or None
        """
        if not self.enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value is None:
                logger.debug(f"Cache MISS: {key}")
                return None
            
            logger.debug(f"Cache HIT: {key}")
            return json.loads(value)
        except Exception as e:
            logger.error(f"Error getting cache key '{key}': {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Store value in cache with TTL
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time-to-live in seconds (default: 1 hour)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            serialized = json.dumps(value, default=str)  # default=str handles datetime objects
            self.redis_client.setex(key, ttl, serialized)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Error setting cache key '{key}': {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key existed and was deleted, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            result = self.redis_client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting cache key '{key}': {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern
        
        Args:
            pattern: Pattern to match (e.g., 'user:*', 'dishes:chef:123:*')
            
        Returns:
            Number of keys deleted
        """
        if not self.enabled:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.debug(f"Cache DELETE PATTERN: {pattern} ({deleted} keys)")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Error deleting cache pattern '{pattern}': {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking cache key '{key}': {e}")
            return False
    
    def flush_all(self) -> bool:
        """
        Clear all cache (use with caution!)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            self.redis_client.flushdb()
            logger.warning("Cache FLUSH ALL: All keys deleted")
            return True
        except Exception as e:
            logger.error(f"Error flushing cache: {e}")
            return False
    
    def get_ttl(self, key: str) -> int:
        """
        Get remaining TTL for a key
        
        Args:
            key: Cache key
            
        Returns:
            Remaining seconds (-1 if no expiration, -2 if key doesn't exist)
        """
        if not self.enabled:
            return -2
        
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Error getting TTL for key '{key}': {e}")
            return -2


# Global cache instance
_cache_instance = None


def get_cache() -> CacheManager:
    """
    Get singleton cache manager instance
    
    Returns:
        CacheManager instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager()
    return _cache_instance


# Decorator for caching function results
def cached(key_prefix: str, ttl: int = 3600, skip_self: bool = True):
    """
    Decorator to cache function results with improved key generation.
    
    Args:
        key_prefix: Prefix for cache key (will append function args)
        ttl: Time-to-live in seconds
        skip_self: Skip 'self' parameter in cache key (default: True)
        
    Usage:
        @cached(key_prefix='user:id', ttl=600)
        def get_user_by_id(self, user_id):
            # ... database query
            return user
    
    Improvements:
        - Skips 'self' parameter to avoid instance-specific keys
        - Caches None values to prevent repeated queries for non-existent data
        - Better logging with cache key visibility
        - Handles class methods and static functions
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Skip cache if disabled
            if not cache.enabled:
                return func(*args, **kwargs)
            
            # Skip 'self' or 'cls' if it's a method
            cache_args = args
            if skip_self and args and hasattr(args[0], '__dict__'):
                # Skip first arg if it looks like an instance (has __dict__)
                cache_args = args[1:]
            elif skip_self and args and isinstance(args[0], type):
                # Skip first arg if it's a class (classmethod)
                cache_args = args[1:]
            
            # Build cache key from prefix and arguments
            args_str = ':'.join(str(arg) for arg in cache_args) if cache_args else ''
            kwargs_str = ':'.join(f"{k}={v}" for k, v in sorted(kwargs.items())) if kwargs else ''
            
            # Combine parts, removing trailing colons
            key_parts = [key_prefix, args_str, kwargs_str]
            cache_key = ':'.join(part for part in key_parts if part)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                # Handle special __NONE__ marker for cached None values
                if cached_result == "__CACHE_NONE__":
                    logger.debug(f"Cache HIT (None): {func.__name__}({cache_key})")
                    return None
                logger.debug(f"Cache HIT: {func.__name__}({cache_key})")
                return cached_result
            
            # Execute function
            logger.debug(f"Cache MISS: {func.__name__}({cache_key})")
            result = func(*args, **kwargs)
            
            # Cache result (including None to avoid repeated queries)
            if result is None:
                # Use special marker for None to distinguish from cache miss
                cache.set(cache_key, "__CACHE_NONE__", ttl)
                logger.debug(f"Result cached (None): {func.__name__}({cache_key}) - TTL: {ttl}s")
            else:
                cache.set(cache_key, result, ttl)
                logger.debug(f"Result cached: {func.__name__}({cache_key}) - TTL: {ttl}s")
            
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """
    Helper function to invalidate cache by pattern
    
    Args:
        pattern: Pattern to match and delete
        
    Usage:
        invalidate_cache('user:123:*')
    """
    cache = get_cache()
    deleted = cache.delete_pattern(pattern)
    logger.info(f"Invalidated {deleted} cache entries matching: {pattern}")
    return deleted

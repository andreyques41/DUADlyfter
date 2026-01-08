"""
Cache Configuration Module

Provides centralized Redis cache management for the application.
Similar pattern to database.py for consistency across the application.

Essential Components:
- CacheManager: Redis connection and operations wrapper
- get_cache(): Get cache instance (singleton pattern)
- close_cache(): Close cache connections on teardown
- cache_scope(): Context manager for cache operations (optional)

Usage (RECOMMENDED - Singleton Pattern):
    from app.core.cache_manager import get_cache
    
    # In services:
    class ProductService:
        def __init__(self):
            self.cache = get_cache()
            
        def get_product(self, product_id):
            cache_key = f"product:{product_id}"
            cached = self.cache.get_data(cache_key)
            if cached:
                return json.loads(cached)
            # ... fetch from database
            self.cache.store_data(cache_key, json.dumps(product))

Features:
- Connection pooling via Redis client
- Automatic reconnection on connection loss
- Consistent error handling and logging
- Singleton pattern for resource efficiency
"""

import redis
import logging
from typing import Optional
from config.settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB

# Configure module logger
logger = logging.getLogger(__name__)

# Global cache manager instance (singleton)
_cache_manager_instance: Optional['CacheManager'] = None


class CacheManager:
    """
    Redis cache manager with connection pooling and error handling.
    Provides methods for storing, retrieving, and deleting cached data.
    """
    
    def __init__(self, host: str, port: int, password: str, db: int = 0, **kwargs):
        """
        Initialize Redis cache manager.
        
        Args:
            host: Redis host address
            port: Redis port
            password: Redis password (empty string for no password)
            db: Redis database number (default: 0)
            **kwargs: Additional Redis client arguments
        """
        self.logger = logging.getLogger(__name__)
        
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                password=password if password else None,
                db=db,
                decode_responses=False,  # We'll handle decoding manually for flexibility
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
                **kwargs
            )
            
            # Test connection
            connection_status = self.redis_client.ping()
            if connection_status:
                self.logger.info(f"Redis cache connection established successfully (host={host}, port={port}, db={db})")
            else:
                self.logger.warning("Redis ping returned False - connection may be unstable")
                
        except redis.ConnectionError as e:
            self.logger.error(f"Failed to connect to Redis cache: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error initializing Redis cache: {e}")
            raise

    def store_data(self, key: str, value: str, time_to_live: Optional[int] = None) -> bool:
        """
        Store data in Redis cache.
        
        Args:
            key: Cache key
            value: Data to store (should be JSON string for complex objects)
            time_to_live: Optional TTL in seconds
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            if time_to_live is None:
                self.redis_client.set(key, value)
            else:
                self.redis_client.setex(key, time_to_live, value)
            return True
        except redis.RedisError as error:
            self.logger.error(f"Error storing data in Redis (key={key}): {error}")
            return False
        except Exception as error:
            self.logger.error(f"Unexpected error storing data in Redis (key={key}): {error}")
            return False

    def check_key(self, key: str) -> tuple[bool, Optional[int]]:
        """
        Check if a key exists in Redis and get its TTL.
        
        Args:
            key: Cache key to check
            
        Returns:
            Tuple of (exists: bool, ttl: Optional[int])
        """
        try:
            key_exists = self.redis_client.exists(key)
            if key_exists:
                ttl = self.redis_client.ttl(key)
                return True, ttl
            return False, None
        except redis.RedisError as error:
            self.logger.error(f"Error checking key in Redis (key={key}): {error}")
            return False, None
        except Exception as error:
            self.logger.error(f"Unexpected error checking key in Redis (key={key}): {error}")
            return False, None

    def get_data(self, key: str) -> Optional[str]:
        """
        Retrieve data from Redis cache.
        
        Args:
            key: Cache key to retrieve
            
        Returns:
            Cached data as string, or None if not found
        """
        try:
            output = self.redis_client.get(key)
            if output is not None:
                result = output.decode("utf-8")
                return result
            return None
        except redis.RedisError as error:
            self.logger.error(f"Error retrieving data from Redis (key={key}): {error}")
            return None
        except Exception as error:
            self.logger.error(f"Unexpected error retrieving data from Redis (key={key}): {error}")
            return None

    def delete_data(self, key: str) -> bool:
        """
        Delete a key from Redis cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            output = self.redis_client.delete(key)
            return output == 1
        except redis.RedisError as error:
            self.logger.error(f"Error deleting data from Redis (key={key}): {error}")
            return False
        except Exception as error:
            self.logger.error(f"Unexpected error deleting data from Redis (key={key}): {error}")
            return False

    def delete_data_with_pattern(self, pattern: str) -> bool:
        """
        Delete all keys matching a pattern.
        
        Args:
            pattern: Pattern to match (e.g., "products:*")
            
        Returns:
            True if operation completed, False on error
        """
        try:
            deleted_count = 0
            for key in self.redis_client.scan_iter(match=pattern):
                if self.delete_data(key):
                    deleted_count += 1
            self.logger.info(f"Deleted {deleted_count} keys matching pattern: {pattern}")
            return True
        except redis.RedisError as error:
            self.logger.error(f"Error deleting data with pattern from Redis (pattern={pattern}): {error}")
            return False
        except Exception as error:
            self.logger.error(f"Unexpected error deleting data with pattern from Redis (pattern={pattern}): {error}")
            return False
    
    def flush_all(self) -> bool:
        """
        Clear all data from the current Redis database.
        Use with caution!
        
        Returns:
            True if flushed successfully, False otherwise
        """
        try:
            self.redis_client.flushdb()
            self.logger.warning("Redis database flushed - all cache data cleared")
            return True
        except redis.RedisError as error:
            self.logger.error(f"Error flushing Redis database: {error}")
            return False
    
    def ping(self) -> bool:
        """
        Check if Redis connection is alive.
        
        Returns:
            True if connection is alive, False otherwise
        """
        try:
            return self.redis_client.ping()
        except redis.RedisError as error:
            self.logger.error(f"Redis ping failed: {error}")
            return False
    
    def close(self):
        """Close the Redis connection."""
        try:
            self.redis_client.close()
            self.logger.info("Redis cache connection closed")
        except Exception as error:
            self.logger.error(f"Error closing Redis connection: {error}")


# ============ SINGLETON PATTERN FUNCTIONS ============

def get_cache() -> CacheManager:
    """
    Get the global CacheManager instance (singleton pattern).
    Creates the instance on first call, returns existing instance on subsequent calls.
    
    This is the RECOMMENDED way to access cache in services.
    
    Returns:
        CacheManager: Global cache manager instance
        
    Example:
        from app.core.cache_manager import get_cache
        
        class ProductService:
            def __init__(self):
                self.cache = get_cache()
    """
    global _cache_manager_instance
    
    if _cache_manager_instance is None:
        logger.info("Initializing global CacheManager instance...")
        try:
            _cache_manager_instance = CacheManager(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                db=REDIS_DB
            )
            logger.info("Global CacheManager instance created successfully")
        except Exception as e:
            logger.error(f"Failed to create global CacheManager instance: {e}")
            raise
    
    return _cache_manager_instance


def close_cache(exception=None):
    """
    Close the global cache connection.
    This should be registered as a teardown function in Flask app.
    
    Args:
        exception: Optional exception that triggered teardown
        
    Usage in app/__init__.py:
        from app.core.cache_manager import close_cache
        app.teardown_appcontext(close_cache)
    """
    global _cache_manager_instance
    
    if _cache_manager_instance is not None:
        try:
            _cache_manager_instance.close()
            _cache_manager_instance = None
        except Exception as e:
            logger.error(f"Error during cache teardown: {e}")


def reset_cache_instance():
    """
    Reset the global cache instance.
    Useful for testing or when you need to reinitialize the cache.
    """
    global _cache_manager_instance
    
    if _cache_manager_instance is not None:
        try:
            _cache_manager_instance.close()
        except Exception:
            pass
        _cache_manager_instance = None
    
    logger.info("Global CacheManager instance reset")

            
            

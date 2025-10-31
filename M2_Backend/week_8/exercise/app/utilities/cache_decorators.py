"""
Cache decorators for get/set/invalidate cache logic.
Reusable for product and other modules.
"""
import json
from functools import wraps

# Decorator for caching GET methods

def cache_get(cache_key_func):
    """
    Decorator to cache the result of a GET method.
    cache_key_func: function to generate cache key from args/kwargs
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            cache_key = cache_key_func(self, *args, **kwargs)
            cache_exists, _ = self.cache_manager.check_key(cache_key)
            if cache_exists:
                cached = self.cache_manager.get_data(cache_key)
                try:
                    return json.loads(cached)
                except Exception as e:
                    self.logger.error(f"Cache decode error for '{cache_key}': {e}")
            result = func(self, *args, **kwargs)
            if result is not None:
                try:
                    self.cache_manager.store_data(cache_key, json.dumps(result))
                    self.logger.info(f"Cached result under '{cache_key}'.")
                except Exception as e:
                    self.logger.error(f"Failed to cache result for '{cache_key}': {e}")
            return result
        return wrapper
    return decorator

# Decorator for invalidating cache after create/update/delete

def cache_invalidate(cache_key_funcs):
    """
    Decorator to invalidate cache keys after a mutation method.
    cache_key_funcs: list of functions to generate cache keys from args/kwargs
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            for key_func in cache_key_funcs:
                cache_key = key_func(self, *args, **kwargs)
                try:
                    self.cache_manager.delete_data(cache_key)
                    self.logger.info(f"Cache for {cache_key} invalidated.")
                except Exception as e:
                    self.logger.error(f"Failed to invalidate cache for {cache_key}: {e}")
            return result
        return wrapper
    return decorator

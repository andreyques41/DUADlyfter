"""
Cache decorators for route-level caching

Provides decorators for caching Flask route responses.
"""

from functools import wraps
from flask import request, jsonify
from app.core.cache_manager import get_cache
from config.logging import get_logger

logger = get_logger(__name__)


def cache_response(ttl: int = 300, key_prefix: str = None):
    """
    Decorator to cache route responses
    
    Args:
        ttl: Time-to-live in seconds (default: 5 minutes)
        key_prefix: Custom key prefix (default: route path)
        
    Usage:
        @app.route('/api/chefs')
        @cache_response(ttl=600, key_prefix='public_chefs')
        def get_chefs():
            return jsonify(chefs)
    
    Note: 
        - Only caches GET requests
        - Includes query parameters in cache key
        - Does not cache authenticated requests (different users)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Only cache GET requests
            if request.method != 'GET':
                return func(*args, **kwargs)
            
            cache = get_cache()
            if not cache.enabled:
                return func(*args, **kwargs)
            
            # Build cache key
            prefix = key_prefix or request.path
            query_string = request.query_string.decode('utf-8')
            cache_key = f"route:{prefix}:{query_string}" if query_string else f"route:{prefix}"
            
            # Try to get cached response
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cached response returned for: {request.path}")
                return jsonify(cached_result), 200
            
            # Execute route and cache response
            response = func(*args, **kwargs)
            
            # Only cache successful responses (status 200)
            if hasattr(response, 'status_code') and response.status_code == 200:
                try:
                    # Extract JSON data from response
                    response_data = response.get_json()
                    cache.set(cache_key, response_data, ttl)
                    logger.debug(f"Response cached for: {request.path} (TTL: {ttl}s)")
                except Exception as e:
                    logger.warning(f"Could not cache response: {e}")
            
            return response
        return wrapper
    return decorator


def invalidate_on_modify(pattern: str):
    """
    Decorator to invalidate cache when route is called (POST/PUT/DELETE)
    
    Args:
        pattern: Cache key pattern to invalidate
        
    Usage:
        @app.route('/api/dishes', methods=['POST'])
        @invalidate_on_modify('route:/api/dishes*')
        def create_dish():
            # ... create dish
            return jsonify(dish), 201
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the route
            response = func(*args, **kwargs)
            
            # Invalidate cache after successful modification
            if hasattr(response, 'status_code') and 200 <= response.status_code < 300:
                cache = get_cache()
                if cache.enabled:
                    deleted = cache.delete_pattern(pattern)
                    logger.info(f"Cache invalidated: {pattern} ({deleted} keys)")
            
            return response
        return wrapper
    return decorator

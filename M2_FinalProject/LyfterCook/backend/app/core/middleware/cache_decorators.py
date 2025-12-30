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
            # If Redis cache is disabled, we still want to emit cache headers so
            # clients/proxies can cache responses based on TTL.
            if not cache.enabled:
                result = func(*args, **kwargs)
                if isinstance(result, tuple):
                    response_obj, status_code = result
                    try:
                        response_obj.headers['Cache-Control'] = f"public, max-age={ttl}"
                    except Exception:
                        pass
                    return response_obj, status_code
                try:
                    result.headers['Cache-Control'] = f"public, max-age={ttl}"
                except Exception:
                    pass
                return result
            
            # Build cache key
            #
            # key_prefix is treated as a *namespace*, not the full key.
            # Always include request.path so routes with path params (e.g. /public/chefs/<id>)
            # don't collide and return the wrong cached response.
            prefix = key_prefix or request.path
            path = request.path
            query_string = request.query_string.decode('utf-8')
            base_key = f"route:{prefix}:{path}"
            cache_key = f"{base_key}:{query_string}" if query_string else base_key
            
            # Try to get cached response
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache HIT for: {cache_key}")
                response = jsonify(cached_result)
                response.headers['Cache-Control'] = f"public, max-age={ttl}"
                return response, 200
            
            # Execute route and cache response
            result = func(*args, **kwargs)

            # Add cache header to successful responses. This is useful even on cache MISS,
            # because clients/proxies can still cache based on Cache-Control.
            if isinstance(result, tuple):
                response_obj, status_code = result
                try:
                    response_obj.headers['Cache-Control'] = f"public, max-age={ttl}"
                except Exception:
                    pass
                result_for_header = (response_obj, status_code)
            else:
                try:
                    result.headers['Cache-Control'] = f"public, max-age={ttl}"
                except Exception:
                    pass
                result_for_header = result
            
            # Handle both Response objects and tuples (response, status_code)
            response_data = None
            status_code = 200
            
            if isinstance(result, tuple):
                # Tuple format: (response, status_code)
                response_obj, status_code = result
                if hasattr(response_obj, 'get_json'):
                    response_data = response_obj.get_json()
            elif hasattr(result, 'status_code'):
                # Response object
                status_code = result.status_code
                if hasattr(result, 'get_json'):
                    response_data = result.get_json()
            
            # Only cache successful responses (status 200)
            if status_code == 200 and response_data is not None:
                try:
                    cache.set(cache_key, response_data, ttl)
                    logger.debug(f"Cache SET for: {cache_key} (TTL: {ttl}s)")
                except Exception as e:
                    logger.warning(f"Could not cache response: {e}")

            return result_for_header
        return wrapper
    return decorator


def invalidate_on_modify(*patterns: str):
    """
    Decorator to invalidate cache when route is called (POST/PUT/DELETE)
    
    Args:
        *patterns: One or more cache key patterns to invalidate
        
    Usage:
        @app.route('/api/dishes', methods=['POST'])
        @invalidate_on_modify('route:public:dishes:*', 'route:dishes:*')
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
                    for pattern in patterns:
                        deleted = cache.delete_pattern(pattern)
                        logger.info(f"Cache invalidated: {pattern} ({deleted} keys)")
            elif isinstance(response, tuple):
                # Handle tuple responses (jsonify_obj, status_code)
                _, status_code = response
                if 200 <= status_code < 300:
                    cache = get_cache()
                    if cache.enabled:
                        for pattern in patterns:
                            deleted = cache.delete_pattern(pattern)
                            logger.info(f"Cache invalidated: {pattern} ({deleted} keys)")
            
            return response
        return wrapper
    return decorator

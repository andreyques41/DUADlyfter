"""
Tests for cache_decorators module to improve coverage.

Focuses on uncovered edge cases:
- Disabled cache scenarios
- Error handling in cache operations
- Cache-Control header injection
- Tuple response handling
- Invalidation on modify decorator
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, jsonify
from app.core.middleware.cache_decorators import cache_response, invalidate_on_modify


class TestCacheResponseDecoratorEdgeCases:
    """Tests for cache_response decorator edge cases."""
    
    @pytest.fixture
    def app(self):
        """Create minimal Flask app for testing."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    def test_cache_response_skips_non_get_requests(self, app, client):
        """Test that cache decorator only caches GET requests."""
        mock_cache = MagicMock()
        mock_cache.enabled = True
        
        with patch('app.core.middleware.cache_decorators.get_cache', return_value=mock_cache):
            @app.route('/test', methods=['GET', 'POST'])
            @cache_response(ttl=60)
            def test_route():
                return jsonify({"data": "test"}), 200
            
            # POST request should NOT interact with cache
            response = client.post('/test')
            assert response.status_code == 200
            mock_cache.get.assert_not_called()
            mock_cache.set.assert_not_called()
    
    def test_cache_response_when_cache_disabled_adds_cache_control_header_tuple(self, app, client):
        """Test that Cache-Control header is added even when cache is disabled (tuple response)."""
        mock_cache = MagicMock()
        mock_cache.enabled = False
        
        with patch('app.core.middleware.cache_decorators.get_cache', return_value=mock_cache):
            @app.route('/test')
            @cache_response(ttl=120)
            def test_route():
                return jsonify({"data": "test"}), 200
            
            response = client.get('/test')
            assert response.status_code == 200
            assert 'Cache-Control' in response.headers
            assert response.headers['Cache-Control'] == 'public, max-age=120'
    
    def test_cache_response_when_cache_disabled_adds_cache_control_header_response(self, app, client):
        """Test that Cache-Control header is added when cache disabled (Response object)."""
        mock_cache = MagicMock()
        mock_cache.enabled = False
        
        with patch('app.core.middleware.cache_decorators.get_cache', return_value=mock_cache):
            @app.route('/test')
            @cache_response(ttl=90)
            def test_route():
                # Return Response object directly (not tuple)
                return jsonify({"data": "test"})
            
            response = client.get('/test')
            assert response.status_code == 200
            assert 'Cache-Control' in response.headers
            assert response.headers['Cache-Control'] == 'public, max-age=90'
    
    def test_cache_response_handles_exception_setting_cache_control_tuple(self, app, client):
        """Test graceful handling when Cache-Control header cannot be set (tuple)."""
        mock_cache = MagicMock()
        mock_cache.enabled = False
        
        with patch('app.core.middleware.cache_decorators.get_cache', return_value=mock_cache):
            @app.route('/test')
            @cache_response(ttl=60)
            def test_route():
                # Return a valid response but patch to simulate header setting failure
                response = jsonify({"data": "test"})
                # Simulate exception in header setting (caught by try/except in decorator)
                with patch.object(response, 'headers', new_callable=lambda: MagicMock(side_effect=Exception("Cannot set"))):
                    return response, 200
            
            # Should not crash, exception is caught
            response = client.get('/test')
            assert response.status_code == 200
    
    def test_cache_response_with_query_params_includes_in_key(self, app, client):
        """Test that query parameters are included in cache key."""
        mock_cache = MagicMock()
        mock_cache.enabled = True
        mock_cache.get.return_value = None  # Cache miss
        
        with patch('app.core.middleware.cache_decorators.get_cache', return_value=mock_cache):
            @app.route('/test')
            @cache_response(ttl=60)
            def test_route():
                return jsonify({"data": "test"}), 200
            
            response = client.get('/test?page=1&limit=10')
            assert response.status_code == 200
            
            # Verify cache key includes query parameters
            call_args = mock_cache.get.call_args
            cache_key = call_args[0][0]
            assert 'page=1' in cache_key
            assert 'limit=10' in cache_key
    
    def test_cache_response_with_custom_key_prefix(self, app, client):
        """Test that custom key_prefix is used in cache key."""
        mock_cache = MagicMock()
        mock_cache.enabled = True
        mock_cache.get.return_value = None
        
        with patch('app.core.middleware.cache_decorators.get_cache', return_value=mock_cache):
            @app.route('/test')
            @cache_response(ttl=60, key_prefix='custom_namespace')
            def test_route():
                return jsonify({"data": "test"}), 200
            
            response = client.get('/test')
            assert response.status_code == 200
            
            # Verify cache key uses custom prefix
            cache_key = mock_cache.get.call_args[0][0]
            assert 'custom_namespace' in cache_key
    
    def test_cache_response_handles_cache_hit(self, app, client):
        """Test that cached response is returned on cache hit."""
        cached_data = {"data": "cached", "from_cache": True}
        mock_cache = MagicMock()
        mock_cache.enabled = True
        mock_cache.get.return_value = cached_data
        
        with patch('app.core.middleware.cache_decorators.get_cache', return_value=mock_cache):
            @app.route('/test')
            @cache_response(ttl=60)
            def test_route():
                # This should NOT be called (cache hit)
                return jsonify({"data": "fresh"}), 200
            
            response = client.get('/test')
            assert response.status_code == 200
            assert response.json == cached_data
            assert 'Cache-Control' in response.headers
    
    def test_cache_response_only_caches_200_status(self, app, client):
        """Test that non-200 responses are not cached."""
        mock_cache = MagicMock()
        mock_cache.enabled = True
        mock_cache.get.return_value = None
        
        with patch('app.core.middleware.cache_decorators.get_cache', return_value=mock_cache):
            @app.route('/test')
            @cache_response(ttl=60)
            def test_route():
                return jsonify({"error": "Not found"}), 404
            
            response = client.get('/test')
            assert response.status_code == 404
            
            # Verify cache.set was NOT called (404 not cached)
            mock_cache.set.assert_not_called()
    
    def test_cache_response_handles_cache_set_exception(self, app, client):
        """Test graceful handling when cache.set() raises exception."""
        mock_cache = MagicMock()
        mock_cache.enabled = True
        mock_cache.get.return_value = None
        mock_cache.set.side_effect = Exception("Redis connection failed")
        
        with patch('app.core.middleware.cache_decorators.get_cache', return_value=mock_cache):
            @app.route('/test')
            @cache_response(ttl=60)
            def test_route():
                return jsonify({"data": "test"}), 200
            
            # Should not crash, just log warning
            response = client.get('/test')
            assert response.status_code == 200
            assert response.json == {"data": "test"}
    
    def test_cache_response_handles_response_without_json_data(self, app, client):
        """Test that responses without JSON data are not cached."""
        mock_cache = MagicMock()
        mock_cache.enabled = True
        mock_cache.get.return_value = None
        
        with patch('app.core.middleware.cache_decorators.get_cache', return_value=mock_cache):
            @app.route('/test')
            @cache_response(ttl=60)
            def test_route():
                # Return plain text response (no JSON)
                from flask import Response
                return Response("Plain text", status=200, mimetype='text/plain')
            
            response = client.get('/test')
            assert response.status_code == 200
            # Verify cache.set was not called (no JSON data to cache)
            mock_cache.set.assert_not_called()


class TestInvalidateOnModifyDecorator:
    """Tests for invalidate_on_modify decorator."""
    
    @pytest.fixture
    def app(self):
        """Create minimal Flask app."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    def test_invalidate_on_modify_with_tuple_response(self, app, client):
        """Test cache invalidation with tuple response (jsonify_obj, status_code)."""
        mock_cache = MagicMock()
        mock_cache.enabled = True
        mock_cache.delete_pattern.return_value = 5
        
        with patch('app.core.middleware.cache_decorators.get_cache', return_value=mock_cache):
            @app.route('/test', methods=['POST'])
            @invalidate_on_modify('route:test:*', 'route:related:*')
            def test_route():
                # Return tuple format
                return jsonify({"data": "created"}), 201
            
            response = client.post('/test')
            assert response.status_code == 201
            
            # Verify both patterns were invalidated
            assert mock_cache.delete_pattern.call_count == 2
            calls = [call[0][0] for call in mock_cache.delete_pattern.call_args_list]
            assert 'route:test:*' in calls
            assert 'route:related:*' in calls
    
    def test_invalidate_on_modify_with_response_object(self, app, client):
        """Test cache invalidation with Response object."""
        mock_cache = MagicMock()
        mock_cache.enabled = True
        mock_cache.delete_pattern.return_value = 3
        
        with patch('app.core.middleware.cache_decorators.get_cache', return_value=mock_cache):
            @app.route('/test', methods=['PUT'])
            @invalidate_on_modify('route:updated:*')
            def test_route():
                response = jsonify({"data": "updated"})
                response.status_code = 200
                return response
            
            response = client.put('/test')
            assert response.status_code == 200
            
            # Verify pattern was invalidated
            mock_cache.delete_pattern.assert_called_once_with('route:updated:*')
    
    def test_invalidate_on_modify_skips_non_success_responses_tuple(self, app, client):
        """Test that cache is NOT invalidated for non-2xx tuple responses."""
        mock_cache = MagicMock()
        mock_cache.enabled = True
        
        with patch('app.core.middleware.cache_decorators.get_cache', return_value=mock_cache):
            @app.route('/test', methods=['DELETE'])
            @invalidate_on_modify('route:test:*')
            def test_route():
                return jsonify({"error": "Not found"}), 404
            
            response = client.delete('/test')
            assert response.status_code == 404
            
            # Verify cache was NOT invalidated (404 response)
            mock_cache.delete_pattern.assert_not_called()
    
    def test_invalidate_on_modify_skips_non_success_responses_response_obj(self, app, client):
        """Test that cache is NOT invalidated for non-2xx Response objects."""
        mock_cache = MagicMock()
        mock_cache.enabled = True
        
        with patch('app.core.middleware.cache_decorators.get_cache', return_value=mock_cache):
            @app.route('/test', methods=['POST'])
            @invalidate_on_modify('route:test:*')
            def test_route():
                response = jsonify({"error": "Validation failed"})
                response.status_code = 400
                return response
            
            response = client.post('/test')
            assert response.status_code == 400
            
            # Verify cache was NOT invalidated (400 response)
            mock_cache.delete_pattern.assert_not_called()
    
    def test_invalidate_on_modify_skips_when_cache_disabled(self, app, client):
        """Test that invalidation is skipped when cache is disabled."""
        mock_cache = MagicMock()
        mock_cache.enabled = False
        
        with patch('app.core.middleware.cache_decorators.get_cache', return_value=mock_cache):
            @app.route('/test', methods=['POST'])
            @invalidate_on_modify('route:test:*')
            def test_route():
                return jsonify({"data": "created"}), 201
            
            response = client.post('/test')
            assert response.status_code == 201
            
            # Verify delete_pattern was NOT called (cache disabled)
            mock_cache.delete_pattern.assert_not_called()
    
    def test_invalidate_on_modify_with_multiple_patterns(self, app, client):
        """Test invalidating multiple cache patterns."""
        mock_cache = MagicMock()
        mock_cache.enabled = True
        mock_cache.delete_pattern.return_value = 10
        
        with patch('app.core.middleware.cache_decorators.get_cache', return_value=mock_cache):
            @app.route('/test', methods=['POST'])
            @invalidate_on_modify('route:dishes:*', 'route:menus:*', 'route:public:*')
            def test_route():
                return jsonify({"data": "created"}), 201
            
            response = client.post('/test')
            assert response.status_code == 201
            
            # Verify all 3 patterns were invalidated
            assert mock_cache.delete_pattern.call_count == 3

"""
API Test Helpers
~~~~~~~~~~~~~~~

Utility functions for API testing.
"""
import json
from typing import Dict, Any, Optional


def assert_status_code(response, expected_code: int, message: str = ""):
    """
    Assert response status code with helpful error message.
    
    Args:
        response: Flask response object
        expected_code: Expected HTTP status code
        message: Optional custom message
    """
    actual = response.status_code
    if actual != expected_code:
        error_msg = f"Expected {expected_code}, got {actual}"
        if message:
            error_msg = f"{message}: {error_msg}"
        if response.data:
            try:
                error_msg += f"\nResponse: {response.get_json()}"
            except:
                error_msg += f"\nResponse: {response.data.decode()}"
        raise AssertionError(error_msg)


def assert_json_contains(response, **kwargs):
    """
    Assert that response JSON contains specified key-value pairs.
    
    Usage:
        assert_json_contains(response, status='success', code=200)
    """
    data = response.get_json()
    for key, value in kwargs.items():
        assert key in data, f"Key '{key}' not in response JSON"
        assert data[key] == value, f"Expected {key}={value}, got {data[key]}"


def assert_json_has_keys(response, *keys):
    """
    Assert that response JSON has specified keys.
    
    Usage:
        assert_json_has_keys(response, 'id', 'username', 'email')
    """
    data = response.get_json()
    for key in keys:
        assert key in data, f"Key '{key}' not in response JSON: {list(data.keys())}"


def assert_json_missing_keys(response, *keys):
    """
    Assert that response JSON does NOT have specified keys (e.g., password).
    
    Usage:
        assert_json_missing_keys(response, 'password', 'password_hash')
    """
    data = response.get_json()
    for key in keys:
        assert key not in data, f"Key '{key}' should not be in response JSON"


def get_auth_headers(token: str) -> Dict[str, str]:
    """
    Generate authentication headers from JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        dict: Headers with Authorization bearer token
    """
    return {'Authorization': f'Bearer {token}'}


def post_json(client, url: str, data: Dict[str, Any], headers: Optional[Dict] = None):
    """
    Helper to POST JSON data.
    
    Args:
        client: Flask test client
        url: Endpoint URL
        data: Dictionary to send as JSON
        headers: Optional headers
    
    Returns:
        Flask response
    """
    return client.post(
        url,
        data=json.dumps(data),
        content_type='application/json',
        headers=headers or {}
    )


def put_json(client, url: str, data: Dict[str, Any], headers: Optional[Dict] = None):
    """
    Helper to PUT JSON data.
    """
    return client.put(
        url,
        data=json.dumps(data),
        content_type='application/json',
        headers=headers or {}
    )


def patch_json(client, url: str, data: Dict[str, Any], headers: Optional[Dict] = None):
    """
    Helper to PATCH JSON data.
    """
    return client.patch(
        url,
        data=json.dumps(data),
        content_type='application/json',
        headers=headers or {}
    )

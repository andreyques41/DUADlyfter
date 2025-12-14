"""
Chef Module Tests
Tests for chef list and get endpoints.
"""

import pytest
from tests.unit.test_helpers import (
    assert_success_response,
    assert_not_found_error,
    ResponseValidator
)


class TestChefList:
    """Tests for listing chefs."""
    
    def test_list_chefs_success(self, client, auth_headers, test_chef):
        """Test successful chef listing."""
        response = client.get('/chefs', headers=auth_headers)
        
        result = assert_success_response(response, 200)
        assert isinstance(result['data'], list)


class TestChefGet:
    """Tests for getting single chef."""
    
    def test_get_chef_success(self, client, auth_headers, test_chef):
        """Test successful chef retrieval."""
        response = client.get(f'/chefs/{test_chef.id}', headers=auth_headers)
        
        result = assert_success_response(response, 200)
        assert result['data']['id'] == test_chef.id
        ResponseValidator.validate_chef_response(result['data'])
    
    def test_get_chef_not_found(self, client, auth_headers):
        """Test getting non-existent chef."""
        response = client.get('/chefs/99999', headers=auth_headers)
        assert_not_found_error(response)

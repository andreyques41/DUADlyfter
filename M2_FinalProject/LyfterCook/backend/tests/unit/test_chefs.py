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
    """Tests for listing chefs via public endpoint."""
    
    def test_list_chefs_success(self, client, auth_headers, test_chef):
        """Test successful chef listing (using public endpoint)."""
        response = client.get('/public/chefs', headers=auth_headers)
        
        result = assert_success_response(response, 200)
        assert 'chefs' in result['data']
        assert isinstance(result['data']['chefs'], list)


class TestChefGet:
    """Tests for getting single chef via public endpoint."""
    
    def test_get_chef_success(self, client, auth_headers, test_chef):
        """Test successful chef retrieval (using public endpoint)."""
        response = client.get(f'/public/chefs/{test_chef.id}', headers=auth_headers)
        
        result = assert_success_response(response, 200)
        assert 'chef' in result['data']
        assert result['data']['chef']['id'] == test_chef.id
        ResponseValidator.validate_chef_response(result['data']['chef'])
    
    def test_get_chef_not_found(self, client, auth_headers):
        """Test getting non-existent chef."""
        response = client.get('/public/chefs/99999', headers=auth_headers)
        assert_not_found_error(response)

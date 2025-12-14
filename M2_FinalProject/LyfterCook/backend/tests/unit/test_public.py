"""
Public Module Tests
Tests for public endpoints (no authentication required).
"""

import pytest
from tests.unit.test_helpers import (
    assert_success_response,
    assert_error_response,
    assert_not_found_error,
    ResponseValidator
)


class TestPublicChefsList:
    """Tests for public chefs listing."""
    
    def test_list_chefs_no_auth(self, client, test_chef):
        """Test listing chefs without authentication."""
        response = client.get('/public/chefs')
        
        result = assert_success_response(response, 200)
        assert 'chefs' in result['data']
        assert isinstance(result['data']['chefs'], list)
        ResponseValidator.validate_pagination(result['data'])
    
    def test_list_chefs_with_pagination(self, client, test_chef):
        """Test chefs listing with pagination parameters."""
        response = client.get('/public/chefs?page=1&per_page=5')
        
        result = assert_success_response(response, 200)
        assert 'pagination' in result['data']
        assert result['data']['pagination']['page'] == 1
        assert result['data']['pagination']['per_page'] == 5
    
    def test_list_chefs_filter_by_specialty(self, client, test_chef):
        """Test filtering chefs by specialty."""
        response = client.get(f'/public/chefs?specialty={test_chef.specialty}')
        
        result = assert_success_response(response, 200)
        assert 'chefs' in result['data']
    
    def test_list_chefs_filter_by_location(self, client, test_chef):
        """Test filtering chefs by location."""
        response = client.get(f'/public/chefs?location={test_chef.location}')
        
        result = assert_success_response(response, 200)
        assert 'chefs' in result['data']
    
    def test_list_chefs_with_search(self, client, test_chef):
        """Test searching chefs by text."""
        response = client.get(f'/public/chefs?search=Italian')
        
        result = assert_success_response(response, 200)
        assert 'chefs' in result['data']


class TestPublicChefProfile:
    """Tests for public chef profile endpoint."""
    
    def test_get_chef_profile_success(self, client, test_chef, test_dish, test_menu):
        """Test getting chef profile with dishes and menus."""
        response = client.get(f'/public/chefs/{test_chef.id}')
        
        result = assert_success_response(response, 200)
        assert 'chef' in result['data']
        assert 'dishes' in result['data']
        assert 'menus' in result['data']
        assert 'stats' in result['data']
        assert result['data']['chef']['id'] == test_chef.id
        ResponseValidator.validate_chef_response(result['data']['chef'])
    
    def test_get_chef_profile_not_found(self, client):
        """Test getting non-existent chef profile."""
        response = client.get('/public/chefs/99999')
        assert_not_found_error(response)


class TestPublicSearch:
    """Tests for public search endpoint."""
    
    def test_search_chefs_success(self, client, test_chef):
        """Test successful chef search."""
        response = client.get(f'/public/search?q={test_chef.specialty[:4]}')
        
        result = assert_success_response(response, 200)
        assert 'chefs' in result['data']
        ResponseValidator.validate_pagination(result['data'])
    
    def test_search_minimum_query_length(self, client):
        """Test search with query too short."""
        response = client.get('/public/search?q=a')
        
        assert_error_response(response, 400)
    
    def test_search_missing_query(self, client):
        """Test search without query parameter."""
        response = client.get('/public/search')
        
        assert_error_response(response, 400)


class TestPublicFilters:
    """Tests for public filters endpoint."""
    
    def test_get_filters_success(self, client, test_chef):
        """Test getting available filters."""
        response = client.get('/public/filters')
        
        result = assert_success_response(response, 200)
        assert 'specialties' in result['data']
        assert 'locations' in result['data']
        assert isinstance(result['data']['specialties'], list)
        assert isinstance(result['data']['locations'], list)


class TestPublicMenuDetails:
    """Tests for public menu details endpoint."""
    
    def test_get_menu_details_success(self, client, test_menu, test_chef):
        """Test getting menu details with chef and dishes."""
        response = client.get(f'/public/menus/{test_menu.id}')
        
        result = assert_success_response(response, 200)
        assert 'menu' in result['data']
        assert 'chef' in result['data']
        assert 'dishes' in result['data']
        ResponseValidator.validate_menu_response(result['data']['menu'])
    
    def test_get_menu_not_found(self, client):
        """Test getting non-existent menu."""
        response = client.get('/public/menus/99999')
        assert_not_found_error(response)


class TestPublicDishDetails:
    """Tests for public dish details endpoint."""
    
    def test_get_dish_details_success(self, client, test_dish, test_chef):
        """Test getting dish details with chef info."""
        response = client.get(f'/public/dishes/{test_dish.id}')
        
        result = assert_success_response(response, 200)
        assert 'dish' in result['data']
        assert 'chef' in result['data']
        ResponseValidator.validate_dish_response(result['data']['dish'])
        ResponseValidator.validate_chef_response(result['data']['chef'])
    
    def test_get_dish_not_found(self, client):
        """Test getting non-existent dish."""
        response = client.get('/public/dishes/99999')
        assert_not_found_error(response)

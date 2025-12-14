"""
Menu Module Tests
Tests for menu CRUD endpoints and dish associations.
"""

import pytest
from tests.unit.test_helpers import (
    assert_success_response,
    assert_not_found_error,
    assert_validation_error,
    ResponseValidator
)


class TestMenuCreate:
    """Tests for creating menus."""
    
    def test_create_menu_success(self, client, chef_headers, test_chef, sample_menu_data):
        """Test successful menu creation."""
        response = client.post('/menus', json=sample_menu_data, headers=chef_headers)
        
        result = assert_success_response(response, 201)
        assert result['data']['name'] == sample_menu_data['name']
        ResponseValidator.validate_menu_response(result['data'])
    
    def test_create_menu_missing_fields(self, client, chef_headers):
        """Test menu creation with missing required fields."""
        data = {
            'name': 'Incomplete Menu'
            # Missing required fields
        }
        
        response = client.post('/menus', json=data, headers=chef_headers)
        assert_validation_error(response)


class TestMenuList:
    """Tests for listing menus."""
    
    def test_list_menus_success(self, client, chef_headers, test_menu):
        """Test successful menu listing."""
        response = client.get('/menus', headers=chef_headers)
        
        result = assert_success_response(response, 200)
        assert isinstance(result['data'], list)
    
    def test_list_menus_by_chef(self, client, chef_headers, test_chef, test_menu):
        """Test listing menus filtered by chef."""
        response = client.get(f'/menus?chef_id={test_chef.id}', headers=chef_headers)
        
        result = assert_success_response(response, 200)
        assert isinstance(result['data'], list)


class TestMenuGet:
    """Tests for getting single menu."""
    
    def test_get_menu_success(self, client, chef_headers, test_menu):
        """Test successful menu retrieval."""
        response = client.get(f'/menus/{test_menu.id}', headers=chef_headers)
        
        result = assert_success_response(response, 200)
        assert result['data']['id'] == test_menu.id
        assert result['data']['name'] == test_menu.name
        ResponseValidator.validate_menu_response(result['data'])
    



class TestMenuUpdate:
    """Tests for updating menus."""
    
    def test_update_menu_success(self, client, chef_headers, test_menu):
        """Test successful menu update."""
        data = {
            'name': 'Updated Menu Name'
        }
        
        response = client.put(f'/menus/{test_menu.id}', json=data, headers=chef_headers)
        
        result = assert_success_response(response, 200)
        assert result['data']['name'] == 'Updated Menu Name'
    
    def test_update_menu_status(self, client, chef_headers, test_menu):
        """Test updating menu status."""
        data = {
            'status': 'inactive'
        }
        
        response = client.put(f'/menus/{test_menu.id}', json=data, headers=chef_headers)
        
        result = assert_success_response(response, 200)
        assert result['data']['status'] == 'inactive'
    



class TestMenuDelete:
    """Tests for deleting menus."""
    
    def test_delete_menu_success(self, client, chef_headers, test_menu):
        """Test successful menu deletion."""
        response = client.delete(f'/menus/{test_menu.id}', headers=chef_headers)
        
        assert_success_response(response, 200)
    



class TestMenuDishAssociation:
    """Tests for adding/removing dishes from menus."""
    
    def test_assign_dishes_to_menu_success(self, client, chef_headers, test_menu, test_dish):
        """Test successfully assigning dishes to menu."""
        data = {
            'dishes': [
                {
                    'dish_id': test_dish.id,
                    'order_position': 1
                }
            ]
        }
        
        response = client.put(f'/menus/{test_menu.id}/dishes', 
                              json=data, 
                              headers=chef_headers)
        
        assert_success_response(response, 200)

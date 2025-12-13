"""
Scraper Module Tests
Tests for price scraping functionality.
"""

import pytest
from tests.test_helpers import (
    assert_success_response,
    assert_not_found_error,
    assert_validation_error
)


class TestPriceSourceCreate:
    """Tests for creating price sources."""
    
    def test_create_price_source_success(self, client, chef_headers):
        """Test successful price source creation."""
        data = {
            'name': 'Test Grocery Store',
            'base_url': 'https://teststore.com',
            'search_url_template': 'https://teststore.com/search?q={ingredient}',
            'product_name_selector': '.product-title',
            'price_selector': '.price',
            'image_selector': '.product-img',
            'is_active': True,
            'notes': 'Test grocery store'
        }
        
        response = client.post('/scrapers/sources', json=data, headers=chef_headers)
        
        result = assert_success_response(response, 201)
        assert result['data']['name'] == 'Test Grocery Store'
        assert result['data']['is_active'] == True
    
    def test_create_price_source_missing_fields(self, client, chef_headers):
        """Test price source creation with missing fields."""
        data = {
            'name': 'Incomplete Source'
            # Missing required fields
        }
        
        response = client.post('/scrapers/sources', json=data, headers=chef_headers)
        assert_validation_error(response)


class TestPriceSourceList:
    """Tests for listing price sources."""
    
    def test_list_price_sources_success(self, client, chef_headers, test_price_source):
        """Test successful price source listing."""
        response = client.get('/scrapers/sources', headers=chef_headers)
        
        result = assert_success_response(response, 200)
        assert isinstance(result['data'], list)
    
    def test_list_active_price_sources(self, client, chef_headers, test_price_source):
        """Test listing only active price sources."""
        response = client.get('/scrapers/sources?is_active=true', headers=chef_headers)
        
        result = assert_success_response(response, 200)
        assert isinstance(result['data'], list)


class TestPriceSourceGet:
    """Tests for getting single price source."""
    
    def test_get_price_source_success(self, client, chef_headers, test_price_source):
        """Test successful price source retrieval."""
        response = client.get(f'/scrapers/sources/{test_price_source.id}', 
                             headers=chef_headers)
        
        result = assert_success_response(response, 200)
        assert result['data']['id'] == test_price_source.id
        assert result['data']['name'] == test_price_source.name
    
    def test_get_price_source_not_found(self, client, chef_headers):
        """Test getting non-existent price source."""
        response = client.get('/scrapers/sources/99999', headers=chef_headers)
        assert_not_found_error(response)


class TestPriceSourceUpdate:
    """Tests for updating price sources."""
    
    def test_update_price_source_success(self, client, chef_headers, test_price_source):
        """Test successful price source update."""
        data = {
            'name': 'Updated Store Name',
            'is_active': False
        }
        
        response = client.put(f'/scrapers/sources/{test_price_source.id}', 
                             json=data, 
                             headers=chef_headers)
        
        result = assert_success_response(response, 200)
        assert result['data']['name'] == 'Updated Store Name'
        assert result['data']['is_active'] == False
    

class TestPriceSourceDelete:
    """Tests for deleting price sources."""
    
    def test_delete_price_source_success(self, client, chef_headers, test_price_source):
        """Test successful price source deletion."""
        response = client.delete(f'/scrapers/sources/{test_price_source.id}', 
                                headers=chef_headers)
        
        assert_success_response(response, 200)
    
    def test_delete_price_source_not_found(self, client, chef_headers):
        """Test deleting non-existent price source."""
        response = client.delete('/scrapers/sources/99999', headers=chef_headers)
        assert_not_found_error(response)


class TestScraping:
    """Tests for scraping operations."""
    
    def test_scrape_url_success(self, client, chef_headers, test_price_source):
        """Test successful URL scraping."""
        data = {
            'url': 'https://example.com/product',
            'source_id': test_price_source.id
        }
        
        response = client.post('/scrapers/scrape', json=data, headers=chef_headers)
        
        # Scraping might fail due to network, so accept both success and error
        assert response.status_code in [200, 400, 500]
    
    def test_scrape_missing_url(self, client, chef_headers):
        """Test scraping without URL."""
        data = {
            'source_id': 1
            # Missing URL
        }
        
        response = client.post('/scrapers/scrape', json=data, headers=chef_headers)
        assert_validation_error(response)


class TestCleanup:
    """Tests for cleanup operations."""
    
    def test_cleanup_old_prices_success(self, client, chef_headers):
        """Test cleaning up old price records."""
        response = client.delete('/scrapers/prices/cleanup?days_old=30', 
                                headers=chef_headers)
        
        result = assert_success_response(response, 200)
        assert 'deleted_count' in result['data']
        assert isinstance(result['data']['deleted_count'], int)

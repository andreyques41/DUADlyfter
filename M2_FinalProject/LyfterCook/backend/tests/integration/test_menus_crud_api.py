"""
Integration tests for Menus CRUD API endpoints.

Tests real HTTP requests against live Flask server with Docker infrastructure.
Validates menu operations, dish assignments, and status transitions.

Prerequisites:
- Docker containers running (postgres:5433, redis:6380)
- Flask server running on localhost:5000
- Database initialized with all schemas

Run: pytest tests/integration/test_menus_crud_api.py -v
"""

import requests
import pytest
import uuid


BASE_URL = "http://localhost:5000"


class TestMenusCRUDValidation:
    """
    Sequential integration tests for Menus endpoints.
    Tests share class-scoped fixtures to maintain state across tests.
    """
    
    # Shared state across tests (class variable)
    _created_menu_id = None
    _created_dish_ids = []  # Store dish IDs for menu assignment tests
    
    @pytest.fixture(scope="class")
    def unique_suffix(self):
        """Generate unique suffix for test data to avoid conflicts."""
        return str(uuid.uuid4())[:8]
    
    @pytest.fixture(scope="class")
    def chef_token(self, unique_suffix):
        """Register, login, and create chef profile. Returns Bearer token."""
        # 1. Register
        register_data = {
            "username": f"menu_chef_{unique_suffix}",
            "email": f"menu_chef_{unique_suffix}@test.com",
            "password": "SecurePass123!",
            "role": "chef"
        }
        register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        assert register_response.status_code == 201, f"Registration failed: {register_response.text}"
        
        # 2. Login
        login_data = {
            "username": f"menu_chef_{unique_suffix}",
            "password": "SecurePass123!"
        }
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        token = login_response.json()["data"]["token"]
        
        # 3. Create chef profile (required before using menus)
        profile_data = {
            "bio": "Integration test chef for menus",
            "specialty": "Menu Testing",
            "phone": "+15551234567",
            "location": "Test City"
        }
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = requests.post(f"{BASE_URL}/chefs/profile", json=profile_data, headers=headers)
        assert profile_response.status_code == 201, f"Profile creation failed: {profile_response.text}"
        
        return token
    
    @pytest.fixture(scope="class")
    def auth_headers(self, chef_token):
        """Return authorization headers with Bearer token."""
        return {"Authorization": f"Bearer {chef_token}"}
    
    # Test 01: Create menu with basic data
    def test_01_create_menu_success(self, auth_headers, unique_suffix):
        """Test creating a menu with required fields."""
        menu_data = {
            "name": f"Test Menu {unique_suffix}",
            "description": "A comprehensive menu for testing",
            "status": "draft"
        }
        
        response = requests.post(f"{BASE_URL}/menus", json=menu_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert "data" in data
        assert data["data"]["name"] == menu_data["name"]
        assert data["data"]["description"] == menu_data["description"]
        assert data["data"]["status"] == "draft"
        assert "id" in data["data"]
        assert "chef_id" in data["data"]
        
        # Store menu ID for subsequent tests
        TestMenusCRUDValidation._created_menu_id = data["data"]["id"]
    
    # Test 02: Create menu with validation error
    def test_02_create_menu_validation_error(self, auth_headers):
        """Test creating a menu with missing required fields."""
        menu_data = {
            "name": "Incomplete Menu"
            # Missing: description
        }
        
        response = requests.post(f"{BASE_URL}/menus", json=menu_data, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert "details" in data
        assert "description" in data["details"]
    
    # Test 03: List menus
    def test_03_list_menus_success(self, auth_headers):
        """Test listing all menus for authenticated chef."""
        response = requests.get(f"{BASE_URL}/menus", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1  # At least the menu we created
        
        # Verify menu structure
        menu = data["data"][0]
        assert "id" in menu
        assert "name" in menu
        assert "description" in menu
        assert "status" in menu
        assert "dishes" in menu
    
    # Test 04: List menus with status filter
    def test_04_list_menus_draft_only(self, auth_headers):
        """Test listing menus filtered by status=draft."""
        response = requests.get(f"{BASE_URL}/menus?status=draft", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"], list)
        
        # All returned menus should be draft
        for menu in data["data"]:
            assert menu["status"] == "draft"
    
    # Test 05: Get menu by ID
    def test_05_get_menu_success(self, auth_headers):
        """Test retrieving a specific menu by ID."""
        menu_id = TestMenusCRUDValidation._created_menu_id
        assert menu_id is not None, "Menu ID not set from previous test"
        
        response = requests.get(f"{BASE_URL}/menus/{menu_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["id"] == menu_id
        assert "name" in data["data"]
        assert "dishes" in data["data"]  # Menu should include dishes array
        assert isinstance(data["data"]["dishes"], list)
    
    # Test 06: Test caching for menu GET
    def test_06_get_menu_caching(self, auth_headers):
        """Test that second GET request uses cache."""
        menu_id = TestMenusCRUDValidation._created_menu_id
        
        # First request (should cache)
        response1 = requests.get(f"{BASE_URL}/menus/{menu_id}", headers=auth_headers)
        assert response1.status_code == 200
        
        # Second request (should use cache)
        response2 = requests.get(f"{BASE_URL}/menus/{menu_id}", headers=auth_headers)
        assert response2.status_code == 200
        
        # Both should return same data
        assert response1.json()["data"] == response2.json()["data"]
    
    # Test 07: Get non-existent menu
    def test_07_get_menu_not_found(self, auth_headers):
        """Test 404 response for non-existent menu."""
        response = requests.get(f"{BASE_URL}/menus/999999", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
    
    # Test 08: Update menu basic fields
    def test_08_update_menu_success(self, auth_headers):
        """Test updating menu name and description."""
        menu_id = TestMenusCRUDValidation._created_menu_id
        
        update_data = {
            "name": "Updated Menu Name",
            "description": "Updated description via integration test"
        }
        
        response = requests.put(f"{BASE_URL}/menus/{menu_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == update_data["name"]
        assert data["data"]["description"] == update_data["description"]
    
    # Test 09: Create dishes for menu assignment tests
    def test_09_create_dishes_for_menu(self, auth_headers, unique_suffix):
        """Create sample dishes to assign to menu."""
        dishes = [
            {
                "name": f"Dish 1 for Menu {unique_suffix}",
                "description": "First dish",
                "price": "25.00",
                "category": "Main Course",
                "prep_time": 30,
                "servings": 2
            },
            {
                "name": f"Dish 2 for Menu {unique_suffix}",
                "description": "Second dish",
                "price": "35.00",
                "category": "Dessert",
                "prep_time": 20,
                "servings": 4
            },
            {
                "name": f"Dish 3 for Menu {unique_suffix}",
                "description": "Third dish",
                "price": "30.00",
                "category": "Appetizer",
                "prep_time": 15,
                "servings": 3
            }
        ]
        
        for dish_data in dishes:
            response = requests.post(f"{BASE_URL}/dishes", json=dish_data, headers=auth_headers)
            assert response.status_code == 201
            dish_id = response.json()["data"]["id"]
            TestMenusCRUDValidation._created_dish_ids.append(dish_id)
        
        assert len(TestMenusCRUDValidation._created_dish_ids) == 3
    
    # Test 10: Assign dishes to menu
    def test_10_assign_dishes_to_menu(self, auth_headers):
        """Test assigning dishes to menu via PUT /menus/:id/dishes."""
        menu_id = TestMenusCRUDValidation._created_menu_id
        dish_ids = TestMenusCRUDValidation._created_dish_ids
        assert len(dish_ids) >= 2, "Need at least 2 dishes for this test"
        
        # Assign first 2 dishes
        assign_data = {
            "dishes": [
                {"dish_id": dish_ids[0], "order_position": 0},
                {"dish_id": dish_ids[1], "order_position": 1}
            ]
        }
        
        response = requests.put(f"{BASE_URL}/menus/{menu_id}/dishes", json=assign_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        
        # Verify by fetching menu again
        get_response = requests.get(f"{BASE_URL}/menus/{menu_id}", headers=auth_headers)
        assert get_response.status_code == 200
        menu_data = get_response.json()["data"]
        assert len(menu_data["dishes"]) == 2
        returned_dish_ids = [d["dish"]["id"] for d in menu_data["dishes"]]
        assert dish_ids[0] in returned_dish_ids
        assert dish_ids[1] in returned_dish_ids
    
    # Test 11: Update dish assignment (replace with different dishes)
    def test_11_update_dish_assignment(self, auth_headers):
        """Test updating menu to have different dishes."""
        menu_id = TestMenusCRUDValidation._created_menu_id
        dish_ids = TestMenusCRUDValidation._created_dish_ids
        
        # Now assign all 3 dishes
        assign_data = {
            "dishes": [
                {"dish_id": dish_ids[0], "order_position": 0},
                {"dish_id": dish_ids[1], "order_position": 1},
                {"dish_id": dish_ids[2], "order_position": 2}
            ]
        }
        
        response = requests.put(f"{BASE_URL}/menus/{menu_id}/dishes", json=assign_data, headers=auth_headers)
        assert response.status_code == 200
        
        # Verify
        get_response = requests.get(f"{BASE_URL}/menus/{menu_id}", headers=auth_headers)
        menu_data = get_response.json()["data"]
        assert len(menu_data["dishes"]) == 3
    
    # Test 12: Update menu status to published
    def test_12_update_menu_status_published(self, auth_headers):
        """Test updating menu status from draft to published."""
        menu_id = TestMenusCRUDValidation._created_menu_id
        
        update_data = {
            "status": "published"
        }
        
        response = requests.put(f"{BASE_URL}/menus/{menu_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "published"
    
    # Test 13: Update menu status to archived
    def test_13_update_menu_status_archived(self, auth_headers):
        """Test updating menu status from published to archived."""
        menu_id = TestMenusCRUDValidation._created_menu_id
        
        update_data = {
            "status": "archived"
        }
        
        response = requests.put(f"{BASE_URL}/menus/{menu_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "archived"
    
    # Test 14: Update non-existent menu
    def test_14_update_menu_not_found(self, auth_headers):
        """Test 404 response when updating non-existent menu."""
        update_data = {
            "name": "Updated Name"
        }
        
        response = requests.put(f"{BASE_URL}/menus/999999", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
    
    # Test 15: Delete menu
    def test_15_delete_menu_success(self, auth_headers):
        """Test deleting a menu."""
        menu_id = TestMenusCRUDValidation._created_menu_id
        
        response = requests.delete(f"{BASE_URL}/menus/{menu_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "data" in data
    
    # Test 16: Get deleted menu returns 404
    def test_16_get_deleted_menu_returns_404(self, auth_headers):
        """Test that accessing deleted menu returns 404."""
        menu_id = TestMenusCRUDValidation._created_menu_id
        
        response = requests.get(f"{BASE_URL}/menus/{menu_id}", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
    
    # Test 17: Delete non-existent menu
    def test_17_delete_menu_not_found(self, auth_headers):
        """Test 404 response when deleting non-existent menu."""
        response = requests.delete(f"{BASE_URL}/menus/999999", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
    
    # Test 18: Unauthenticated request
    def test_18_unauthenticated_request_returns_401(self):
        """Test that requests without auth token return 401."""
        response = requests.get(f"{BASE_URL}/menus")
        
        assert response.status_code == 401
        data = response.json()
        assert data["status"] == "error"

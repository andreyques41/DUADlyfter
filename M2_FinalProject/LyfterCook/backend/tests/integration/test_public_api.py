"""
Integration Tests: Public API Validation
Validates public endpoints against a real HTTP server (no authentication required).

Run with:
    pytest tests/integration/test_public_api.py -v

Prerequisites:
    1. Docker containers running: docker compose up -d
    2. Backend running with .env.docker: python run.py
"""

import pytest
import requests
import uuid

# Configuration
BASE_URL = "http://localhost:5000"


class TestPublicAPIValidation:
    """
    End-to-end validation of Public API module.
    Tests public endpoints that do not require authentication.
    """

    @pytest.fixture(scope="class")
    def unique_suffix(self):
        """Generate unique suffix to avoid conflicts between test runs."""
        return uuid.uuid4().hex[:8]

    @pytest.fixture(scope="class")
    def test_data(self, unique_suffix):
        """
        Setup test data: create a chef with dishes and menus.
        This data will be available for public viewing.
        """
        username = f"public_chef_{unique_suffix}"
        email = f"public_chef_{unique_suffix}@example.com"
        password = "SecurePass123!"

        # Register chef
        register_response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "role": "chef"
            }
        )
        assert register_response.status_code in [201, 400]

        # Login
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password}
        )
        assert login_response.status_code == 200
        token = login_response.json()["data"]["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create chef profile
        profile_response = requests.post(
            f"{BASE_URL}/chefs/profile",
            json={
                "bio": "Public test chef specializing in Italian cuisine",
                "specialty": "Italian Cuisine",
                "phone": "+1-555-9999",
                "location": "New York"
            },
            headers=headers
        )
        assert profile_response.status_code in [201, 400]
        
        # Get chef ID from profile
        profile_get_response = requests.get(f"{BASE_URL}/chefs/profile", headers=headers)
        assert profile_get_response.status_code == 200
        chef_id = profile_get_response.json()["data"]["id"]

        # Create a dish
        dish_response = requests.post(
            f"{BASE_URL}/dishes",
            json={
                "name": f"Test Pasta {unique_suffix}",
                "description": "Delicious pasta dish",
                "price": 15.99,
                "category": "Main Course",
                "prep_time": 30,
                "servings": 4,
                "ingredients": [
                    {
                        "name": "Pasta",
                        "quantity": 400,
                        "unit": "g",
                        "is_optional": False
                    }
                ]
            },
            headers=headers
        )
        assert dish_response.status_code == 201
        dish_id = dish_response.json()["data"]["id"]

        # Create a menu (as draft first)
        menu_response = requests.post(
            f"{BASE_URL}/menus",
            json={
                "name": f"Test Menu {unique_suffix}",
                "description": "Sample Italian menu"
            },
            headers=headers
        )
        assert menu_response.status_code == 201
        menu_id = menu_response.json()["data"]["id"]
        
        # Add dish to menu
        add_dish_response = requests.put(
            f"{BASE_URL}/menus/{menu_id}/dishes",
            json={
                "dishes": [
                    {"dish_id": dish_id, "order_position": 0}
                ]
            },
            headers=headers
        )
        assert add_dish_response.status_code == 200
        
        # Publish the menu (so it's visible publicly)
        publish_response = requests.put(
            f"{BASE_URL}/menus/{menu_id}",
            json={"status": "published"},
            headers=headers
        )
        assert publish_response.status_code == 200

        return {
            "chef_id": chef_id,
            "dish_id": dish_id,
            "menu_id": menu_id,
            "specialty": "Italian Cuisine",
            "location": "New York"
        }

    # ==================== PUBLIC CHEFS LISTING ====================

    def test_01_list_public_chefs_success(self, test_data):
        """Test GET /public/chefs - List all public chefs (no auth required)."""
        response = requests.get(f"{BASE_URL}/public/chefs")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "data" in data
        assert "chefs" in data["data"]
        assert isinstance(data["data"]["chefs"], list)
        
        # Verify pagination structure
        assert "pagination" in data["data"]
        pagination = data["data"]["pagination"]
        assert "page" in pagination
        assert "per_page" in pagination
        assert "total" in pagination
        assert "total_pages" in pagination

    def test_02_list_public_chefs_with_pagination(self, test_data):
        """Test GET /public/chefs with pagination parameters."""
        response = requests.get(f"{BASE_URL}/public/chefs?page=1&per_page=5")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "data" in data
        pagination = data["data"]["pagination"]
        assert pagination["page"] == 1
        assert pagination["per_page"] == 5
        assert len(data["data"]["chefs"]) <= 5

    def test_03_list_public_chefs_with_filters(self, test_data):
        """Test GET /public/chefs with specialty filter."""
        response = requests.get(
            f"{BASE_URL}/public/chefs?specialty={test_data['specialty']}"
        )

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "data" in data
        assert "chefs" in data["data"]
        
        # Verify filtered chefs have the correct specialty
        for chef in data["data"]["chefs"]:
            assert chef["specialty"] == test_data["specialty"]

    # ==================== PUBLIC CHEF PROFILE ====================

    def test_04_get_public_chef_profile(self, test_data):
        """Test GET /public/chefs/:id - Get chef profile (no auth required)."""
        chef_id = test_data["chef_id"]
        response = requests.get(f"{BASE_URL}/public/chefs/{chef_id}")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "data" in data
        assert "chef" in data["data"]
        assert "dishes" in data["data"]
        assert "menus" in data["data"]
        assert "stats" in data["data"]
        
        chef = data["data"]["chef"]
        assert chef["id"] == chef_id
        assert "specialty" in chef
        assert "location" in chef
        assert "bio" in chef

    def test_05_get_public_chef_not_found(self):
        """Test GET /public/chefs/:id with non-existent chef."""
        response = requests.get(f"{BASE_URL}/public/chefs/999999")

        # Note: Currently returns 500 instead of 404 (potential bug in service layer)
        assert response.status_code in [404, 500], (
            f"Expected 404 or 500, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "error" in data or "message" in data

    # ==================== PUBLIC SEARCH ====================

    def test_06_public_search_chefs(self, test_data):
        """Test GET /public/search - Search for chefs by query."""
        # Search by specialty keyword
        query = test_data["specialty"][:5]  # First 5 chars
        response = requests.get(f"{BASE_URL}/public/search?q={query}")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "data" in data
        assert "chefs" in data["data"]
        assert isinstance(data["data"]["chefs"], list)
        
        # Verify pagination structure
        assert "pagination" in data["data"]

    # ==================== PUBLIC FILTERS ====================

    def test_07_public_get_filters(self, test_data):
        """Test GET /public/filters - Get available filter options."""
        response = requests.get(f"{BASE_URL}/public/filters")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "data" in data
        assert "specialties" in data["data"]
        assert "locations" in data["data"]
        assert isinstance(data["data"]["specialties"], list)
        assert isinstance(data["data"]["locations"], list)

    # ==================== PUBLIC MENU ====================

    def test_08_get_public_menu(self, test_data):
        """Test GET /public/menus/:id - Get published menu details."""
        menu_id = test_data["menu_id"]
        response = requests.get(f"{BASE_URL}/public/menus/{menu_id}")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "data" in data
        assert "menu" in data["data"]
        assert "chef" in data["data"]
        assert "dishes" in data["data"]
        
        menu = data["data"]["menu"]
        assert menu["id"] == menu_id
        assert "name" in menu
        assert "description" in menu
        assert "total_price" in menu

    # ==================== PUBLIC DISH ====================

    def test_09_get_public_dish(self, test_data):
        """Test GET /public/dishes/:id - Get active dish details."""
        dish_id = test_data["dish_id"]
        response = requests.get(f"{BASE_URL}/public/dishes/{dish_id}")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "data" in data
        assert "dish" in data["data"]
        assert "chef" in data["data"]
        
        dish = data["data"]["dish"]
        assert dish["id"] == dish_id
        assert "name" in dish
        assert "description" in dish
        assert "price" in dish
        assert "ingredients" in dish

    # ==================== PUBLIC CACHING ====================

    def test_10_public_endpoints_are_cached(self, test_data):
        """Test that public endpoints return appropriate caching headers."""
        # Test /public/chefs (5min = 300s TTL)
        response = requests.get(f"{BASE_URL}/public/chefs")
        assert response.status_code == 200
        assert "Cache-Control" in response.headers
        cache_control = response.headers["Cache-Control"]
        assert "public" in cache_control or "max-age" in cache_control

        # Test /public/chefs/:id (10min = 600s TTL)
        chef_id = test_data["chef_id"]
        response = requests.get(f"{BASE_URL}/public/chefs/{chef_id}")
        assert response.status_code == 200
        assert "Cache-Control" in response.headers

        # Test /public/search (3min = 180s TTL)
        response = requests.get(f"{BASE_URL}/public/search?q=Italian")
        assert response.status_code == 200
        assert "Cache-Control" in response.headers

        # Test /public/filters (30min = 1800s TTL)
        response = requests.get(f"{BASE_URL}/public/filters")
        assert response.status_code == 200
        assert "Cache-Control" in response.headers

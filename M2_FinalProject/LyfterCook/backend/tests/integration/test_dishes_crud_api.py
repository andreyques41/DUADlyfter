"""
Integration Tests: Dishes CRUD API Validation
Validates the Dishes module endpoints against a real HTTP server.

Run with:
    pytest tests/integration/test_dishes_crud_api.py -v

Prerequisites:
    1. Docker containers running: docker compose up -d
    2. Backend running with .env.docker: python run.py
"""

import pytest
import requests
import uuid
import time

# Configuration
BASE_URL = "http://localhost:5000"


class TestDishesCRUDValidation:
    """
    End-to-end validation of Dishes module.
    Tests the full CRUD lifecycle against a running server.
    """

    @pytest.fixture(scope="class")
    def unique_suffix(self):
        """Generate unique suffix to avoid conflicts between test runs."""
        return uuid.uuid4().hex[:8]

    @pytest.fixture(scope="class")
    def chef_token(self, unique_suffix):
        """
        Register a new chef, login, and create chef profile.
        Scoped to class so all tests share the same chef.
        """
        username = f"chef_dishes_{unique_suffix}"
        email = f"chef_dishes_{unique_suffix}@example.com"
        password = "SecurePass123!"

        # Register
        register_response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "role": "chef"
            }
        )
        assert register_response.status_code in [201, 400], (
            f"Unexpected register status: {register_response.status_code} - {register_response.text}"
        )

        # Login
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password}
        )
        assert login_response.status_code == 200, (
            f"Login failed: {login_response.status_code} - {login_response.text}"
        )

        token = login_response.json()["data"]["token"]

        # Create chef profile
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = requests.post(
            f"{BASE_URL}/chefs/profile",
            json={
                "bio": "Integration test chef for dishes",
                "specialty": "Italian Cuisine",
                "phone": "+1-555-0101",
                "location": "Test City"
            },
            headers=headers
        )
        assert profile_response.status_code in [201, 400], (
            f"Chef profile creation failed: {profile_response.status_code} - {profile_response.text}"
        )

        return token

    @pytest.fixture(scope="class")
    def auth_headers(self, chef_token):
        """Authorization headers for authenticated requests."""
        return {"Authorization": f"Bearer {chef_token}"}

    # ==================== CREATE ====================

    def test_01_create_dish_with_ingredients(self, auth_headers, unique_suffix):
        """Test creating a dish with ingredients."""
        dish_data = {
            "name": f"Pasta Carbonara {unique_suffix}",
            "description": "Classic Italian pasta",
            "price": 18.99,
            "category": "Main Course",
            "preparation_steps": "1. Boil pasta\n2. Cook bacon\n3. Mix with eggs and cheese",
            "prep_time": 30,
            "servings": 4,
            "photo_url": "https://example.com/carbonara.jpg",
            "ingredients": [
                {
                    "name": "Spaghetti",
                    "quantity": 400,
                    "unit": "g",
                    "is_optional": False
                },
                {
                    "name": "Eggs",
                    "quantity": 4,
                    "unit": "units",
                    "is_optional": False
                },
                {
                    "name": "Bacon",
                    "quantity": 200,
                    "unit": "g",
                    "is_optional": False
                },
                {
                    "name": "Parmesan",
                    "quantity": 100,
                    "unit": "g",
                    "is_optional": True
                }
            ]
        }

        response = requests.post(
            f"{BASE_URL}/dishes",
            json=dish_data,
            headers=auth_headers
        )

        assert response.status_code == 201, (
            f"Expected 201, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "data" in data
        assert data["data"]["name"] == dish_data["name"]
        assert data["data"]["price"] == "18.99", "Price should be string with 2 decimals"
        assert "ingredients" in data["data"]
        assert len(data["data"]["ingredients"]) == 4
        
        # Verify ingredients have IDs and quantities are strings
        for ingredient in data["data"]["ingredients"]:
            assert "id" in ingredient
            if ingredient["quantity"]:
                assert isinstance(ingredient["quantity"], str), "Quantity should be string"

        # Store dish_id for subsequent tests
        TestDishesCRUDValidation._created_dish_id = data["data"]["id"]

    def test_02_create_dish_minimal_data(self, auth_headers, unique_suffix):
        """Test creating a dish with only required fields."""
        dish_data = {
            "name": f"Simple Salad {unique_suffix}",
            "description": "Fresh garden salad",
            "price": 8.50,
            "category": "Appetizer",
            "prep_time": 10,
            "servings": 2
        }

        response = requests.post(
            f"{BASE_URL}/dishes",
            json=dish_data,
            headers=auth_headers
        )

        assert response.status_code == 201, (
            f"Expected 201, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert data["data"]["name"] == dish_data["name"]
        assert data["data"]["price"] == "8.50"

    def test_03_create_dish_validation_error(self, auth_headers):
        """Test that missing required fields returns 400 with details."""
        dish_data = {
            "name": "Incomplete Dish"
            # Missing required fields
        }

        response = requests.post(
            f"{BASE_URL}/dishes",
            json=dish_data,
            headers=auth_headers
        )

        assert response.status_code == 400, (
            f"Expected 400 for validation error, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert data["status"] == "error"
        assert "details" in data

    # ==================== LIST ====================

    def test_04_list_dishes_success(self, auth_headers):
        """Test listing dishes returns created dishes."""
        response = requests.get(
            f"{BASE_URL}/dishes",
            headers=auth_headers
        )

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 2, "Should have at least 2 dishes"

    def test_05_list_dishes_active_only(self, auth_headers):
        """Test filtering dishes by active status."""
        response = requests.get(
            f"{BASE_URL}/dishes?active_only=true",
            headers=auth_headers
        )

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        # All returned dishes should be active
        for dish in data["data"]:
            assert dish["is_active"] == True

    # ==================== GET ====================

    def test_06_get_dish_success(self, auth_headers):
        """Test getting a specific dish by ID."""
        dish_id = TestDishesCRUDValidation._created_dish_id

        response = requests.get(
            f"{BASE_URL}/dishes/{dish_id}",
            headers=auth_headers
        )

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "data" in data
        assert data["data"]["id"] == dish_id
        assert "ingredients" in data["data"]

    def test_07_get_dish_caching(self, auth_headers):
        """Test that cached endpoint returns consistent results."""
        dish_id = TestDishesCRUDValidation._created_dish_id

        # First request
        response1 = requests.get(
            f"{BASE_URL}/dishes/{dish_id}",
            headers=auth_headers
        )
        assert response1.status_code == 200
        data1 = response1.json()

        # Second request (should hit cache)
        response2 = requests.get(
            f"{BASE_URL}/dishes/{dish_id}",
            headers=auth_headers
        )
        assert response2.status_code == 200
        data2 = response2.json()

        # Data should be identical
        assert data1["data"]["id"] == data2["data"]["id"]
        assert data1["data"]["name"] == data2["data"]["name"]

    def test_08_get_dish_not_found(self, auth_headers):
        """Test getting a non-existent dish returns 404."""
        response = requests.get(
            f"{BASE_URL}/dishes/999999",
            headers=auth_headers
        )

        assert response.status_code == 404, (
            f"Expected 404, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert data["status"] == "error"

    # ==================== UPDATE ====================

    def test_09_update_dish_success(self, auth_headers):
        """Test updating a dish."""
        dish_id = TestDishesCRUDValidation._created_dish_id

        update_data = {
            "description": "Updated description via integration test",
            "price": 19.99,
            "prep_time": 35
        }

        response = requests.put(
            f"{BASE_URL}/dishes/{dish_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert data["data"]["description"] == update_data["description"]
        assert data["data"]["price"] == "19.99"
        assert data["data"]["prep_time"] == update_data["prep_time"]

    def test_10_update_dish_with_ingredients(self, auth_headers):
        """Test updating dish ingredients."""
        dish_id = TestDishesCRUDValidation._created_dish_id

        update_data = {
            "ingredients": [
                {
                    "name": "Spaghetti",
                    "quantity": 500,
                    "unit": "g",
                    "is_optional": False
                },
                {
                    "name": "Eggs",
                    "quantity": 5,
                    "unit": "units",
                    "is_optional": False
                }
            ]
        }

        response = requests.put(
            f"{BASE_URL}/dishes/{dish_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        # Verify by fetching the dish again
        get_response = requests.get(
            f"{BASE_URL}/dishes/{dish_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        data = get_response.json()
        assert len(data["data"]["ingredients"]) == 2, (
            f"Expected 2 ingredients after update, got {len(data['data']['ingredients'])}"
        )

    def test_11_update_dish_toggle_active(self, auth_headers):
        """Test toggling dish active status."""
        dish_id = TestDishesCRUDValidation._created_dish_id

        # Deactivate
        response = requests.put(
            f"{BASE_URL}/dishes/{dish_id}",
            json={"is_active": False},
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["data"]["is_active"] == False

        # Reactivate
        response = requests.put(
            f"{BASE_URL}/dishes/{dish_id}",
            json={"is_active": True},
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["data"]["is_active"] == True

    def test_12_update_dish_not_found(self, auth_headers):
        """Test updating a non-existent dish returns 404."""
        response = requests.put(
            f"{BASE_URL}/dishes/999999",
            json={"description": "Should fail"},
            headers=auth_headers
        )

        assert response.status_code == 404, (
            f"Expected 404, got {response.status_code}: {response.text}"
        )

    # ==================== DELETE ====================

    def test_13_delete_dish_success(self, auth_headers):
        """Test deleting a dish."""
        dish_id = TestDishesCRUDValidation._created_dish_id

        response = requests.delete(
            f"{BASE_URL}/dishes/{dish_id}",
            headers=auth_headers
        )

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

    def test_14_get_deleted_dish_returns_404(self, auth_headers):
        """Test that getting a deleted dish returns 404."""
        dish_id = TestDishesCRUDValidation._created_dish_id

        response = requests.get(
            f"{BASE_URL}/dishes/{dish_id}",
            headers=auth_headers
        )

        assert response.status_code == 404, (
            f"Expected 404 after delete, got {response.status_code}: {response.text}"
        )

    def test_15_delete_dish_not_found(self, auth_headers):
        """Test deleting a non-existent dish returns 404."""
        response = requests.delete(
            f"{BASE_URL}/dishes/999999",
            headers=auth_headers
        )

        assert response.status_code == 404, (
            f"Expected 404, got {response.status_code}: {response.text}"
        )

    # ==================== AUTH VALIDATION ====================

    def test_16_unauthenticated_request_returns_401(self):
        """Test that requests without token return 401."""
        response = requests.get(f"{BASE_URL}/dishes")

        assert response.status_code == 401, (
            f"Expected 401 without auth, got {response.status_code}: {response.text}"
        )

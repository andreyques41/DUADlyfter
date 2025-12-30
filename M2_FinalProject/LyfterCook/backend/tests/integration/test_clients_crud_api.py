"""
Integration Tests: Clients CRUD API Validation
Validates the Clients module endpoints against a real HTTP server.

Run with:
    pytest tests/integration/test_clients_crud_api.py -v

Prerequisites:
    1. Docker containers running: docker compose up -d
    2. Backend running with .env.docker: python run.py
       (or copy .env.docker to .env and run normally)
"""

import pytest
import requests
import uuid

# Configuration
BASE_URL = "http://localhost:5000"


class TestClientsCRUDValidation:
    """
    End-to-end validation of Clients module.
    Tests the full CRUD lifecycle against a running server.
    """

    @pytest.fixture(scope="class")
    def unique_suffix(self):
        """Generate unique suffix to avoid conflicts between test runs."""
        return uuid.uuid4().hex[:8]

    @pytest.fixture(scope="class")
    def chef_token(self, unique_suffix):
        """
        Register a new chef and login to get a valid token.
        Scoped to class so all tests in this class share the same chef.
        """
        username = f"chef_validator_{unique_suffix}"
        email = f"chef_validator_{unique_suffix}@example.com"
        password = "SecurePass123!"

        # Register (ignore if already exists)
        register_response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "role": "chef"
            }
        )
        # Accept 201 (created) or 400 (already exists)
        assert register_response.status_code in [201, 400], (
            f"Unexpected register status: {register_response.status_code} - {register_response.text}"
        )

        # Login to get token
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password}
        )
        assert login_response.status_code == 200, (
            f"Login failed: {login_response.status_code} - {login_response.text}"
        )

        token = login_response.json()["data"]["token"]
        
        # Create chef profile (required before using /clients and other endpoints)
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = requests.post(
            f"{BASE_URL}/chefs/profile",
            json={
                "bio": "Integration test chef",
                "specialty": "Italian Cuisine",
                "phone": "+1-555-0100",
                "location": "Test City"
            },
            headers=headers
        )
        # Accept 201 (created) or 400 (already exists)
        assert profile_response.status_code in [201, 400], (
            f"Chef profile creation failed: {profile_response.status_code} - {profile_response.text}"
        )
        
        return token

    @pytest.fixture(scope="class")
    def auth_headers(self, chef_token):
        """Authorization headers for authenticated requests."""
        return {"Authorization": f"Bearer {chef_token}"}

    # ==================== CREATE ====================

    def test_01_create_client_success(self, auth_headers, unique_suffix):
        """Test creating a new client."""
        client_data = {
            "name": f"Test Client {unique_suffix}",
            "email": f"client_{unique_suffix}@example.com",
            "phone": "+1-555-0200",
            "company": "Test Corp",
            "notes": "Integration test client"
        }

        response = requests.post(
            f"{BASE_URL}/clients",
            json=client_data,
            headers=auth_headers
        )

        assert response.status_code == 201, (
            f"Expected 201, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "data" in data, f"Response missing 'data' key: {data}"
        assert data["data"]["name"] == client_data["name"]
        assert data["data"]["email"] == client_data["email"]
        assert "id" in data["data"]
        assert "chef_id" in data["data"]

        # Store client_id for subsequent tests
        TestClientsCRUDValidation._created_client_id = data["data"]["id"]

    def test_02_create_client_duplicate_email_fails(self, auth_headers, unique_suffix):
        """Test that creating a client with duplicate email returns 400."""
        client_data = {
            "name": "Another Client",
            "email": f"client_{unique_suffix}@example.com",  # Same email as before
            "phone": "+1-555-0201"
        }

        response = requests.post(
            f"{BASE_URL}/clients",
            json=client_data,
            headers=auth_headers
        )

        assert response.status_code == 400, (
            f"Expected 400 for duplicate email, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert data["status"] == "error"
        assert "already exists" in data["error"].lower()

    def test_03_create_client_validation_error(self, auth_headers):
        """Test that missing required fields returns 400 with details."""
        client_data = {
            "name": "Incomplete Client"
            # Missing email and phone
        }

        response = requests.post(
            f"{BASE_URL}/clients",
            json=client_data,
            headers=auth_headers
        )

        assert response.status_code == 400, (
            f"Expected 400 for validation error, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert data["status"] == "error"
        assert "details" in data, "Validation error should include 'details'"

    # ==================== LIST ====================

    def test_04_list_clients_success(self, auth_headers):
        """Test listing clients returns the created client."""
        response = requests.get(
            f"{BASE_URL}/clients",
            headers=auth_headers
        )

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1, "Should have at least 1 client"

    # ==================== GET ====================

    def test_05_get_client_success(self, auth_headers):
        """Test getting a specific client by ID."""
        client_id = TestClientsCRUDValidation._created_client_id

        response = requests.get(
            f"{BASE_URL}/clients/{client_id}",
            headers=auth_headers
        )

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "data" in data
        assert data["data"]["id"] == client_id

    def test_06_get_client_not_found(self, auth_headers):
        """Test getting a non-existent client returns 404."""
        response = requests.get(
            f"{BASE_URL}/clients/999999",
            headers=auth_headers
        )

        assert response.status_code == 404, (
            f"Expected 404, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert data["status"] == "error"

    # ==================== UPDATE ====================

    def test_07_update_client_success(self, auth_headers):
        """Test updating a client."""
        client_id = TestClientsCRUDValidation._created_client_id

        update_data = {
            "notes": "Updated via integration test",
            "company": "Updated Corp"
        }

        response = requests.put(
            f"{BASE_URL}/clients/{client_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert data["data"]["notes"] == update_data["notes"]
        assert data["data"]["company"] == update_data["company"]

    def test_08_update_client_not_found(self, auth_headers):
        """Test updating a non-existent client returns 404."""
        response = requests.put(
            f"{BASE_URL}/clients/999999",
            json={"notes": "Should fail"},
            headers=auth_headers
        )

        assert response.status_code == 404, (
            f"Expected 404, got {response.status_code}: {response.text}"
        )

    # ==================== DELETE ====================

    def test_09_delete_client_success(self, auth_headers):
        """Test deleting a client."""
        client_id = TestClientsCRUDValidation._created_client_id

        response = requests.delete(
            f"{BASE_URL}/clients/{client_id}",
            headers=auth_headers
        )

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

    def test_10_get_deleted_client_returns_404(self, auth_headers):
        """Test that getting a deleted client returns 404."""
        client_id = TestClientsCRUDValidation._created_client_id

        response = requests.get(
            f"{BASE_URL}/clients/{client_id}",
            headers=auth_headers
        )

        assert response.status_code == 404, (
            f"Expected 404 after delete, got {response.status_code}: {response.text}"
        )

    def test_11_delete_client_not_found(self, auth_headers):
        """Test deleting a non-existent client returns 404."""
        response = requests.delete(
            f"{BASE_URL}/clients/999999",
            headers=auth_headers
        )

        assert response.status_code == 404, (
            f"Expected 404, got {response.status_code}: {response.text}"
        )

    # ==================== AUTH VALIDATION ====================

    def test_12_unauthenticated_request_returns_401(self):
        """Test that requests without token return 401."""
        response = requests.get(f"{BASE_URL}/clients")

        assert response.status_code == 401, (
            f"Expected 401 without auth, got {response.status_code}: {response.text}"
        )

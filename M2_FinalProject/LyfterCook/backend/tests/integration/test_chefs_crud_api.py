"""
Integration Tests: Chefs Profile CRUD API Validation
Validates the Chefs module profile management endpoints against a real HTTP server.

Run with:
    pytest tests/integration/test_chefs_crud_api.py -v

Prerequisites:
    1. Docker containers running: docker compose up -d
    2. Backend running (http://localhost:5000)
"""

import pytest
import requests
import uuid


BASE_URL = "http://localhost:5000"


class TestChefsProfileCRUDValidation:
    """End-to-end validation of authenticated chef profile management."""

    _created_chef_id = None

    @pytest.fixture(scope="class")
    def unique_suffix(self):
        return uuid.uuid4().hex[:8]

    @pytest.fixture(scope="class")
    def chef_token_no_profile(self, unique_suffix):
        """Register + login a chef user without creating a profile."""
        username = f"chef_profile_{unique_suffix}"
        email = f"chef_profile_{unique_suffix}@example.com"
        password = "SecurePass123!"

        register_response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "role": "chef",
            },
        )
        assert register_response.status_code in [201, 400], (
            f"Unexpected register status: {register_response.status_code} - {register_response.text}"
        )

        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password},
        )
        assert login_response.status_code == 200, (
            f"Login failed: {login_response.status_code} - {login_response.text}"
        )

        return login_response.json()["data"]["token"]

    @pytest.fixture(scope="class")
    def auth_headers(self, chef_token_no_profile):
        return {"Authorization": f"Bearer {chef_token_no_profile}"}

    @pytest.fixture(scope="class")
    def other_chef_token_no_profile(self, unique_suffix):
        """Second chef user without profile (used for 404 scenarios)."""
        username = f"chef_profile_np_{unique_suffix}"
        email = f"chef_profile_np_{unique_suffix}@example.com"
        password = "SecurePass123!"

        register_response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "role": "chef",
            },
        )
        assert register_response.status_code in [201, 400], (
            f"Unexpected register status: {register_response.status_code} - {register_response.text}"
        )

        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password},
        )
        assert login_response.status_code == 200, (
            f"Login failed: {login_response.status_code} - {login_response.text}"
        )

        return login_response.json()["data"]["token"]

    # ==================== CREATE ====================

    def test_01_create_profile_success(self, auth_headers, unique_suffix):
        """POST /chefs/profile creates a profile for the authenticated chef."""
        payload = {
            "bio": "Integration test chef profile",
            "specialty": f"Chef Testing {unique_suffix}",
            "phone": "+1-555-0202",
            "location": "Test City",
        }

        response = requests.post(f"{BASE_URL}/chefs/profile", json=payload, headers=auth_headers)

        assert response.status_code == 201, (
            f"Expected 201, got {response.status_code}: {response.text}"
        )

        body = response.json()
        assert "data" in body
        data = body["data"]
        assert "id" in data
        assert data["is_active"] is True
        assert data["specialty"] == payload["specialty"]
        assert "user" in data
        assert "username" in data["user"]
        assert "email" in data["user"]

        TestChefsProfileCRUDValidation._created_chef_id = data["id"]

    def test_02_create_profile_duplicate_fails(self, auth_headers, unique_suffix):
        """POST /chefs/profile twice should return 400 (profile already exists)."""
        payload = {
            "bio": "Duplicate should fail",
            "specialty": f"Dup {unique_suffix}",
            "phone": "+1-555-0303",
            "location": "Test City",
        }

        response = requests.post(f"{BASE_URL}/chefs/profile", json=payload, headers=auth_headers)

        assert response.status_code == 400, (
            f"Expected 400, got {response.status_code}: {response.text}"
        )
        body = response.json()
        assert body.get("status") == "error"
        assert "already exists" in body.get("message", "").lower()

    # ==================== READ ====================

    def test_03_get_my_profile_success(self, auth_headers):
        """GET /chefs/profile returns the authenticated user's profile."""
        response = requests.get(f"{BASE_URL}/chefs/profile", headers=auth_headers)

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        body = response.json()
        assert "data" in body
        data = body["data"]
        assert data["id"] == TestChefsProfileCRUDValidation._created_chef_id
        assert "user" in data
        assert "username" in data["user"]

    def test_04_get_my_profile_unauthenticated_401(self):
        """GET /chefs/profile without token returns 401."""
        response = requests.get(f"{BASE_URL}/chefs/profile")
        assert response.status_code == 401
        body = response.json()
        assert body.get("status") == "error"
        assert "authorization" in body.get("message", "").lower()

    def test_05_get_my_profile_not_found_404(self, other_chef_token_no_profile):
        """GET /chefs/profile returns 404 if chef profile doesn't exist."""
        headers = {"Authorization": f"Bearer {other_chef_token_no_profile}"}
        response = requests.get(f"{BASE_URL}/chefs/profile", headers=headers)

        assert response.status_code == 404, (
            f"Expected 404, got {response.status_code}: {response.text}"
        )
        body = response.json()
        assert body.get("status") == "error"
        assert "not found" in body.get("message", "").lower()

    # ==================== UPDATE ====================

    def test_06_update_my_profile_success(self, auth_headers, unique_suffix):
        """PUT /chefs/profile updates the authenticated user's profile."""
        payload = {
            "specialty": f"Updated Specialty {unique_suffix}",
            "location": "Updated City",
        }

        response = requests.put(f"{BASE_URL}/chefs/profile", json=payload, headers=auth_headers)

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        body = response.json()
        assert "data" in body
        data = body["data"]
        assert data["id"] == TestChefsProfileCRUDValidation._created_chef_id
        assert data["specialty"] == payload["specialty"]
        assert data["location"] == payload["location"]

    def test_07_update_my_profile_validation_error(self, auth_headers):
        """PUT /chefs/profile with invalid phone returns 400 + details."""
        payload = {"phone": "NOT_A_PHONE"}

        response = requests.put(f"{BASE_URL}/chefs/profile", json=payload, headers=auth_headers)

        assert response.status_code == 400, (
            f"Expected 400, got {response.status_code}: {response.text}"
        )

        body = response.json()
        assert body.get("status") == "error"
        assert body.get("message") == "Validation failed"
        assert "details" in body
        assert "phone" in body["details"]

    def test_08_update_my_profile_not_found_404(self, other_chef_token_no_profile):
        """PUT /chefs/profile returns 404 if profile doesn't exist."""
        headers = {"Authorization": f"Bearer {other_chef_token_no_profile}"}
        payload = {"location": "Nowhere"}

        response = requests.put(f"{BASE_URL}/chefs/profile", json=payload, headers=headers)

        assert response.status_code == 404, (
            f"Expected 404, got {response.status_code}: {response.text}"
        )
        body = response.json()
        assert body.get("status") == "error"
        assert "not found" in body.get("message", "").lower()

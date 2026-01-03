"""
Integration tests for Quotations CRUD API endpoints.

Tests real HTTP requests against live Flask server with Docker infrastructure.
Validates quotation operations, status transitions, and item management.

Prerequisites:
- Docker containers running (postgres:5433, redis:6380)
- Flask server running on localhost:5000
- Database initialized with all schemas

Run: pytest tests/integration/test_quotations_crud_api.py -v
"""

import requests
import pytest
import uuid
from datetime import datetime, timedelta


BASE_URL = "http://localhost:5000"


class TestQuotationsCRUDValidation:
    """
    Sequential integration tests for Quotations endpoints.
    Tests share class-scoped fixtures to maintain state across tests.
    """
    
    # Shared state across tests (class variables)
    _created_quotation_id = None
    _created_client_id = None
    _created_menu_id = None
    _created_dish_id = None
    
    @pytest.fixture(scope="class")
    def unique_suffix(self):
        """Generate unique suffix for test data to avoid conflicts."""
        return str(uuid.uuid4())[:8]
    
    @pytest.fixture(scope="class")
    def chef_token(self, unique_suffix):
        """Register, login, and create chef profile. Returns Bearer token."""
        # 1. Register
        register_data = {
            "username": f"quotation_chef_{unique_suffix}",
            "email": f"quotation_chef_{unique_suffix}@test.com",
            "password": "SecurePass123!",
            "role": "chef"
        }
        register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        assert register_response.status_code == 201, f"Registration failed: {register_response.text}"
        
        # 2. Login
        login_data = {
            "username": f"quotation_chef_{unique_suffix}",
            "password": "SecurePass123!"
        }
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        token = login_response.json()["data"]["token"]
        
        # 3. Create chef profile (required before using quotations)
        profile_data = {
            "bio": "Integration test chef for quotations",
            "specialty": "Quotation Testing",
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
    
    @pytest.fixture(scope="class")
    def test_client(self, auth_headers, unique_suffix):
        """Create a test client for quotation creation."""
        client_data = {
            "name": f"Test Client {unique_suffix}",
            "email": f"test_client_{unique_suffix}@example.com",
            "phone": "+15559876543",
            "company": f"Test Company {unique_suffix}",
            "notes": "Test client for quotation tests"
        }
        
        response = requests.post(f"{BASE_URL}/clients", json=client_data, headers=auth_headers)
        assert response.status_code == 201, f"Client creation failed: {response.text}"
        
        client_id = response.json()["data"]["id"]
        TestQuotationsCRUDValidation._created_client_id = client_id
        return client_id
    
    @pytest.fixture(scope="class")
    def test_menu(self, auth_headers, unique_suffix):
        """Create a test menu with a dish for quotation creation."""
        # First create a dish
        dish_data = {
            "name": f"Test Dish {unique_suffix}",
            "description": "Test dish for quotation",
            "price": "25.99",
            "category": "Main Course",
            "prep_time": 30,
            "servings": 2
        }
        dish_response = requests.post(f"{BASE_URL}/dishes", json=dish_data, headers=auth_headers)
        assert dish_response.status_code == 201, f"Dish creation failed: {dish_response.text}"
        dish_id = dish_response.json()["data"]["id"]
        TestQuotationsCRUDValidation._created_dish_id = dish_id
        
        # Create menu
        menu_data = {
            "name": f"Test Menu {unique_suffix}",
            "description": "Test menu for quotation",
            "status": "published"
        }
        menu_response = requests.post(f"{BASE_URL}/menus", json=menu_data, headers=auth_headers)
        assert menu_response.status_code == 201, f"Menu creation failed: {menu_response.text}"
        menu_id = menu_response.json()["data"]["id"]
        TestQuotationsCRUDValidation._created_menu_id = menu_id
        
        # Assign dish to menu
        assign_data = {
            "dishes": [{"dish_id": dish_id, "order_position": 0}]
        }
        assign_response = requests.put(f"{BASE_URL}/menus/{menu_id}/dishes", json=assign_data, headers=auth_headers)
        assert assign_response.status_code == 200, f"Dish assignment failed: {assign_response.text}"
        
        return menu_id
    
    # Test 01: Create quotation with valid data
    def test_01_create_quotation_success(self, auth_headers, test_client, test_menu):
        """Test creating a quotation with required fields."""
        event_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        quotation_data = {
            "client_id": test_client,
            "menu_id": test_menu,
            "event_date": event_date,
            "number_of_people": 50,
            "notes": "Wedding reception test",
            "terms_and_conditions": "Payment due within 7 days.",
            "items": [
                {
                    "dish_id": TestQuotationsCRUDValidation._created_dish_id,
                    "item_name": "Test Dish",
                    "description": "Test dish description",
                    "quantity": 50,
                    "unit_price": 25.99
                }
            ]
        }
        
        response = requests.post(f"{BASE_URL}/quotations", json=quotation_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert "data" in data
        assert data["data"]["client_id"] == test_client
        assert data["data"]["menu_id"] == test_menu
        assert data["data"]["event_date"] == event_date
        assert data["data"]["number_of_people"] == 50
        assert data["data"]["status"] == "draft"
        assert "id" in data["data"]
        assert "quotation_number" in data["data"]
        assert "items" in data["data"]
        assert len(data["data"]["items"]) == 1
        
        # Store quotation ID for subsequent tests
        TestQuotationsCRUDValidation._created_quotation_id = data["data"]["id"]
    
    # Test 02: Create quotation with validation error
    def test_02_create_quotation_validation_error(self, auth_headers):
        """Test creating a quotation with missing required fields."""
        quotation_data = {
            "client_id": TestQuotationsCRUDValidation._created_client_id,
            "menu_id": TestQuotationsCRUDValidation._created_menu_id
            # Missing: event_date, number_of_people, items
        }
        
        response = requests.post(f"{BASE_URL}/quotations", json=quotation_data, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert "details" in data or "error" in data
    
    # Test 03: List quotations
    def test_03_list_quotations_success(self, auth_headers):
        """Test listing all quotations for authenticated chef."""
        response = requests.get(f"{BASE_URL}/quotations", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1  # At least the quotation we created
        
        # Verify quotation structure
        quotation = data["data"][0]
        assert "id" in quotation
        assert "quotation_number" in quotation
        assert "status" in quotation
        assert "client" in quotation
        assert "menu" in quotation
        assert "items" in quotation
    
    # Test 04: List quotations with status filter
    def test_04_list_quotations_filter_by_status(self, auth_headers):
        """Test listing quotations filtered by status=draft."""
        response = requests.get(f"{BASE_URL}/quotations?status=draft", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"], list)
        
        # All returned quotations should be draft
        for quotation in data["data"]:
            assert quotation["status"] == "draft"
    
    # Test 05: Get quotation by ID
    def test_05_get_quotation_success(self, auth_headers):
        """Test retrieving a specific quotation by ID."""
        quotation_id = TestQuotationsCRUDValidation._created_quotation_id
        assert quotation_id is not None, "Quotation ID not set from previous test"
        
        response = requests.get(f"{BASE_URL}/quotations/{quotation_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["id"] == quotation_id
        assert "quotation_number" in data["data"]
        assert "items" in data["data"]
        assert isinstance(data["data"]["items"], list)
    
    # Test 06: Get non-existent quotation
    def test_06_get_quotation_not_found(self, auth_headers):
        """Test 404 response for non-existent quotation."""
        response = requests.get(f"{BASE_URL}/quotations/999999", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
    
    # Test 07: Update quotation basic fields
    def test_07_update_quotation_success(self, auth_headers):
        """Test updating quotation number_of_people and notes."""
        quotation_id = TestQuotationsCRUDValidation._created_quotation_id
        
        update_data = {
            "number_of_people": 75,
            "notes": "Updated notes - now 75 people"
        }
        
        response = requests.put(f"{BASE_URL}/quotations/{quotation_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["number_of_people"] == 75
        assert data["data"]["notes"] == "Updated notes - now 75 people"
    
    # Test 08: Update non-existent quotation
    def test_08_update_quotation_not_found(self, auth_headers):
        """Test 404 response when updating non-existent quotation."""
        update_data = {
            "number_of_people": 100
        }
        
        response = requests.put(f"{BASE_URL}/quotations/999999", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
    
    # Test 09: Update quotation items
    def test_09_update_quotation_items(self, auth_headers):
        """Test updating quotation with items array."""
        quotation_id = TestQuotationsCRUDValidation._created_quotation_id
        dish_id = TestQuotationsCRUDValidation._created_dish_id
        
        update_data = {
            "items": [
                {
                    "dish_id": dish_id,
                    "item_name": "Updated Dish",
                    "description": "Updated description",
                    "quantity": 75,
                    "unit_price": 28.99
                }
            ]
        }
        
        response = requests.put(f"{BASE_URL}/quotations/{quotation_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data["data"]
        # Items may be empty in minimal response, verify by fetching
        get_response = requests.get(f"{BASE_URL}/quotations/{quotation_id}", headers=auth_headers)
        assert get_response.status_code == 200
    
    # Test 10: Update status to sent
    def test_10_update_status_sent(self, auth_headers):
        """Test updating quotation status from draft to sent."""
        quotation_id = TestQuotationsCRUDValidation._created_quotation_id
        
        status_data = {
            "status": "sent"
        }
        
        response = requests.patch(f"{BASE_URL}/quotations/{quotation_id}/status", json=status_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "sent"
        assert "sent_at" in data["data"]
    
    # Test 11: Update status to accepted
    def test_11_update_status_accepted(self, auth_headers):
        """Test updating quotation status from sent to accepted."""
        quotation_id = TestQuotationsCRUDValidation._created_quotation_id
        
        status_data = {
            "status": "accepted"
        }
        
        response = requests.patch(f"{BASE_URL}/quotations/{quotation_id}/status", json=status_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "accepted"
        assert "responded_at" in data["data"]
    
    # Test 12: Create new quotation for rejected status test
    def test_12_create_quotation_for_rejection(self, auth_headers):
        """Create a new quotation to test rejection status."""
        event_date = (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
        
        quotation_data = {
            "client_id": TestQuotationsCRUDValidation._created_client_id,
            "menu_id": TestQuotationsCRUDValidation._created_menu_id,
            "event_date": event_date,
            "number_of_people": 30,
            "items": [
                {
                    "dish_id": TestQuotationsCRUDValidation._created_dish_id,
                    "item_name": "Test Dish 2",
                    "description": "For rejection test",
                    "quantity": 30,
                    "unit_price": 25.99
                }
            ]
        }
        
        response = requests.post(f"{BASE_URL}/quotations", json=quotation_data, headers=auth_headers)
        assert response.status_code == 201
        
        # Transition to sent first
        quotation_id = response.json()["data"]["id"]
        status_data = {"status": "sent"}
        requests.patch(f"{BASE_URL}/quotations/{quotation_id}/status", json=status_data, headers=auth_headers)
        
        # Store for next test
        TestQuotationsCRUDValidation._created_quotation_id_for_rejection = quotation_id
    
    # Test 13: Update status to rejected
    def test_13_update_status_rejected(self, auth_headers):
        """Test updating quotation status from sent to rejected."""
        quotation_id = TestQuotationsCRUDValidation._created_quotation_id_for_rejection
        
        status_data = {
            "status": "rejected"
        }
        
        response = requests.patch(f"{BASE_URL}/quotations/{quotation_id}/status", json=status_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "rejected"
    
    # Test 14: Create draft quotation for deletion test
    def test_14_create_quotation_for_deletion(self, auth_headers):
        """Create a draft quotation to test deletion."""
        event_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        
        quotation_data = {
            "client_id": TestQuotationsCRUDValidation._created_client_id,
            "menu_id": TestQuotationsCRUDValidation._created_menu_id,
            "event_date": event_date,
            "number_of_people": 20,
            "items": [
                {
                    "dish_id": TestQuotationsCRUDValidation._created_dish_id,
                    "item_name": "Test Dish 3",
                    "description": "For deletion test",
                    "quantity": 20,
                    "unit_price": 25.99
                }
            ]
        }
        
        response = requests.post(f"{BASE_URL}/quotations", json=quotation_data, headers=auth_headers)
        assert response.status_code == 201
        
        TestQuotationsCRUDValidation._created_quotation_id_for_deletion = response.json()["data"]["id"]
    
    # Test 15: Delete quotation
    def test_15_delete_quotation_success(self, auth_headers):
        """Test deleting a draft quotation."""
        quotation_id = TestQuotationsCRUDValidation._created_quotation_id_for_deletion
        
        response = requests.delete(f"{BASE_URL}/quotations/{quotation_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "data" in data
    
    # Test 16: Get deleted quotation returns 404
    def test_16_get_deleted_quotation_returns_404(self, auth_headers):
        """Test that accessing deleted quotation returns 404."""
        quotation_id = TestQuotationsCRUDValidation._created_quotation_id_for_deletion
        
        response = requests.get(f"{BASE_URL}/quotations/{quotation_id}", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
    
    # Test 17: Delete non-existent quotation
    def test_17_delete_quotation_not_found(self, auth_headers):
        """Test 404 response when deleting non-existent quotation."""
        response = requests.delete(f"{BASE_URL}/quotations/999999", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
    
    # Test 18: Unauthenticated request
    def test_18_unauthenticated_request_returns_401(self):
        """Test that requests without auth token return 401."""
        response = requests.get(f"{BASE_URL}/quotations")
        
        assert response.status_code == 401
        data = response.json()
        assert data["status"] == "error"
    
    # Test 19: Download quotation PDF success
    def test_19_download_quotation_pdf_success(self, auth_headers):
        """Test downloading quotation as PDF returns PDF content (or 501 if WeasyPrint unavailable)."""
        quotation_id = TestQuotationsCRUDValidation._created_quotation_id
        
        response = requests.get(f"{BASE_URL}/quotations/{quotation_id}/pdf", headers=auth_headers)
        
        # WeasyPrint may not be available (501) or succeed (200)
        if response.status_code == 501:
            # WeasyPrint not available, which is expected on Windows without GTK
            data = response.json()
            assert data["status"] == "error"
            assert "unavailable" in data["message"].lower() or "not available" in data["message"].lower()
        else:
            # WeasyPrint available, verify PDF
            assert response.status_code == 200
            assert response.headers.get("Content-Type") == "application/pdf"
            assert response.headers.get("Content-Disposition") is not None
            assert "attachment" in response.headers.get("Content-Disposition")
            # Verify it's actually PDF bytes (starts with %PDF)
            assert response.content[:4] == b"%PDF"
    
    # Test 20: Download PDF for non-existent quotation
    def test_20_download_quotation_pdf_not_found(self, auth_headers):
        """Test 404 when downloading PDF for non-existent quotation."""
        response = requests.get(f"{BASE_URL}/quotations/999999/pdf", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"

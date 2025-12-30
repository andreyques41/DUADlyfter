"""
Integration tests for Appointments CRUD API endpoints.

Tests real HTTP requests against live Flask server with Docker infrastructure.
Validates appointment operations, status transitions, and scheduling.

Prerequisites:
- Docker containers running (postgres:5433, redis:6380)
- Flask server running on localhost:5000
- Database initialized with all schemas

Run: pytest tests/integration/test_appointments_crud_api.py -v
"""

import requests
import pytest
import uuid
from datetime import datetime, timedelta


BASE_URL = "http://localhost:5000"


class TestAppointmentsCRUDValidation:
    """
    Sequential integration tests for Appointments endpoints.
    Tests share class-scoped fixtures to maintain state across tests.
    """
    
    # Shared state across tests (class variables)
    _created_appointment_id = None
    _created_client_id = None
    _created_appointment_id_for_deletion = None
    
    @pytest.fixture(scope="class")
    def unique_suffix(self):
        """Generate unique suffix for test data to avoid conflicts."""
        return str(uuid.uuid4())[:8]
    
    @pytest.fixture(scope="class")
    def chef_token(self, unique_suffix):
        """Register, login, and create chef profile. Returns Bearer token."""
        # 1. Register
        register_data = {
            "username": f"appointment_chef_{unique_suffix}",
            "email": f"appointment_chef_{unique_suffix}@test.com",
            "password": "SecurePass123!",
            "role": "chef"
        }
        register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        assert register_response.status_code == 201, f"Registration failed: {register_response.text}"
        
        # 2. Login
        login_data = {
            "username": f"appointment_chef_{unique_suffix}",
            "password": "SecurePass123!"
        }
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        token = login_response.json()["data"]["token"]
        
        # 3. Create chef profile (required before using appointments)
        profile_data = {
            "bio": "Integration test chef for appointments",
            "specialty": "Appointment Testing",
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
        """Create a test client for appointment creation."""
        client_data = {
            "name": f"Test Client {unique_suffix}",
            "email": f"test_client_{unique_suffix}@example.com",
            "phone": "+15559876543",
            "company": f"Test Company {unique_suffix}",
            "notes": "Test client for appointment tests"
        }
        
        response = requests.post(f"{BASE_URL}/clients", json=client_data, headers=auth_headers)
        assert response.status_code == 201, f"Client creation failed: {response.text}"
        
        client_id = response.json()["data"]["id"]
        TestAppointmentsCRUDValidation._created_client_id = client_id
        return client_id
    
    # Test 01: Create appointment with valid data
    def test_01_create_appointment_success(self, auth_headers, test_client):
        """Test creating an appointment with required fields."""
        scheduled_at = (datetime.now() + timedelta(days=7)).isoformat()
        
        appointment_data = {
            "client_id": test_client,
            "title": "Initial Consultation",
            "description": "Discuss menu options and event details",
            "scheduled_at": scheduled_at,
            "duration_minutes": 60,
            "location": "123 Main St, Test City",
            "notes": "Client prefers morning appointments"
        }
        
        response = requests.post(f"{BASE_URL}/appointments", json=appointment_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert "data" in data
        assert data["data"]["title"] == appointment_data["title"]
        assert data["data"]["description"] == appointment_data["description"]
        assert data["data"]["duration_minutes"] == 60
        assert data["data"]["location"] == appointment_data["location"]
        assert data["data"]["status"] == "scheduled"
        assert "id" in data["data"]
        assert "chef_id" in data["data"]
        assert data["data"]["client_id"] == test_client
        
        # Store appointment ID for subsequent tests
        TestAppointmentsCRUDValidation._created_appointment_id = data["data"]["id"]
    
    # Test 02: Create appointment with validation error
    def test_02_create_appointment_validation_error(self, auth_headers):
        """Test creating an appointment with missing required fields."""
        appointment_data = {
            "client_id": TestAppointmentsCRUDValidation._created_client_id,
            "description": "Missing title and scheduled_at"
            # Missing: title, scheduled_at
        }
        
        response = requests.post(f"{BASE_URL}/appointments", json=appointment_data, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert "details" in data or "error" in data
    
    # Test 03: List appointments
    def test_03_list_appointments_success(self, auth_headers):
        """Test listing all appointments for authenticated chef."""
        response = requests.get(f"{BASE_URL}/appointments", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1  # At least the appointment we created
        
        # Verify appointment structure
        appointment = data["data"][0]
        assert "id" in appointment
        assert "title" in appointment
        assert "status" in appointment
        assert "scheduled_at" in appointment
        assert "client" in appointment or "client_id" in appointment
    
    # Test 04: List appointments with status filter
    def test_04_list_appointments_filter_by_status(self, auth_headers):
        """Test listing appointments filtered by status=scheduled."""
        response = requests.get(f"{BASE_URL}/appointments?status=scheduled", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"], list)
        
        # All returned appointments should be scheduled
        for appointment in data["data"]:
            assert appointment["status"] == "scheduled"
    
    # Test 05: Get appointment by ID
    def test_05_get_appointment_success(self, auth_headers):
        """Test retrieving a specific appointment by ID."""
        appointment_id = TestAppointmentsCRUDValidation._created_appointment_id
        assert appointment_id is not None, "Appointment ID not set from previous test"
        
        response = requests.get(f"{BASE_URL}/appointments/{appointment_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["id"] == appointment_id
        assert "title" in data["data"]
        assert "scheduled_at" in data["data"]
        assert "status" in data["data"]
    
    # Test 06: Get non-existent appointment
    def test_06_get_appointment_not_found(self, auth_headers):
        """Test 404 response for non-existent appointment."""
        response = requests.get(f"{BASE_URL}/appointments/999999", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
    
    # Test 07: Update appointment basic fields
    def test_07_update_appointment_success(self, auth_headers):
        """Test updating appointment title, location, and notes."""
        appointment_id = TestAppointmentsCRUDValidation._created_appointment_id
        
        update_data = {
            "title": "Updated Consultation",
            "location": "456 Oak Ave, Test City",
            "notes": "Updated notes - client confirmed new location"
        }
        
        response = requests.put(f"{BASE_URL}/appointments/{appointment_id}", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == "Updated Consultation"
        assert data["data"]["location"] == "456 Oak Ave, Test City"
        assert data["data"]["notes"] == "Updated notes - client confirmed new location"
    
    # Test 08: Update non-existent appointment
    def test_08_update_appointment_not_found(self, auth_headers):
        """Test 404 response when updating non-existent appointment."""
        update_data = {
            "title": "Should Not Work"
        }
        
        response = requests.put(f"{BASE_URL}/appointments/999999", json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
    
    # Test 09: Update status to confirmed
    def test_09_update_status_confirmed(self, auth_headers):
        """Test updating appointment status from scheduled to confirmed."""
        appointment_id = TestAppointmentsCRUDValidation._created_appointment_id
        
        status_data = {
            "status": "confirmed"
        }
        
        response = requests.patch(f"{BASE_URL}/appointments/{appointment_id}/status", json=status_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "confirmed"
    
    # Test 10: Update status to completed
    def test_10_update_status_completed(self, auth_headers):
        """Test updating appointment status from confirmed to completed."""
        appointment_id = TestAppointmentsCRUDValidation._created_appointment_id
        
        status_data = {
            "status": "completed"
        }
        
        response = requests.patch(f"{BASE_URL}/appointments/{appointment_id}/status", json=status_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "completed"
        assert "completed_at" in data["data"]
    
    # Test 11: Create new appointment for cancellation test
    def test_11_create_appointment_for_cancellation(self, auth_headers):
        """Create a new appointment to test cancellation status."""
        scheduled_at = (datetime.now() + timedelta(days=14)).isoformat()
        
        appointment_data = {
            "client_id": TestAppointmentsCRUDValidation._created_client_id,
            "title": "Follow-up Meeting",
            "scheduled_at": scheduled_at,
            "duration_minutes": 30
        }
        
        response = requests.post(f"{BASE_URL}/appointments", json=appointment_data, headers=auth_headers)
        assert response.status_code == 201
        
        # Store for cancellation test
        TestAppointmentsCRUDValidation._created_appointment_id_for_cancellation = response.json()["data"]["id"]
    
    # Test 12: Update status to cancelled
    def test_12_update_status_cancelled(self, auth_headers):
        """Test updating appointment status to cancelled with reason."""
        appointment_id = TestAppointmentsCRUDValidation._created_appointment_id_for_cancellation
        
        status_data = {
            "status": "cancelled",
            "cancellation_reason": "Client requested reschedule"
        }
        
        response = requests.patch(f"{BASE_URL}/appointments/{appointment_id}/status", json=status_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "cancelled"
        assert "cancelled_at" in data["data"]
        # Note: cancellation_reason might not be in response if not exposed
    
    # Test 13: Create appointment for deletion test
    def test_13_create_appointment_for_deletion(self, auth_headers):
        """Create an appointment to test deletion."""
        scheduled_at = (datetime.now() + timedelta(days=21)).isoformat()
        
        appointment_data = {
            "client_id": TestAppointmentsCRUDValidation._created_client_id,
            "title": "To Be Deleted",
            "scheduled_at": scheduled_at,
            "duration_minutes": 45
        }
        
        response = requests.post(f"{BASE_URL}/appointments", json=appointment_data, headers=auth_headers)
        assert response.status_code == 201
        
        TestAppointmentsCRUDValidation._created_appointment_id_for_deletion = response.json()["data"]["id"]
    
    # Test 14: Delete appointment
    def test_14_delete_appointment_success(self, auth_headers):
        """Test deleting an appointment."""
        appointment_id = TestAppointmentsCRUDValidation._created_appointment_id_for_deletion
        
        response = requests.delete(f"{BASE_URL}/appointments/{appointment_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data or "data" in data
    
    # Test 15: Get deleted appointment returns 404
    def test_15_get_deleted_appointment_returns_404(self, auth_headers):
        """Test that accessing deleted appointment returns 404."""
        appointment_id = TestAppointmentsCRUDValidation._created_appointment_id_for_deletion
        
        response = requests.get(f"{BASE_URL}/appointments/{appointment_id}", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
    
    # Test 16: Delete non-existent appointment
    def test_16_delete_appointment_not_found(self, auth_headers):
        """Test 404 response when deleting non-existent appointment."""
        response = requests.delete(f"{BASE_URL}/appointments/999999", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
    
    # Test 17: Unauthenticated request
    def test_17_unauthenticated_request_returns_401(self):
        """Test that requests without auth token return 401."""
        response = requests.get(f"{BASE_URL}/appointments")
        
        assert response.status_code == 401
        data = response.json()
        assert data["status"] == "error"

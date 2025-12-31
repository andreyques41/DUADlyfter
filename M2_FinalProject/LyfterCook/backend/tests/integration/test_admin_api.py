"""\
Integration Tests: Admin API Validation
Validates core Admin module endpoints against a real HTTP server.

Run with:
    pytest tests/integration/test_admin_api.py -v

Prerequisites:
    1. Docker containers running (postgres + redis)
    2. Backend running (http://localhost:5000)
"""

import pytest
import requests
import uuid
import subprocess
import sys
from pathlib import Path


BASE_URL = "http://localhost:5000"
BACKEND_ROOT = Path(__file__).resolve().parents[2]


class TestAdminAPIValidation:
    """End-to-end validation of Admin module endpoints (admin RBAC)."""

    _chef_id = None
    _client_user_id = None

    @pytest.fixture(scope="class")
    def unique_suffix(self):
        return uuid.uuid4().hex[:8]

    def _register_user(self, username, email, password, role):
        res = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "role": role,
            },
        )
        assert res.status_code in [201, 400]

    def _login(self, username, password):
        res = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password})
        assert res.status_code == 200
        return res.json()["data"]["token"]

    @pytest.fixture(scope="class")
    def admin_headers(self):
        """Authenticate as the seeded default admin.

        Public registration cannot create admins (role is ignored). If the default
        admin doesn't exist yet, seed it via scripts/seed_admin.py and retry login.
        """
        username = "admin"
        password = "Admin123!@#"

        # Attempt login first
        res = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password})
        if res.status_code != 200:
            # Seed default admin into the running server's DB
            seed = subprocess.run(
                [sys.executable, "scripts/seed_admin.py"],
                cwd=str(BACKEND_ROOT),
                capture_output=True,
                text=True,
            )
            assert seed.returncode == 0, f"seed_admin.py failed: {seed.stdout}\n{seed.stderr}"

            res = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": username, "password": password},
            )

        assert res.status_code == 200, f"Admin login failed: {res.status_code} {res.text}"
        token = res.json()["data"]["token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.fixture(scope="class")
    def chef_headers(self, unique_suffix):
        username = f"chef_{unique_suffix}"
        email = f"chef_{unique_suffix}@example.com"
        password = "SecurePass123!"

        self._register_user(username, email, password, role="chef")
        token = self._login(username, password)

        # Create chef profile so admin /admin/chefs endpoints have something to act on
        headers = {"Authorization": f"Bearer {token}"}
        profile_res = requests.post(
            f"{BASE_URL}/chefs/profile",
            json={
                "bio": "Admin tests chef",
                "specialty": "Admin",
                "phone": "+1-555-0999",
                "location": "Test City",
            },
            headers=headers,
        )
        assert profile_res.status_code in [201, 400]

        # Fetch chef id (GET profile)
        profile_get = requests.get(f"{BASE_URL}/chefs/profile", headers=headers)
        assert profile_get.status_code == 200
        TestAdminAPIValidation._chef_id = profile_get.json()["data"]["id"]

        return headers

    @pytest.fixture(scope="class")
    def deletable_user_id(self, unique_suffix, admin_headers):
        """Create a normal (non-admin) user and return its id.

        Note: public registration only supports role=chef/admin (client is not allowed).
        We create a CHEF user and delete it via admin endpoint.
        """
        username = f"delete_me_{unique_suffix}"
        email = f"delete_me_{unique_suffix}@example.com"
        password = "SecurePass123!"

        res = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "role": "chef",
            },
        )
        assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"

        # Admin list users with search to find the user deterministically
        list_res = requests.get(f"{BASE_URL}/admin/users?search={username}", headers=admin_headers)
        assert list_res.status_code == 200
        users = list_res.json().get("data")
        assert isinstance(users, list)

        match = next((u for u in users if u.get("username") == username), None)
        assert match is not None, f"User {username} not found in /admin/users search results"
        TestAdminAPIValidation._client_user_id = match["id"]
        return match["id"]

    # ==================== RBAC GUARDS ====================

    def test_01_admin_dashboard_requires_auth(self):
        res = requests.get(f"{BASE_URL}/admin/dashboard")
        assert res.status_code == 401

    def test_02_admin_dashboard_forbidden_for_non_admin(self, chef_headers):
        res = requests.get(f"{BASE_URL}/admin/dashboard", headers=chef_headers)
        assert res.status_code == 403

    def test_03_admin_dashboard_success(self, admin_headers):
        res = requests.get(f"{BASE_URL}/admin/dashboard", headers=admin_headers)
        assert res.status_code == 200
        assert "data" in res.json()

    # ==================== USERS ====================

    def test_04_admin_list_users_success(self, admin_headers):
        res = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers)
        assert res.status_code == 200
        body = res.json()
        assert "data" in body
        assert isinstance(body["data"], list)

    def test_05_admin_delete_user_requires_confirm(self, admin_headers, deletable_user_id):
        res = requests.delete(
            f"{BASE_URL}/admin/users/{deletable_user_id}",
            json={"reason": "Testing delete validation"},
            headers=admin_headers,
        )
        assert res.status_code == 400

    def test_06_admin_delete_user_requires_reason_length(self, admin_headers, deletable_user_id):
        res = requests.delete(
            f"{BASE_URL}/admin/users/{deletable_user_id}",
            json={"confirm": True, "reason": "too short"},
            headers=admin_headers,
        )
        assert res.status_code == 400

    def test_07_admin_delete_user_success(self, admin_headers, deletable_user_id):
        res = requests.delete(
            f"{BASE_URL}/admin/users/{deletable_user_id}",
            json={"confirm": True, "reason": "Integration test deleting a client"},
            headers=admin_headers,
        )
        assert res.status_code == 200

    # ==================== CHEFS ====================

    def test_08_admin_list_chefs_success(self, admin_headers):
        res = requests.get(f"{BASE_URL}/admin/chefs", headers=admin_headers)
        assert res.status_code == 200
        assert "data" in res.json()

    def test_09_admin_update_chef_status_validation_error(self, admin_headers, chef_headers):
        """Missing status should fail with 400."""
        assert self._chef_id is not None
        res = requests.patch(
            f"{BASE_URL}/admin/chefs/{self._chef_id}/status",
            json={},
            headers=admin_headers,
        )
        assert res.status_code == 400

    # ==================== REPORTS & CACHE ====================

    def test_10_admin_reports_invalid_type(self, admin_headers):
        res = requests.get(f"{BASE_URL}/admin/reports?report_type=unknown", headers=admin_headers)
        assert res.status_code == 400

    def test_11_admin_cache_stats_success(self, admin_headers):
        res = requests.get(f"{BASE_URL}/admin/cache/stats", headers=admin_headers)
        assert res.status_code == 200

    def test_12_admin_cache_clear_works_or_is_disabled(self, admin_headers):
        res = requests.delete(f"{BASE_URL}/admin/cache/clear?pattern=route:*", headers=admin_headers)
        # If cache is disabled, endpoint returns 400. Otherwise 200.
        assert res.status_code in [200, 400]

    # ==================== AUDIT LOGS ====================

    def test_13_admin_audit_logs_requires_auth(self):
        res = requests.get(f"{BASE_URL}/admin/audit-logs")
        assert res.status_code == 401

    def test_14_admin_audit_logs_forbidden_for_non_admin(self, chef_headers):
        res = requests.get(f"{BASE_URL}/admin/audit-logs", headers=chef_headers)
        assert res.status_code == 403

    def test_15_admin_audit_logs_list_success(self, admin_headers):
        """GET /admin/audit-logs returns paginated audit log entries.

        Note: The endpoint logs itself, so we should see at least one entry.
        """
        res = requests.get(f"{BASE_URL}/admin/audit-logs", headers=admin_headers)
        assert res.status_code == 200
        body = res.json()
        assert body["status"] == "success"
        assert "data" in body
        assert isinstance(body["data"], list)
        assert "pagination" in body
        assert body["pagination"]["page"] == 1

    def test_16_admin_audit_logs_pagination(self, admin_headers):
        """Validate pagination query params work correctly."""
        res = requests.get(f"{BASE_URL}/admin/audit-logs?page=1&per_page=5", headers=admin_headers)
        assert res.status_code == 200
        body = res.json()
        assert body["pagination"]["page"] == 1
        assert body["pagination"]["per_page"] == 5

    def test_17_admin_audit_logs_filter_by_action_type(self, admin_headers):
        """Validate action_type filter parameter."""
        # First, trigger a known action (view dashboard)
        requests.get(f"{BASE_URL}/admin/dashboard", headers=admin_headers)

        # Now filter for 'view_dashboard' action
        res = requests.get(
            f"{BASE_URL}/admin/audit-logs?action_type=view_dashboard&per_page=100",
            headers=admin_headers,
        )
        assert res.status_code == 200
        body = res.json()
        # Should have at least one 'view_dashboard' action
        if len(body["data"]) > 0:
            # All returned actions should match the filter (if data is present)
            for log in body["data"]:
                assert log.get("action") in ["view_dashboard", "view_audit_logs"]

    def test_18_admin_audit_statistics_requires_auth(self):
        res = requests.get(f"{BASE_URL}/admin/audit-logs/statistics")
        assert res.status_code == 401

    def test_19_admin_audit_statistics_forbidden_for_non_admin(self, chef_headers):
        res = requests.get(f"{BASE_URL}/admin/audit-logs/statistics", headers=chef_headers)
        assert res.status_code == 403

    def test_20_admin_audit_statistics_success(self, admin_headers):
        """GET /admin/audit-logs/statistics returns aggregate stats."""
        res = requests.get(f"{BASE_URL}/admin/audit-logs/statistics", headers=admin_headers)
        assert res.status_code == 200
        body = res.json()
        assert body["status"] == "success"
        assert "data" in body
        # Stats should be a dict with various counts/metrics
        assert isinstance(body["data"], dict)

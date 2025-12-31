"""\
Integration Tests: Scrapers API Validation
Validates Scrapers module endpoints against a real HTTP server.

Run with:
    pytest tests/integration/test_scrapers_api.py -v

Prerequisites:
    1. Docker containers running (postgres + redis)
    2. Backend running (http://localhost:5000)
    3. Scrapers blueprint enabled (requires beautifulsoup4 installed)
"""

import pytest
import requests
import uuid


BASE_URL = "http://localhost:5000"


class TestScrapersAPIValidation:
    """End-to-end validation of Scrapers module (authenticated)."""

    _source_id = None

    @pytest.fixture(scope="class")
    def unique_suffix(self):
        return uuid.uuid4().hex[:8]

    @pytest.fixture(scope="class")
    def chef_token(self, unique_suffix):
        """Register + login a chef and create chef profile (common prerequisite)."""
        username = f"scraper_chef_{unique_suffix}"
        email = f"scraper_chef_{unique_suffix}@example.com"
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
        assert register_response.status_code in [201, 400]

        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password},
        )
        assert login_response.status_code == 200
        token = login_response.json()["data"]["token"]

        # Create chef profile (not strictly required for scrapers, but keeps user consistent)
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = requests.post(
            f"{BASE_URL}/chefs/profile",
            json={
                "bio": "Integration test chef for scrapers",
                "specialty": "Scrapers",
                "phone": "+1-555-0444",
                "location": "Test City",
            },
            headers=headers,
        )
        assert profile_response.status_code in [201, 400]

        return token

    @pytest.fixture(scope="class")
    def auth_headers(self, chef_token):
        return {"Authorization": f"Bearer {chef_token}"}

    # ==================== PRICE SOURCES ====================

    def test_01_create_price_source_success(self, auth_headers, unique_suffix):
        payload = {
            "name": f"Test Source {unique_suffix}",
            "base_url": "http://127.0.0.1:1",
            "search_url_template": "http://127.0.0.1:1/search?q={ingredient}",
            "product_name_selector": ".product-name",
            "price_selector": ".price",
            "image_selector": None,
            "is_active": True,
            "notes": "Integration test source",
        }

        res = requests.post(f"{BASE_URL}/scrapers/sources", json=payload, headers=auth_headers)
        assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"

        body = res.json()
        assert "data" in body
        data = body["data"]
        assert "id" in data
        assert data["name"] == payload["name"]

        TestScrapersAPIValidation._source_id = data["id"]

    def test_02_list_price_sources_success(self, auth_headers):
        res = requests.get(f"{BASE_URL}/scrapers/sources", headers=auth_headers)
        assert res.status_code == 200

        body = res.json()
        assert "data" in body
        assert isinstance(body["data"], list)

        # Ensure our source is present
        assert any(str(item.get("id")) == str(self._source_id) for item in body["data"])  # type: ignore[attr-defined]

    def test_03_get_price_source_success(self, auth_headers):
        res = requests.get(f"{BASE_URL}/scrapers/sources/{self._source_id}", headers=auth_headers)
        assert res.status_code == 200
        body = res.json()
        assert body.get("data", {}).get("id") == self._source_id

    def test_04_update_price_source_success(self, auth_headers, unique_suffix):
        payload = {
            "name": f"Updated Source {unique_suffix}",
            "notes": "Updated notes",
            "is_active": True,
        }

        res = requests.put(
            f"{BASE_URL}/scrapers/sources/{self._source_id}",
            json=payload,
            headers=auth_headers,
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"

        body = res.json()
        assert "data" in body
        assert body["data"]["id"] == self._source_id
        assert body["data"]["name"] == payload["name"]

    def test_05_create_duplicate_price_source_name_fails(self, auth_headers, unique_suffix):
        """Creating a second source with the same name should fail (400)."""
        payload = {
            "name": f"Dup Source {unique_suffix}",
            "base_url": "http://127.0.0.1:1",
            "search_url_template": "http://127.0.0.1:1/search?q={ingredient}",
            "product_name_selector": ".product-name",
            "price_selector": ".price",
        }

        res1 = requests.post(f"{BASE_URL}/scrapers/sources", json=payload, headers=auth_headers)
        assert res1.status_code == 201, f"Expected 201, got {res1.status_code}: {res1.text}"

        res2 = requests.post(f"{BASE_URL}/scrapers/sources", json=payload, headers=auth_headers)
        assert res2.status_code == 400, f"Expected 400, got {res2.status_code}: {res2.text}"

    # ==================== SCRAPING & PRICES ====================

    def test_06_scrape_prices_no_results_returns_200(self, auth_headers):
        """Scrape uses an unreachable local URL so it should return 200 with empty data."""
        payload = {
            "ingredient_name": "tomato",
            "price_source_ids": [self._source_id],
            "force_refresh": True,
        }

        res = requests.post(f"{BASE_URL}/scrapers/scrape", json=payload, headers=auth_headers)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"

        body = res.json()
        assert "data" in body
        assert isinstance(body["data"], list)

    def test_07_get_scraped_prices_success(self, auth_headers):
        res = requests.get(f"{BASE_URL}/scrapers/prices?ingredient_name=tomato", headers=auth_headers)
        assert res.status_code == 200
        body = res.json()
        assert "data" in body
        assert isinstance(body["data"], list)

    def test_08_price_comparison_requires_ingredient_name(self, auth_headers):
        res = requests.get(f"{BASE_URL}/scrapers/prices/compare", headers=auth_headers)
        assert res.status_code == 400

    def test_09_cleanup_old_prices_success(self, auth_headers):
        res = requests.delete(f"{BASE_URL}/scrapers/prices/cleanup?days_old=0", headers=auth_headers)
        assert res.status_code == 200
        body = res.json()
        assert body.get("data") is not None
        assert "deleted_count" in body["data"]

    # ==================== DELETE SOURCE ====================

    def test_10_delete_price_source_success(self, auth_headers):
        res = requests.delete(f"{BASE_URL}/scrapers/sources/{self._source_id}", headers=auth_headers)
        assert res.status_code == 200

    def test_11_get_deleted_price_source_404(self, auth_headers):
        res = requests.get(f"{BASE_URL}/scrapers/sources/{self._source_id}", headers=auth_headers)
        assert res.status_code == 404

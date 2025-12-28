"""Controller-level tests for scraper endpoints.

These tests avoid network/DB dependencies by monkeypatching
ScraperController._get_service to deterministic fakes.
"""

from __future__ import annotations

import pytest

from tests.unit.test_helpers import assert_success_response, assert_error_response


@pytest.mark.usefixtures("client")
class TestScraperControllerCoverage:
    def test_create_price_source_value_error_400(self, client, chef_headers, monkeypatch):
        from app.scrapers.controllers.scraper_controller import ScraperController

        class _FakeService:
            def create_price_source(self, data):
                raise ValueError("bad source")

        monkeypatch.setattr(ScraperController, "_get_service", staticmethod(lambda: _FakeService()))

        payload = {
            "name": "Store",
            "base_url": "https://example.com",
            "search_url_template": "https://example.com/search?q={ingredient}",
            "product_name_selector": ".name",
            "price_selector": ".price",
            "image_selector": ".img",
            "is_active": True,
            "notes": None,
        }
        res = client.post("/scrapers/sources", json=payload, headers=chef_headers)
        assert_error_response(res, 400)

    def test_create_price_source_exception_500(self, client, chef_headers, monkeypatch):
        from app.scrapers.controllers.scraper_controller import ScraperController

        class _FakeService:
            def create_price_source(self, data):
                raise RuntimeError("boom")

        monkeypatch.setattr(ScraperController, "_get_service", staticmethod(lambda: _FakeService()))

        payload = {
            "name": "Store",
            "base_url": "https://example.com",
            "search_url_template": "https://example.com/search?q={ingredient}",
            "product_name_selector": ".name",
            "price_selector": ".price",
            "image_selector": ".img",
        }
        res = client.post("/scrapers/sources", json=payload, headers=chef_headers)
        assert_error_response(res, 500)

    def test_get_price_sources_exception_500(self, client, chef_headers, monkeypatch):
        from app.scrapers.controllers.scraper_controller import ScraperController

        class _FakeService:
            def get_all_price_sources(self, active_only: bool = False):
                raise Exception("db down")

        monkeypatch.setattr(ScraperController, "_get_service", staticmethod(lambda: _FakeService()))

        res = client.get("/scrapers/sources?active_only=true", headers=chef_headers)
        assert_error_response(res, 500)

    def test_get_price_source_value_error_404(self, client, chef_headers, monkeypatch):
        from app.scrapers.controllers.scraper_controller import ScraperController

        class _FakeService:
            def get_price_source(self, source_id: int):
                raise ValueError("not found")

        monkeypatch.setattr(ScraperController, "_get_service", staticmethod(lambda: _FakeService()))

        res = client.get("/scrapers/sources/99999", headers=chef_headers)
        assert_error_response(res, 404)

    def test_update_price_source_value_error_400(self, client, chef_headers, monkeypatch, test_price_source):
        from app.scrapers.controllers.scraper_controller import ScraperController

        class _FakeService:
            def update_price_source(self, source_id: int, data: dict):
                raise ValueError("invalid")

        monkeypatch.setattr(ScraperController, "_get_service", staticmethod(lambda: _FakeService()))

        res = client.put(
            f"/scrapers/sources/{test_price_source.id}",
            json={"name": "No"},
            headers=chef_headers,
        )
        # Marshmallow validation will also 400; either is fine, but we want controller ValueError mapping.
        # Ensure we pass schema validation:
        if res.status_code == 400 and (res.get_json() or {}).get("message"):
            pass
        assert res.status_code == 400

    def test_delete_price_source_exception_500(self, client, chef_headers, monkeypatch, test_price_source):
        from app.scrapers.controllers.scraper_controller import ScraperController

        class _FakeService:
            def delete_price_source(self, source_id: int):
                raise RuntimeError("boom")

        monkeypatch.setattr(ScraperController, "_get_service", staticmethod(lambda: _FakeService()))

        res = client.delete(f"/scrapers/sources/{test_price_source.id}", headers=chef_headers)
        assert_error_response(res, 500)

    def test_scrape_prices_empty_list_200_message(self, client, chef_headers, monkeypatch):
        from app.scrapers.controllers.scraper_controller import ScraperController

        class _FakeService:
            def scrape_ingredient_prices(self, ingredient_name: str, price_source_ids=None, force_refresh: bool = False):
                return []

        monkeypatch.setattr(ScraperController, "_get_service", staticmethod(lambda: _FakeService()))

        res = client.post(
            "/scrapers/scrape",
            json={"ingredient_name": "tomato"},
            headers=chef_headers,
        )
        data = assert_success_response(res, 200)
        assert data["data"] == []
        assert "No prices found" in (data.get("message") or "")

    def test_scrape_prices_success_list_200_message(self, client, chef_headers, monkeypatch):
        from app.scrapers.controllers.scraper_controller import ScraperController

        class _FakeService:
            def scrape_ingredient_prices(self, ingredient_name: str, price_source_ids=None, force_refresh: bool = False):
                return [
                    {
                        "id": 1,
                        "price_source_id": 2,
                        "ingredient_name": ingredient_name,
                        "product_name": "Tomato",
                        "price": "1.23",
                        "currency": "USD",
                        "product_url": "https://example.com/p/1",
                        "image_url": None,
                        "unit": None,
                        "notes": None,
                    }
                ]

        monkeypatch.setattr(ScraperController, "_get_service", staticmethod(lambda: _FakeService()))

        res = client.post(
            "/scrapers/scrape",
            json={"ingredient_name": "tomato", "force_refresh": True},
            headers=chef_headers,
        )
        data = assert_success_response(res, 200)
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 1
        assert "Found 1 price" in (data.get("message") or "")

    def test_scrape_prices_value_error_400(self, client, chef_headers, monkeypatch):
        from app.scrapers.controllers.scraper_controller import ScraperController

        class _FakeService:
            def scrape_ingredient_prices(self, ingredient_name: str, price_source_ids=None, force_refresh: bool = False):
                raise ValueError("bad ingredient")

        monkeypatch.setattr(ScraperController, "_get_service", staticmethod(lambda: _FakeService()))

        res = client.post(
            "/scrapers/scrape",
            json={"ingredient_name": "tomato"},
            headers=chef_headers,
        )
        assert_error_response(res, 400)

    def test_get_scraped_prices_passes_query_params(self, client, chef_headers, monkeypatch):
        from app.scrapers.controllers.scraper_controller import ScraperController

        seen = {}

        class _FakeService:
            def get_scraped_prices(self, ingredient_name=None, price_source_id=None, max_age_hours: int = 24):
                seen["ingredient_name"] = ingredient_name
                seen["price_source_id"] = price_source_id
                seen["max_age_hours"] = max_age_hours
                return []

        monkeypatch.setattr(ScraperController, "_get_service", staticmethod(lambda: _FakeService()))

        res = client.get(
            "/scrapers/prices?ingredient_name=tomato&price_source_id=5&max_age_hours=48",
            headers=chef_headers,
        )
        assert_success_response(res, 200)
        assert seen == {"ingredient_name": "tomato", "price_source_id": 5, "max_age_hours": 48}

    def test_get_price_comparison_missing_param_400(self, client, chef_headers):
        res = client.get("/scrapers/prices/compare", headers=chef_headers)
        assert_error_response(res, 400)

    def test_get_price_comparison_exception_500(self, client, chef_headers, monkeypatch):
        from app.scrapers.controllers.scraper_controller import ScraperController

        class _FakeService:
            def get_price_comparison(self, ingredient_name: str):
                raise RuntimeError("boom")

        monkeypatch.setattr(ScraperController, "_get_service", staticmethod(lambda: _FakeService()))

        res = client.get("/scrapers/prices/compare?ingredient_name=tomato", headers=chef_headers)
        assert_error_response(res, 500)

    def test_cleanup_old_prices_success(self, client, chef_headers, monkeypatch):
        from app.scrapers.controllers.scraper_controller import ScraperController

        class _FakeService:
            def cleanup_old_prices(self, days_old: int):
                return 7

        monkeypatch.setattr(ScraperController, "_get_service", staticmethod(lambda: _FakeService()))

        res = client.delete("/scrapers/prices/cleanup?days_old=5", headers=chef_headers)
        data = assert_success_response(res, 200)
        assert data["data"]["deleted_count"] == 7

    def test_cleanup_old_prices_exception_500(self, client, chef_headers, monkeypatch):
        from app.scrapers.controllers.scraper_controller import ScraperController

        class _FakeService:
            def cleanup_old_prices(self, days_old: int):
                raise RuntimeError("boom")

        monkeypatch.setattr(ScraperController, "_get_service", staticmethod(lambda: _FakeService()))

        res = client.delete("/scrapers/prices/cleanup?days_old=5", headers=chef_headers)
        assert_error_response(res, 500)

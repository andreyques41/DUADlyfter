"""Targeted unit tests for ScraperService.

Testing scope only: mocks network calls and repository persistence.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

import pytest

from app.scrapers.services.scraper_service import ScraperService
from app.core.lib.time_utils import utcnow_aware


@dataclass
class _Source:
    id: int
    name: str
    search_url_template: str
    product_name_selector: str
    price_selector: str
    image_selector: str | None = None
    is_active: bool = True


class _FakeResponse:
    def __init__(self, content: bytes):
        self.content = content

    def raise_for_status(self):
        return None


class _FakeRepo:
    def __init__(self, cached=None):
        self._cached = cached
        self.created_payloads = []

    def get_latest_price(self, ingredient_name, price_source_id):
        return self._cached

    def create_scraped_price(self, data: dict):
        self.created_payloads.append(data)
        # Return a lightweight object with the expected attributes.
        return type("Scraped", (), data)()


def test_extract_price_formats():
    svc = ScraperService()

    assert svc._extract_price("$12.99") == 12.99
    assert svc._extract_price("12,99€") == 12.99
    assert svc._extract_price("USD 1,234.50") == 1234.50
    assert svc._extract_price("invalid") is None


def test_get_cached_price_expired(monkeypatch):
    svc = ScraperService()

    cached = type(
        "Cached",
        (),
        {"scraped_at": utcnow_aware() - timedelta(hours=25)},
    )()
    svc.repository = _FakeRepo(cached=cached)

    assert svc._get_cached_price("rice", 1, max_age_hours=24) is None


def test_scrape_from_source_happy_path(monkeypatch):
    svc = ScraperService()
    repo = _FakeRepo()
    svc.repository = repo

    html = (
        "<html><body>"
        "<div class='name'>Rice 1kg</div>"
        "<span class='price'>$12.50</span>"
        "<img class='img' src='http://example.com/x.png'/>"
        "</body></html>"
    ).encode("utf-8")

    # Mock requests.get used by ScraperService.
    import app.scrapers.services.scraper_service as mod

    monkeypatch.setattr(mod.requests, "get", lambda url, headers=None, timeout=10: _FakeResponse(html))

    source = _Source(
        id=7,
        name="TestStore",
        search_url_template="https://example.com/search?q={ingredient}",
        product_name_selector=".name",
        price_selector=".price",
        image_selector=".img",
    )

    result = svc._scrape_from_source("rice", source)
    assert result is not None
    assert repo.created_payloads

    payload = repo.created_payloads[0]
    assert payload["price_source_id"] == 7
    assert payload["ingredient_name"] == "rice"
    assert payload["product_name"] == "Rice 1kg"
    assert payload["price"] == 12.50
    assert payload["image_url"] == "http://example.com/x.png"

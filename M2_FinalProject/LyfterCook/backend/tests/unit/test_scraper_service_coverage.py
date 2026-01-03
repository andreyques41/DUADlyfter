from datetime import datetime, timedelta, timezone
from types import SimpleNamespace


def _utcnow_aware_fixed():
    return datetime(2026, 1, 3, 12, 0, 0, tzinfo=timezone.utc)


def test_extract_price_formats():
    from app.scrapers.services.scraper_service import ScraperService

    service = ScraperService()
    assert service._extract_price("$12.99") == 12.99
    assert service._extract_price("12,99€") == 12.99
    assert service._extract_price("USD 1,234.50") == 1234.50
    assert service._extract_price("1.234,50 €") == 1.23450  # both present -> comma treated as thousands
    assert service._extract_price("not a price") is None


def test_get_cached_price_no_cached_returns_none(monkeypatch):
    from app.scrapers.services.scraper_service import ScraperService

    service = ScraperService()
    service.repository = SimpleNamespace(get_latest_price=lambda *_args, **_kwargs: None)
    assert service._get_cached_price("rice", 1, max_age_hours=24) is None


def test_get_cached_price_expired_returns_none(monkeypatch):
    from app.scrapers.services.scraper_service import ScraperService
    import app.scrapers.services.scraper_service as mod

    service = ScraperService()

    now = _utcnow_aware_fixed()
    monkeypatch.setattr(mod, "utcnow_aware", lambda: now)

    cached = SimpleNamespace(scraped_at=now - timedelta(hours=25))
    service.repository = SimpleNamespace(get_latest_price=lambda *_args, **_kwargs: cached)
    assert service._get_cached_price("rice", 1, max_age_hours=24) is None


def test_get_cached_price_fresh_returns_cached(monkeypatch):
    from app.scrapers.services.scraper_service import ScraperService
    import app.scrapers.services.scraper_service as mod

    service = ScraperService()

    now = _utcnow_aware_fixed()
    monkeypatch.setattr(mod, "utcnow_aware", lambda: now)

    cached = SimpleNamespace(scraped_at=now - timedelta(hours=1))
    service.repository = SimpleNamespace(get_latest_price=lambda *_args, **_kwargs: cached)
    assert service._get_cached_price("rice", 1, max_age_hours=24) is cached


def test_scrape_from_source_happy_path(monkeypatch):
    from app.scrapers.services.scraper_service import ScraperService
    import app.scrapers.services.scraper_service as mod

    service = ScraperService()

    now = _utcnow_aware_fixed()
    monkeypatch.setattr(mod, "utcnow_aware", lambda: now)

    class _Resp:
        status_code = 200
        content = b"<html><div class='name'>Product X</div><span class='price'>$12.99</span><img class='img' src='http://img/x.png'/></html>"

        def raise_for_status(self):
            return None

    monkeypatch.setattr(mod.requests, "get", lambda *_args, **_kwargs: _Resp())

    created = {}

    def _create_scraped_price(data):
        created.update(data)
        return SimpleNamespace(**data)

    service.repository = SimpleNamespace(create_scraped_price=_create_scraped_price)

    source = SimpleNamespace(
        id=10,
        name="TestSource",
        is_active=True,
        search_url_template="https://example.com/search?q={ingredient}",
        product_name_selector=".name",
        price_selector=".price",
        image_selector=".img",
    )

    scraped = service._scrape_from_source("rice", source)
    assert scraped is not None
    assert scraped.price_source_id == 10
    assert scraped.ingredient_name == "rice"
    assert scraped.product_name == "Product X"
    assert float(scraped.price) == 12.99
    assert scraped.image_url == "http://img/x.png"
    assert scraped.scraped_at == now
    assert created["product_url"].startswith("https://example.com/search")


def test_scrape_from_source_missing_product_returns_none(monkeypatch):
    from app.scrapers.services.scraper_service import ScraperService
    import app.scrapers.services.scraper_service as mod

    service = ScraperService()

    class _Resp:
        status_code = 200
        content = b"<html><span class='price'>$12.99</span></html>"

        def raise_for_status(self):
            return None

    monkeypatch.setattr(mod.requests, "get", lambda *_args, **_kwargs: _Resp())
    service.repository = SimpleNamespace(create_scraped_price=lambda _data: SimpleNamespace(**_data))

    source = SimpleNamespace(
        id=10,
        name="TestSource",
        is_active=True,
        search_url_template="https://example.com/search?q={query}",
        product_name_selector=".name",
        price_selector=".price",
        image_selector=None,
    )

    assert service._scrape_from_source("rice", source) is None


def test_scrape_from_source_unparseable_price_returns_none(monkeypatch):
    from app.scrapers.services.scraper_service import ScraperService
    import app.scrapers.services.scraper_service as mod

    service = ScraperService()

    class _Resp:
        status_code = 200
        content = b"<html><div class='name'>Product X</div><span class='price'>FREE</span></html>"

        def raise_for_status(self):
            return None

    monkeypatch.setattr(mod.requests, "get", lambda *_args, **_kwargs: _Resp())
    service.repository = SimpleNamespace(create_scraped_price=lambda _data: SimpleNamespace(**_data))

    source = SimpleNamespace(
        id=10,
        name="TestSource",
        is_active=True,
        search_url_template="https://example.com/search?q={ingredient}",
        product_name_selector=".name",
        price_selector=".price",
        image_selector=None,
    )

    assert service._scrape_from_source("rice", source) is None


def test_scrape_ingredient_prices_raises_when_no_sources(monkeypatch):
    from app.scrapers.services.scraper_service import ScraperService

    service = ScraperService()
    service.repository = SimpleNamespace(get_all_price_sources=lambda **_kwargs: [])

    try:
        service.scrape_ingredient_prices("rice")
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "No active price sources" in str(e)


def test_scrape_ingredient_prices_uses_cache_when_available(monkeypatch):
    from app.scrapers.services.scraper_service import ScraperService

    service = ScraperService()

    source = SimpleNamespace(id=1, name="S1", is_active=True)
    service.repository = SimpleNamespace(get_all_price_sources=lambda **_kwargs: [source])

    cached = SimpleNamespace(price_source_id=1, ingredient_name="rice")
    monkeypatch.setattr(service, "_get_cached_price", lambda *_args, **_kwargs: cached)
    monkeypatch.setattr(service, "_scrape_from_source", lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("should not scrape")))

    results = service.scrape_ingredient_prices("rice")
    assert results == [cached]


def test_scrape_ingredient_prices_scrapes_when_no_cache_and_continues_on_error(monkeypatch):
    from app.scrapers.services.scraper_service import ScraperService

    service = ScraperService()

    s1 = SimpleNamespace(id=1, name="S1", is_active=True)
    s2 = SimpleNamespace(id=2, name="S2", is_active=True)
    service.repository = SimpleNamespace(get_all_price_sources=lambda **_kwargs: [s1, s2])

    monkeypatch.setattr(service, "_get_cached_price", lambda *_args, **_kwargs: None)

    def _scrape(ingredient, source):
        if source.id == 1:
            raise RuntimeError("boom")
        return SimpleNamespace(price_source_id=2, ingredient_name=ingredient)

    monkeypatch.setattr(service, "_scrape_from_source", _scrape)

    results = service.scrape_ingredient_prices("rice")
    assert len(results) == 1
    assert results[0].price_source_id == 2


def test_get_price_comparison_not_found_returns_message(monkeypatch):
    from app.scrapers.services.scraper_service import ScraperService

    service = ScraperService()
    monkeypatch.setattr(service, "get_scraped_prices", lambda **_kwargs: [])

    out = service.get_price_comparison("rice")
    assert out["ingredient_name"] == "rice"
    assert out["found"] is False
    assert "No recent prices" in out["message"]


def test_get_price_comparison_found_builds_stats(monkeypatch):
    from app.scrapers.services.scraper_service import ScraperService

    service = ScraperService()

    now = _utcnow_aware_fixed()
    prices = [
        SimpleNamespace(
            price_source_id=1,
            product_name="P1",
            price=10.0,
            product_url="u1",
            scraped_at=now,
        ),
        SimpleNamespace(
            price_source_id=2,
            product_name="P2",
            price=20.0,
            product_url="u2",
            scraped_at=now,
        ),
    ]
    monkeypatch.setattr(service, "get_scraped_prices", lambda **_kwargs: prices)

    out = service.get_price_comparison("rice")
    assert out["found"] is True
    assert out["total_sources"] == 2
    assert out["min_price"] == 10.0
    assert out["max_price"] == 20.0
    assert out["avg_price"] == 15.0
    assert len(out["prices"]) == 2
    assert out["prices"][0]["scraped_at"].startswith("2026-01-03T12:00:00")

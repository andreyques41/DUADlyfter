"""Integration workflow to verify route-level caching decorator behavior.

This uses an in-memory cache via monkeypatch to avoid Redis.
It verifies that a second request returns the cached payload without re-invoking the service.
"""

from __future__ import annotations

import fnmatch

import pytest

from app.public.controllers.public_controller import PublicController


class _InMemoryCache:
    def __init__(self):
        self.enabled = True
        self._store: dict[str, object] = {}

    def get(self, key: str):
        return self._store.get(key)

    def set(self, key: str, value, ttl: int = 3600):
        self._store[key] = value
        return True

    def delete(self, key: str):
        return self._store.pop(key, None) is not None

    def delete_pattern(self, pattern: str):
        keys = [k for k in list(self._store.keys()) if fnmatch.fnmatch(k, pattern)]
        for k in keys:
            self._store.pop(k, None)
        return len(keys)


@pytest.mark.integration
def test_public_chefs_endpoint_is_cached(client, monkeypatch):
    import app.core.middleware.cache_decorators as cache_decorators

    cache = _InMemoryCache()
    # cache_response() imports get_cache into its own module scope, so patch there.
    monkeypatch.setattr(cache_decorators, "get_cache", lambda: cache)

    calls = {"n": 0}

    class _FakeService:
        def get_chefs(self, **kwargs):
            calls["n"] += 1
            return {"chefs": [], "total": 0, "page": 1, "per_page": 20, "total_pages": 0}

    monkeypatch.setattr(PublicController, "_get_service", staticmethod(lambda: _FakeService()))

    r1 = client.get("/public/chefs")
    assert r1.status_code == 200

    r2 = client.get("/public/chefs")
    assert r2.status_code == 200

    # Second request should be served from cache (service called once).
    assert calls["n"] == 1

    assert r1.get_json() == r2.get_json()

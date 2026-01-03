"""Coverage-focused tests for admin cache routes.

These routes have branchy behavior (cache enabled/disabled, patterns, error
handling) and are cheap to cover by mocking the cache manager.

Note: We monkeypatch auth decorators to no-ops and reload the module so the
routes are registered without auth wrappers for unit testing.
"""

from __future__ import annotations

import importlib

from unittest.mock import MagicMock

import pytest
from flask import Flask


@pytest.fixture
def app(monkeypatch):
    # Patch auth decorators to no-ops BEFORE importing routes
    import app.core.middleware.auth_middleware as am

    monkeypatch.setattr(am, "jwt_required", lambda f: f)
    monkeypatch.setattr(am, "admin_required", lambda f: f)

    import app.admin.routes.admin_routes as ar

    importlib.reload(ar)

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(ar.admin_bp)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_cache_stats_when_disabled_returns_enabled_false(app, client, monkeypatch):
    import app.admin.routes.admin_routes as ar

    cache = MagicMock()
    cache.enabled = False
    monkeypatch.setattr(ar, "get_cache", lambda: cache)

    resp = client.get("/admin/cache/stats")
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["enabled"] is False


def test_get_cache_stats_when_enabled_returns_hit_rate(app, client, monkeypatch):
    import app.admin.routes.admin_routes as ar

    redis_client = MagicMock()
    redis_client.info.return_value = {
        "keyspace_hits": 8,
        "keyspace_misses": 2,
        "used_memory_human": "1M",
        "used_memory_peak_human": "2M",
        "connected_clients": 1,
        "uptime_in_days": 0,
    }
    redis_client.dbsize.return_value = 11

    cache = MagicMock()
    cache.enabled = True
    cache.redis_client = redis_client

    monkeypatch.setattr(ar, "get_cache", lambda: cache)

    resp = client.get("/admin/cache/stats")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "success"
    assert body["data"]["enabled"] is True
    assert body["data"]["keys_count"] == 11
    assert body["data"]["hit_rate"] == 80.0


def test_get_cache_stats_exception_returns_500(app, client, monkeypatch):
    import app.admin.routes.admin_routes as ar

    redis_client = MagicMock()
    redis_client.info.side_effect = Exception("boom")

    cache = MagicMock()
    cache.enabled = True
    cache.redis_client = redis_client

    monkeypatch.setattr(ar, "get_cache", lambda: cache)

    resp = client.get("/admin/cache/stats")
    assert resp.status_code == 500
    assert "Failed to get cache stats" in resp.get_json()["message"]


def test_clear_cache_when_disabled_returns_400(app, client, monkeypatch):
    import app.admin.routes.admin_routes as ar

    cache = MagicMock()
    cache.enabled = False
    monkeypatch.setattr(ar, "get_cache", lambda: cache)

    resp = client.delete("/admin/cache/clear")
    assert resp.status_code == 400


def test_clear_cache_flush_all_pattern_star(app, client, monkeypatch):
    import app.admin.routes.admin_routes as ar

    cache = MagicMock()
    cache.enabled = True
    monkeypatch.setattr(ar, "get_cache", lambda: cache)

    resp = client.delete("/admin/cache/clear")
    assert resp.status_code == 200
    cache.flush_all.assert_called_once()


def test_clear_cache_delete_pattern(app, client, monkeypatch):
    import app.admin.routes.admin_routes as ar

    cache = MagicMock()
    cache.enabled = True
    cache.delete_pattern.return_value = 5
    monkeypatch.setattr(ar, "get_cache", lambda: cache)

    resp = client.delete("/admin/cache/clear?pattern=public:*")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["deleted_count"] == 5
    assert body["pattern"] == "public:*"


def test_clear_cache_exception_returns_500(app, client, monkeypatch):
    import app.admin.routes.admin_routes as ar

    cache = MagicMock()
    cache.enabled = True
    cache.flush_all.side_effect = Exception("boom")
    monkeypatch.setattr(ar, "get_cache", lambda: cache)

    resp = client.delete("/admin/cache/clear")
    assert resp.status_code == 500
    assert "Failed to clear cache" in resp.get_json()["message"]


def test_get_chef_route_delegates_to_controller(app, client, monkeypatch):
    import app.admin.routes.admin_routes as ar

    monkeypatch.setattr(
        ar.admin_controller,
        "get_chef",
        MagicMock(return_value=({"status": "success", "chef_id": 123}, 200)),
    )

    resp = client.get("/admin/chefs/123")
    assert resp.status_code == 200
    assert resp.get_json()["chef_id"] == 123


def test_get_audit_statistics_route_delegates_to_controller(app, client, monkeypatch):
    import app.admin.routes.admin_routes as ar

    monkeypatch.setattr(
        ar.admin_controller,
        "get_audit_statistics",
        MagicMock(return_value=({"status": "success", "total_logs": 0}, 200)),
    )

    resp = client.get("/admin/audit-logs/statistics")
    assert resp.status_code == 200
    assert resp.get_json()["total_logs"] == 0

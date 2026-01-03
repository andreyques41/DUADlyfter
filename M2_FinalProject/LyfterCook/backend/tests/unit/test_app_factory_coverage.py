from types import SimpleNamespace


def _create_isolated_app(monkeypatch):
    """Create a fresh app instance safe to add routes to.

    The session-scoped `app` fixture is shared across many tests and may have
    already handled requests, so Flask won't allow adding routes.
    """

    from app import create_app

    # Avoid side effects during app creation.
    from config import logging as cfg_logging
    monkeypatch.setattr(cfg_logging, "setup_logging", lambda: None)

    from app.core import database as db
    monkeypatch.setattr(db, "init_db", lambda: None)
    monkeypatch.setattr(db, "close_db", lambda _exc=None: None)

    from app.blueprints import register_blueprints
    monkeypatch.setattr(
        __import__("app.blueprints", fromlist=["register_blueprints"]),
        "register_blueprints",
        lambda _app: None,
    )

    from app.core.limiter import limiter
    monkeypatch.setattr(limiter, "init_app", lambda _app: None)

    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "DEBUG": True,
            "PROPAGATE_EXCEPTIONS": False,
        }
    )
    return app


def test_health_endpoints_basic(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "healthy"

    resp = client.get("/health/live")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "alive"


def test_test_endpoint_post_reports_data_received(client):
    resp = client.post("/test", json={"hello": "world"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["method"] == "POST"
    assert data["data_received"] is True


def test_method_not_allowed_handler_returns_valid_methods(client):
    resp = client.put("/health")
    assert resp.status_code == 405
    data = resp.get_json()
    assert data["success"] is False
    assert data["error"] == "Method Not Allowed"
    assert isinstance(data.get("valid_methods"), list)


def test_readiness_check_healthy_with_cache_disabled(app, monkeypatch):
    # The test app fixture sets PROPAGATE_EXCEPTIONS=True; for handler coverage we keep it.
    # Readiness endpoint does not raise, it returns a payload.

    class _Conn:
        def execute(self, _sql):
            return 1

    class _ConnCtx:
        def __enter__(self):
            return _Conn()

        def __exit__(self, exc_type, exc, tb):
            return False

    class _Engine:
        def connect(self):
            return _ConnCtx()

    from app.core import database as db
    monkeypatch.setattr(db, "engine", _Engine())

    from app import core as _core_pkg  # noqa: F401  (ensures package exists)
    from app.core import cache_manager as cm

    class _CacheManagerDisabled:
        def __init__(self):
            self.enabled = False

    monkeypatch.setattr(cm, "CacheManager", _CacheManagerDisabled)

    with app.test_client() as c:
        resp = c.get("/health/ready")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ready"
    assert data["checks"]["database"]["status"] == "healthy"
    assert data["checks"]["cache"]["status"] == "disabled"


def test_readiness_check_cache_unhealthy_sets_503(app, monkeypatch):
    class _Conn:
        def execute(self, _sql):
            return 1

    class _ConnCtx:
        def __enter__(self):
            return _Conn()

        def __exit__(self, exc_type, exc, tb):
            return False

    class _Engine:
        def connect(self):
            return _ConnCtx()

    from app.core import database as db
    monkeypatch.setattr(db, "engine", _Engine())

    from app.core import cache_manager as cm

    class _CacheManagerEnabledButBroken:
        def __init__(self):
            self.enabled = True
            self.redis_client = SimpleNamespace(ping=lambda: (_ for _ in ()).throw(RuntimeError("no redis")))

    monkeypatch.setattr(cm, "CacheManager", _CacheManagerEnabledButBroken)

    with app.test_client() as c:
        resp = c.get("/health/ready")
    assert resp.status_code == 503
    data = resp.get_json()
    assert data["status"] == "not_ready"
    assert data["checks"]["cache"]["status"] == "unhealthy"


def test_global_exception_handler_http_exception_branch(monkeypatch):
    # Cover handle_exception() path for an HTTPException that doesn't have a specific handler.
    app = _create_isolated_app(monkeypatch)

    from werkzeug.exceptions import NotImplemented

    @app.get("/__raise_http__")
    def _raise_http():
        raise NotImplemented("nope")

    with app.test_client() as c:
        resp = c.get("/__raise_http__")

    assert resp.status_code == 501
    data = resp.get_json()
    assert data["success"] is False
    assert data["error"] == "Not Implemented"


def test_global_exception_handler_non_http_debug_branch_includes_traceback(monkeypatch):
    # Cover handle_exception() non-HTTP branch in DEBUG mode.
    app = _create_isolated_app(monkeypatch)

    @app.get("/__raise_exception__")
    def _raise_exc():
        raise RuntimeError("boom")

    with app.test_client() as c:
        resp = c.get("/__raise_exception__")

    assert resp.status_code == 500
    data = resp.get_json()
    assert data["success"] is False
    assert data["error"] == "Internal Server Error"
    assert data["message"] == "boom"
    assert "traceback" in data

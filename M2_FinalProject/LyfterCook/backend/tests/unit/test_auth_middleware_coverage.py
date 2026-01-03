from __future__ import annotations

from flask import Flask, g, jsonify


def _make_app():
    app = Flask(__name__)
    app.config.update({"TESTING": True})
    return app


def test_jwt_required_missing_header_returns_401(monkeypatch):
    import app.core.middleware.auth_middleware as am

    app = _make_app()

    @app.get("/protected")
    @am.jwt_required
    def protected():
        return jsonify({"ok": True})

    with app.test_client() as client:
        resp = client.get("/protected")
    assert resp.status_code == 401
    data = resp.get_json()
    assert "Missing authorization header" in (data.get("message") or data.get("error") or "")


def test_jwt_required_invalid_header_format_returns_401(monkeypatch):
    import app.core.middleware.auth_middleware as am

    app = _make_app()

    @app.get("/protected")
    @am.jwt_required
    def protected():
        return jsonify({"ok": True})

    with app.test_client() as client:
        resp = client.get("/protected", headers={"Authorization": "Bearer"})
    assert resp.status_code == 401
    data = resp.get_json()
    assert "Invalid authorization header format" in (data.get("message") or data.get("error") or "")


def test_jwt_required_invalid_token_type_returns_401(monkeypatch):
    import app.core.middleware.auth_middleware as am

    app = _make_app()

    @app.get("/protected")
    @am.jwt_required
    def protected():
        return jsonify({"ok": True})

    with app.test_client() as client:
        resp = client.get("/protected", headers={"Authorization": "Token abc"})
    assert resp.status_code == 401
    data = resp.get_json()
    assert "Invalid token type" in (data.get("message") or data.get("error") or "")


def test_jwt_required_invalid_token_returns_401(monkeypatch):
    import app.core.middleware.auth_middleware as am

    class _Auth:
        def __init__(self, _repo):
            pass

        def verify_jwt_token(self, _token):
            return None

    monkeypatch.setattr(am, "AuthService", _Auth)
    monkeypatch.setattr(am, "UserRepository", lambda _db: object())
    monkeypatch.setattr(am, "get_db", lambda: object())

    app = _make_app()

    @app.get("/protected")
    @am.jwt_required
    def protected():
        return jsonify({"ok": True})

    with app.test_client() as client:
        resp = client.get("/protected", headers={"Authorization": "Bearer abc"})
    assert resp.status_code == 401
    data = resp.get_json()
    assert "Invalid or expired token" in (data.get("message") or data.get("error") or "")


def test_jwt_required_inactive_user_returns_401(monkeypatch):
    import app.core.middleware.auth_middleware as am

    class _Auth:
        def __init__(self, _repo):
            pass

        def verify_jwt_token(self, _token):
            return {"user_id": 1}

        def get_user_by_id(self, _user_id):
            return {"id": 1, "is_active": False}

    monkeypatch.setattr(am, "AuthService", _Auth)
    monkeypatch.setattr(am, "UserRepository", lambda _db: object())
    monkeypatch.setattr(am, "get_db", lambda: object())

    app = _make_app()

    @app.get("/protected")
    @am.jwt_required
    def protected():
        return jsonify({"ok": True})

    with app.test_client() as client:
        resp = client.get("/protected", headers={"Authorization": "Bearer abc"})
    assert resp.status_code == 401
    data = resp.get_json()
    assert "User not found or inactive" in (data.get("message") or data.get("error") or "")


def test_jwt_required_success_sets_g_and_allows(monkeypatch):
    import app.core.middleware.auth_middleware as am

    class _Auth:
        def __init__(self, _repo):
            pass

        def verify_jwt_token(self, _token):
            return {"user_id": 7}

        def get_user_by_id(self, _user_id):
            return {"id": 7, "username": "u", "role": "chef", "is_active": True}

    monkeypatch.setattr(am, "AuthService", _Auth)
    monkeypatch.setattr(am, "UserRepository", lambda _db: object())
    monkeypatch.setattr(am, "get_db", lambda: object())

    app = _make_app()

    @app.get("/protected")
    @am.jwt_required
    def protected():
        return jsonify({"user_id": g.user_id, "username": g.current_user["username"]})

    with app.test_client() as client:
        resp = client.get("/protected", headers={"Authorization": "Bearer abc"})
    assert resp.status_code == 200
    assert resp.get_json() == {"user_id": 7, "username": "u"}


def test_admin_required_requires_auth_and_role(monkeypatch):
    import app.core.middleware.auth_middleware as am

    # Case 1: No g.current_user
    app1 = _make_app()

    @app1.get("/admin")
    @am.admin_required
    def admin1():
        return jsonify({"ok": True})

    with app1.test_client() as client:
        resp = client.get("/admin")
    assert resp.status_code == 401

    # Case 2: Non-admin user
    app2 = _make_app()

    @app2.before_request
    def _set_non_admin():
        g.current_user = {"role": "chef"}

    @app2.get("/admin")
    @am.admin_required
    def admin2():
        return jsonify({"ok": True})

    with app2.test_client() as client:
        resp = client.get("/admin")
    assert resp.status_code == 403


def test_admin_required_allows_admin(monkeypatch):
    import app.core.middleware.auth_middleware as am

    app = _make_app()

    @app.before_request
    def _set_admin():
        g.current_user = {"role": "admin"}

    @app.get("/admin")
    @am.admin_required
    def admin():
        return jsonify({"ok": True})

    with app.test_client() as client:
        resp = client.get("/admin")
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True


def test_optional_auth_sets_user_when_valid_and_swallows_errors(monkeypatch):
    import app.core.middleware.auth_middleware as am

    class _Auth:
        def __init__(self, _repo):
            pass

        def verify_jwt_token(self, token):
            if token == "good":
                return {"user_id": 1}
            raise RuntimeError("boom")

        def get_user_by_id(self, _user_id):
            return {"id": 1, "username": "u", "is_active": True}

    monkeypatch.setattr(am, "AuthService", _Auth)
    monkeypatch.setattr(am, "UserRepository", lambda _db: object())
    monkeypatch.setattr(am, "get_db", lambda: object())

    app = _make_app()

    @app.get("/maybe")
    @am.optional_auth
    def maybe():
        if hasattr(g, "current_user"):
            return jsonify({"user_id": g.user_id})
        return jsonify({"user_id": None})

    with app.test_client() as client:
        ok = client.get("/maybe", headers={"Authorization": "Bearer good"})
        bad = client.get("/maybe", headers={"Authorization": "Bearer bad"})

    assert ok.status_code == 200
    assert ok.get_json()["user_id"] == 1
    assert bad.status_code == 200
    assert bad.get_json()["user_id"] is None

"""Coverage-focused tests for request_decorators and cache_helper.

These modules are small but have multiple error-handling branches that are
otherwise hard to hit via full endpoint tests.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from flask import Flask, jsonify, request
from marshmallow import Schema, ValidationError, fields


class TestRequestDecoratorsCoverage:
    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        app.config["TESTING"] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_validate_json_invalid_json_returns_400(self, app, client):
        from app.core.middleware.request_decorators import validate_json

        @app.post("/t")
        @validate_json()
        def handler():
            return jsonify({"ok": True}), 200

        resp = client.post("/t", data="{not json", content_type="application/json")
        assert resp.status_code == 400
        body = resp.get_json()
        assert body["error"] == "Invalid JSON format"

    def test_validate_json_missing_body_returns_400(self, app, client, monkeypatch):
        from flask.wrappers import Request
        from app.core.middleware.request_decorators import validate_json

        monkeypatch.setattr(Request, "get_json", lambda *_args, **_kwargs: None)

        @app.post("/t")
        @validate_json()
        def handler():
            return jsonify({"ok": True}), 200

        resp = client.post("/t", data="", content_type="application/json")
        assert resp.status_code == 400
        body = resp.get_json()
        assert body["error"] == "Request body is required"

    def test_validate_json_schema_validation_error_includes_details(self, app, client):
        from app.core.middleware.request_decorators import validate_json

        class ReqSchema(Schema):
            name = fields.String(required=True)

        @app.post("/t")
        @validate_json(ReqSchema)
        def handler():
            return jsonify({"ok": True}), 200

        resp = client.post("/t", json={})
        assert resp.status_code == 400
        body = resp.get_json()
        assert body["error"] == "Validation failed"
        assert "details" in body
        assert "name" in body["details"]

    def test_validate_json_success_sets_request_validated_data(self, app, client):
        from app.core.middleware.request_decorators import validate_json

        class ReqSchema(Schema):
            name = fields.String(required=True)

        @app.post("/t")
        @validate_json(ReqSchema)
        def handler():
            return jsonify({"validated": request.validated_data}), 200

        resp = client.post("/t", json={"name": "Alice"})
        assert resp.status_code == 200
        assert resp.get_json()["validated"] == {"name": "Alice"}

    def test_require_content_type_rejects_mismatch_415(self, app, client):
        from app.core.middleware.request_decorators import require_content_type

        @app.post("/t")
        @require_content_type("application/json")
        def handler():
            return jsonify({"ok": True}), 200

        resp = client.post("/t", data="hi", content_type="text/plain")
        assert resp.status_code == 415
        assert resp.get_json()["error"] == "Content-Type must be application/json"

    def test_require_content_type_allows_match(self, app, client):
        from app.core.middleware.request_decorators import require_content_type

        @app.post("/t")
        @require_content_type("application/json")
        def handler():
            return jsonify({"ok": True}), 200

        resp = client.post("/t", json={"x": 1})
        assert resp.status_code == 200


class TestCacheHelperCoverage:
    def test_get_or_set_cache_hit_returns_cached_and_skips_fetch(self, monkeypatch):
        import app.core.middleware.cache_helper as ch

        cache = MagicMock()
        cache.get.return_value = {"value": 123}
        monkeypatch.setattr(ch, "get_cache", lambda: cache)

        helper = ch.CacheHelper(resource_name="chef", version="v1")
        fetch = MagicMock()

        class AnySchema(Schema):
            value = fields.Integer()

        result = helper.get_or_set("profile:1", fetch_func=fetch, schema_class=AnySchema)
        assert result == {"value": 123}
        fetch.assert_not_called()

    def test_get_or_set_cache_miss_data_none_returns_none(self, monkeypatch):
        import app.core.middleware.cache_helper as ch

        cache = MagicMock()
        cache.get.return_value = None
        monkeypatch.setattr(ch, "get_cache", lambda: cache)

        helper = ch.CacheHelper(resource_name="chef", version="v1")

        class AnySchema(Schema):
            value = fields.Integer()

        result = helper.get_or_set("profile:1", fetch_func=lambda: None, schema_class=AnySchema)
        assert result is None
        cache.set.assert_not_called()

    def test_get_or_set_schema_dump_error_returns_none(self, monkeypatch):
        import app.core.middleware.cache_helper as ch

        cache = MagicMock()
        cache.get.return_value = None
        monkeypatch.setattr(ch, "get_cache", lambda: cache)

        helper = ch.CacheHelper(resource_name="chef", version="v1")

        class BrokenSchema(Schema):
            def dump(self, obj, *, many=None):  # type: ignore[override]
                raise ValidationError("boom")

        result = helper.get_or_set("profile:1", fetch_func=lambda: {"x": 1}, schema_class=BrokenSchema)
        assert result is None

    def test_get_or_set_cache_set_failure_returns_serialized_anyway(self, monkeypatch):
        import app.core.middleware.cache_helper as ch

        cache = MagicMock()
        cache.get.return_value = None
        cache.set.side_effect = Exception("redis down")
        monkeypatch.setattr(ch, "get_cache", lambda: cache)

        helper = ch.CacheHelper(resource_name="chef", version="v1")

        class AnySchema(Schema):
            value = fields.Integer()

        result = helper.get_or_set(
            "profile:1",
            fetch_func=lambda: {"value": 7},
            schema_class=AnySchema,
            ttl=10,
        )
        assert result == {"value": 7}

    def test_get_or_set_many_true_counts_len_branch(self, monkeypatch):
        import app.core.middleware.cache_helper as ch

        cache = MagicMock()
        cache.get.return_value = None
        monkeypatch.setattr(ch, "get_cache", lambda: cache)

        helper = ch.CacheHelper(resource_name="dish", version="v2")

        class AnySchema(Schema):
            value = fields.Integer()

        data = [{"value": 1}, {"value": 2}]
        result = helper.get_or_set("list:all", fetch_func=lambda: data, schema_class=AnySchema, many=True)
        assert result == [{"value": 1}, {"value": 2}]

    def test_invalidate_deletes_keys_and_handles_missing(self, monkeypatch):
        import app.core.middleware.cache_helper as ch

        cache = MagicMock()
        cache.delete.side_effect = [True, False]
        monkeypatch.setattr(ch, "get_cache", lambda: cache)

        helper = ch.CacheHelper(resource_name="chef", version="v1")
        helper.invalidate("profile:1", "profile:2")

        assert cache.delete.call_count == 2

    def test_invalidate_swallows_delete_exception(self, monkeypatch):
        import app.core.middleware.cache_helper as ch

        cache = MagicMock()
        cache.delete.side_effect = Exception("boom")
        monkeypatch.setattr(ch, "get_cache", lambda: cache)

        helper = ch.CacheHelper(resource_name="chef", version="v1")
        helper.invalidate("profile:1")

    def test_invalidate_pattern_returns_deleted_count_and_handles_exception(self, monkeypatch):
        import app.core.middleware.cache_helper as ch

        cache = MagicMock()
        cache.delete_pattern.return_value = 3
        monkeypatch.setattr(ch, "get_cache", lambda: cache)

        helper = ch.CacheHelper(resource_name="chef", version="v1")
        assert helper.invalidate_pattern("*") == 3

        cache.delete_pattern.side_effect = Exception("boom")
        assert helper.invalidate_pattern("*") == 0

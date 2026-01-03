from types import SimpleNamespace


def test_get_db_raises_when_not_initialized(app, monkeypatch):
    import app.core.database as db

    monkeypatch.setattr(db, "SessionLocal", None)
    with app.test_request_context("/"):
        try:
            db.get_db()
            assert False, "Expected RuntimeError"
        except RuntimeError as e:
            assert "init_db" in str(e)


def test_get_db_creates_once_and_reuses_in_g(app, monkeypatch):
    import app.core.database as db
    from flask import g

    created = {"n": 0}

    def _factory():
        created["n"] += 1
        return SimpleNamespace(name=f"s{created['n']}")

    monkeypatch.setattr(db, "SessionLocal", _factory)

    with app.test_request_context("/"):
        # The session-scoped app fixture keeps an app_context pushed, so `g` can
        # retain state across tests. Ensure clean slate.
        g.pop("db", None)
        s1 = db.get_db()
        s2 = db.get_db()
        assert s1 is s2
        assert g.db is s1
        assert created["n"] == 1


def test_close_db_commits_when_no_exception(app, monkeypatch):
    import app.core.database as db
    from flask import g

    calls = {"commit": 0, "rollback": 0, "close": 0}

    class _Session:
        def commit(self):
            calls["commit"] += 1

        def rollback(self):
            calls["rollback"] += 1

        def close(self):
            calls["close"] += 1

    with app.test_request_context("/"):
        g.db = _Session()
        db.close_db(None)

    assert calls == {"commit": 1, "rollback": 0, "close": 1}


def test_close_db_rolls_back_when_exception(app):
    import app.core.database as db
    from flask import g

    calls = {"commit": 0, "rollback": 0, "close": 0}

    class _Session:
        def commit(self):
            calls["commit"] += 1

        def rollback(self):
            calls["rollback"] += 1

        def close(self):
            calls["close"] += 1

    with app.test_request_context("/"):
        g.db = _Session()
        db.close_db(Exception("boom"))

    assert calls == {"commit": 0, "rollback": 1, "close": 1}


def test_close_db_rolls_back_on_sqlalchemy_error(app):
    import app.core.database as db
    from flask import g
    from sqlalchemy.exc import SQLAlchemyError

    calls = {"commit": 0, "rollback": 0, "close": 0}

    class _Session:
        def commit(self):
            calls["commit"] += 1
            raise SQLAlchemyError("commit failed")

        def rollback(self):
            calls["rollback"] += 1

        def close(self):
            calls["close"] += 1

    with app.test_request_context("/"):
        g.db = _Session()
        db.close_db(None)

    assert calls["commit"] == 1
    assert calls["rollback"] == 1
    assert calls["close"] == 1


def test_create_and_drop_tables_call_metadata(monkeypatch):
    import app.core.database as db

    called = {"create": 0, "drop": 0}

    monkeypatch.setattr(db, "engine", object())

    monkeypatch.setattr(
        db.Base.metadata,
        "create_all",
        lambda **kwargs: called.__setitem__("create", called["create"] + 1),
    )
    monkeypatch.setattr(
        db.Base.metadata,
        "drop_all",
        lambda **kwargs: called.__setitem__("drop", called["drop"] + 1),
    )

    db.create_tables()
    db.drop_tables()

    assert called == {"create": 1, "drop": 1}


def test_init_db_sets_engine_and_sessionlocal(monkeypatch):
    import app.core.database as db

    fake_engine = object()
    created = {"engine": 0, "sessionmaker": 0}

    def _create_engine(url, **kwargs):
        created["engine"] += 1
        assert url == "postgresql://fake"
        return fake_engine

    def _sessionmaker(**kwargs):
        created["sessionmaker"] += 1
        assert kwargs["bind"] is fake_engine
        return lambda: SimpleNamespace()

    monkeypatch.setattr(db, "create_engine", _create_engine)
    monkeypatch.setattr(db, "sessionmaker", _sessionmaker)

    from config import settings
    monkeypatch.setattr(settings, "get_database_url", lambda: "postgresql://fake")
    monkeypatch.setattr(settings, "DB_HOST", "h")
    monkeypatch.setattr(settings, "DB_PORT", 123)
    monkeypatch.setattr(settings, "DB_NAME", "n")
    monkeypatch.setattr(settings, "FLASK_DEBUG", False)

    # Reset globals
    monkeypatch.setattr(db, "engine", None)
    monkeypatch.setattr(db, "SessionLocal", None)

    db.init_db()
    assert db.engine is fake_engine
    assert callable(db.SessionLocal)
    assert created["engine"] == 1
    assert created["sessionmaker"] == 1

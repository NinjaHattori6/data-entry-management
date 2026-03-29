"""
Basic test suite for the Flask oncology data-entry application.

Tests cover:
- Flask app initialisation and configuration
- Database connection via utils.db.get_db_connection
- Route registration
"""

import os
import sqlite3

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def app():
    """
    Import and configure the Flask app for testing.

    app_new.py calls init_db() at module level, which creates the SQLite
    database in the current working directory if it does not already exist.
    The *.db pattern is listed in .gitignore so the file is never committed.
    """
    import app_new  # noqa: F401 - side-effect import registers routes and DB

    app_new.app.config["TESTING"] = True
    app_new.app.config["WTF_CSRF_ENABLED"] = False

    yield app_new.app


@pytest.fixture
def client(app):
    """Return a test client for the app."""
    return app.test_client()


# ---------------------------------------------------------------------------
# Configuration tests
# ---------------------------------------------------------------------------

class TestAppConfig:
    """Verify that the Flask application configuration loads correctly."""

    def test_app_is_not_none(self, app):
        assert app is not None

    def test_testing_flag_set(self, app):
        assert app.config["TESTING"] is True

    def test_secret_key_configured(self, app):
        assert app.config.get("SECRET_KEY") is not None

    def test_sqlalchemy_track_modifications_disabled(self, app):
        assert app.config.get("SQLALCHEMY_TRACK_MODIFICATIONS") is False

    def test_config_class_defaults(self):
        from config_new import Config
        assert Config.OTP_EXPIRY_MINUTES == 10
        assert Config.SQLALCHEMY_TRACK_MODIFICATIONS is False


# ---------------------------------------------------------------------------
# Database connection tests
# ---------------------------------------------------------------------------

class TestDatabaseConnection:
    """Verify that utils.db.get_db_connection works correctly."""

    def test_get_db_connection_returns_connection(self, tmp_path):
        import utils.db as db_module

        original = db_module.DATABASE
        db_module.DATABASE = str(tmp_path / "conn_test.db")
        try:
            conn = db_module.get_db_connection()
            assert conn is not None
            conn.close()
        finally:
            db_module.DATABASE = original

    def test_connection_uses_row_factory(self, tmp_path):
        import utils.db as db_module

        original = db_module.DATABASE
        db_module.DATABASE = str(tmp_path / "row_test.db")
        try:
            conn = db_module.get_db_connection()
            assert conn.row_factory == sqlite3.Row
            conn.close()
        finally:
            db_module.DATABASE = original

    def test_connection_can_execute_query(self, tmp_path):
        import utils.db as db_module

        original = db_module.DATABASE
        db_module.DATABASE = str(tmp_path / "query_test.db")
        try:
            conn = db_module.get_db_connection()
            conn.execute(
                "CREATE TABLE IF NOT EXISTS ping (id INTEGER PRIMARY KEY)"
            )
            conn.commit()
            result = conn.execute("SELECT COUNT(*) FROM ping").fetchone()
            assert result[0] == 0
            conn.close()
        finally:
            db_module.DATABASE = original


# ---------------------------------------------------------------------------
# Route registration tests
# ---------------------------------------------------------------------------

class TestRouteRegistration:
    """Verify that all expected routes are registered in the app."""

    def _rules(self, app):
        return [rule.rule for rule in app.url_map.iter_rules()]

    def test_login_route_registered(self, app):
        assert any("login" in r for r in self._rules(app))

    def test_dashboard_route_registered(self, app):
        assert any("dashboard" in r for r in self._rules(app))

    def test_static_route_registered(self, app):
        assert "/static/<path:filename>" in self._rules(app)

    def test_login_redirects_unauthenticated(self, client):
        response = client.get("/dashboard", follow_redirects=False)
        # Unauthenticated access should redirect (302) or return 401/403
        assert response.status_code in (302, 401, 403)

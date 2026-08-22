import pytest
from django.core.exceptions import ImproperlyConfigured

from coffeetrace.config.database import SqlServerConfiguration

_REQUIRED_ENVIRONMENT = {
    "DB_PASSWORD": "UnitTestPassword2026!",
    "DB_NAME": "CoffeeTrace",
    "DB_USER": "coffeetrace_app",
    "DB_HOST": "localhost",
    "DB_PORT": "1433",
}


def configure_environment(monkeypatch) -> None:
    for name, value in _REQUIRED_ENVIRONMENT.items():
        monkeypatch.setenv(name, value)


def test_sql_server_is_the_only_runtime_engine(monkeypatch):
    configure_environment(monkeypatch)

    database = SqlServerConfiguration.from_environment().as_django_database()

    assert database["ENGINE"] == "mssql"
    assert database["NAME"] == "CoffeeTrace"
    assert database["USER"] == "coffeetrace_app"


def test_database_password_is_required(monkeypatch):
    configure_environment(monkeypatch)
    monkeypatch.delenv("DB_PASSWORD")

    with pytest.raises(ImproperlyConfigured):
        SqlServerConfiguration.from_environment()


def test_connection_security_options_are_explicit(monkeypatch):
    configure_environment(monkeypatch)
    monkeypatch.setenv("DB_ENCRYPT", "True")
    monkeypatch.setenv("DB_TRUST_SERVER_CERTIFICATE", "False")

    database = SqlServerConfiguration.from_environment().as_django_database()

    extra_params = database["OPTIONS"]["extra_params"]
    assert "Encrypt=yes" in extra_params
    assert "TrustServerCertificate=no" in extra_params

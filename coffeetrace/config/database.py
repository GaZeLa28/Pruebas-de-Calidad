"""SQL Server configuration for an already-existing CoffeeTrace database."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from coffeetrace.config.environment import Environment


@dataclass(frozen=True, slots=True)
class SqlServerConfiguration:
    """Build Django's SQL Server settings without creating database resources.

    The configuration is intentionally strict: CoffeeTrace supports SQL Server
    only in normal execution and requires explicit credentials. Django opens the
    connection lazily when a command or request needs database access.
    """

    name: str
    user: str
    password: str
    host: str
    port: str
    driver: str
    encrypt: bool
    trust_server_certificate: bool
    connection_timeout: int
    query_timeout: int
    connection_retries: int
    retry_backoff_seconds: int
    max_connection_age: int

    @classmethod
    def from_environment(cls) -> SqlServerConfiguration:
        return cls(
            name=Environment.get("DB_NAME", "CoffeeTrace"),
            user=Environment.get("DB_USER", "coffeetrace_app"),
            password=Environment.require("DB_PASSWORD"),
            host=Environment.get("DB_HOST", "localhost"),
            port=Environment.get("DB_PORT", "1433"),
            driver=Environment.get("DB_DRIVER", "ODBC Driver 18 for SQL Server"),
            encrypt=Environment.get_bool("DB_ENCRYPT", True),
            trust_server_certificate=Environment.get_bool(
                "DB_TRUST_SERVER_CERTIFICATE",
                True,
            ),
            connection_timeout=Environment.get_int(
                "DB_CONNECTION_TIMEOUT",
                10,
                minimum=1,
            ),
            query_timeout=Environment.get_int("DB_QUERY_TIMEOUT", 30, minimum=0),
            connection_retries=Environment.get_int(
                "DB_CONNECTION_RETRIES",
                2,
                minimum=0,
            ),
            retry_backoff_seconds=Environment.get_int(
                "DB_RETRY_BACKOFF_SECONDS",
                2,
                minimum=0,
            ),
            max_connection_age=Environment.get_int(
                "DB_CONN_MAX_AGE",
                60,
                minimum=0,
            ),
        )

    def as_django_database(self) -> dict[str, Any]:
        return {
            "ENGINE": "mssql",
            "NAME": self.name,
            "USER": self.user,
            "PASSWORD": self.password,
            "HOST": self.host,
            "PORT": self.port,
            "CONN_MAX_AGE": self.max_connection_age,
            "CONN_HEALTH_CHECKS": True,
            "OPTIONS": {
                "driver": self.driver,
                "extra_params": self._build_extra_params(),
                "connection_timeout": self.connection_timeout,
                "query_timeout": self.query_timeout,
                "connection_retries": self.connection_retries,
                "connection_retry_backoff_time": self.retry_backoff_seconds,
            },
        }

    def _build_extra_params(self) -> str:
        encrypt = "yes" if self.encrypt else "no"
        trust_certificate = "yes" if self.trust_server_certificate else "no"
        return f"Encrypt={encrypt};TrustServerCertificate={trust_certificate};MARS_Connection=yes"

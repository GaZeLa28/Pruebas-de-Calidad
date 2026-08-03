"""Read-only diagnostics for the configured SQL Server database."""

from __future__ import annotations

from dataclasses import dataclass

from django.db import connection


@dataclass(frozen=True, slots=True)
class DatabaseHealth:
    database_name: str
    login_name: str
    database_user: str
    server_name: str
    sql_server_version: str
    can_select: bool
    can_insert: bool
    can_update: bool
    can_delete: bool
    can_create_table: bool


class DatabaseHealthService:
    """Inspect connection identity and permissions without changing the database."""

    _QUERY = """
        SELECT
            DB_NAME() AS database_name,
            ORIGINAL_LOGIN() AS login_name,
            USER_NAME() AS database_user,
            CAST(SERVERPROPERTY('ServerName') AS nvarchar(128)) AS server_name,
            CAST(SERVERPROPERTY('ProductVersion') AS nvarchar(128)) AS sql_server_version,
            HAS_PERMS_BY_NAME(DB_NAME(), 'DATABASE', 'SELECT') AS can_select,
            HAS_PERMS_BY_NAME(DB_NAME(), 'DATABASE', 'INSERT') AS can_insert,
            HAS_PERMS_BY_NAME(DB_NAME(), 'DATABASE', 'UPDATE') AS can_update,
            HAS_PERMS_BY_NAME(DB_NAME(), 'DATABASE', 'DELETE') AS can_delete,
            HAS_PERMS_BY_NAME(DB_NAME(), 'DATABASE', 'CREATE TABLE') AS can_create_table;
    """

    @classmethod
    def inspect(cls) -> DatabaseHealth:
        with connection.cursor() as cursor:
            cursor.execute(cls._QUERY)
            row = cursor.fetchone()

        if row is None:
            raise RuntimeError("SQL Server no devolvió información de conexión.")

        return DatabaseHealth(
            database_name=str(row[0]),
            login_name=str(row[1]),
            database_user=str(row[2]),
            server_name=str(row[3]),
            sql_server_version=str(row[4]),
            can_select=bool(row[5]),
            can_insert=bool(row[6]),
            can_update=bool(row[7]),
            can_delete=bool(row[8]),
            can_create_table=bool(row[9]),
        )

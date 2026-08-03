"""Django command that verifies the existing SQL Server connection."""

from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError

from apps.common.database_health import DatabaseHealthService


class Command(BaseCommand):
    help = "Verifica la conexión y permisos sin crear ni modificar objetos."

    def handle(self, *args, **options):
        try:
            health = DatabaseHealthService.inspect()
        except DatabaseError as exc:
            raise CommandError(
                "No fue posible conectarse a SQL Server. Revise .env, TCP/IP, "
                "el puerto y ODBC Driver 18."
            ) from exc

        self.stdout.write(self.style.SUCCESS("Conexión con SQL Server correcta."))
        self.stdout.write(f"Servidor: {health.server_name}")
        self.stdout.write(f"Versión: {health.sql_server_version}")
        self.stdout.write(f"Base de datos: {health.database_name}")
        self.stdout.write(f"Login: {health.login_name}")
        self.stdout.write(f"Usuario de base: {health.database_user}")
        self.stdout.write("Permisos detectados:")
        self.stdout.write(f"  SELECT: {self._yes_no(health.can_select)}")
        self.stdout.write(f"  INSERT: {self._yes_no(health.can_insert)}")
        self.stdout.write(f"  UPDATE: {self._yes_no(health.can_update)}")
        self.stdout.write(f"  DELETE: {self._yes_no(health.can_delete)}")
        self.stdout.write(
            f"  CREATE TABLE: {self._yes_no(health.can_create_table)}"
        )

    @staticmethod
    def _yes_no(value: bool) -> str:
        return "sí" if value else "no"

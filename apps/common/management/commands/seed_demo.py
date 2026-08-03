from __future__ import annotations

import os

from django.core.management.base import BaseCommand

from apps.common.demo_data import DemoDataSeeder


class Command(BaseCommand):
    help = "Crea usuarios y datos demostrativos idempotentes para CoffeeTrace."

    def add_arguments(self, parser):
        parser.add_argument(
            "--admin-password",
            default=os.getenv("DEMO_ADMIN_PASSWORD", "CoffeeTrace2026!"),
            help="Contraseña del usuario admin de demostración.",
        )

    def handle(self, *args, **options):
        admin_password = options["admin_password"]
        DemoDataSeeder.seed(admin_password=admin_password)
        self._write_result(admin_password=admin_password)

    def _write_result(self, *, admin_password: str) -> None:
        self.stdout.write(self.style.SUCCESS("Datos demo creados o actualizados."))
        self.stdout.write("Usuario: admin")
        self.stdout.write(f"Contraseña: {admin_password}")
        self.stdout.write(
            self.style.WARNING(
                "Cambie todas las contraseñas antes de una entrega real."
            )
        )

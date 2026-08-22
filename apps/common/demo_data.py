"""Idempotent demo data creation kept outside management commands."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import UserRole
from apps.accounts.services import UserService
from apps.lots.models import Lot, LotStatus
from apps.lots.services import LotService, QRCodeService
from apps.producers.models import Farm, Producer
from apps.receptions.models import CoffeeReception
from apps.receptions.services import ReceptionService
from apps.traceability.models import TraceabilityEventType
from apps.traceability.services import TraceabilityService


@dataclass(frozen=True, slots=True)
class DemoAccounts:
    administrator: object
    operator: object


class DemoDataSeeder:
    """Create a coherent CoffeeTrace demonstration scenario."""

    @classmethod
    @transaction.atomic
    def seed(cls, *, admin_password: str) -> None:
        accounts = cls._create_accounts(admin_password=admin_password)
        producer = cls._get_or_create_producer(actor=accounts.administrator)
        farm = cls._get_or_create_farm(producer=producer, actor=accounts.administrator)
        reception = cls._get_or_create_reception(
            producer=producer,
            farm=farm,
            actor=accounts.operator,
        )
        lot = cls._get_or_create_lot(actor=accounts.administrator)
        cls._associate_reception(lot=lot, reception=reception, actor=accounts.operator)
        QRCodeService.get_or_create(lot=lot, actor=accounts.administrator)
        cls._create_traceability_events(
            lot=lot,
            reception=reception,
            administrator=accounts.administrator,
            operator=accounts.operator,
        )

    @classmethod
    def _create_accounts(cls, *, admin_password: str) -> DemoAccounts:
        administrator = cls._get_or_create_user(
            username="admin",
            password=admin_password,
            role=UserRole.ADMIN,
            first_name="Administrador",
            last_name="CoffeeTrace",
            email="admin@coffeetrace.local",
            is_staff=True,
            is_superuser=True,
        )
        operator = cls._get_or_create_user(
            username="operador",
            password="Operador2026!",
            role=UserRole.OPERATOR,
            first_name="Ana",
            last_name="Vargas",
            email="operador@coffeetrace.local",
        )
        cls._get_or_create_user(
            username="auditor",
            password="Auditor2026!",
            role=UserRole.AUDITOR,
            first_name="Carlos",
            last_name="Solano",
            email="auditor@coffeetrace.local",
        )
        return DemoAccounts(administrator=administrator, operator=operator)

    @staticmethod
    def _get_or_create_user(*, username: str, password: str, role: str, **data):
        user_model = get_user_model()
        user = user_model.objects.filter(username=username).first()
        if user is None:
            return UserService.create_user(
                username=username,
                password=password,
                role=role,
                **data,
            )
        return UserService.update_user(
            user=user,
            password=password,
            role=role,
            **data,
        )

    @staticmethod
    def _get_or_create_producer(*, actor) -> Producer:
        producer, _ = Producer.objects.get_or_create(
            code="PROD-001",
            defaults={
                "national_id": "1-1111-1111",
                "full_name": "María Fernández Rojas",
                "email": "maria@example.com",
                "phone": "8888-1111",
                "address": "San Marcos de Tarrazú, San José",
                "created_by": actor,
            },
        )
        return producer

    @staticmethod
    def _get_or_create_farm(*, producer: Producer, actor) -> Farm:
        farm, _ = Farm.objects.get_or_create(
            code="FIN-001",
            defaults={
                "producer": producer,
                "name": "Finca El Mirador",
                "province": "San José",
                "canton": "Tarrazú",
                "district": "San Marcos",
                "address": "2 km al norte del centro",
                "altitude_masl": 1650,
                "area_hectares": Decimal("8.50"),
                "certification": "C.A.F.E. Practices",
                "created_by": actor,
            },
        )
        return farm

    @staticmethod
    def _get_or_create_reception(
        *,
        producer: Producer,
        farm: Farm,
        actor,
    ) -> CoffeeReception:
        reception = CoffeeReception.objects.filter(code="REC-2026-001").first()
        if reception is not None:
            return reception
        return ReceptionService.create(
            actor=actor,
            validated_data={
                "code": "REC-2026-001",
                "producer": producer,
                "farm": farm,
                "received_at": timezone.now(),
                "coffee_variety": "Caturra",
                "process_type": "Lavado",
                "gross_weight_kg": Decimal("500.00"),
                "tare_weight_kg": Decimal("20.00"),
                "declared_net_weight_kg": Decimal("480.00"),
                "moisture_percentage": Decimal("11.80"),
                "notes": "Datos demostrativos del proyecto académico.",
            },
        )

    @staticmethod
    def _get_or_create_lot(*, actor) -> Lot:
        lot, _ = Lot.objects.get_or_create(
            code="LOT-2026-001",
            defaults={
                "name": "Cosecha Tarrazú Selección",
                "harvest_year": 2026,
                "warehouse_location": "Bodega A · Estante 03",
                "status": LotStatus.IN_PROCESS,
                "created_by": actor,
            },
        )
        return lot

    @staticmethod
    def _associate_reception(*, lot: Lot, reception: CoffeeReception, actor) -> None:
        LotService.associate_reception(
            lot=lot,
            reception=reception,
            assigned_weight=Decimal("480.00"),
            actor=actor,
        )

    @classmethod
    def _create_traceability_events(
        cls,
        *,
        lot: Lot,
        reception: CoffeeReception,
        administrator,
        operator,
    ) -> None:
        if lot.traceability_events.exists():
            return
        cls._create_reception_event(lot=lot, reception=reception, actor=operator)
        cls._create_association_event(lot=lot, actor=administrator)

    @staticmethod
    def _create_reception_event(*, lot: Lot, reception: CoffeeReception, actor) -> None:
        TraceabilityService.create_event(
            actor=actor,
            validated_data={
                "lot": lot,
                "reception": reception,
                "event_type": TraceabilityEventType.RECEPTION,
                "occurred_at": timezone.now(),
                "location": "Punto de recepción central",
                "description": "Recepción y validación inicial del café entregado.",
                "metadata": {"moisture_percentage": "11.8"},
            },
        )

    @staticmethod
    def _create_association_event(*, lot: Lot, actor) -> None:
        TraceabilityService.create_event(
            actor=actor,
            validated_data={
                "lot": lot,
                "event_type": TraceabilityEventType.ASSOCIATION,
                "occurred_at": timezone.now(),
                "location": "Bodega A",
                "description": "Materia prima asociada y lote consolidado.",
                "metadata": {"assigned_weight_kg": "480.00"},
            },
        )

from decimal import Decimal

from django.utils import timezone

from apps.accounts.models import UserRole
from apps.accounts.services import UserService
from apps.producers.models import Farm, Producer
from apps.receptions.services import ReceptionService


def create_user(*, username="admin", role=UserRole.ADMIN):
    return UserService.create_user(
        username=username,
        password="StrongPass2026!",
        role=role,
        email=f"{username}@example.com",
    )


def create_origin(*, actor):
    producer = Producer.objects.create(
        code="P-001",
        national_id="1-0000-0001",
        full_name="Productor de prueba",
        created_by=actor,
    )
    farm = Farm.objects.create(
        producer=producer,
        code="F-001",
        name="Finca de prueba",
        province="San José",
        canton="Tarrazú",
        district="San Marcos",
        created_by=actor,
    )
    reception = ReceptionService.create(
        actor=actor,
        validated_data={
            "code": "R-001",
            "producer": producer,
            "farm": farm,
            "received_at": timezone.now(),
            "coffee_variety": "Caturra",
            "gross_weight_kg": Decimal("110.00"),
            "tare_weight_kg": Decimal("10.00"),
            "declared_net_weight_kg": Decimal("100.00"),
        },
    )
    return producer, farm, reception

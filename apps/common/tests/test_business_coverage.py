from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.accounts.models import UserRole
from apps.common.tests.factories import create_origin, create_user
from apps.lots.models import LotStatus
from apps.lots.services import LotService, QRCodeService
from apps.producers.models import Farm, Producer
from apps.producers.selectors import FarmSelector, ProducerSelector
from apps.receptions.models import (
    ReceptionStatus,
    WeightInconsistencyStatus,
)
from apps.receptions.services import (
    InconsistencyService,
    ReceptionService,
)
from apps.reports.services import (
    DateRange,
    ReportDataService,
    ReportExportDataService,
    ReportQueryService,
)


@pytest.mark.django_db
def test_created_admin_keeps_admin_role():
    user = create_user(username="coverage-admin")

    assert user.profile.role == UserRole.ADMIN


@pytest.mark.django_db
def test_selectors_and_report_queries():
    actor = create_user(username="report-admin")
    producer, farm, reception = create_origin(actor=actor)

    producers = list(ProducerSelector.list_with_farms())
    farms = list(FarmSelector.list_detailed())

    assert producers[0].pk == producer.pk
    assert farms[0].pk == farm.pk

    report_date = timezone.localdate(reception.received_at)
    date_range = DateRange(
        start_date=report_date,
        end_date=report_date,
    )

    producer_rows = ReportDataService.producer_rows(
        date_range=date_range,
    )

    assert producer_rows[0]["producer_code"] == producer.code
    assert Decimal(producer_rows[0]["received_weight_kg"]) == Decimal("100.00")

    reception_rows = list(
        ReportQueryService.reception_detail(
            date_range=date_range,
        )
    )

    assert reception_rows[0].pk == reception.pk

    lot = LotService.create(
        actor=actor,
        validated_data={
            "code": "L-REPORT",
            "name": "Lote de reporte",
            "harvest_year": 2026,
        },
    )

    lot_rows = ReportDataService.lot_rows(
        harvest_year=2026,
    )

    assert lot_rows[0]["lot_code"] == lot.code

    empty_year = list(
        ReportQueryService.lots_summary(
            harvest_year=1999,
        )
    )

    assert empty_year == []


def test_report_export_payloads(monkeypatch):
    monkeypatch.setattr(
        ReportDataService,
        "producer_rows",
        lambda *, date_range: [
            {
                "producer_code": "P-100",
                "producer_name": "Productor prueba",
                "national_id": "1-1111-1111",
                "reception_count": 2,
                "received_weight_kg": "200.00",
            }
        ],
    )

    producer_payload = ReportExportDataService.build(
        report_type="producers",
        date_range=DateRange(),
        harvest_year=None,
    )

    assert producer_payload.title == ("CoffeeTrace - Recepciones por productor")
    assert producer_payload.rows[0][0] == "P-100"

    monkeypatch.setattr(
        ReportDataService,
        "lot_rows",
        lambda *, harvest_year: [
            {
                "lot_code": "L-100",
                "lot_name": "Lote prueba",
                "harvest_year": 2026,
                "status": "Borrador",
                "total_weight_kg": "100.00",
                "origin_count": 1,
                "producer_count": 1,
                "event_count": 0,
            }
        ],
    )

    lot_payload = ReportExportDataService.build(
        report_type="lots",
        date_range=DateRange(),
        harvest_year=2026,
    )

    assert lot_payload.title == "CoffeeTrace - Reporte por lote"
    assert lot_payload.rows[0][0] == "L-100"


@pytest.mark.django_db
def test_reception_inconsistency_lifecycle():
    actor = create_user(username="reception-admin")

    producer = Producer.objects.create(
        code="P-INC",
        national_id="1-2000-3000",
        full_name="Productor inconsistencia",
        created_by=actor,
    )

    farm = Farm.objects.create(
        producer=producer,
        code="F-INC",
        name="Finca inconsistencia",
        province="San José",
        canton="Tarrazú",
        district="San Marcos",
        created_by=actor,
    )

    reception = ReceptionService.create(
        actor=actor,
        validated_data={
            "code": "R-INC",
            "producer": producer,
            "farm": farm,
            "received_at": timezone.now(),
            "coffee_variety": "Caturra",
            "gross_weight_kg": Decimal("110.00"),
            "tare_weight_kg": Decimal("10.00"),
            "declared_net_weight_kg": Decimal("90.00"),
        },
    )

    assert reception.status == ReceptionStatus.INCONSISTENT

    inconsistency = reception.weight_inconsistencies.get()
    assert inconsistency.status == WeightInconsistencyStatus.OPEN

    ReceptionService.update(
        reception=reception,
        validated_data={
            "declared_net_weight_kg": Decimal("100.00"),
        },
    )

    inconsistency.refresh_from_db()

    assert reception.status == ReceptionStatus.VALIDATED
    assert inconsistency.status == WeightInconsistencyStatus.RESOLVED

    second_reception = ReceptionService.create(
        actor=actor,
        validated_data={
            "code": "R-INC-2",
            "producer": producer,
            "farm": farm,
            "received_at": timezone.now(),
            "coffee_variety": "Catuaí",
            "gross_weight_kg": Decimal("110.00"),
            "tare_weight_kg": Decimal("10.00"),
            "declared_net_weight_kg": Decimal("80.00"),
        },
    )

    second_inconsistency = second_reception.weight_inconsistencies.get()

    InconsistencyService.resolve(
        inconsistency=second_inconsistency,
        actor=actor,
        notes="Verificada manualmente.",
    )

    assert second_inconsistency.status == WeightInconsistencyStatus.RESOLVED

    with pytest.raises(ValidationError):
        InconsistencyService.resolve(
            inconsistency=second_inconsistency,
            actor=actor,
            notes="Segundo intento.",
        )


@pytest.mark.django_db
def test_lot_lifecycle_and_validation_rules():
    actor = create_user(username="lot-admin")
    _, _, reception = create_origin(actor=actor)

    lot = LotService.create(
        actor=actor,
        validated_data={
            "code": "L-COVERAGE",
            "name": "Lote de cobertura",
            "harvest_year": 2026,
        },
    )

    link = LotService.associate_reception(
        lot=lot,
        reception=reception,
        assigned_weight=Decimal("50.00"),
        actor=actor,
    )

    lot.refresh_from_db()
    assert lot.total_weight_kg == Decimal("50.00")

    LotService.update(
        lot=lot,
        validated_data={
            "name": "Lote actualizado",
            "status": LotStatus.IN_PROCESS,
        },
    )

    assert lot.name == "Lote actualizado"
    assert lot.status == LotStatus.IN_PROCESS

    qr_code = QRCodeService.get_or_create(
        lot=lot,
        actor=actor,
    )

    qr_code.is_active = False
    qr_code.save(update_fields=["is_active"])

    qr_code = QRCodeService.get_or_create(
        lot=lot,
        actor=actor,
    )

    assert qr_code.is_active is True

    LotService.remove_reception(link=link)

    lot.refresh_from_db()
    assert lot.total_weight_kg == Decimal("0.00")

    lot.is_active = False
    lot.save(update_fields=["is_active"])

    with pytest.raises(ValidationError):
        LotService.associate_reception(
            lot=lot,
            reception=reception,
            assigned_weight=Decimal("10.00"),
            actor=actor,
        )

    lot.is_active = True
    lot.save(update_fields=["is_active"])

    reception.status = ReceptionStatus.INCONSISTENT
    reception.save(update_fields=["status"])

    with pytest.raises(ValidationError):
        LotService.associate_reception(
            lot=lot,
            reception=reception,
            assigned_weight=Decimal("10.00"),
            actor=actor,
        )

    reception.status = ReceptionStatus.VALIDATED
    reception.save(update_fields=["status"])

    with pytest.raises(ValidationError):
        LotService.associate_reception(
            lot=lot,
            reception=reception,
            assigned_weight=Decimal("101.00"),
            actor=actor,
        )

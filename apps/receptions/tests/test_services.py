from decimal import Decimal

import pytest
from rest_framework.exceptions import ValidationError

from apps.receptions.services import WeightValidationService


class TestWeightValidationService:
    def test_calculates_net_weight(self):
        result = WeightValidationService.calculate_net(
            gross_weight=Decimal("120.50"),
            tare_weight=Decimal("20.25"),
        )
        assert result == Decimal("100.25")

    def test_rejects_tare_equal_to_gross(self):
        with pytest.raises(ValidationError):
            WeightValidationService.calculate_net(
                gross_weight=Decimal("20.00"),
                tare_weight=Decimal("20.00"),
            )

    def test_accepts_difference_inside_tolerance(self, settings):
        settings.WEIGHT_TOLERANCE_KG = "0.50"
        assert WeightValidationService.is_consistent(
            declared_weight=Decimal("100.40"),
            calculated_weight=Decimal("100.00"),
        )

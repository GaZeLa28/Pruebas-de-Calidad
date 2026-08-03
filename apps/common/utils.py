from decimal import ROUND_HALF_UP, Decimal

TWO_DECIMALS = Decimal("0.01")


def quantize_weight(value: Decimal) -> Decimal:
    return value.quantize(TWO_DECIMALS, rounding=ROUND_HALF_UP)

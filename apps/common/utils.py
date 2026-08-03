from decimal import Decimal, ROUND_HALF_UP
TWO_DECIMALS = Decimal("0.01")
def quantize_weight(value: Decimal) -> Decimal:
    return value.quantize(TWO_DECIMALS, rounding=ROUND_HALF_UP)

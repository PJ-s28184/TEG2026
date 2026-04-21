"""Layer 8 — Tools. Deterministyczny silnik podatkowy (skala / liniowy / ryczałt)."""

BRACKET_THRESHOLD = 120_000
LOWER_RATE = 0.12
UPPER_RATE = 0.32
TAX_REDUCING_AMOUNT = 3_600
FLAT_RATE = 0.19
INTERNET_DEDUCTION_CAP = 760


def skala_podatkowa(income, deductions=0):
    base = max(0, income - deductions)
    if base <= BRACKET_THRESHOLD:
        tax = base * LOWER_RATE - TAX_REDUCING_AMOUNT
    else:
        tax = 10_800 + (base - BRACKET_THRESHOLD) * UPPER_RATE
    return {"metoda": "skala podatkowa (12% / 32%)", "podstawa": base, "podatek": max(0, round(tax, 2))}


def podatek_liniowy(income, deductions=0):
    base = max(0, income - deductions)
    return {"metoda": "podatek liniowy 19%", "podstawa": base, "podatek": round(base * FLAT_RATE, 2)}


def ryczalt(revenue, rate=0.085):
    return {"metoda": f"ryczałt {rate * 100:.1f}%", "podstawa": revenue, "podatek": round(revenue * rate, 2)}


def compare(income, deductions=0, ryczalt_rate=0.085):
    return [
        skala_podatkowa(income, deductions),
        podatek_liniowy(income, deductions),
        ryczalt(income, ryczalt_rate),
    ]

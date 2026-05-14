"""Layer 8 — Tools. Deterministyczny silnik podatkowy (skala / liniowy / ryczałt)."""

BRACKET_THRESHOLD = 120_000
LOWER_RATE = 0.12
UPPER_RATE = 0.32
TAX_REDUCING_AMOUNT = 3_600
FLAT_RATE = 0.19
INTERNET_DEDUCTION_CAP = 760


def skala_podatkowa(income, deductions=0):
    base = max(0, income - deductions)
    operacje = []
    if base <= BRACKET_THRESHOLD:
        tax_raw = base * LOWER_RATE - TAX_REDUCING_AMOUNT
        tax = max(0, tax_raw)
        operacje.append(f"{base:,} zł × 12% = {base * LOWER_RATE:,.2f} zł")
        operacje.append(f"− kwota zmniejszająca podatek: {TAX_REDUCING_AMOUNT:,} zł")
        operacje.append(f"= {tax:,.2f} zł")
    else:
        lower_tax = BRACKET_THRESHOLD * LOWER_RATE - TAX_REDUCING_AMOUNT  # 10 800
        upper_excess = base - BRACKET_THRESHOLD
        upper_tax = upper_excess * UPPER_RATE
        tax = lower_tax + upper_tax
        operacje.append(f"Pierwszy próg: 120 000 zł × 12% = {BRACKET_THRESHOLD * LOWER_RATE:,.2f} zł")
        operacje.append(f"− Kwota zmniejszająca podatek: {TAX_REDUCING_AMOUNT:,} zł")
        operacje.append(f"= {lower_tax:,.2f} zł")
        operacje.append(f"Drugi próg: ({base:,} − 120 000) = {upper_excess:,} zł × 32% = {upper_tax:,.2f} zł")
        operacje.append(f"Suma: {lower_tax:,.2f} + {upper_tax:,.2f} = {round(tax, 2):,.2f} zł")
    return {
        "metoda": "skala podatkowa (12% / 32%)",
        "podstawa": base,
        "podatek": round(tax, 2),
        "operacje": operacje,
    }


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

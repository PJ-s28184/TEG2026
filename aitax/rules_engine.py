from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class TaxScenario:
    income: float
    expenses: float = 0.0
    internet_expenses: float = 0.0
    children: int = 0
    married: bool = False
    under_26_income: float = 0.0
    taxation_form: str = "scale"
    lump_sum_rate: float = 0.085


@dataclass
class RuleResult:
    name: str
    amount: float
    explanation: str
    source: str


@dataclass
class TaxCalculation:
    taxable_income: float
    tax_due: float
    results: list[RuleResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "taxable_income": self.taxable_income,
            "tax_due": self.tax_due,
            "results": [asdict(result) for result in self.results],
            "warnings": self.warnings,
        }


class TaxRulesEngine:
    """Deterministic PIT demo rules kept separate from RAG/LLM generation."""

    INTERNET_LIMIT = 760.0
    UNDER_26_LIMIT = 85_528.0
    SCALE_THRESHOLD = 120_000.0
    TAX_REDUCTION = 3_600.0
    FIRST_BRACKET_RATE = 0.12
    SECOND_BRACKET_RATE = 0.32
    SECOND_BRACKET_FIXED_TAX = 10_800.0

    def calculate(self, scenario: TaxScenario) -> TaxCalculation:
        results: list[RuleResult] = []
        warnings: list[str] = []

        base_income = max(0.0, scenario.income - scenario.expenses)
        if scenario.expenses:
            results.append(
                RuleResult(
                    name="Koszty uzyskania przychodow",
                    amount=scenario.expenses,
                    explanation="Koszty pomniejszaja przychod, jezeli sluza uzyskaniu albo zabezpieczeniu przychodu.",
                    source="pit-definicja-kosztow-uzyskania.txt | Art. 22",
                )
            )

        under_26_exempt = min(max(0.0, scenario.under_26_income), self.UNDER_26_LIMIT)
        if under_26_exempt:
            base_income = max(0.0, base_income - under_26_exempt)
            results.append(
                RuleResult(
                    name="Ulga dla mlodych",
                    amount=under_26_exempt,
                    explanation="Przychody podatnika do ukonczenia 26 lat sa zwolnione do limitu 85 528 zl.",
                    source="pit-ulga-26.txt | Art. 21",
                )
            )

        internet_deduction = min(max(0.0, scenario.internet_expenses), self.INTERNET_LIMIT)
        if internet_deduction:
            base_income = max(0.0, base_income - internet_deduction)
            results.append(
                RuleResult(
                    name="Ulga internetowa",
                    amount=internet_deduction,
                    explanation="Odliczenie wydatkow na Internet jest limitowane do 760 zl rocznie.",
                    source="pit-ulga-internet.txt | Art. 26",
                )
            )

        tax_due = self._calculate_tax(base_income, scenario)

        child_credit = self._child_credit(scenario.children, scenario.income, scenario.married)
        if child_credit:
            tax_due = max(0.0, tax_due - child_credit)
            results.append(
                RuleResult(
                    name="Ulga na dzieci",
                    amount=child_credit,
                    explanation="Ulga pomniejsza podatek wedlug miesiecznych kwot zależnych od liczby dzieci.",
                    source="pit-ulga-dziecko.txt | Art. 27f",
                )
            )

        if scenario.taxation_form not in {"scale", "linear", "lump_sum"}:
            warnings.append("Nieznana forma opodatkowania; zastosowano skale podatkowa.")

        return TaxCalculation(
            taxable_income=round(base_income, 2),
            tax_due=round(max(0.0, tax_due), 2),
            results=results,
            warnings=warnings,
        )

    def _calculate_tax(self, taxable_income: float, scenario: TaxScenario) -> float:
        form = scenario.taxation_form
        if form == "linear":
            return taxable_income * 0.19
        if form == "lump_sum":
            return max(0.0, scenario.income) * scenario.lump_sum_rate
        if taxable_income <= self.SCALE_THRESHOLD:
            return max(0.0, taxable_income * self.FIRST_BRACKET_RATE - self.TAX_REDUCTION)
        return self.SECOND_BRACKET_FIXED_TAX + (taxable_income - self.SCALE_THRESHOLD) * self.SECOND_BRACKET_RATE

    @staticmethod
    def _child_credit(children: int, income: float, married: bool) -> float:
        if children <= 0:
            return 0.0
        if children == 1:
            limit = 112_000.0 if married else 56_000.0
            if income > limit:
                return 0.0
            return 92.67 * 12
        if children == 2:
            return 92.67 * 12 * 2
        return (92.67 * 12 * 2) + (166.67 * 12) + max(0, children - 3) * 225.0 * 12

    def compare(self, income: float, expenses: float, lump_sum_rate: float = 0.085) -> dict:
        scenarios = {
            "scale": TaxScenario(income=income, expenses=expenses, taxation_form="scale"),
            "linear": TaxScenario(income=income, expenses=expenses, taxation_form="linear"),
            "lump_sum": TaxScenario(
                income=income,
                expenses=expenses,
                taxation_form="lump_sum",
                lump_sum_rate=lump_sum_rate,
            ),
        }
        calculations = {
            name: self.calculate(scenario).to_dict()
            for name, scenario in scenarios.items()
        }
        best = min(calculations, key=lambda key: calculations[key]["tax_due"])
        return {"calculations": calculations, "best_option": best}

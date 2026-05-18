import sys
from pathlib import Path

# Dodajemy katalog główny projektu do sys.path zanim zaimportujemy config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from test.config import PROMPTS_FILE

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
SKIP = "\033[93mSKIP\033[0m"
_results = []


def check(label, condition, detail=""):
    status = PASS if condition else FAIL
    suffix = f"  ({detail})" if detail else ""
    print(f"  [{status}] {label}{suffix}")
    _results.append((label, condition))
    return condition


# ---- BLOK 1: logika deterministyczna (bez LLM) ------------------------------

def test_logic():
    from aitax.layer9_agent import (
        _extract_amounts, _extract_profile, _extract_expenses, _is_multi_source,
    )
    import aitax.layer8_tools as tools

    print("\n" + "=" * 60)
    print("BLOK 1 - Logika deterministyczna (bez LLM)")
    print("=" * 60)

    print("\n[_extract_amounts]")
    check("60 000 PLN",  _extract_amounts("60 000 PLN rocznie") == [60000])
    check("3 miliony",   _extract_amounts("3 miliony zlotych") == [3000000])
    check("kilka kwot",  _extract_amounts("60 000, 1 200, 2 400, 3 600") == [60000, 1200, 2400, 3600])

    print("\n[_extract_profile]")
    check("wiek 23",        _extract_profile("Mam 23 lata")["wiek"] == 23)
    check("ulga26 ponizej", _extract_profile("ponizej 26 lat")["wiek"] == 25)
    check("2 dzieci",       _extract_profile("mam 2 dzieci")["dzieci"] == 2)
    check("jedno dziecko",  _extract_profile("mam jedno dziecko")["dzieci"] == 1)

    print("\n[_is_multi_source]")
    qm = "zarabiajacym 40 000 PLN z pracy i 25 000 PLN z freelancingu"
    qs = "zarabiajacym 60 000 PLN rocznie"
    check("multi-source TAK", _is_multi_source(qm))
    check("multi-source NIE", not _is_multi_source(qs))

    print("\n[_extract_expenses]")
    qe = "60 000 PLN rocznie. Moje wydatki to: internet (1 200 PLN), oprogramowanie (2 400 PLN), biuro domowe (3 600 PLN)"
    qn = "Zarabiam 80 000 PLN rocznie."
    got = _extract_expenses(qe)
    check("wydatki = 7200",    got == 7200, f"got {got}")
    check("brak wydatkow = 0", _extract_expenses(qn) == 0)

    print("\n[layer8_tools.skala_podatkowa]")
    r = tools.skala_podatkowa(60000)
    check("60k -> 3600",   r["podatek"] == 3600.0,  f"got {r['podatek']}")
    r2 = tools.skala_podatkowa(60000, 7200)
    exp2 = round(max(0, (60000 - 7200) * 0.12 - 3600), 2)
    check("60k-7200 -> 2736", r2["podatek"] == exp2, f"got {r2['podatek']}, exp {exp2}")
    r3 = tools.skala_podatkowa(300000)
    exp3 = round(10800 + (300000 - 120000) * 0.32, 2)
    check("300k -> 68400", r3["podatek"] == exp3,  f"got {r3['podatek']}")
    r4 = tools.skala_podatkowa(65000)
    exp4 = round(65000 * 0.12 - 3600, 2)
    check("65k -> 4200",   r4["podatek"] == exp4,  f"got {r4['podatek']}")

    print("\n[layer8_tools.compare]")
    sc = tools.compare(80000, 20000)
    check("3 warianty",      len(sc) == 3)
    check("skala w compare", any("skala" in s["metoda"] for s in sc))
    check("liniowy w compare", any("liniowy" in s["metoda"] for s in sc))


# ---- BLOK 2: routing intencji -----------------------------------------------

def test_routing():
    print("\n" + "=" * 60)
    print("BLOK 2 - Routing intencji (bez LLM)")
    print("=" * 60)

    class FakeStore:
        chunks = []
        matrix = None
        def search(self, *a, **kw): return []

    from aitax.layer9_agent import Advisor
    adv = Advisor.__new__(Advisor)
    adv.store = FakeStore()

    cases = [
        ("Ile odprowadze podatku?",                             "calculate"),
        ("Oblicz moj podatek",                                  "calculate"),
        ("Jaki bedzie moj podatek PIT?",                        "calculate"),
        ("Mam 2 dzieci i zarabiam 80 000 zl. Ile wyniesie moj podatek?", "calculate"),
        # routing sprawdza "porówn" z diacritic; podajemy wersję z polskimi znakami
        ("Chcę porównać ryczalt i skalę podatkową",             "compare"),
        ("Czym jest kwota wolna od podatku?",                   "explain"),
        ("Jakie wydatki moge odliczyc?",                        "explain"),
    ]
    for q, expected in cases:
        got = adv._route(q)
        check(f"route '{q}'", got == expected, f"got={got}, exp={expected}")


# ---- BLOK 3: _calculate deterministyczny ------------------------------------

def test_calculate():
    print("\n" + "=" * 60)
    print("BLOK 3 - _calculate deterministyczny (bez LLM)")
    print("=" * 60)

    class FakeStore:
        chunks = []
        matrix = None
        def search(self, *a, **kw): return []

    from aitax.layer9_agent import Advisor
    adv = Advisor.__new__(Advisor)
    adv.store = FakeStore()

    # Uwaga: Python f"{2736:,}" = "2,736"  (separator = przecinek, nie spacja)
    tests = [
        {
            "label": "Test-2: freelancer 60k, wydatki 7200 -> podatek 2,736",
            "q": ("Jestem freelancerem zarabiajacym 60 000 PLN rocznie. "
                  "Moje wydatki to: internet (1 200 PLN), oprogramowanie (2 400 PLN), "
                  "biuro domowe (3 600 PLN na amortyzacje). Jaki bedzie moj podatek PIT?"),
            "contains": ["2,736", "7,200", "52,800"],
        },
        {
            "label": "Test-6: nauczyciel+freelancer 40k+25k=65k -> podatek 4,200",
            "q": ("Jestem nauczycielem-freelancerem zarabiajacym 40 000 PLN z pracy "
                  "i 25 000 PLN z freelancingu. Jakie odliczenia moge zastosowac i jaki bedzie moj podatek?"),
            "contains": ["65,000", "4,200"],
        },
        {
            "label": "Test: 300 000 zl -> podatek 68,400",
            "q": "Moj dochod roczny wynosi 300 000 zl. Ile odprowadze podatku?",
            "contains": ["68,400"],
        },
        {
            "label": "Test: ulga dla mlodych (23 lata, 85k)",
            "q": "Mam 23 lata i mam roczny dochod rowny 85 000 zl. Ile odprowadze podatku?",
            "contains": ["23 lat", "Ulga dla"],
        },
        {
            "label": "Test: ulga prorodzinna (2 dzieci, 80k)",
            "q": "Mam 2 dzieci i zarabiam 80 000 zl rocznie. Ile wyniesie moj podatek?",
            # 80k*12%-3600=6000, ulga prorodzinna 2 dzieci=2224.08, podatek=3775.92
            "contains": ["prorodzinna", "3,775", "2,224"],
        },
        {
            "label": "Test: danina solidarnosciowa (3 mln)",
            "q": "Moj dochod roczny wynosi 3 000 000 zl. Ile odprowadze podatku?",
            "contains": ["solidarno", "4%"],
        },
    ]

    for t in tests:
        result = adv._calculate(t["q"])
        print(f"\n  >> {t['label']}")
        for frag in t["contains"]:
            check(f"   zawiera '{frag}'", frag in result)


# ---- BLOK 4: pelny Advisor z LLM (wymaga Ollama) ----------------------------

def test_full_advisor():
    print("\n" + "=" * 60)
    print("BLOK 4 - Pelny Advisor z LLM (wymaga Ollama)")
    print("=" * 60)

    with open(PROMPTS_FILE, encoding="utf-8") as f:
        prompts = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    print(f"  Zaladowano {len(prompts)} pytan z test_prompts.txt")

    try:
        from aitax import Advisor
        print("  Inicjalizacja Advisora (ladowanie embeddingow)...")
        advisor = Advisor()
        print("  OK - Ollama dostepna\n")
    except Exception as e:
        print(f"  [{SKIP}] Ollama niedostepna: {e}")
        print("  Aby uruchomic pelne testy: ollama serve")
        return

    for i, prompt in enumerate(prompts, 1):
        short = prompt[:55] + ("..." if len(prompt) > 55 else "")
        label = f"Q{i:02d}: {short}"
        try:
            answer = advisor.ask(prompt)
            ok = bool(answer and len(answer.strip()) > 20)
            check(label, ok, f"{len(answer)} znakow")
        except Exception as e:
            check(label, False, str(e)[:80])


# ---- main -------------------------------------------------------------------

if __name__ == "__main__":
    logic_only = "--logic" in sys.argv

    test_logic()
    test_routing()
    test_calculate()

    if not logic_only:
        test_full_advisor()

    total  = len(_results)
    passed = sum(1 for _, ok in _results if ok)
    failed = total - passed
    print("\n" + "=" * 60)
    print(f"PODSUMOWANIE: {passed}/{total} testow przeszlo, {failed} nie przeszlo")
    print("=" * 60)
    sys.exit(0 if failed == 0 else 1)

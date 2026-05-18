"""Layer 5 — Knowledge graph. Mały graf pojęć podatkowych (PIT) uzupełniający wyszukiwanie wektorowe.

Węzły = pojęcia (formy opodatkowania, parametry, ulgi, deklaracje).
Krawędzie = relacje (ma_parametr, rozliczana_przez, dopuszcza, wyklucza).
"""

_NODES = {
    # Formy opodatkowania
    "skala_podatkowa": {
        "label": "Skala podatkowa",
        "kind": "forma_opodatkowania",
        "opis": "Progresywna skala podatkowa: 12% do 120 000 zł dochodu, 32% od nadwyżki ponad 120 000 zł. W Polsce obowiązują 2 progi podatkowe.",
        "source": "pit-definicja-podatek-dochodowy.txt",
    },
    "podatek_liniowy": {"label": "Podatek liniowy", "kind": "forma_opodatkowania"},
    "ryczalt": {
        "label": "Ryczałt ewidencjonowany",
        "kind": "forma_opodatkowania",
        "opis": "Uproszczona forma opodatkowania od przychodu (bez odliczania kosztów). Stawki: 2–17% zależnie od PKD. Rozliczany na PIT-28. Warto gdy koszty niskie i stawka ryczałtu korzystna.",
        "source": "pit-ryczalt.txt",
    },
    # Parametry skali
    "prog_120k": {
        "label": "Próg podatkowy 120 000 zł",
        "kind": "parametr",
        "opis": "Pierwszy (i jedyny) próg podatkowy w skali PIT wynosi 120 000 zł. Dochód do 120 000 zł opodatkowany jest stawką 12%, powyżej – 32%.",
        "source": "pit-definicja-podatek-dochodowy.txt",
    },
    "stawka_12": {
        "label": "Stawka 12%",
        "kind": "parametr",
        "opis": "Stawka podatku PIT dla dochodów do 120 000 zł rocznie (minus kwota zmniejszająca podatek 3 600 zł).",
        "source": "pit-definicja-podatek-dochodowy.txt",
    },
    "stawka_32": {
        "label": "Stawka 32%",
        "kind": "parametr",
        "opis": "Stawka podatku PIT dla nadwyżki dochodu ponad 120 000 zł rocznie.",
        "source": "pit-definicja-podatek-dochodowy.txt",
    },
    "stawka_19": {"label": "Stawka 19%", "kind": "parametr"},
    "prog_1mln": {
        "label": "Próg daniny solidarnościowej 1 000 000 zł",
        "kind": "parametr",
        "opis": "Dochody przekraczające 1 000 000 zł rocznie podlegają dodatkowej daninie solidarnościowej w wysokości 4% od nadwyżki. Nie jest to oficjalny próg podatkowy, ale działa jak trzeci próg.",
        "source": "pit-definicja-danina-solidarnościowa.txt",
    },
    "kwota_wolna": {
        "label": "Kwota zmniejszająca podatek (3 600 zł)",
        "kind": "parametr",
        "opis": "Kwota zmniejszająca podatek w skali podatkowej wynosi 3 600 zł rocznie.",
        "source": "pit-definicja-podatek-dochodowy.txt",
    },
    # Ulgi podatkowe
    "danina_solidarnosciowa": {
        "label": "Danina solidarnościowa (art. 30h)",
        "kind": "danina",
        "opis": "Dodatkowa danina w wysokości 4% od nadwyżki dochodów ponad 1 000 000 zł rocznie. Obowiązuje od 2019 roku. Dotyczy dochodów ze skali podatkowej, podatku liniowego i innych. Technicznie nie jest progiem podatkowym, lecz oddzielną daniną — w praktyce działa jak trzeci próg.",
        "source": "pit-definicja-danina-solidarnościowa.txt",
    },
    "ulga_internet": {
        "label": "Ulga internetowa",
        "kind": "ulga",
        "opis": "Odliczenie wydatków na internet, max 760 zł rocznie.",
        "source": "pit-ulga-internet.txt",
    },
    "ulga_dzieci": {
        "label": "Ulga prorodzinna",
        "kind": "ulga",
        "opis": "Ulga na dzieci odliczana od podatku. Na pierwsze i drugie dziecko: 1 112,04 zł rocznie (92,67 zł × 12 miesięcy). Na trzecie dziecko: 2 000,04 zł rocznie. Na czwarte i każde kolejne: 2 700 zł rocznie.",
        "source": "pit-ulga-dziecko.txt",
    },
    "ulga_26": {
        "label": "Ulga dla młodych (zerowy PIT, art. 21 ust. 1 pkt 148)",
        "kind": "ulga",
        "opis": "Zwolnienie z PIT dla podatników do 26. roku życia; przychody ze stosunku pracy, umów zlecenia i praktyk do 85 528 zł rocznie są wolne od podatku.",
        "source": "pit-ulga-26.txt",
    },
    "ulga_rehabilitacja": {
        "label": "Ulga rehabilitacyjna (art. 26 ust. 1 pkt 6)",
        "kind": "ulga",
        "opis": "Odliczenie wydatków na cele rehabilitacyjne oraz ułatwiające wykonywanie czynności życiowych, poniesionych przez osobę niepełnosprawną lub osobę utrzymującą osobę niepełnosprawną.",
        "source": "pit-ulga-rehabilitacja.txt",
    },
    "ulga_termomodernizacja": {
        "label": "Ulga termomodernizacyjna (art. 26h)",
        "kind": "ulga",
        "opis": "Odliczenie wydatków na termomodernizację budynku jednorodzinnego; limit 53 000 zł.",
        "source": "pit-ulga-termomodernizcja.txt",
    },
    "ulga_rodzina_4": {
        "label": "Ulga dla rodzin 4+ (zerowy PIT)",
        "kind": "ulga",
        "opis": "Zwolnienie z PIT dla rodziców co najmniej czworga dzieci; przychody do 85 528 zł rocznie są wolne od podatku.",
        "source": "pit-ulga-rodzina-4.txt",
    },
    # Koszty uzyskania przychodów
    "koszty_freelancer": {
        "label": "Koszty uzyskania przychodów — freelancer/DG",
        "kind": "koszty",
        "opis": (
            "Freelancerzy i osoby prowadzące działalność gospodarczą mogą odliczać "
            "rzeczywiste, udokumentowane koszty (art. 22 ust. 1): sprzęt, oprogramowanie, "
            "internet, biuro domowe, szkolenia, transport, usługi księgowe. "
            "Brak ryczałtowego limitu 3000 zł — ten limit dotyczy wyłącznie pracowników etatowych. "
            "Umowy zlecenia/o dzieło: 20% kosztów zryczałtowanych lub 50% przy prawach autorskich "
            "(max 120 000 zł rocznie)."
        ),
        "source": "pit-koszty-freelancer.txt",
    },
    "koszty_pracownik": {
        "label": "Koszty uzyskania przychodów — pracownik etatowy",
        "kind": "koszty",
        "opis": (
            "Pracownicy etatowi mają ryczałtowe koszty uzyskania przychodów (art. 22 ust. 2): "
            "250 zł miesięcznie / 3 000 zł rocznie (jeden etat) lub max 4 500 zł (kilka etatów). "
            "Wyższe stawki gdy miejsce zamieszkania poza miejscem pracy: 300 zł/mies. lub max 5 400 zł."
        ),
        "source": "pit-definicja-koszty-pracownikow.txt",
    },
    # Deklaracje
    "pit36": {"label": "PIT-36", "kind": "deklaracja"},
    "pit37": {"label": "PIT-37", "kind": "deklaracja"},
    "pit28": {"label": "PIT-28", "kind": "deklaracja"},
    "pit36l": {"label": "PIT-36L", "kind": "deklaracja"},
    # Optymalizacja podatkowa
    "optymalizacja_podatkowa": {
        "label": "Optymalizacja podatkowa — metody zmniejszenia podatku",
        "kind": "strategia",
        "opis": "Legalne metody zmniejszenia podatku PIT: ulgi (prorodzinna, internetowa, rehabilitacyjna, termomodernizacyjna), koszty uzyskania przychodów, wybór formy opodatkowania, ulgi zerowego PIT (ulga dla młodych, rodzin 4+).",
        "source": "pit-optymalizacja-podatkowa.txt",
    },
    # Rozliczenie roczne — dokumenty i terminy
    "rozliczenie_roczne": {
        "label": "Roczne rozliczenie PIT — dokumenty i terminy",
        "kind": "procedura",
        "opis": "Dokumenty potrzebne do rocznego rozliczenia PIT: formularze (PIT-36, PIT-37, PIT-28, PIT-36L), ewidencje przychodów, faktury kosztowe, dokumenty ZUS, dokumenty do ulg. Termin złożenia: 30 kwietnia.",
        "source": "pit-dokumenty-rozliczenie.txt",
    },
}

_EDGES = [
    # Skala podatkowa
    ("skala_podatkowa", "ma_parametr", "prog_120k"),
    ("skala_podatkowa", "ma_parametr", "stawka_12"),
    ("skala_podatkowa", "ma_parametr", "stawka_32"),
    ("skala_podatkowa", "ma_parametr", "kwota_wolna"),
    ("skala_podatkowa", "rozliczana_przez", "pit37"),
    ("skala_podatkowa", "rozliczana_przez", "pit36"),
    ("skala_podatkowa", "dopuszcza", "ulga_internet"),
    ("skala_podatkowa", "dopuszcza", "ulga_dzieci"),
    ("skala_podatkowa", "dopuszcza", "ulga_26"),
    ("skala_podatkowa", "dopuszcza", "ulga_rehabilitacja"),
    ("skala_podatkowa", "dopuszcza", "ulga_termomodernizacja"),
    ("skala_podatkowa", "dopuszcza", "ulga_rodzina_4"),
    # Podatek liniowy
    ("podatek_liniowy", "ma_parametr", "stawka_19"),
    ("podatek_liniowy", "rozliczana_przez", "pit36l"),
    ("podatek_liniowy", "wyklucza", "ulga_dzieci"),
    ("podatek_liniowy", "dopuszcza", "ulga_termomodernizacja"),
    # Ryczałt
    ("ryczalt", "rozliczana_przez", "pit28"),
    ("ryczalt", "wyklucza", "ulga_dzieci"),
    ("ryczalt", "dopuszcza", "ulga_rodzina_4"),
    # Danina solidarnościowa
    ("danina_solidarnosciowa", "ma_parametr", "prog_1mln"),
    ("skala_podatkowa", "rozszerza", "danina_solidarnosciowa"),
    ("podatek_liniowy", "rozszerza", "danina_solidarnosciowa"),
    # Koszty uzyskania przychodów
    ("skala_podatkowa", "dopuszcza", "koszty_freelancer"),
    ("podatek_liniowy", "dopuszcza", "koszty_freelancer"),
    ("skala_podatkowa", "dopuszcza", "koszty_pracownik"),
]

_ALIASES = {
    # Formy opodatkowania
    "skala": "skala_podatkowa",
    "skala podatkowa": "skala_podatkowa",
    "liniowy": "podatek_liniowy",
    "podatek liniowy": "podatek_liniowy",
    "ryczałt": "ryczalt",
    "ryczalt": "ryczalt",
    # Progi i stawki podatkowe
    "próg": "prog_120k",
    "prog": "prog_120k",
    "progi": "prog_120k",
    "próg podatkowy": "prog_120k",
    "progi podatkowe": "prog_120k",
    "ile progów": "prog_120k",
    "ile progi": "prog_120k",
    # Danina solidarnościowa
    "danina": "danina_solidarnosciowa",
    "danina solidarnościowa": "danina_solidarnosciowa",
    "danina solidarnosciowa": "danina_solidarnosciowa",
    "solidarnościowa": "danina_solidarnosciowa",
    "solidarnosciowa": "danina_solidarnosciowa",
    "1000000": "danina_solidarnosciowa",
    "1 000 000": "danina_solidarnosciowa",
    "milion": "danina_solidarnosciowa",
    "stawka podatku": "skala_podatkowa",
    "stawki podatku": "skala_podatkowa",
    "stawka pit": "skala_podatkowa",
    "kwota wolna": "kwota_wolna",
    "kwota zmniejszająca": "kwota_wolna",
    "12%": "stawka_12",
    "32%": "stawka_32",
    "19%": "stawka_19",
    # Ulgi - internet
    "internet": "ulga_internet",
    "ulga internet": "ulga_internet",
    "ulga internetowa": "ulga_internet",
    # Ulgi - dzieci
    "dzieci": "ulga_dzieci",
    "prorodzinna": "ulga_dzieci",
    "ulga na dzieci": "ulga_dzieci",
    "ulga prorodzinna": "ulga_dzieci",
    # Ulga 26 / zerowy PIT dla młodych
    "ulga 26": "ulga_26",
    "ulga dla mlodych": "ulga_26",
    "ulga dla młodych": "ulga_26",
    "zerowy pit": "ulga_26",
    "pit zero": "ulga_26",
    "mlodzi": "ulga_26",
    "młodzi": "ulga_26",
    "do 26": "ulga_26",
    "26 lat": "ulga_26",
    "85528": "ulga_26",
    "85 528": "ulga_26",
    "art. 21 ust. 1 pkt 148": "ulga_26",
    "pkt 148": "ulga_26",
    "art 21 ust 1 pkt 148": "ulga_26",
    # Ulga rehabilitacyjna
    "rehabilitacja": "ulga_rehabilitacja",
    "rehabilitacyjna": "ulga_rehabilitacja",
    "ulga rehabilitacyjna": "ulga_rehabilitacja",
    "niepelnosprawni": "ulga_rehabilitacja",
    "niepełnosprawni": "ulga_rehabilitacja",
    "niepelnosprawnosc": "ulga_rehabilitacja",
    "niepełnosprawność": "ulga_rehabilitacja",
    # Ulga termomodernizacyjna
    "termomodernizacja": "ulga_termomodernizacja",
    "termomodernizacyjna": "ulga_termomodernizacja",
    "ulga termomodernizacyjna": "ulga_termomodernizacja",
    "ocieplenie": "ulga_termomodernizacja",
    "budynek": "ulga_termomodernizacja",
    "53000": "ulga_termomodernizacja",
    "53 000": "ulga_termomodernizacja",
    # Ulga rodzina 4+
    "rodzina 4+": "ulga_rodzina_4",
    "rodzina 4": "ulga_rodzina_4",
    "czworo dzieci": "ulga_rodzina_4",
    "czwórka dzieci": "ulga_rodzina_4",
    "ulga rodzina": "ulga_rodzina_4",
    # Koszty freelancera / DG
    "freelancer": "koszty_freelancer",
    "freelancerzy": "koszty_freelancer",
    "koszty freelancer": "koszty_freelancer",
    "wydatki freelancer": "koszty_freelancer",
    "wydatki odliczyc": "koszty_freelancer",
    "jakie wydatki": "koszty_freelancer",
    "koszty dzialalnosci": "koszty_freelancer",
    "koszty działalności": "koszty_freelancer",
    "koszty dg": "koszty_freelancer",
    "odliczenia freelancer": "koszty_freelancer",
    "prawa autorskie": "koszty_freelancer",
    "umowa zlecenie": "koszty_freelancer",
    "umowa o dzielo": "koszty_freelancer",
    "50% koszty": "koszty_freelancer",
    # Koszty pracownika etatowego
    "koszty pracownika": "koszty_pracownik",
    # Ryczałt ewidencjonowany
    "ryczałt ewidencjonowany": "ryczalt",
    "ryczalt ewidencjonowany": "ryczalt",
    "kiedy warto ryczalt": "ryczalt",
    "kiedy ryczalt": "ryczalt",
    "stawki ryczaltu": "ryczalt",
    "stawki ryczałtu": "ryczalt",
    # Optymalizacja podatkowa
    "zmniejszyć podatek": "optymalizacja_podatkowa",
    "zmniejszyc podatek": "optymalizacja_podatkowa",
    "aby zmniejszyć": "optymalizacja_podatkowa",
    "aby zmniejszyc": "optymalizacja_podatkowa",
    "obniżyć podatek": "optymalizacja_podatkowa",
    "obnizyc podatek": "optymalizacja_podatkowa",
    "jak zaoszczędzić na podatku": "optymalizacja_podatkowa",
    "jak zaoszczedzic": "optymalizacja_podatkowa",
    "optymalizacja podatkowa": "optymalizacja_podatkowa",
    "jak zmniejszyć": "optymalizacja_podatkowa",
    "jak zmniejszyc": "optymalizacja_podatkowa",
    "co zrobic aby zmniejszyc": "optymalizacja_podatkowa",
    "co zrobić aby zmniejszyć": "optymalizacja_podatkowa",
    "cos zrobic": "optymalizacja_podatkowa",
    "coś zrobić": "optymalizacja_podatkowa",
    # Roczne rozliczenie — dokumenty
    "dokumenty": "rozliczenie_roczne",
    "dokumenty do rozliczenia": "rozliczenie_roczne",
    "dokumenty pit": "rozliczenie_roczne",
    "roczne rozliczenie": "rozliczenie_roczne",
    "rozliczenie roczne": "rozliczenie_roczne",
    "roczne rozliczenie pit": "rozliczenie_roczne",
    "jak rozliczyć pit": "rozliczenie_roczne",
    "jak rozliczyc pit": "rozliczenie_roczne",
    "złożyć pit": "rozliczenie_roczne",
    "złożenie pit": "rozliczenie_roczne",
    "termin pit": "rozliczenie_roczne",
    "termin rozliczenia": "rozliczenie_roczne",
    "30 kwietnia": "rozliczenie_roczne",
    "e-pit": "rozliczenie_roczne",
    "epity": "rozliczenie_roczne",
    "twój e-pit": "rozliczenie_roczne",
    # Deklaracje
    "pit-37": "pit37",
    "pit-36": "pit36",
    "pit-36l": "pit36l",
    "pit-28": "pit28",
}


def node(key):
    return _NODES.get(key)


def neighbors(key, relation=None):
    out = []
    for src, rel, dst in _EDGES:
        if src == key and (relation is None or rel == relation):
            out.append((rel, dst, _NODES[dst]["label"]))
        elif dst == key and (relation is None or rel == relation):
            out.append((rel, src, _NODES[src]["label"]))
    return out


def mentioned_in(text):
    found = set()
    tl = text.lower()
    for alias, key in _ALIASES.items():
        if alias in tl:
            found.add(key)
    for key in _NODES:
        if key.replace("_", " ") in tl:
            found.add(key)
    return sorted(found)


def describe(keys):
    lines = []
    for k in keys:
        n = _NODES.get(k)
        if not n:
            continue
        rels = neighbors(k)
        rel_str = "; ".join(f"{r} → {label}" for r, _, label in rels) or "brak powiązań"
        base = f"- {n['label']} ({n['kind']})"
        if n.get("opis"):
            base += f": {n['opis']}"
        if n.get("source"):
            base += f" [źródło: {n['source']}]"
        base += f" | relacje: {rel_str}"
        lines.append(base)
    return "\n".join(lines)

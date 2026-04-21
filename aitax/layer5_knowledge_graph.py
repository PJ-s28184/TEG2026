"""Layer 5 — Knowledge graph. Mały graf pojęć podatkowych (PIT) uzupełniający wyszukiwanie wektorowe.

Węzły = pojęcia (formy opodatkowania, parametry, ulgi, deklaracje).
Krawędzie = relacje (ma_parametr, rozliczana_przez, dopuszcza, wyklucza).
"""

_NODES = {
    "skala_podatkowa": {"label": "Skala podatkowa", "kind": "forma_opodatkowania"},
    "podatek_liniowy": {"label": "Podatek liniowy", "kind": "forma_opodatkowania"},
    "ryczalt": {"label": "Ryczałt ewidencjonowany", "kind": "forma_opodatkowania"},
    "prog_120k": {"label": "Próg 120 000 zł", "kind": "parametr"},
    "stawka_12": {"label": "Stawka 12%", "kind": "parametr"},
    "stawka_32": {"label": "Stawka 32%", "kind": "parametr"},
    "stawka_19": {"label": "Stawka 19%", "kind": "parametr"},
    "kwota_wolna": {"label": "Kwota zmniejszająca podatek (3 600 zł)", "kind": "parametr"},
    "ulga_internet": {"label": "Ulga internetowa", "kind": "ulga"},
    "ulga_dzieci": {"label": "Ulga prorodzinna", "kind": "ulga"},
    "pit36": {"label": "PIT-36", "kind": "deklaracja"},
    "pit37": {"label": "PIT-37", "kind": "deklaracja"},
    "pit28": {"label": "PIT-28", "kind": "deklaracja"},
    "pit36l": {"label": "PIT-36L", "kind": "deklaracja"},
}

_EDGES = [
    ("skala_podatkowa", "ma_parametr", "prog_120k"),
    ("skala_podatkowa", "ma_parametr", "stawka_12"),
    ("skala_podatkowa", "ma_parametr", "stawka_32"),
    ("skala_podatkowa", "ma_parametr", "kwota_wolna"),
    ("skala_podatkowa", "rozliczana_przez", "pit37"),
    ("skala_podatkowa", "rozliczana_przez", "pit36"),
    ("skala_podatkowa", "dopuszcza", "ulga_internet"),
    ("skala_podatkowa", "dopuszcza", "ulga_dzieci"),
    ("podatek_liniowy", "ma_parametr", "stawka_19"),
    ("podatek_liniowy", "rozliczana_przez", "pit36l"),
    ("podatek_liniowy", "wyklucza", "ulga_dzieci"),
    ("ryczalt", "rozliczana_przez", "pit28"),
    ("ryczalt", "wyklucza", "ulga_dzieci"),
]

_ALIASES = {
    "skala": "skala_podatkowa",
    "skala podatkowa": "skala_podatkowa",
    "liniowy": "podatek_liniowy",
    "podatek liniowy": "podatek_liniowy",
    "ryczałt": "ryczalt",
    "ryczalt": "ryczalt",
    "internet": "ulga_internet",
    "dzieci": "ulga_dzieci",
    "prorodzinna": "ulga_dzieci",
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
        lines.append(f"- {n['label']} ({n['kind']}): {rel_str}")
    return "\n".join(lines)

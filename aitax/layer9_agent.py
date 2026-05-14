"""Layer 9 — Agent. Router intencji + orkiestracja warstw 1–8."""

import re

from . import (
    layer1_loader,
    layer2_chunker,
    layer4_vectorstore,
    layer5_knowledge_graph,
    layer6_prompt,
    layer7_llm,
    layer8_tools,
)


_ULGA_26_LIMIT = 85_528
_DANINA_THRESHOLD = 1_000_000
_DANINA_RATE = 0.04
# Ulga na dzieci (roczna kwota odliczenia od podatku)
_CHILD_DEDUCTION = [0, 1_112.04, 2_224.08, 4_224.12]  # 0,1,2,3 dzieci


_WORD_MULTIPLIERS = [
    (r"mil+ion[yów]*", 1_000_000),   # milion, miliony, milionów, million, milliony
    (r"tys(?:i[ęe]c[y]?|\.)?", 1_000),  # tysięcy, tysiące, tys.
]


def _extract_amounts(text):
    """Parsuje kwoty z tekstu, obsługując zapis słowny (miliony, tysiące) i cyfrowy."""
    normalized = re.sub(r"(?<=\d)\s+(?=\d{3}\b)", "", text)
    results = []
    # Kwoty słowne: "2 miliony", "140 tysięcy"
    for pattern, multiplier in _WORD_MULTIPLIERS:
        for m in re.finditer(rf"(\d+(?:[.,]\d+)?)\s*{pattern}", normalized, re.IGNORECASE):
            results.append((m.start(), int(float(m.group(1).replace(",", ".")) * multiplier)))
    # Kwoty cyfrowe (min. 3 cyfry) — pomijamy pozycje już rozpoznane słownie
    word_spans = {r[0] for r in results}
    for m in re.finditer(r"\b\d{3,}\b", normalized):
        if m.start() not in word_spans:
            results.append((m.start(), int(m.group())))
    results.sort(key=lambda x: x[0])
    return [v for _, v in results]


def _extract_profile(text):
    """Wyciąga sytuację oraz status podatnika z tekstu, np. wiek i liczbę dzieci."""
    ql = text.lower()
    profile = {}
    # "poniżej/mniej niż X lat" → wiek traktujemy jako X-1 (warunek ulgi 26: do ukończenia 26. roku)
    m = re.search(r"(?:poni[żz]ej|mniej\s+ni[żz])\s+(\d+)\s*lat", ql)
    if m:
        profile["wiek"] = int(m.group(1)) - 1
    else:
        m = re.search(r"(\d+)\s*lat[a]?\b", ql)
        if m:
            profile["wiek"] = int(m.group(1))
    m = re.search(r"(\d+)\s*dziec[ika]\b", ql)
    if m:
        profile["dzieci"] = int(m.group(1))
    elif any(w in ql for w in ["dziecko", "dzieckiem", "jedno dziecko"]):
        profile["dzieci"] = 1
    return profile


def _detect_additional_reliefs(text):
    ql = text.lower()
    reliefs = []
    if "internet" in ql:
        reliefs.append(
            "Ulga internetowa: możliwe odliczenie wydatków na internet do 760 zł rocznie [pit-ulga-internet.txt]."
        )
    if any(w in ql for w in ["rehabilitacja", "rehabilitacyjna", "niepełnospraw", "niepelnospraw"]):
        reliefs.append(
            "Ulga rehabilitacyjna: możliwe odliczenie wydatków na cele rehabilitacyjne lub związanych z ułatwieniem życia osobom niepełnosprawnym [pit-ulga-rehabilitacja.txt]."
        )
    if any(w in ql for w in ["termomoderniz", "ocieplenie", "budynek"]) and "internet" not in ql:
        reliefs.append(
            "Ulga termomodernizacyjna: możliwe odliczenie wydatków na termomodernizację budynku jednorodzinnego do 53 000 zł [pit-ulga-termomodernizcja.txt]."
        )
    if re.search(r"rodzina\s*4\+|rodzina\s*4|czworo\s*dzieci|co najmniej czworga dzie(c|ci)", ql):
        reliefs.append(
            "Ulga rodzina 4+: możliwe zwolnienie z PIT dla rodziców co najmniej czworga dzieci przy dochodach do 85 528 zł [pit-ulga-rodzina-4.txt]."
        )
    return reliefs


class Advisor:
    def __init__(self, store=None):
        if store is None:
            docs = layer1_loader.load_documents()
            chunks = layer2_chunker.chunk_documents(docs)
            store = layer4_vectorstore.VectorStore().index(chunks)
        self.store = store

    def ask(self, question):
        intent = self._route(question)
        if intent == "compare":
            return self._compare(question)
        if intent == "calculate":
            return self._calculate(question)
        return self._rag_answer(question)

    def _route(self, q):
        ql = q.lower()
        if "porówn" in ql or ("ryczałt" in ql and "skala" in ql):
            return "compare"
        calculate_triggers = [
            "ile podatku", "ile zapłacę", "ile zaplace", "ile wyniesie podatek",
            "ile odprowadz", "odprowadzę", "odprowadzic", "odprowadzić",
            "oblicz", "policz", "wyliczyć", "wyliczy", "wylicz",
            "podatek od", "podatek wynosi", "ile wynosi podatek",
            "ile muszę zapłacić", "ile musze zaplacic",
            "ile mam", "ile ma", "kwota podatku", "wysokość podatku",
        ]
        if any(w in ql for w in calculate_triggers):
            return "calculate"
        return "explain"

    def _graph_context(self, question):
        keys = layer5_knowledge_graph.mentioned_in(question)
        if not keys:
            return ""
        return "Powiązane pojęcia (graf wiedzy):\n" + layer5_knowledge_graph.describe(keys)

    def _vector_context(self, question, k=None):
        matched_sources = self._graph_sources(question)
        if matched_sources:
            # Graf wskazał konkretne źródło — ładuj chunki bezpośrednio, bez wyszukiwania semantycznego
            chunks = [c for c in self.store.chunks if c["source"] in matched_sources]
            return "\n---\n".join(f"[{c['source']}] {c['text']}" for c in chunks)
        hits = self.store.search(question, k=k) if k else self.store.search(question)
        return "\n---\n".join(f"[{h[0]['source']}] {h[0]['text']}" for h in hits)

    def _graph_sources(self, question):
        """Zwraca zbiór plików źródłowych wskazanych przez węzły grafu wiedzy dla pytania."""
        keys = layer5_knowledge_graph.mentioned_in(question)
        return {
            layer5_knowledge_graph._NODES[k]["source"]
            for k in keys
            if layer5_knowledge_graph._NODES.get(k, {}).get("source")
        }

    def _rag_answer(self, question):
        context = "\n\n".join(
            p for p in (self._graph_context(question), self._vector_context(question, k=5)) if p
        )
        return self._complete(question, context)

    def _calculate(self, question):
        amounts = _extract_amounts(question)
        if not amounts:
            return self._rag_answer(question)
        income = amounts[0]
        profile = _extract_profile(question)
        notes = []
        exempt = 0
        danina = 0.0
        child_deduction = 0.0

        # Ulga dla młodych (art. 21 ust. 1 pkt 148)
        if profile.get("wiek", 99) < 26:
            exempt = min(income, _ULGA_26_LIMIT)
            notes.append(
                f"Ulga dla młodych: podatnik ma {profile['wiek']} lat (poniżej 26), "
                f"dochód do {_ULGA_26_LIMIT:,} zł zwolniony z PIT. "
                f"Kwota zwolnienia: {exempt:,} zł [pit-ulga-26.txt]."
            )

        # Danina solidarnościowa (art. 30h)
        if income > _DANINA_THRESHOLD:
            danina = round((income - _DANINA_THRESHOLD) * _DANINA_RATE, 2)
            notes.append(
                f"Danina solidarnościowa: dochód {income:,} zł przekracza 1 000 000 zł, "
                f"4% od nadwyżki {income - _DANINA_THRESHOLD:,} zł = {danina:,.2f} zł [pit-definicja-danina-solidarnościowa.txt]."
            )

        # Ulga prorodzinna (odliczenie od podatku)
        dzieci = profile.get("dzieci", 0)
        if dzieci > 0:
            if dzieci < len(_CHILD_DEDUCTION):
                child_deduction = _CHILD_DEDUCTION[dzieci]
            else:
                child_deduction = _CHILD_DEDUCTION[3] + (dzieci - 3) * 2_700.0
            notes.append(
                f"Ulga prorodzinna: {dzieci} {'dziecko' if dzieci == 1 else 'dzieci'}, "
                f"odliczenie od podatku: {child_deduction:,.2f} zł [pit-ulga-dziecko.txt]."
            )

        additional_reliefs = _detect_additional_reliefs(question)
        result = layer8_tools.skala_podatkowa(income, exempt)
        podatek_po_uldze = max(0.0, round(result["podatek"] - child_deduction, 2))
        podatek_lacznie = round(podatek_po_uldze + danina, 2)

        taxable = income - exempt
        if taxable <= layer8_tools.BRACKET_THRESHOLD:
            bracket_info = f"Dochód {taxable:,} zł mieści się w pierwszym progu podatkowym (do 120 000 zł) — stawka 12%."
        elif taxable > _DANINA_THRESHOLD:
            bracket_info = f"Dochód {taxable:,} zł przekracza oba progi: drugi próg (32% powyżej 120 000 zł) oraz próg daniny solidarnościowej (4% powyżej 1 000 000 zł)."
        else:
            bracket_info = f"Dochód {taxable:,} zł przekracza pierwszy próg (120 000 zł) — część powyżej opodatkowana jest stawką 32%."

        lines = []
        lines.append(f"1. Dochód brutto: {income:,} zł")
        if exempt:
            lines.append(f"   - Ulga dla młodych: {exempt:,} zł zwolniona z PIT")
        lines.append(f"   - Dochód podlegający opodatkowaniu: {taxable:,} zł")
        lines.append(f"   - {bracket_info}")
        lines.append("2. Obliczenie krok po kroku:")
        for krok in result["operacje"]:
            lines.append(f"   {krok}")
        relief_lines = []
        if exempt:
            relief_lines.append(
                f"Ulga dla młodych: dochód do {_ULGA_26_LIMIT:,} zł zwolniony z PIT, kwota zwolnienia {exempt:,} zł [pit-ulga-26.txt]."
            )
        if child_deduction:
            relief_lines.append(
                f"Ulga prorodzinna ({dzieci} {'dziecko' if dzieci == 1 else 'dzieci'}): {child_deduction:,.2f} zł"
            )
        if danina:
            relief_lines.append(
                f"Danina solidarnościowa: ({income:,} − 1 000 000) × 4% = {danina:,.2f} zł"
            )
        relief_lines.extend(additional_reliefs)

        if relief_lines:
            lines.append("")
            lines.append("3. Ulgi / danina:")
            for relief in relief_lines:
                lines.append(f"   {relief}")
            lines.append("")
            lines.append(f"4. Podatek do zapłaty: {podatek_lacznie:,.2f} zł")
        else:
            lines.append("")
            lines.append("3. Nie zastosowano żadnych ulg ani danin solidarnościowych.")
            lines.append("")
            lines.append(f"4. Podatek do zapłaty: {podatek_lacznie:,.2f} zł")
        if notes:
            lines.append("")
            lines.append("Zastosowane przepisy:")
            for n in notes:
                lines.append(f"- {n}")
        return "\n".join(lines)

    def _compare(self, question):
        amounts = _extract_amounts(question)
        if not amounts:
            return self._rag_answer(question)
        income = amounts[0]
        deductions = amounts[1] if len(amounts) > 1 else 0
        scenarios = layer8_tools.compare(income, deductions)
        context = "Porównanie wariantów rozliczenia:\n" + "\n".join(str(s) for s in scenarios)
        graph = self._graph_context(question)
        if graph:
            context += "\n\n" + graph
        return self._complete(question, context)

    def _complete(self, question, context, template=None):
        if template is None:
            template = layer6_prompt.USER_TEMPLATE_EXPLAIN
        return layer7_llm.chat(
            [
                {"role": "system", "content": layer6_prompt.SYSTEM},
                {
                    "role": "user",
                    "content": template.format(question=question, context=context),
                },
            ]
        )

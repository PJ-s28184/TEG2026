from __future__ import annotations

import re
from dataclasses import dataclass

from .documents import DocumentChunk, format_source, unique_sources
from .embeddings import normalize_token
from .vector_store import LocalVectorStore, SearchResult


GENERIC_QUERY_TERMS = {
    "jakie",
    "jaki",
    "moge",
    "czy",
    "wydatki",
    "wydatek",
    "odliczyc",
    "odliczenie",
    "podatek",
    "podatku",
    "ulga",
    "ulge",
}


@dataclass(frozen=True)
class GroundedAnswer:
    answer: str
    citations: list[str]
    retrieved_chunks: list[SearchResult]
    insufficient_context: bool


class SimpleRAGPipeline:
    """Retrieve local legal chunks and produce context-grounded answers."""

    def __init__(self, vector_store: LocalVectorStore, min_score: float = 0.08):
        self.vector_store = vector_store
        self.min_score = min_score

    def answer(self, query: str, top_k: int = 5) -> GroundedAnswer:
        results = self.vector_store.query(query, top_k=top_k)
        relevant = [result for result in results if result.score >= self.min_score]
        distinctive_terms = self._distinctive_terms(query)
        focused = self._focus_on_distinctive_terms(distinctive_terms, relevant)
        if distinctive_terms and focused:
            relevant = focused
        elif distinctive_terms:
            relevant = []
        if not relevant:
            return GroundedAnswer(
                answer=(
                    "Nie mam wystarczajacego kontekstu w lokalnych zrodlach, aby "
                    "odpowiedziec na to pytanie bez zgadywania. Dodaj odpowiednie "
                    "akty lub fragmenty do data/raw i przebuduj indeks."
                ),
                citations=[],
                retrieved_chunks=results,
                insufficient_context=True,
            )

        chunks = [result.chunk for result in relevant]
        excerpts = [self._supporting_excerpt(query, chunk) for chunk in chunks[:3]]
        citations = unique_sources(chunks)

        bullet_lines = [
            f"- \"{excerpt}\" ({format_source(chunk.metadata)})"
            for excerpt, chunk in zip(excerpts, chunks[:3])
        ]
        answer = (
            "Odpowiedz oparta wylacznie na znalezionych fragmentach:\n"
            + "\n".join(bullet_lines)
            + "\n\nWniosek: "
            + self._synthesize(query, chunks)
            + "\n\nZrodla:\n"
            + "\n".join(f"- {source}" for source in citations)
        )
        return GroundedAnswer(
            answer=answer,
            citations=citations,
            retrieved_chunks=relevant,
            insufficient_context=False,
        )

    def _supporting_excerpt(self, query: str, chunk: DocumentChunk, max_chars: int = 360) -> str:
        query_terms = set(self._tokens(query))
        sentences = re.split(r"(?<=[.!?;])\s+", chunk.text)
        ranked = sorted(
            sentences,
            key=lambda sentence: len(query_terms.intersection(self._tokens(sentence))),
            reverse=True,
        )
        excerpt = ranked[0] if ranked else chunk.text
        excerpt = re.sub(r"\s+", " ", excerpt).strip()
        if len(excerpt) > max_chars:
            return excerpt[: max_chars - 3].rstrip() + "..."
        return excerpt

    def _synthesize(self, query: str, chunks: list[DocumentChunk]) -> str:
        combined = " ".join(chunk.text.lower() for chunk in chunks)
        topics: list[str] = []
        if "internet" in combined:
            topics.append("wydatki na Internet sa wskazane jako odliczenie z limitem 760 zl rocznie")
        if "kosztami uzyskania" in combined:
            topics.append("koszty zwiazane z uzyskaniem lub zabezpieczeniem przychodu moga pomniejszac dochod")
        if "dziecko" in combined or "dzieci" in combined:
            topics.append("ulga na dzieci zalezy od liczby dzieci, miesiecznych kwot oraz czesci limitow dochodu")
        if "26" in combined and "85 528" in combined:
            topics.append("przychody osob do 26 roku zycia moga byc zwolnione do limitu 85 528 zl")
        if "120 000" in combined and "12 %" in combined:
            topics.append("skala PIT uzywa progu 120 000 zl, stawki 12% oraz 32% od nadwyzki")

        if topics:
            return "; ".join(topics) + "."
        return (
            "lokalne zrodla zawieraja fragmenty powiazane z pytaniem, ale system "
            "nie wyprowadza dalej idacych twierdzen poza zacytowanym kontekstem."
        )

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {normalize_token(token) for token in re.findall(r"[\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+", text)}

    def _focus_on_distinctive_terms(
        self,
        terms: set[str],
        results: list[SearchResult],
    ) -> list[SearchResult]:
        if not terms:
            return []
        focused: list[SearchResult] = []
        for result in results:
            chunk = result.chunk
            source = format_source(chunk.metadata)
            haystack = self._tokens(chunk.text + " " + source)
            if terms.intersection(haystack):
                focused.append(result)
        return focused

    def _distinctive_terms(self, query: str) -> set[str]:
        return {
            term for term in self._tokens(query)
            if len(term) > 2 and term not in GENERIC_QUERY_TERMS
        }

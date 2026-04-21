from __future__ import annotations

import re

from .config import GRAPH_PATH, RAW_DATA_DIR, VECTOR_INDEX_PATH
from .documents import load_raw_documents
from .knowledge_graph import TaxKnowledgeGraph
from .rag import SimpleRAGPipeline
from .rules_engine import TaxRulesEngine, TaxScenario
from .vector_store import LocalVectorStore


class AiTaxAdvisor:
    """Orchestrates RAG, knowledge graph lookup, and deterministic rules."""

    def __init__(
        self,
        vector_index_path=VECTOR_INDEX_PATH,
        graph_path=GRAPH_PATH,
        raw_data_dir=RAW_DATA_DIR,
    ):
        self.vector_store = LocalVectorStore(vector_index_path)
        self.graph_path = graph_path
        self.raw_data_dir = raw_data_dir
        self.rules = TaxRulesEngine()

    def build_indexes(self) -> dict:
        chunks = load_raw_documents(self.raw_data_dir)
        self.vector_store.build(chunks)
        graph = TaxKnowledgeGraph()
        graph.build_from_chunks(chunks)
        graph.save(self.graph_path)
        return {
            "chunks": len(chunks),
            "entities": len(graph.entities),
            "relationships": len(graph.relationships),
            "vector_index": str(self.vector_store.path),
            "graph": str(self.graph_path),
        }

    def ask(self, query: str, top_k: int = 5) -> dict:
        rag = SimpleRAGPipeline(self.vector_store)
        rag_answer = rag.answer(query, top_k=top_k)

        graph_hits = {}
        try:
            graph_term = self._graph_term(query)
            if graph_term:
                graph = TaxKnowledgeGraph.load(self.graph_path)
                graph_hits = graph.query(graph_term, limit=8)
            else:
                graph_hits = {"entities": [], "relationships": []}
        except FileNotFoundError:
            graph_hits = {"entities": [], "relationships": []}

        calculation = None
        scenario = self._scenario_from_query(query)
        if scenario:
            calculation = self.rules.calculate(scenario).to_dict()

        final_answer = rag_answer.answer
        if calculation:
            final_answer += "\n\nObliczenia z silnika regul:\n"
            final_answer += f"- Podstawa opodatkowania: {calculation['taxable_income']:.2f} PLN\n"
            final_answer += f"- Szacowany podatek: {calculation['tax_due']:.2f} PLN\n"
            for result in calculation["results"]:
                final_answer += f"- {result['name']}: {result['amount']:.2f} PLN ({result['source']})\n"

        if graph_hits.get("entities") and not rag_answer.insufficient_context:
            final_answer += "\nPowiazania z grafu wiedzy:\n"
            for entity in graph_hits["entities"][:5]:
                final_answer += f"- {entity['label']} [{entity['type']}] z {entity['source']}\n"

        return {
            "answer": final_answer,
            "citations": rag_answer.citations,
            "insufficient_context": rag_answer.insufficient_context,
            "graph": graph_hits,
            "calculation": calculation,
        }

    def query_graph(self, term: str, limit: int = 10) -> dict:
        graph = TaxKnowledgeGraph.load(self.graph_path)
        return graph.query(term, limit=limit)

    def calculate(self, scenario: TaxScenario) -> dict:
        return self.rules.calculate(scenario).to_dict()

    @staticmethod
    def _graph_term(query: str) -> str:
        for keyword in ("internet", "dziecko", "dzieci", "koszt", "podatek", "ulga", "26", "120"):
            if keyword in query.lower():
                return keyword
        return ""

    def _scenario_from_query(self, query: str) -> TaxScenario | None:
        lowered = query.lower()
        if not any(word in lowered for word in ("podatek", "oblicz", "zarab", "doch")):
            return None
        amounts = [self._parse_amount(match.group(0)) for match in re.finditer(r"\d[\d\s]*(?:,\d+)?", query)]
        if not amounts:
            return None
        income = amounts[0]
        expenses = 0.0
        if "wydatk" in lowered or "koszt" in lowered:
            expenses = sum(amounts[1:])
        taxation_form = "scale"
        if "liniow" in lowered or "19%" in lowered:
            taxation_form = "linear"
        if "rycz" in lowered:
            taxation_form = "lump_sum"
        internet_expenses = 0.0
        if "internet" in lowered and len(amounts) > 1:
            internet_expenses = amounts[1]
        under_26_income = income if ("26" in lowered or "student" in lowered) else 0.0
        return TaxScenario(
            income=income,
            expenses=expenses,
            internet_expenses=internet_expenses,
            under_26_income=under_26_income,
            taxation_form=taxation_form,
        )

    @staticmethod
    def _parse_amount(raw: str) -> float:
        normalized = raw.replace(" ", "").replace(",", ".")
        try:
            return float(normalized)
        except ValueError:
            return 0.0

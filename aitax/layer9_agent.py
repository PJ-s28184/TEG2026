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


def _extract_amounts(text):
    normalized = re.sub(r"(?<=\d)\s+(?=\d{3}\b)", "", text)
    return [int(x) for x in re.findall(r"\b\d{3,}\b", normalized)]


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
        if any(w in ql for w in ["ile podatku", "oblicz", "policz", "wyliczyć", "wyliczy"]):
            return "calculate"
        return "explain"

    def _graph_context(self, question):
        keys = layer5_knowledge_graph.mentioned_in(question)
        if not keys:
            return ""
        return "Powiązane pojęcia (graf wiedzy):\n" + layer5_knowledge_graph.describe(keys)

    def _vector_context(self, question, k=None):
        hits = self.store.search(question, k=k) if k else self.store.search(question)
        return "\n---\n".join(f"[{h[0]['source']}] {h[0]['text']}" for h in hits)

    def _rag_answer(self, question):
        context = "\n\n".join(
            p for p in (self._graph_context(question), self._vector_context(question)) if p
        )
        return self._complete(question, context)

    def _calculate(self, question):
        amounts = _extract_amounts(question)
        if not amounts:
            return self._rag_answer(question)
        income = amounts[0]
        deductions = amounts[1] if len(amounts) > 1 else 0
        result = layer8_tools.skala_podatkowa(income, deductions)
        context = f"Wynik silnika podatkowego: {result}\n---\n{self._vector_context(question, k=2)}"
        return self._complete(question, context)

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

    def _complete(self, question, context):
        return layer7_llm.chat(
            [
                {"role": "system", "content": layer6_prompt.SYSTEM},
                {
                    "role": "user",
                    "content": layer6_prompt.USER_TEMPLATE.format(question=question, context=context),
                },
            ]
        )

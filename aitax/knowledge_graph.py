from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from .documents import DocumentChunk, format_source


@dataclass(frozen=True)
class Entity:
    id: str
    label: str
    type: str
    source: str


@dataclass(frozen=True)
class Relationship:
    source_id: str
    type: str
    target_id: str
    evidence: str


ENTITY_PATTERNS: list[tuple[str, str, re.Pattern[str]]] = [
    ("tax_rule", "TaxRule", re.compile(r"\bArt\.\s*\d+[a-z]?", re.IGNORECASE)),
    ("deduction", "Deduction", re.compile(r"\bulg[aię]|odlicze\w+|kosztami uzyskania", re.IGNORECASE)),
    ("taxpayer_type", "TaxpayerType", re.compile(r"podatnik|freelancer|samozatrudnion|dziecko|ma[lł]oletnie", re.IGNORECASE)),
    ("threshold", "Threshold", re.compile(r"\d[\d\s]*(?:,\d+)?\s*(?:z[lł]|%)", re.IGNORECASE)),
    ("condition", "Condition", re.compile(r"je[zż]eli|pod warunkiem|w stosunku do|do wysoko[sś]ci", re.IGNORECASE)),
    ("exception", "Exception", re.compile(r"z wyj[aą]tkiem|nie przekroczy|wolne od podatku", re.IGNORECASE)),
    ("obligation", "ReportingObligation", re.compile(r"dokument|formularz|rozliczen|zg[lł]osz|przechowyw", re.IGNORECASE)),
]


class TaxKnowledgeGraph:
    """In-memory graph abstraction that can later be backed by Neo4j."""

    def __init__(self):
        self.entities: dict[str, Entity] = {}
        self.relationships: list[Relationship] = []

    def build_from_chunks(self, chunks: list[DocumentChunk]) -> None:
        for chunk in chunks:
            self._extract_from_chunk(chunk)

    def _extract_from_chunk(self, chunk: DocumentChunk) -> None:
        text = chunk.text
        source = format_source(chunk.metadata)
        rule_id = self._ensure_entity(
            label=chunk.metadata.article or chunk.metadata.chunk_id,
            entity_type="TaxRule",
            source=source,
        )

        for key, entity_type, pattern in ENTITY_PATTERNS:
            for match in pattern.finditer(text):
                label = self._normalize_label(match.group(0))
                entity_id = self._ensure_entity(label=label, entity_type=entity_type, source=source)
                if entity_id != rule_id:
                    relation_type = self._relation_for(key)
                    self.relationships.append(
                        Relationship(
                            source_id=rule_id,
                            type=relation_type,
                            target_id=entity_id,
                            evidence=self._evidence_around(text, match.start(), match.end()),
                        )
                    )

    def _ensure_entity(self, label: str, entity_type: str, source: str) -> str:
        entity_id = f"{entity_type}:{label.lower()}"
        if entity_id not in self.entities:
            self.entities[entity_id] = Entity(
                id=entity_id,
                label=label,
                type=entity_type,
                source=source,
            )
        return entity_id

    @staticmethod
    def _normalize_label(label: str) -> str:
        return re.sub(r"\s+", " ", label.strip())

    @staticmethod
    def _relation_for(key: str) -> str:
        return {
            "deduction": "MENTIONS_DEDUCTION",
            "taxpayer_type": "APPLIES_TO",
            "threshold": "HAS_THRESHOLD",
            "condition": "HAS_CONDITION",
            "exception": "HAS_EXCEPTION",
            "obligation": "HAS_OBLIGATION",
            "tax_rule": "REFERENCES_RULE",
        }.get(key, "MENTIONS")

    @staticmethod
    def _evidence_around(text: str, start: int, end: int, window: int = 130) -> str:
        excerpt = text[max(0, start - window) : min(len(text), end + window)]
        return re.sub(r"\s+", " ", excerpt).strip()

    def query(self, term: str, limit: int = 10) -> dict:
        needle = term.lower()
        entities = [
            entity
            for entity in self.entities.values()
            if needle in entity.label.lower() or needle in entity.type.lower()
        ][:limit]
        entity_ids = {entity.id for entity in entities}
        relationships = [
            rel
            for rel in self.relationships
            if rel.source_id in entity_ids or rel.target_id in entity_ids or needle in rel.evidence.lower()
        ][:limit]
        return {
            "entities": [asdict(entity) for entity in entities],
            "relationships": [asdict(rel) for rel in relationships],
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "entities": [asdict(entity) for entity in self.entities.values()],
            "relationships": [asdict(rel) for rel in self.relationships],
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "TaxKnowledgeGraph":
        if not path.exists():
            raise FileNotFoundError(f"Knowledge graph not found at {path}. Run ingestion first.")
        payload = json.loads(path.read_text(encoding="utf-8"))
        graph = cls()
        graph.entities = {
            item["id"]: Entity(**item)
            for item in payload.get("entities", [])
        }
        graph.relationships = [
            Relationship(**item)
            for item in payload.get("relationships", [])
        ]
        return graph

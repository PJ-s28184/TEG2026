"""Layer 1 — Loader. Wczytuje surowe dokumenty tekstowe z katalogu `data/raw`."""

from pathlib import Path

from . import config


def load_documents(data_dir=None):
    data_dir = Path(data_dir or config.DATA_DIR)
    documents = []
    for path in sorted(data_dir.glob("*.txt")):
        documents.append(
            {
                "source": path.name,
                "stem": path.stem,
                "text": path.read_text(encoding="utf-8").strip(),
            }
        )
    return documents

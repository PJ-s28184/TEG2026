"""Demo funkcji `chunk_documents` z aitax.layer2_chunker.

Uruchomienie:
    python demo/layer2_chunker/chunk_documents.py

Skrypt wczytuje dokumenty z katalogu demonstracyjnego (poprzez `load_documents`),
następnie dzieli je na chunki za pomocą `chunk_documents` i wypisuje wynik
jako listę — po jednym elemencie w linii.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from aitax.layer1_loader import load_documents
from aitax.layer2_chunker import chunk_documents

CUSTOM_DIR = "demo/layer1_loader/demo_dir"

from aitax import config

config.CHUNK_SIZE = 20
config.CHUNK_OVERLAP = 5

def main():
    print("=" * 70)
    print("DEMO: aitax.layer2_chunker.chunk_documents")
    print("=" * 70)
    print(f"Katalog danych: {CUSTOM_DIR}")
    print("-" * 70)

    documents = load_documents(data_dir=CUSTOM_DIR)
    print(f"Wczytano {len(documents)} dokument(ów).")

    chunks = chunk_documents(documents)
    print(f"Powstało {len(chunks)} chunk(ów) łącznie.\n")

    print("[")
    for chunk in chunks:
        print(" {")
        print(f"  'id': {chunk['id']!r},")
        print(f"  'source': {chunk['source']!r},")
        print(f"  'text': {chunk['text']!r}")
        print(" },")
    print("]")


if __name__ == "__main__":
    main()

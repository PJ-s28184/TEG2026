"""Demo funkcji `chunk_text` z aitax.layer2_chunker.

Uruchomienie:
    python demo/layer2_chunker/chunk_text.py

Skrypt dzieli pojedynczy tekst na fragmenty (chunki) z zakładką słów
i wypisuje wynik w czytelnej, wciętej formie.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from aitax.layer2_chunker import chunk_text

SAMPLE_TEXT = (
    "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod "
    "tempor incididunt ut labore et dolore magna aliqua ut enim ad minim "
    "veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea "
    "commodo consequat duis aute irure dolor in reprehenderit in voluptate "
    "velit esse cillum dolore eu fugiat nulla pariatur excepteur sint occaecat "
    "cupidatat non proident sunt in culpa qui officia deserunt mollit anim id "
    "est laborum sed ut perspiciatis unde omnis iste natus error sit voluptatem "
    "accusantium doloremque laudantium totam rem aperiam eaque ipsa quae ab illo "
    "inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo"
)

CHUNK_SIZE = 20
CHUNK_OVERLAP = 5

def main():
    print("=" * 70)
    print("DEMO: aitax.layer2_chunker.chunk_text")
    print("=" * 70)
    print(f"Długość tekstu: {len(SAMPLE_TEXT.split())} słów")
    print(f"CHUNK_SIZE    = {CHUNK_SIZE}")
    print(f"CHUNK_OVERLAP = {CHUNK_OVERLAP}")
    print("-" * 70)

    chunks = chunk_text(SAMPLE_TEXT, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)

    print(f"Powstało {len(chunks)} fragment(ów).\n")

    print("[")
    for chunk in chunks:
        print(f"- {chunk!r},")
    print("]")


if __name__ == "__main__":
    main()

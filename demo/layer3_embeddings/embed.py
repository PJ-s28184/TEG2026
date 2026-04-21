"""Demo funkcji `embed` z aitax.layer3_embeddings na stałym zestawie chunków.

Uruchomienie:
    python demo/layer3_embeddings/embed.py

Skrypt przyjmuje stałą listę chunków (w formacie identycznym jak output
warstwy drugiej — `chunk_documents`) i osadza teksty każdego chunku przy użyciu
modelu `nomic-embed-text` z Ollamy. Dla każdego chunku wypisuje jego ID, źródło,
tekst oraz informacje o embedding'u (wymiary, pierwsze wartości, norma L2).
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from aitax.layer3_embeddings import embed

# Stała wartość wejściowa — taka sama struktura jak output warstwy 2 (`chunk_documents`).
SAMPLE_CHUNKS = [
    {
        'id': 'demo_file_1#0',
        'source': 'demo_file_1.txt',
        'text': "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy"
    },
    {
        'id': 'demo_file_1#1',
        'source': 'demo_file_1.txt',
        'text': "been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and"
    },
    {
        'id': 'demo_file_1#2',
        'source': 'demo_file_1.txt',
        'text': 'a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries,'
    },
    {
        'id': 'demo_file_1#3',
        'source': 'demo_file_1.txt',
        'text': 'survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the'
    },
    {
        'id': 'demo_file_1#4',
        'source': 'demo_file_1.txt',
        'text': 'It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with'
    },
    {
        'id': 'demo_file_1#5',
        'source': 'demo_file_1.txt',
        'text': 'passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.'
    },
    {
        'id': 'demo_file_1#6',
        'source': 'demo_file_1.txt',
        'text': 'Ipsum.'
    },
]


def main():
    print("=" * 70)
    print("DEMO: aitax.layer3_embeddings.embed (stałe chunki z warstwy 2)")
    print("=" * 70)
    print(f"Liczba chunków do osadzenia: {len(SAMPLE_CHUNKS)}")
    print("-" * 70)

    # Wyciągnij same teksty chunków (tak jak to robi właściwa pipeline)
    chunk_texts = [chunk["text"] for chunk in SAMPLE_CHUNKS]

    # Osadź wszystkie chunki naraz
    embeddings = embed(chunk_texts)

    print(f"Osadzono {len(embeddings)} embedding(ów) "
          f"(każdy o wymiarze {len(embeddings[0])}).\n")

    # Wypisz informacje o każdym chunku i jego embedding'u
    for chunk, embedding in zip(SAMPLE_CHUNKS, embeddings):
        print(f"Chunk ID: {chunk['id']!r}")
        print(f"  Source: {chunk['source']!r}")
        print(f"  Tekst:  {chunk['text']!r}")
        print(f"  Embedding dim: {len(embedding)}")
        print(f"  Pierwsze 5 wartości: {[f'{v:.4f}' for v in embedding[:5]]}")
        print(f"  Norma L2: {sum(v**2 for v in embedding)**0.5:.6f}")
        print()


if __name__ == "__main__":
    main()

"""Demo funkcji `load_documents` z aitax.layer1_loader.

Uruchomienie:
    python demo/layer1_loader/demo_load_documents.py

Skrypt wczytuje wszystkie pliki .txt z katalogu `data/raw` i wypisuje:
- liczbę wczytanych dokumentów,
- metadane każdego dokumentu (source, stem),
- pierwsze 200 znaków tekstu jako podgląd.
"""

import sys
from pathlib import Path

# Dodajemy katalog główny projektu do sys.path, aby można było zaimportować pakiet `aitax`.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from aitax.layer1_loader import load_documents

CUSTOM_DIR = "demo/layer1_loader/demo_dir"

def format_output(raw):
    indent = 0
    out = []
    i = 0
    while i < len(raw):
        ch = raw[i]
        if ch in "[{":
            indent += 1
            out.append(ch + "\n" + "    " * indent)
        elif ch in "]}":
            indent -= 1
            out.append("\n" + "    " * indent + ch)
        elif ch == "," and raw[i:i + 2] == ", ":
            out.append(",\n" + "    " * indent)
            i += 1
        else:
            out.append(ch)
        i += 1
        
    return "".join(out)

def main():
    print("=" * 70)
    print("DEMO: aitax.layer1_loader.load_documents")
    print("=" * 70)
    print(f"Katalog danych: {CUSTOM_DIR}")
    print("-" * 70)

    documents = load_documents(data_dir=CUSTOM_DIR)

    print(f"Wczytano {len(documents)} dokument(ów).\n")

    raw = repr(documents)
    formatted = format_output(raw)
    print(formatted)

if __name__ == "__main__":
    main()

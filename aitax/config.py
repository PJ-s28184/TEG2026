from pathlib import Path

<<<<<<< prototype
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY = "ollama"

CHAT_MODEL = "llama3.2"
EMBED_MODEL = "nomic-embed-text"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"

CHUNK_SIZE = 700
CHUNK_OVERLAP = 100
TOP_K = 3
=======

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
VECTOR_INDEX_PATH = PROCESSED_DATA_DIR / "vector_index.json"
GRAPH_PATH = PROCESSED_DATA_DIR / "knowledge_graph.json"
>>>>>>> main

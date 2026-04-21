from pathlib import Path

OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY = "ollama"

CHAT_MODEL = "llama3.2"
EMBED_MODEL = "nomic-embed-text"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"

CHUNK_SIZE = 700
CHUNK_OVERLAP = 100
TOP_K = 3

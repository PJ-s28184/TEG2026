from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
VECTOR_INDEX_PATH = PROCESSED_DATA_DIR / "vector_index.json"
GRAPH_PATH = PROCESSED_DATA_DIR / "knowledge_graph.json"

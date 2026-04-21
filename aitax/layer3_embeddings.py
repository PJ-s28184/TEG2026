"""Layer 3 — Embeddings. Zamienia tekst na wektory (Ollama `nomic-embed-text`)."""

from openai import OpenAI

from . import config

_client = OpenAI(base_url=config.OLLAMA_BASE_URL, api_key=config.OLLAMA_API_KEY)


def embed(texts):
    if isinstance(texts, str):
        texts = [texts]
    resp = _client.embeddings.create(model=config.EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]

"""Layer 7 — LLM. Klient czatu (Ollama via OpenAI-compatible API)."""

from openai import OpenAI

from . import config

_client = OpenAI(base_url=config.OLLAMA_BASE_URL, api_key=config.OLLAMA_API_KEY)


def chat(messages, model=None, temperature=0.2):
    resp = _client.chat.completions.create(
        model=model or config.CHAT_MODEL,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content

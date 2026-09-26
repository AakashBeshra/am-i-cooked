"""
Groq provider. Groq's API is OpenAI-compatible, so we reuse the same logic
with a different base URL and key. This is the free-tier-friendly option.
"""
from __future__ import annotations

from .openai_provider import OpenAIProvider


class GroqProvider(OpenAIProvider):
    name = "groq"

    def __init__(self, api_key: str, model: str, base_url: str, timeout: float = 25.0) -> None:
        super().__init__(api_key=api_key, model=model, base_url=base_url, timeout=timeout)
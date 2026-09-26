"""
Centralized configuration. Reads from environment variables (.env supported).
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str | None) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    """Runtime configuration. Instantiated once via `get_settings()`."""

    def __init__(self) -> None:
        # Provider selection
        self.ai_provider: str = (os.getenv("AI_PROVIDER") or "mock").strip().lower()

        # OpenAI
        self.openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
        self.openai_model: str = os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        self.openai_base_url: str = (
            os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
        ).rstrip("/")

        # Groq
        self.groq_api_key: str | None = os.getenv("GROQ_API_KEY")
        self.groq_model: str = os.getenv("GROQ_MODEL") or "llama-3.1-70b-versatile"
        self.groq_base_url: str = (
            os.getenv("GROQ_BASE_URL") or "https://api.groq.com/openai/v1"
        ).rstrip("/")

        # Timeouts
        try:
            self.ai_timeout_seconds: float = float(
                os.getenv("AI_TIMEOUT_SECONDS") or "25"
            )
        except ValueError:
            self.ai_timeout_seconds = 25.0

        # CORS
        origins = _split_csv(
            os.getenv("CORS_ORIGINS")
            or "http://localhost:5173,http://127.0.0.1:5173"
        )
        self.cors_origins: List[str] = origins

    def provider_is_configured(self) -> bool:
        """True if the selected provider has the keys it needs."""
        if self.ai_provider == "openai":
            return bool(self.openai_api_key)
        if self.ai_provider == "groq":
            return bool(self.groq_api_key)
        return True  # mock always works


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
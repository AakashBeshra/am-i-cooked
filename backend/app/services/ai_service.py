"""
The AIService orchestrates the providers:

1. Pick the configured provider (mock / openai / groq).
2. Call it.
3. Validate the response with Pydantic.
4. On ANY failure, fall back to MockProvider.
5. Return a strictly-typed `CookedResponse`.

This is the only file the routes depend on.
"""
from __future__ import annotations

import logging
from typing import Optional

from pydantic import ValidationError

from ..config import Settings, get_settings
from ..schemas.cooked import CookedResponse, WhatHappensNextItem
from .providers import (
    AIProvider,
    MockProvider,
    OpenAIProvider,
    GroqProvider,
    ProviderError,
)

logger = logging.getLogger("am_i_cooked.ai")


class AIService:
    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.primary: AIProvider = self._build_primary()
        self.fallback: AIProvider = MockProvider()

    def _build_primary(self) -> AIProvider:
        s = self.settings
        try:
            if s.ai_provider == "openai" and s.openai_api_key:
                return OpenAIProvider(
                    api_key=s.openai_api_key,
                    model=s.openai_model,
                    base_url=s.openai_base_url,
                    timeout=s.ai_timeout_seconds,
                )
            if s.ai_provider == "groq" and s.groq_api_key:
                return GroqProvider(
                    api_key=s.groq_api_key,
                    model=s.groq_model,
                    base_url=s.groq_base_url,
                    timeout=s.ai_timeout_seconds,
                )
        except ProviderError as e:
            logger.warning("Primary provider init failed (%s); using mock.", e)
        return MockProvider()

    async def aclose(self) -> None:
        await self.primary.aclose()
        await self.fallback.aclose()

    async def analyze(self, situation: str, category: str) -> CookedResponse:
        # First try: primary provider
        try:
            raw = await self.primary.analyze(situation, category)
            return self._validate(raw)
        except (ProviderError, ValidationError) as e:
            logger.warning("Primary provider failed: %s. Falling back to mock.", e)
        except Exception as e:  # noqa: BLE001 — defensive: never let routes 500 on AI hiccups
            logger.exception("Unexpected primary provider error: %s", e)

        # Fallback: mock provider
        try:
            raw = await self.fallback.analyze(situation, category)
            return self._validate(raw)
        except Exception as e:  # noqa: BLE001
            logger.exception("Mock provider failed: %s", e)
            # Last resort: construct a minimal valid response.
            return CookedResponse(
                score=50,
                severity="MEDIUM_RARE",
                category="other",
                diagnosis="Analysis unavailable right now. Please try again.",
                reasons=[{"emoji": "⚠️", "label": "Service temporarily unavailable"}],
                risk_factors=["Unknown"],
                recovery_probability=50,
                recovery_plan=["Try again in a moment."],
                emergency_actions=[],
                funny_commentary="The oven is offline. Ironically.",
                what_happens_next=[],
                confidence=0.3,
                demo_mode=True,
            )

    async def what_next(self, situation: str, score: int) -> list[WhatHappensNextItem]:
        for provider in (self.primary, self.fallback):
            try:
                raw = await provider.what_next(situation, score)
                items = raw.get("items") if isinstance(raw, dict) else None
                if not items:
                    continue
                return [WhatHappensNextItem(**it) for it in items][:6]
            except Exception as e:  # noqa: BLE001
                logger.warning("what_next via %s failed: %s", provider.name, e)
        return []

    def _validate(self, raw: dict) -> CookedResponse:
        return CookedResponse.model_validate(raw)


_service: AIService | None = None


def get_ai_service() -> AIService:
    global _service
    if _service is None:
        _service = AIService()
    return _service
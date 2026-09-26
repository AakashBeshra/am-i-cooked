"""
Abstract AI provider interface. Every provider returns a validated
`CookedResponse` dict. Providers raise `ProviderError` on any failure —
the AIService catches and falls back to MockProvider.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class ProviderError(Exception):
    """Raised by a provider when it cannot produce a valid response."""


class AIProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def analyze(self, situation: str, category: str) -> Dict[str, Any]:
        """Return a dict that can be validated against CookedResponse."""
        raise NotImplementedError

    @abstractmethod
    async def what_next(self, situation: str, score: int) -> Dict[str, Any]:
        """Return a dict with a single key `items`: list of {when, what}."""
        raise NotImplementedError

    async def aclose(self) -> None:
        """Optional cleanup hook (e.g. close httpx clients)."""
        return None
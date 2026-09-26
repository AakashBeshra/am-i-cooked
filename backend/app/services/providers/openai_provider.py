"""
OpenAI (and any OpenAI-compatible endpoint) provider. Uses httpx directly
so we don't pull the whole openai SDK for one endpoint.
"""
from __future__ import annotations

import json
from typing import Any, Dict

import httpx

from .base import AIProvider, ProviderError
from ..prompt import SYSTEM_PROMPT, build_user_prompt


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(self, api_key: str, model: str, base_url: str, timeout: float = 25.0) -> None:
        if not api_key:
            raise ProviderError("OpenAI API key not configured.")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _client_instance(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _chat(self, system: str, user: str) -> str:
        client = await self._client_instance()
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.8,
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            r = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            raise ProviderError(f"OpenAI HTTP {e.response.status_code}: {e.response.text[:200]}") from e
        except (httpx.HTTPError, KeyError, IndexError) as e:
            raise ProviderError(f"OpenAI transport error: {e}") from e

    async def analyze(self, situation: str, category: str) -> Dict[str, Any]:
        raw = await self._chat(SYSTEM_PROMPT, build_user_prompt(situation, category))
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise ProviderError(f"Model did not return valid JSON: {e}") from e

    async def what_next(self, situation: str, score: int) -> Dict[str, Any]:
        prompt = (
            f"Situation: {situation}\n"
            f"Cooked score: {score}.\n"
            "Return JSON: {\"items\": [{\"when\": \"In 10 minutes\", \"what\": \"...\"}, ...]} with 3-5 items."
        )
        raw = await self._chat(
            "You write short, funny, fictional predictions. Reply with JSON only.",
            prompt,
        )
        try:
            data = json.loads(raw)
            if "items" not in data or not isinstance(data["items"], list):
                raise ProviderError("Missing `items` array")
            return {"items": data["items"]}
        except json.JSONDecodeError as e:
            raise ProviderError(f"Invalid JSON from model: {e}") from e
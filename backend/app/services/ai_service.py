"""
AIService — the orchestrator.

Pipeline (per analyze request):
  1. parse_scene(situation)            → Scene (deterministic)
  2. score_scene(scene)                → 0-100 (deterministic)
  3. rules_narrate(scene, score)       → fallback narrative
  4. if Groq configured: groq.narrate → override narrative
  5. Assemble CookedResponse
  6. Cache by hash(situation) to avoid repeated calls

Failure at ANY step falls back to the previous layer. The response always
returns valid shape.
"""
from __future__ import annotations

import hashlib
import logging
from typing import Optional

from ..config import Settings, get_settings
from ..schemas.cooked import (
    CookedReason,
    CookedResponse,
    WhatHappensNextItem,
)
from ..utils.scene import (
    parse_scene,
    score_scene,
    severity_for_score,
    scene_to_dict,
)
from ..utils.narrative import rules_narrate
from .providers import GroqProvider, ProviderError

logger = logging.getLogger("am_i_cooked.ai")


class AIService:
    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._cache: dict[str, CookedResponse] = {}
        self._cache_max = 200
        self.groq: Optional[GroqProvider] = None

        if (
            self.settings.ai_provider == "groq"
            and self.settings.groq_api_key
        ):
            try:
                self.groq = GroqProvider(
                    api_key=self.settings.groq_api_key,
                    model=self.settings.groq_model,
                    base_url=self.settings.groq_base_url,
                    timeout=self.settings.ai_timeout_seconds,
                )
                logger.info("Groq provider active (model=%s)", self.settings.groq_model)
            except ProviderError as e:
                logger.warning("Groq init failed: %s. Falling back to rules.", e)
                self.groq = None
        else:
            logger.info("Groq not configured — rules-only mode.")

    async def aclose(self) -> None:
        if self.groq is not None:
            await self.groq.aclose()

    # ------------------------------------------------------------------

    async def analyze(self, situation: str, category: str) -> CookedResponse:
        cache_key = self._cache_key(situation, category)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 1. Deterministic parse + score
        scene = parse_scene(situation)
        score = score_scene(scene)
        sev = severity_for_score(score)

        resolved_category = category if category != "auto" else scene.domain
        if resolved_category not in _known_categories():
            resolved_category = scene.domain

        # 2. Rules-based narrative (always computed first — it's cheap)
        narrative = rules_narrate(scene, score)
        source = "rules"

        # 3. Groq narrative if available (best-effort, override on success)
        if self.groq is not None:
            try:
                groq_narrative = await self.groq.narrate(
                    situation=situation,
                    scene_dict=scene_to_dict(scene),
                    score=score,
                    severity=sev,
                    category=resolved_category,
                )
                # Sanity-check: must have at least a diagnosis and a plan
                if groq_narrative.get("diagnosis") and groq_narrative.get("recovery_plan"):
                    # If score < 70, force emergency_actions to [] regardless
                    if score < 70:
                        groq_narrative["emergency_actions"] = []
                    narrative = groq_narrative
                    source = "groq"
                    logger.info("Groq narrative used for score=%d", score)
                else:
                    logger.warning("Groq narrative incomplete; using rules.")
            except ProviderError as e:
                logger.warning("Groq failed: %s. Using rules narrative.", e)
            except Exception as e:  # noqa: BLE001
                logger.exception("Unexpected Groq error: %s", e)

        # 4. Assemble
        response = CookedResponse(
            score=score,
            severity=sev,
            category=resolved_category,
            diagnosis=narrative["diagnosis"],
            reasons=[CookedReason(**r) for r in narrative["reasons"]] or
                    [CookedReason(emoji="•", label="No specific reason identified.")],
            risk_factors=narrative["risk_factors"] or ["No notable risk factors."],
            recovery_probability=self._recovery_probability(scene, score),
            recovery_plan=narrative["recovery_plan"] or ["Try again in a moment."],
            emergency_actions=narrative["emergency_actions"],
            funny_commentary=narrative["funny_commentary"],
            what_happens_next=[
                WhatHappensNextItem(**it) for it in narrative["what_happens_next"]
            ],
            confidence=0.85 if source == "groq" else 0.72,
            demo_mode=(source != "groq"),
        )

        # 5. Cache (bounded)
        if len(self._cache) >= self._cache_max:
            # Drop oldest entry
            self._cache.pop(next(iter(self._cache)))
        self._cache[cache_key] = response

        return response

    async def what_next(self, situation: str, score: int):
        """Kept for compatibility. The narrative already includes predictions."""
        scene = parse_scene(situation)
        from ..utils.narrative import build_what_next
        items = build_what_next(scene, score)
        return [WhatHappensNextItem(**it) for it in items]

    # ------------------------------------------------------------------

    @staticmethod
    def _cache_key(situation: str, category: str) -> str:
        h = hashlib.sha256(f"{category}|{situation.strip().lower()}".encode()).hexdigest()
        return h[:24]

    @staticmethod
    def _recovery_probability(scene, score: int) -> int:
        base = 100 - score
        if scene.user_prepared:
            base += 15
        if scene.reversibility >= 0.8:
            base += 10
        if scene.consequence_severity >= 0.7:
            base -= 20
        return max(5, min(95, base))


_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    global _service
    if _service is None:
        _service = AIService()
    return _service


def _known_categories() -> set:
    return {
        "academic", "career", "relationship", "money", "life",
        "technology", "social", "time", "chaos", "other",
    }
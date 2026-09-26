"""
Deterministic mock provider — now driven by a structured Scene instead of
flat signal matching. Same output schema as before, but content is derived
from a real analysis of the situation.
"""
from __future__ import annotations

from typing import Any, Dict

from .base import AIProvider
from ...utils.scene import parse_scene, pick
from ...utils.scoring import severity_for_score
from ...utils.narrative import narrate


class MockProvider(AIProvider):
    name = "mock"

    async def analyze(self, situation: str, category: str) -> Dict[str, Any]:
        scene = parse_scene(situation)
        score = _score_scene(scene)
        sev = severity_for_score(score)
        resolved_category = category if category != "auto" else scene.domain
        if resolved_category not in _known_categories():
            resolved_category = scene.domain

        content = narrate(scene, score)

        return {
            "score": score,
            "severity": sev,
            "category": resolved_category,
            **content,
            "recovery_probability": _recovery_probability(scene, score),
            "confidence": _confidence(scene),
            "demo_mode": True,
        }

    async def what_next(self, situation: str, score: int) -> Dict[str, Any]:
        scene = parse_scene(situation)
        return {"items": narrate(scene, score)["what_happens_next"]}


# -----------------------------------------------------------------------------
# Scoring
# -----------------------------------------------------------------------------

def _score_scene(scene) -> int:
    """
    Score derived from scene dimensions:
      - urgency (time remaining)
      - stakes (domain severity)
      - prep gap (unpreparedness)
      - consequence (already done?)
      - control (agency)

    Weights tuned so most realistic scenarios land in the 20-95 range,
    and irreversible actions push near the top.
    """
    # Base = weighted average of pressure sources
    urgency = _urgency(scene)
    prep_gap = 0.5 if scene.user_prepared is None else (0.15 if scene.user_prepared else 0.85)
    stakes = scene.stakes
    consequence = scene.consequence_severity
    uncontrollability = 1.0 - scene.user_control

    # Base blend — before consequence override
    raw = (
        urgency          * 0.30 +
        stakes           * 0.30 +
        prep_gap         * 0.20 +
        uncontrollability* 0.20
    )
    # Consequence overrides everything
    if consequence > 0:
        raw = max(raw, consequence * 0.95)

    # Map to 0-100, keep 3-99 clamps
    score = int(round(raw * 100))
    return max(3, min(99, score))


def _urgency(scene) -> float:
    h = scene.hours_remaining
    if h is None:
        return 0.45  # unknown timeline → moderate
    if h <= 0.5:      return 1.00
    if h <= 3:        return 0.95
    if h <= 8:        return 0.85
    if h <= 24:       return 0.75
    if h <= 48:       return 0.60
    if h <= 168:      return 0.40
    if h <= 720:      return 0.20
    return 0.10


def _recovery_probability(scene, score: int) -> int:
    base = 100 - score
    if scene.user_prepared:
        base += 15
    if scene.reversibility >= 0.8:
        base += 10
    if scene.consequence_severity >= 0.7:
        base -= 20
    return max(5, min(95, base))


def _confidence(scene) -> float:
    if scene.detected_phrases:
        return 0.78
    return 0.40


def _known_categories() -> set:
    return {
        "academic", "career", "relationship", "money", "life",
        "technology", "social", "time", "chaos", "other",
    }
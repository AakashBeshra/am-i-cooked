"""
Pydantic schemas for the AI response. These are the contract between
the backend and the frontend.

IMPORTANT: The `CookedResponse` schema is what the LLM must produce.
We validate it strictly. Any deviation triggers the MockProvider fallback.
"""
from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

SeverityLabel = Literal[
    "NOT_COOKED",
    "SLIGHTLY_COOKED",
    "GETTING_WARM",
    "MEDIUM_RARE",
    "HEAVILY_COOKED",
    "DEEPLY_COOKED",
    "BEYOND_REPAIR",
]

CategoryId = Literal[
    "academic",
    "career",
    "relationship",
    "money",
    "life",
    "technology",
    "social",
    "time",
    "chaos",
    "other",
]


class CookedRequest(BaseModel):
    situation: str = Field(min_length=3, max_length=800)
    category: str = Field(default="auto", max_length=32)

    @field_validator("situation")
    @classmethod
    def strip_situation(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Situation must be at least 3 characters.")
        return v


class CookedReason(BaseModel):
    emoji: str = Field(default="•", max_length=8)
    label: str = Field(min_length=1, max_length=120)


class WhatHappensNextItem(BaseModel):
    when: str = Field(min_length=1, max_length=60)
    what: str = Field(min_length=1, max_length=200)


class CookedResponse(BaseModel):
    score: int = Field(ge=0, le=100)
    severity: SeverityLabel
    category: CategoryId
    diagnosis: str = Field(min_length=1, max_length=400)
    reasons: List[CookedReason] = Field(min_length=1, max_length=8)
    risk_factors: List[str] = Field(min_length=1, max_length=8)
    recovery_probability: int = Field(ge=0, le=100)
    recovery_plan: List[str] = Field(min_length=1, max_length=10)
    emergency_actions: List[str] = Field(default_factory=list, max_length=8)
    funny_commentary: str = Field(default="", max_length=300)
    what_happens_next: List[WhatHappensNextItem] = Field(default_factory=list, max_length=6)
    confidence: float = Field(ge=0.0, le=1.0, default=0.7)
    demo_mode: bool = False

    @field_validator("severity")
    @classmethod
    def severity_matches_score(cls, v: SeverityLabel, info) -> SeverityLabel:
        """Sanity: ensure severity is plausible for the score."""
        score = info.data.get("score")
        if score is None:
            return v
        expected = _severity_for_score(score)
        # Accept the model's choice if it's within one tier — LLMs are fickle.
        order = [
            "NOT_COOKED",
            "SLIGHTLY_COOKED",
            "GETTING_WARM",
            "MEDIUM_RARE",
            "HEAVILY_COOKED",
            "DEEPLY_COOKED",
            "BEYOND_REPAIR",
        ]
        if abs(order.index(v) - order.index(expected)) > 1:
            return expected
        return v


def _severity_for_score(score: int) -> SeverityLabel:
    if score >= 96:
        return "BEYOND_REPAIR"
    if score >= 86:
        return "DEEPLY_COOKED"
    if score >= 71:
        return "HEAVILY_COOKED"
    if score >= 51:
        return "MEDIUM_RARE"
    if score >= 31:
        return "GETTING_WARM"
    if score >= 11:
        return "SLIGHTLY_COOKED"
    return "NOT_COOKED"


class WhatNextRequest(BaseModel):
    situation: str = Field(min_length=3, max_length=800)
    score: int = Field(ge=0, le=100)


class WhatNextResponse(BaseModel):
    items: List[WhatHappensNextItem] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"] = "ok"
    provider: str
    provider_configured: bool
    version: str = "1.0.0"
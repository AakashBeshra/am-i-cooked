"""
HTTP routes. Everything under /api/*.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from ..config import get_settings
from ..schemas.cooked import (
    CookedRequest,
    CookedResponse,
    HealthResponse,
    WhatNextRequest,
    WhatNextResponse,
)
from ..services.ai_service import get_ai_service

logger = logging.getLogger("am_i_cooked.api")
router = APIRouter(prefix="/api", tags=["cooked"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    service = get_ai_service()

    # New AIService shape: `groq` is an optional GroqProvider, None if unused.
    # We surface a provider label for the frontend based on what's active.
    if service.groq is not None:
        provider_name = "groq"
    else:
        provider_name = "rules"

    return HealthResponse(
        status="ok",
        provider=provider_name,
        provider_configured=settings.provider_is_configured(),
        version="1.0.0",
    )


@router.post("/analyze", response_model=CookedResponse)
async def analyze(payload: CookedRequest) -> CookedResponse:
    service = get_ai_service()
    try:
        return await service.analyze(payload.situation, payload.category)
    except Exception as e:  # noqa: BLE001
        logger.exception("analyze failed entirely: %s", e)
        raise HTTPException(status_code=502, detail="Analysis temporarily unavailable.")


@router.post("/whats-next", response_model=WhatNextResponse)
async def whats_next(payload: WhatNextRequest) -> WhatNextResponse:
    service = get_ai_service()
    try:
        items = await service.what_next(payload.situation, payload.score)
        return WhatNextResponse(items=items)
    except Exception as e:  # noqa: BLE001
        logger.exception("whats_next failed: %s", e)
        return WhatNextResponse(items=[])
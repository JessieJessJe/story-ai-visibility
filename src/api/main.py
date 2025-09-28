"""FastAPI wrapper around the visibility pipeline."""

from __future__ import annotations

import os
from typing import Optional

import anyio
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.common.config import load_settings
from src.pipeline import run_pipeline

DEFAULT_TIMEOUT_SECONDS = 180
DEFAULT_ORIGINS = [
    "http://localhost:3000",
    "https://story-ai-visibility-fe.vercel.app",
]

app = FastAPI(title="Brand Visibility API")

origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", ",".join(DEFAULT_ORIGINS)).split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    text: str = Field(..., description="Full blog post string")
    provider_name: Optional[str] = Field(None, description="Canonical AI provider name")
    provider_aliases: Optional[list[str]] = Field(None, description="Additional aliases to mask")
    story_id: Optional[str] = Field(None, description="Optional story identifier to echo back")
    mode: Optional[str] = Field(None, description="Force 'stub' or 'live' execution")


class HealthResponse(BaseModel):
    ok: bool = True


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Simple health check."""

    return HealthResponse()


def _resolve_mode(requested: Optional[str]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if requested:
        mode = requested.lower()
        if mode not in {"stub", "live"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="mode must be 'stub' or 'live'")
        if mode == "live" and not api_key:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OPENAI_API_KEY required for live mode")
        return mode
    return "live" if api_key else "stub"


def _default_provider_settings() -> tuple[str, list[str]]:
    settings = load_settings()
    return settings.provider.name, settings.provider.aliases


@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    provider_name_default, provider_aliases_default = _default_provider_settings()
    provider_name = request.provider_name or provider_name_default
    provider_aliases = request.provider_aliases or provider_aliases_default
    mode = _resolve_mode(request.mode)

    def _execute() -> dict:
        return run_pipeline(
            text=request.text,
            provider_name=provider_name,
            provider_aliases=provider_aliases,
            mode=mode,
            story_id=request.story_id,
        )

    try:
        with anyio.move_on_after(DEFAULT_TIMEOUT_SECONDS) as scope:
            result = await anyio.to_thread.run_sync(_execute)
        if scope.cancel_called:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail={"code": "TIMEOUT", "message": "Pipeline exceeded 180s", "mode": mode},
            )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    return result

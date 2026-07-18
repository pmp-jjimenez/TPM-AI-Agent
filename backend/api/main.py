"""FastAPI application entry point."""

import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.compat import APPLICATION_VERSION
from backend.api.errors import register_error_handlers
from backend.api.routers import health, programs


DEFAULT_CORS_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)
CORS_ORIGINS_ENV = "TPM_API_CORS_ORIGINS"


def configured_cors_origins() -> List[str]:
    configured = os.getenv(CORS_ORIGINS_ENV, "")
    additional = [origin.strip() for origin in configured.split(",") if origin.strip()]
    return list(dict.fromkeys((*DEFAULT_CORS_ORIGINS, *additional)))


def create_app() -> FastAPI:
    api = FastAPI(
        title="TPM Operating System API",
        version=APPLICATION_VERSION,
        description="Read-only REST interface to TPM Operating System program data.",
    )
    api.add_middleware(
        CORSMiddleware,
        allow_origins=configured_cors_origins(),
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )
    register_error_handlers(api)
    api.include_router(health.router)
    api.include_router(programs.router)
    return api


app = create_app()

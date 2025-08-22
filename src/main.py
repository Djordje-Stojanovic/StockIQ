"""
FastAPI application entry point for StockIQ.

This module initializes the FastAPI application with health check endpoint,
CORS middleware, and basic configuration for local development.
"""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config.settings import get_settings
from src.routers import assessment


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.

    Args:
        app: FastAPI application instance

    Yields:
        None during application runtime
    """
    # Startup
    settings = get_settings()
    print(f"🚀 StockIQ starting up with OpenAI API configured: {bool(settings.openai_api_key)}")

    yield

    # Shutdown
    print("🛑 StockIQ shutting down")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    get_settings()

    app = FastAPI(
        title="StockIQ",
        description="Collaborative multi-agent stock analysis platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS middleware for local development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(assessment.router)

    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    return app


# Create app instance
app = create_app()


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint for application monitoring.

    Returns:
        Dictionary with health status information
    """
    settings = get_settings()
    return {
        "status": "healthy",
        "service": "StockIQ",
        "version": "1.0.0",
        "openai_configured": bool(settings.openai_api_key),
    }


@app.get("/")
async def root() -> dict[str, str]:
    """
    Root endpoint serving basic application information.

    Returns:
        Welcome message and basic app info
    """
    return {
        "message": "Welcome to StockIQ",
        "description": "Collaborative multi-agent stock analysis platform",
        "health_check": "/health",
    }

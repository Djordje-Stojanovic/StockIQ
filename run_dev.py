"""
Development server startup script for StockIQ.

This script starts the FastAPI application with uvicorn in development mode
with auto-reload enabled for Windows 11 local development.
"""

import uvicorn

from config.settings import get_settings


def main():
    """Start the development server with appropriate settings."""
    settings = get_settings()

    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Server will be available at: http://{settings.host}:{settings.port}")
    print(f"Debug mode: {settings.debug}")
    print(f"Auto-reload: {settings.reload}")

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        reload_dirs=["src", "config", "static"],
        log_level="debug" if settings.debug else "info"
    )


if __name__ == "__main__":
    main()

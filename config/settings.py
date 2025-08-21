"""
Application configuration using Pydantic BaseSettings.

This module manages environment variables and application settings
for StockIQ using Pydantic v2 BaseSettings with automatic loading
from environment variables and .env files.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    Loads configuration from environment variables and .env file.
    """

    # OpenAI API Configuration
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key for agent functionality"
    )

    # Application Configuration
    app_name: str = Field(
        default="StockIQ",
        description="Application name"
    )

    app_version: str = Field(
        default="1.0.0",
        description="Application version"
    )

    # Server Configuration
    host: str = Field(
        default="127.0.0.1",
        description="Server host address"
    )

    port: int = Field(
        default=8000,
        description="Server port number"
    )

    debug: bool = Field(
        default=True,
        description="Enable debug mode for development"
    )

    # Research Database Configuration
    research_db_path: str = Field(
        default="research_database",
        description="Path to research database directory"
    )

    # Temporary Files Configuration
    tmp_path: str = Field(
        default="tmp",
        description="Path to temporary files directory"
    )

    # Agent Configuration
    max_tokens_per_request: int = Field(
        default=4000,
        description="Maximum tokens per OpenAI API request"
    )

    agent_temperature: float = Field(
        default=0.7,
        description="Temperature setting for OpenAI agents"
    )

    # Development Configuration
    reload: bool = Field(
        default=True,
        description="Enable auto-reload for development"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings instance.

    Returns:
        Settings instance with loaded configuration

    Note:
        Uses lru_cache for singleton pattern and performance
    """
    return Settings()

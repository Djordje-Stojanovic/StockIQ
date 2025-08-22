"""OpenAI SDK wrapper for StockIQ application."""

import json
import logging
import os

from openai import AsyncOpenAI, OpenAI

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Wrapper for OpenAI SDK with StockIQ-specific configurations."""

    def __init__(self):
        """Initialize OpenAI client with environment configuration."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)

        # Model configuration based on task complexity
        self.complex_model = os.getenv("OPENAI_COMPLEX_MODEL", "gpt-5")  # For intelligent tasks
        self.simple_model = os.getenv("OPENAI_SIMPLE_MODEL", "gpt-5-mini")  # For simple tasks

        self.temperature = float(os.getenv("AGENT_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("MAX_TOKENS_PER_REQUEST", "4000"))

    def create_completion(
        self,
        messages: list[dict],
        max_tokens: int = None,
        temperature: float = None,
        response_format: dict = None,
        use_complex_model: bool = False,
    ) -> str:
        """
        Create a completion using OpenAI API.

        Args:
            messages: List of message dictionaries for the conversation
            max_tokens: Maximum completion tokens for response (uses default if None)
            temperature: Temperature for response randomness (uses default if None)
            response_format: Response format specification for structured outputs
            use_complex_model: Use GPT-5 for complex tasks, GPT-5-mini otherwise

        Returns:
            Response content as string

        Raises:
            Exception: If OpenAI API call fails
        """
        try:
            model = self.complex_model if use_complex_model else self.simple_model

            kwargs = {
                "model": model,
                "messages": messages,
                "max_completion_tokens": max_tokens or self.max_tokens,
            }

            # For GPT-5, set reasoning effort to minimize reasoning token usage
            if model.startswith("gpt-5"):
                kwargs["reasoning_effort"] = "minimal"  # Reduce reasoning tokens for more output

            # Only set temperature if provided (GPT-5 models only support default temperature)
            if temperature is not None:
                kwargs["temperature"] = temperature
            elif not model.startswith("gpt-5"):  # Only set default for non-GPT-5 models
                kwargs["temperature"] = self.temperature

            if response_format:
                kwargs["response_format"] = response_format

            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content

            logger.debug(
                f"OpenAI completion created with {model}, tokens: {response.usage.total_tokens}"
            )

            # Debug: Log content for troubleshooting
            if not content:
                logger.error(f"Empty content received from {model}")
                logger.error(f"Response: {response}")

            return content

        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise

    def create_structured_completion(
        self,
        messages: list[dict],
        response_schema: dict,
        max_tokens: int = None,
        temperature: float = None,
        use_complex_model: bool = True,
    ) -> dict:
        """
        Create a structured completion with JSON response format.

        Args:
            messages: List of message dictionaries for the conversation
            response_schema: JSON schema for structured response
            max_tokens: Maximum completion tokens for response (uses default if None)
            temperature: Temperature for response randomness (uses default if None)
            use_complex_model: Use GPT-5 for complex structured tasks by default

        Returns:
            Parsed JSON response as dictionary

        Raises:
            Exception: If OpenAI API call fails or JSON parsing fails
        """
        try:
            response_format = {
                "type": "json_schema",
                "json_schema": {"name": "structured_response", "schema": response_schema},
            }

            # Log request to server console
            logger.info("🚀 OPENAI API REQUEST")
            logger.info(f"Messages: {messages}")
            logger.info(f"Schema: {response_schema}")
            logger.info(f"Max tokens: {max_tokens}")
            logger.info(f"Temperature: {temperature}")
            logger.info(f"Complex model: {use_complex_model}")

            content = self.create_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                response_format=response_format,
                use_complex_model=use_complex_model,
            )

            if not content:
                raise ValueError("Empty content received from OpenAI API")

            parsed_response = json.loads(content)

            # Log response to server console
            logger.info("✅ OPENAI API RESPONSE")
            logger.info(f"Response: {parsed_response}")

            return parsed_response

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Content received: '{content[:200] if content else 'None'}...'")
            raise
        except Exception as e:
            logger.error(f"Structured completion failed: {str(e)}")
            raise

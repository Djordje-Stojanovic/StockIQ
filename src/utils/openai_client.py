"""OpenAI SDK wrapper for StockIQ application - FIXED GPT-5 Responses API."""

import json
import logging
import os
import time
import random
from typing import Any, Dict, List, Optional

from openai import OpenAI, APIStatusError, APIConnectionError, RateLimitError

logger = logging.getLogger(__name__)


def extract_output_text(resp) -> str:
    """Bulletproof text extraction from GPT-5 Responses API."""
    # 1) Fast path: official helper (SDK >= 1.101.0)
    s = getattr(resp, "output_text", None)
    if s and s.strip():
        logger.debug(f"Using response.output_text: {len(s)} chars")
        return s.strip()
    
    # 2) Manual path: scan outputs for the final assistant message
    chunks = []
    for item in getattr(resp, "output", []) or []:
        if getattr(item, "type", None) == "message" and getattr(item, "role", "") == "assistant":
            for block in getattr(item, "content", []) or []:
                # Blocks often type as "output_text" (sometimes "text")
                if getattr(block, "type", "") in ("output_text", "text"):
                    t = getattr(block, "text", "") or ""
                    if t:
                        chunks.append(t)
    
    if chunks:
        result = "\n".join(chunks).strip()
        logger.debug(f"Extracted {len(result)} chars from assistant message")
        return result
    
    # If we still have nothing, we likely ran out of tokens
    logger.error("No assistant output found - likely token starvation. Increase max_output_tokens.")
    raise ValueError("No assistant output_text found - try increasing max_output_tokens")


class OpenAIClient:
    """Wrapper for OpenAI SDK with bulletproof GPT-5 Responses API usage."""

    def __init__(self):
        """Initialize OpenAI client with environment configuration."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.client = OpenAI(
            api_key=self.api_key,
            timeout=600.0,
            max_retries=2  # SDK built-in retries
        )

        # Model configuration
        self.complex_model = os.getenv("OPENAI_COMPLEX_MODEL", "gpt-5")
        self.simple_model = os.getenv("OPENAI_SIMPLE_MODEL", "gpt-5-mini")

    def create(
        self,
        *,
        messages: List[Dict[str, Any]], 
        tools: Optional[List[Dict[str, Any]]] = None,
        reasoning_effort: str = "low",  # Using "low" as you requested
        verbosity: str = "medium",  # Medium for better output
        max_output_tokens: int = 8000,  # 8k tokens as you requested
        temperature: Optional[float] = None,
        previous_response_id: Optional[str] = None,
        use_complex_model: bool = False,
        use_typed_blocks: bool = True  # Use typed content blocks for better tool compatibility
    ) -> Any:
        """
        Create a response using GPT-5 Responses API with bulletproof error handling.
        
        Key fixes from researcher:
        - Increased max_output_tokens to prevent token starvation
        - Using typed content blocks for better tool compatibility
        - Low reasoning effort to save tokens for actual output
        """
        model = self.complex_model if use_complex_model else self.simple_model
        
        # Convert to typed content blocks if needed (better for tools)
        if use_typed_blocks:
            typed_input = []
            for msg in messages:
                if isinstance(msg.get("content"), str):
                    typed_input.append({
                        "role": msg["role"],
                        "content": [{"type": "input_text", "text": msg["content"]}]
                    })
                else:
                    typed_input.append(msg)
            messages = typed_input
        
        kwargs: Dict[str, Any] = {
            "model": model,
            "input": messages,
            "reasoning": {"effort": reasoning_effort},
            "text": {"format": {"type": "text"}, "verbosity": verbosity},
            "max_output_tokens": max_output_tokens,
        }
        if tools: 
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"  # Explicit for clarity
        if previous_response_id: 
            kwargs["previous_response_id"] = previous_response_id
        if temperature is not None: 
            kwargs["temperature"] = temperature

        # Extra backoff on top of SDK's built-ins for rate limits
        base = 1.0
        for attempt in range(1, 6):  # 6 attempts for better resilience
            try:
                response = self.client.responses.create(**kwargs)
                logger.info(f"GPT-5 response created with {model}, {max_output_tokens} tokens")
                return response
                
            except RateLimitError as e:
                sleep = base * (2 ** (attempt - 1)) + random.uniform(0, 0.333)
                logger.warning(f"Rate limit hit; retrying in {sleep:.2f}s (attempt {attempt}/5)")
                time.sleep(sleep)
                continue
            except (APIStatusError, APIConnectionError) as e:
                code = getattr(e, "status_code", None)
                if code in (500, 502, 503, 504) or isinstance(e, APIConnectionError):
                    sleep = base * (2 ** (attempt - 1)) + random.uniform(0, 0.333)
                    logger.warning(f"Transient error {code}; retrying in {sleep:.2f}s (attempt {attempt}/5)")
                    time.sleep(sleep)
                    continue
                raise
        
        raise RuntimeError("Max retries exceeded after 5 attempts")

    def respond_with_web_search(
        self,
        messages: List[Dict[str, Any]],
        reasoning_effort: str = "low",
        verbosity: str = "high",  # High verbosity for lots of data
        max_output_tokens: int = 32000,  # 32k context for comprehensive research
        temperature: Optional[float] = None
    ) -> str:
        """
        GPT-5 response with web search tool for real data research.
        
        Fixed based on researcher's findings:
        - 8000 tokens to ensure we get the final assistant message
        - Low reasoning effort to save tokens for actual output
        - Medium verbosity for good detail
        """
        try:
            response = self.create(
                messages=messages,
                tools=[{"type": "web_search"}],
                reasoning_effort=reasoning_effort,
                verbosity=verbosity,
                max_output_tokens=max_output_tokens,
                temperature=temperature,
                use_complex_model=False,  # Use GPT-5-mini (200k TPM) for web search
                use_typed_blocks=True  # Use typed blocks for tool compatibility
            )
            
            content = extract_output_text(response)
            
            # If we still got nothing, retry with even more tokens
            if not content or len(content) < 100:
                logger.warning("Got minimal content, retrying with 12k tokens")
                response = self.create(
                    messages=messages,
                    tools=[{"type": "web_search"}],
                    reasoning_effort="low",
                    verbosity="medium",
                    max_output_tokens=12000,  # Give it even more room
                    use_complex_model=True,
                    use_typed_blocks=True
                )
                content = extract_output_text(response)
            
            logger.info(f"GPT-5 web search completed: {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"GPT-5 web search failed: {str(e)}")
            raise

    def create_completion(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        response_format: Optional[Dict] = None,
        use_complex_model: bool = False,
    ) -> str:
        """
        Create a completion using GPT-5 (compatible with legacy code).

        Args:
            messages: List of message dictionaries for the conversation
            max_tokens: Maximum completion tokens for response
            temperature: Temperature for response randomness
            response_format: Response format specification
            use_complex_model: Use GPT-5 for complex tasks

        Returns:
            Response content as string

        Raises:
            Exception: If OpenAI API call fails
        """
        try:
            response = self.create(
                messages=messages,
                reasoning_effort="low",  # Low reasoning effort
                verbosity="medium",  # Medium verbosity for focused output
                max_output_tokens=max_tokens or 12000,  # Default to 12k tokens
                temperature=temperature,
                use_complex_model=use_complex_model,
                use_typed_blocks=True
            )

            content = extract_output_text(response)
            
            if not content:
                logger.error(f"Empty content received from GPT-5")

            return content

        except Exception as e:
            logger.error(f"GPT-5 completion failed: {str(e)}")
            raise

    def create_structured_completion(
        self,
        messages: List[Dict[str, Any]],
        response_schema: Dict,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        use_complex_model: bool = True,
    ) -> Dict:
        """
        Create a structured completion with JSON response format.

        Args:
            messages: List of message dictionaries for the conversation
            response_schema: JSON schema for structured response
            max_tokens: Maximum completion tokens for response
            temperature: Temperature for response randomness
            use_complex_model: Use GPT-5 for complex structured tasks by default

        Returns:
            Parsed JSON response as dictionary

        Raises:
            Exception: If OpenAI API call fails or JSON parsing fails
        """
        try:
            # Add JSON schema instruction to system message
            json_instruction = {
                "role": "system",
                "content": f"Respond with valid JSON matching this schema: {json.dumps(response_schema)}"
            }
            
            structured_messages = [json_instruction] + messages

            content = self.create_completion(
                messages=structured_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                use_complex_model=use_complex_model,
            )

            if not content:
                raise ValueError("Empty content received from OpenAI API")

            parsed_response = json.loads(content)

            return parsed_response

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Content received: '{content[:200] if content else 'None'}...'")
            raise
        except Exception as e:
            logger.error(f"Structured completion failed: {str(e)}")
            raise
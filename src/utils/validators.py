"""Validation utilities for StockIQ application."""

import logging
import re

logger = logging.getLogger(__name__)


def validate_ticker_format(ticker: str) -> tuple[bool, str]:
    """
    Validate ticker symbol format.

    Args:
        ticker: Stock ticker symbol to validate

    Returns:
        Tuple of (is_valid, error_message)
        If valid, error_message is empty string

    Example:
        >>> validate_ticker_format("ASML")
        (True, "")
        >>> validate_ticker_format("123")
        (False, "Ticker must contain only letters (A-Z)")
    """
    if not ticker:
        return False, "Ticker symbol is required"

    ticker = ticker.strip().upper()

    if len(ticker) < 1:
        return False, "Ticker must be at least 1 character"

    if len(ticker) > 6:
        return False, "Ticker must be 6 characters or less"

    if not re.match(r"^[A-Z]{1,6}$", ticker):
        if any(char.isdigit() for char in ticker):
            return False, "Ticker must contain only letters (A-Z)"
        if any(not char.isalpha() for char in ticker):
            return False, "Ticker must not contain special characters"
        return False, "Invalid ticker format"

    logger.debug(f"Ticker {ticker} validated successfully")
    return True, ""


def is_valid_session_id(session_id: str) -> bool:
    """
    Validate session ID format (UUID v4).

    Args:
        session_id: Session ID to validate

    Returns:
        True if valid UUID v4 format, False otherwise
    """
    if not session_id:
        return False

    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.IGNORECASE
    )

    return bool(uuid_pattern.match(session_id))

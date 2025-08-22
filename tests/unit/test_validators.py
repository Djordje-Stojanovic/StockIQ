"""Unit tests for validation utilities."""

from src.utils.validators import is_valid_session_id, validate_ticker_format


class TestTickerValidation:
    """Test ticker format validation."""

    def test_valid_tickers(self):
        """Test that valid tickers pass validation."""
        valid_tickers = ["ASML", "COST", "MSFT", "A", "AA", "GOOGL"]

        for ticker in valid_tickers:
            is_valid, error = validate_ticker_format(ticker)
            assert is_valid is True, f"Ticker {ticker} should be valid"
            assert error == "", f"No error message expected for {ticker}"

    def test_lowercase_tickers_are_converted(self):
        """Test that lowercase tickers are accepted and converted."""
        is_valid, error = validate_ticker_format("asml")
        assert is_valid is True
        assert error == ""

    def test_empty_ticker(self):
        """Test that empty ticker is rejected."""
        is_valid, error = validate_ticker_format("")
        assert is_valid is False
        assert "required" in error.lower()

    def test_ticker_too_long(self):
        """Test that tickers longer than 6 characters are rejected."""
        is_valid, error = validate_ticker_format("VERYLONGTICKER")
        assert is_valid is False
        assert "6 characters or less" in error

    def test_ticker_with_numbers(self):
        """Test that tickers with numbers are rejected."""
        is_valid, error = validate_ticker_format("ABC123")
        assert is_valid is False
        assert "only letters" in error

    def test_ticker_with_special_chars(self):
        """Test that tickers with special characters are rejected."""
        invalid_tickers = ["AB-C", "AB.C", "AB@C", "AB$C", "AB C"]

        for ticker in invalid_tickers:
            is_valid, error = validate_ticker_format(ticker)
            assert is_valid is False, f"Ticker {ticker} should be invalid"
            assert "special characters" in error or "only letters" in error

    def test_whitespace_handling(self):
        """Test that whitespace is properly handled."""
        is_valid, error = validate_ticker_format("  ASML  ")
        assert is_valid is True
        assert error == ""


class TestSessionIdValidation:
    """Test session ID validation."""

    def test_valid_uuid_v4(self):
        """Test that valid UUID v4 is accepted."""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        assert is_valid_session_id(valid_uuid) is True

    def test_invalid_uuid_format(self):
        """Test that invalid UUID formats are rejected."""
        invalid_ids = [
            "not-a-uuid",
            "12345",
            "550e8400-e29b-11d4-a716-446655440000",  # v1 UUID
            "550e8400e29b41d4a716446655440000",  # No hyphens
            "",
            None,
        ]

        for session_id in invalid_ids:
            assert is_valid_session_id(session_id) is False

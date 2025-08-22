"""Assessment router for ticker validation and assessment flow."""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.services.session_manager import SessionManager
from src.utils.validators import validate_ticker_format

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/assessment",
    tags=["assessment"],
    responses={404: {"description": "Not found"}},
)

session_manager = SessionManager()


class TickerSubmission(BaseModel):
    """Request model for ticker submission."""

    ticker_symbol: str = Field(
        ...,
        min_length=1,
        max_length=6,
        description="Stock ticker symbol (1-6 letters)",
        example="ASML",
    )


class SessionResponse(BaseModel):
    """Response model for session initialization."""

    session_id: str = Field(..., description="Unique session identifier")
    ticker_symbol: str = Field(..., description="Validated ticker symbol")
    status: str = Field(..., description="Session status")
    created_at: datetime = Field(..., description="Session creation timestamp")
    message: str = Field(..., description="Response message")


@router.post("/start", response_model=SessionResponse, status_code=status.HTTP_200_OK)
async def start_assessment(submission: TickerSubmission) -> SessionResponse:
    """
    Initialize assessment session with ticker validation.

    Args:
        submission: Ticker submission containing the stock symbol

    Returns:
        SessionResponse with session details

    Raises:
        HTTPException: If ticker format is invalid
    """
    ticker = submission.ticker_symbol.strip().upper()

    logger.info(f"Starting assessment for ticker: {ticker}")

    try:
        is_valid, error_message = validate_ticker_format(ticker)

        if not is_valid:
            logger.warning(f"Invalid ticker format: {ticker} - {error_message}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)

        session = session_manager.create_session(ticker)

        logger.info(f"Session created: {session['session_id']} for ticker: {ticker}")

        return SessionResponse(
            session_id=session["session_id"],
            ticker_symbol=session["ticker_symbol"],
            status=session["status"],
            created_at=session["created_at"],
            message=f"Session initialized for {ticker}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating session for ticker {ticker}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to initialize session"
        ) from e


@router.get("/session/{session_id}", response_model=dict[str, Any])
async def get_session(session_id: str) -> dict[str, Any]:
    """
    Retrieve session information.

    Args:
        session_id: Unique session identifier

    Returns:
        Session details

    Raises:
        HTTPException: If session not found
    """
    session = session_manager.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found"
        )

    return session

"""Assessment router for ticker validation and assessment flow."""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.agents.assessment_agent import AssessmentAgent
from src.models.assessment import AssessmentQuestion, AssessmentResponse, AssessmentResult
from src.services.session_manager import SessionManager
from src.utils.rate_limiter import rate_limit_openai
from src.utils.validators import is_valid_session_id, validate_ticker_format

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/assessment",
    tags=["assessment"],
    responses={404: {"description": "Not found"}},
)

session_manager = SessionManager()
assessment_agent = AssessmentAgent()


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


class QuestionsResponse(BaseModel):
    """Response model for assessment questions."""

    session_id: str = Field(..., description="Session identifier")
    ticker_symbol: str = Field(..., description="Ticker symbol for context")
    questions: list[AssessmentQuestion] = Field(..., description="Generated assessment questions")
    total_questions: int = Field(..., description="Total number of questions")
    message: str = Field(..., description="Response message")


class AssessmentSubmission(BaseModel):
    """Request model for assessment submission."""

    session_id: str = Field(..., description="Session identifier")
    responses: list[AssessmentResponse] = Field(
        ..., min_items=1, max_items=20, description="User responses to assessment questions"
    )


class AssessmentResultResponse(BaseModel):
    """Response model for assessment results."""

    session_id: str = Field(..., description="Session identifier")
    result: AssessmentResult = Field(..., description="Assessment evaluation result")
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


@router.get("/questions", response_model=QuestionsResponse, status_code=status.HTTP_200_OK)
@rate_limit_openai(lambda session_id: f"questions_{session_id}")
async def get_assessment_questions(session_id: str) -> QuestionsResponse:
    """
    Generate and retrieve contextual assessment questions for a session.

    Args:
        session_id: Unique session identifier

    Returns:
        QuestionsResponse with 20 contextual questions

    Raises:
        HTTPException: If session not found or question generation fails
    """
    logger.info(f"Generating assessment questions for session: {session_id}")

    try:
        if not is_valid_session_id(session_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid session ID format"
            )

        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found"
            )

        ticker = session["ticker_symbol"]

        # Generate contextual questions using the assessment agent
        questions = assessment_agent.generate_contextual_assessment_questions(ticker)

        logger.info(f"Generated {len(questions)} questions for session {session_id}")

        return QuestionsResponse(
            session_id=session_id,
            ticker_symbol=ticker,
            questions=questions,
            total_questions=len(questions),
            message=f"Generated {len(questions)} contextual questions for {ticker}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating questions for session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate assessment questions",
        ) from e


@router.post("/submit", response_model=AssessmentResultResponse, status_code=status.HTTP_200_OK)
@rate_limit_openai(lambda submission: f"submit_{submission.session_id}")
async def submit_assessment(submission: AssessmentSubmission) -> AssessmentResultResponse:
    """
    Submit assessment responses and calculate expertise level.

    Args:
        submission: Assessment submission with responses

    Returns:
        AssessmentResultResponse with expertise evaluation

    Raises:
        HTTPException: If session not found or evaluation fails
    """
    session_id = submission.session_id
    logger.info(f"Processing assessment submission for session: {session_id}")

    try:
        if not is_valid_session_id(session_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid session ID format"
            )

        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found"
            )

        ticker = session["ticker_symbol"]

        # Generate questions again for evaluation context
        questions = assessment_agent.generate_contextual_assessment_questions(ticker)

        # Evaluate user expertise
        result = assessment_agent.evaluate_user_expertise(
            questions=questions, responses=submission.responses, ticker=ticker
        )

        # Set session_id in result
        result.session_id = session_id

        # Update session with assessment results
        session_manager.update_session_assessment(session_id, result)

        logger.info(
            f"Assessment completed for session {session_id}: "
            f"Expertise Level {result.expertise_level}/10"
        )

        return AssessmentResultResponse(
            session_id=session_id,
            result=result,
            message=f"Assessment completed: Expertise Level {result.expertise_level}/10",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing assessment for session {session_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process assessment submission",
        ) from e

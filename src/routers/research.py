"""Research workflow API endpoints."""

import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ..services.agent_coordinator import get_agent_coordinator
from ..services.research_database import get_research_database
from ..services.session_manager import get_session_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/research", tags=["research"])

# Security constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit for research files
ALLOWED_FILE_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml"}


def validate_file_path(file_path: str) -> str:
    """
    Validate file path to prevent directory traversal attacks.

    Args:
        file_path: User-provided file path

    Returns:
        Validated file path

    Raises:
        HTTPException: If path is invalid or contains traversal attempts
    """
    try:
        # Normalize path and check for traversal
        path = Path(file_path)

        # Check for path traversal attempts
        if ".." in path.parts or path.is_absolute():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path: directory traversal not allowed",
            )

        # Check file extension
        if path.suffix.lower() not in ALLOWED_FILE_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file extension: {path.suffix}. Allowed: {ALLOWED_FILE_EXTENSIONS}",
            )

        # Return normalized relative path
        safe_path = str(path).replace("\\", "/")

        return safe_path

    except (ValueError, OSError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid file path: {str(e)}"
        ) from e


def validate_session_ownership(session_id: str, requesting_session: str = None) -> None:
    """
    Validate session ownership to prevent unauthorized access.

    Args:
        session_id: Session identifier being accessed
        requesting_session: Session identifier of the requester

    Raises:
        HTTPException: If session ownership validation fails
    """
    # For MVP, we just validate session exists
    # In production, add proper session ownership validation
    session_manager = get_session_manager()
    if not session_manager.get_session(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found or access denied",
        )


class StartResearchRequest(BaseModel):
    """Request model for starting research process."""

    session_id: str = Field(..., description="Session identifier")


class StartResearchResponse(BaseModel):
    """Response model for starting research process."""

    research_id: str = Field(..., description="Research process identifier")
    message: str = Field(..., description="Status message")
    status: str = Field(..., description="Initial status")


@router.post(
    "/start",
    response_model=StartResearchResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start collaborative research process",
    description="Begin the multi-agent research process for a completed assessment session",
)
async def start_research(request: StartResearchRequest) -> StartResearchResponse:
    """
    Start the collaborative research process for a session.

    The session must have completed assessment with expertise level calculated.
    """
    try:
        # Security validation
        validate_session_ownership(request.session_id)

        # Get session manager and validate session
        session_manager = get_session_manager()
        session = session_manager.get_session_as_model(request.session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {request.session_id} not found",
            )

        # Validate session is ready for research
        if not session.assessment_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session must complete assessment before starting research",
            )

        if session.user_expertise_level is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session must have expertise level calculated",
            )

        # Create research database directory structure
        research_db = get_research_database()
        research_db.create_session_directory(request.session_id, session.ticker_symbol)

        # Start research process
        coordinator = get_agent_coordinator()
        research_id = await coordinator.start_research_process(
            session_id=request.session_id,
            ticker=session.ticker_symbol,
            expertise_level=session.user_expertise_level,
        )

        # Update session status
        session.status = "research"
        session_manager.update_session_model(session)

        logger.info(f"Started research process {research_id} for session {request.session_id}")

        return StartResearchResponse(
            research_id=research_id,
            message="Research process started successfully",
            status="active",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting research: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start research process: {str(e)}",
        ) from e


@router.get(
    "/status",
    summary="Get research progress status",
    description="Retrieve current research status and agent activity",
)
async def get_research_status(session_id: str) -> dict[str, Any]:
    """
    Get current research status and progress.

    Args:
        session_id: Session identifier

    Returns:
        Research status information including current agent and progress
    """
    try:
        # Security validation
        validate_session_ownership(session_id)

        coordinator = get_agent_coordinator()
        status_info = await coordinator.get_research_status(session_id)

        if "error" in status_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=status_info["error"])

        return status_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting research status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get research status: {str(e)}",
        ) from e


@router.get(
    "/database",
    summary="Get research database contents",
    description="Retrieve research files and metadata for a session",
)
async def get_research_database_endpoint(session_id: str) -> dict[str, Any]:
    """
    Get research database contents for a session.

    Args:
        session_id: Session identifier

    Returns:
        Research database contents including files and metadata
    """
    try:
        # Security validation
        validate_session_ownership(session_id)

        # Validate session exists
        session_manager = get_session_manager()
        session = session_manager.get_session_as_model(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found"
            )

        # Get research database contents
        research_db = get_research_database()
        files = research_db.get_session_files(session_id, session.ticker_symbol)

        # Get coordinator handoffs
        coordinator = get_agent_coordinator()
        handoffs = coordinator.get_session_handoffs(session_id)

        return {
            "session_id": session_id,
            "ticker": session.ticker_symbol,
            "files": files,
            "handoffs": handoffs,
            "file_count": len(files),
            "handoff_count": len(handoffs),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting research database: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get research database: {str(e)}",
        ) from e


@router.get(
    "/files/{file_path:path}",
    summary="Get specific research file",
    description="Retrieve content and metadata for a specific research file",
)
async def get_research_file(session_id: str, file_path: str) -> dict[str, Any]:
    """
    Get a specific research file with metadata.

    Args:
        session_id: Session identifier
        file_path: Relative path to research file

    Returns:
        File metadata and content
    """
    try:
        # Security validations
        validate_session_ownership(session_id)
        safe_file_path = validate_file_path(file_path)

        # Validate session exists
        session_manager = get_session_manager()
        session = session_manager.get_session_as_model(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found"
            )

        # Get research file with validated path
        research_db = get_research_database()
        try:
            file_data = research_db.read_research_file(
                session_id, session.ticker_symbol, safe_file_path
            )

            # Check file size limit
            content_size = len(file_data["content"])
            if content_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large: {content_size} bytes (max: {MAX_FILE_SIZE})",
                )

            return {
                "session_id": session_id,
                "ticker": session.ticker_symbol,
                "file_path": safe_file_path,
                "metadata": file_data["metadata"],
                "content": file_data["content"],
                "content_length": content_size,
            }

        except FileNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Research file not found: {safe_file_path}",
            ) from e

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting research file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get research file: {str(e)}",
        ) from e

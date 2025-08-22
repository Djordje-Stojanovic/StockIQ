"""Research workflow API endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ..services.agent_coordinator import get_agent_coordinator
from ..services.research_database import get_research_database
from ..services.session_manager import get_session_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/research", tags=["research"])


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
    description="Begin the multi-agent research process for a completed assessment session"
)
async def start_research(request: StartResearchRequest) -> StartResearchResponse:
    """
    Start the collaborative research process for a session.
    
    The session must have completed assessment with expertise level calculated.
    """
    try:
        # Get session manager and validate session
        session_manager = get_session_manager()
        session = session_manager.get_session_as_model(request.session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {request.session_id} not found"
            )

        # Validate session is ready for research
        if not session.assessment_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session must complete assessment before starting research"
            )

        if session.user_expertise_level is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session must have expertise level calculated"
            )

        # Create research database directory structure
        research_db = get_research_database()
        research_db.create_session_directory(request.session_id, session.ticker_symbol)

        # Start research process
        coordinator = get_agent_coordinator()
        research_id = await coordinator.start_research_process(
            session_id=request.session_id,
            ticker=session.ticker_symbol,
            expertise_level=session.user_expertise_level
        )

        # Update session status
        session.status = "research"
        session_manager.update_session_model(session)

        logger.info(f"Started research process {research_id} for session {request.session_id}")

        return StartResearchResponse(
            research_id=research_id,
            message="Research process started successfully",
            status="active"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting research: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start research process: {str(e)}"
        )


@router.get(
    "/status",
    summary="Get research progress status",
    description="Retrieve current research status and agent activity"
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
        coordinator = get_agent_coordinator()
        status_info = await coordinator.get_research_status(session_id)

        if "error" in status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=status_info["error"]
            )

        return status_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting research status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get research status: {str(e)}"
        )


@router.get(
    "/database",
    summary="Get research database contents",
    description="Retrieve research files and metadata for a session"
)
async def get_research_database(session_id: str) -> dict[str, Any]:
    """
    Get research database contents for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Research database contents including files and metadata
    """
    try:
        # Validate session exists
        session_manager = get_session_manager()
        session = session_manager.get_session_as_model(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
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
            "handoff_count": len(handoffs)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting research database: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get research database: {str(e)}"
        )


@router.get(
    "/files/{file_path:path}",
    summary="Get specific research file",
    description="Retrieve content and metadata for a specific research file"
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
        # Validate session exists
        session_manager = get_session_manager()
        session = session_manager.get_session_as_model(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        # Get research file
        research_db = get_research_database()
        try:
            file_data = research_db.read_research_file(session_id, session.ticker_symbol, file_path)

            return {
                "session_id": session_id,
                "ticker": session.ticker_symbol,
                "file_path": file_path,
                "metadata": file_data["metadata"],
                "content": file_data["content"],
                "content_length": len(file_data["content"])
            }

        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Research file not found: {file_path}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting research file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get research file: {str(e)}"
        )

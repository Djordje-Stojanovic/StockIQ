"""Session management service for StockIQ."""

import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ..models.assessment import UserSession

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages user sessions for assessment and analysis."""

    def __init__(self):
        """Initialize session manager with in-memory storage."""
        self._sessions: dict[str, dict[str, Any]] = {}
        logger.info("SessionManager initialized")

    def create_session(self, ticker_symbol: str) -> dict[str, Any]:
        """
        Create a new session for ticker analysis.

        Args:
            ticker_symbol: Validated ticker symbol

        Returns:
            Session dictionary with all details
        """
        session_id = str(uuid.uuid4())

        session = {
            "session_id": session_id,
            "ticker_symbol": ticker_symbol.upper(),
            "user_expertise_level": None,
            "assessment_responses": [],
            "report_complexity": None,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
            "status": "active",
            "research_database_path": f"research_database/sessions/{session_id}/{ticker_symbol}",
        }

        self._sessions[session_id] = session

        self._prepare_research_directory(session["research_database_path"])

        logger.info(f"Created session {session_id} for ticker {ticker_symbol}")

        return session

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """
        Retrieve session by ID.

        Args:
            session_id: Unique session identifier

        Returns:
            Session dictionary if found, None otherwise
        """
        session = self._sessions.get(session_id)
        if session:
            logger.debug(f"Retrieved session {session_id}")
        else:
            logger.warning(f"Session {session_id} not found")
        return session

    def update_session(self, session_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
        """
        Update session data.

        Args:
            session_id: Unique session identifier
            updates: Dictionary of fields to update

        Returns:
            Updated session if found, None otherwise
        """
        session = self._sessions.get(session_id)
        if not session:
            logger.warning(f"Cannot update non-existent session {session_id}")
            return None

        session.update(updates)
        session["updated_at"] = datetime.now(UTC)

        logger.info(f"Updated session {session_id} with {len(updates)} fields")

        return session

    def update_session_assessment(
        self, session_id: str, assessment_result: Any
    ) -> dict[str, Any] | None:
        """
        Update session with assessment results.

        Args:
            session_id: Unique session identifier
            assessment_result: AssessmentResult object

        Returns:
            Updated session if found, None otherwise
        """
        session = self._sessions.get(session_id)
        if not session:
            logger.warning(f"Cannot update assessment for non-existent session {session_id}")
            return None

        session.update(
            {
                "user_expertise_level": assessment_result.expertise_level,
                "assessment_result": assessment_result,
                "report_complexity": assessment_result.report_complexity,
                "updated_at": datetime.now(UTC),
            }
        )

        logger.info(
            f"Updated session {session_id} with assessment: "
            f"Level {assessment_result.expertise_level}/10"
        )

        return session

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Unique session identifier

        Returns:
            True if deleted, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Deleted session {session_id}")
            return True

        logger.warning(f"Cannot delete non-existent session {session_id}")
        return False

    def get_active_sessions(self) -> dict[str, dict[str, Any]]:
        """
        Get all active sessions.

        Returns:
            Dictionary of active sessions
        """
        active = {
            sid: session
            for sid, session in self._sessions.items()
            if session.get("status") == "active"
        }
        logger.debug(f"Found {len(active)} active sessions")
        return active

    def get_session_as_model(self, session_id: str) -> UserSession | None:
        """
        Get session as a UserSession model object.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            UserSession object if found, None otherwise
        """
        session_dict = self.get_session(session_id)
        if not session_dict:
            return None
        
        try:
            # Convert dictionary to UserSession model
            return UserSession(**session_dict)
        except Exception as e:
            logger.error(f"Error converting session {session_id} to UserSession model: {str(e)}")
            return None

    def update_session_model(self, session: UserSession) -> UserSession | None:
        """
        Update session using a UserSession model.
        
        Args:
            session: UserSession model object
            
        Returns:
            Updated UserSession if successful, None otherwise
        """
        try:
            # Convert model to dictionary and update
            session_dict = session.model_dump()
            updated = self.update_session(session.session_id, session_dict)
            if updated:
                return UserSession(**updated)
            return None
        except Exception as e:
            logger.error(f"Error updating session {session.session_id} from model: {str(e)}")
            return None

    def _prepare_research_directory(self, path: str) -> None:
        """
        Prepare research database directory structure.

        Args:
            path: Path to research directory
        """
        try:
            research_path = Path(path)

            subdirs = ["valuation", "strategic", "historical", "synthesis"]
            for subdir in subdirs:
                subdir_path = research_path / subdir
                subdir_path.mkdir(parents=True, exist_ok=True)

            logger.debug(f"Prepared research directory: {path}")
        except Exception as e:
            logger.error(f"Failed to prepare research directory {path}: {str(e)}")


# Global session manager instance
_session_manager_instance: SessionManager | None = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager_instance
    if _session_manager_instance is None:
        _session_manager_instance = SessionManager()
    return _session_manager_instance

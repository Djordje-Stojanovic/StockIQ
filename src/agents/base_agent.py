"""Base agent implementation with research database access."""

import logging
from abc import ABC, abstractmethod
from typing import Any

from ..models.collaboration import AgentResult
from ..services.research_database import get_research_database

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all research agents with standard interface."""

    def __init__(self, agent_name: str):
        """
        Initialize base agent.
        
        Args:
            agent_name: Unique name for this agent
        """
        self.agent_name = agent_name
        self.research_db = get_research_database()
        self.logger = logging.getLogger(f"agent.{agent_name}")

    @abstractmethod
    async def conduct_research(
        self, session_id: str, ticker: str, expertise_level: int, context: dict[str, Any] | None = None
    ) -> AgentResult:
        """
        Conduct research for a specific ticker and session.
        
        Args:
            session_id: Unique session identifier
            ticker: Stock ticker symbol
            expertise_level: User expertise level (1-10)
            context: Previous research context from other agents
            
        Returns:
            AgentResult with research findings and metadata
        """
        pass

    def read_research_context(self, session_id: str, ticker: str) -> dict[str, Any]:
        """
        Read available research context from previous agents.
        
        Args:
            session_id: Session identifier
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with context from previous research
        """
        try:
            # Determine agent type from agent name
            agent_type = self._get_agent_type()
            context = self.research_db.get_agent_context(session_id, ticker, agent_type)

            self.logger.info(f"Retrieved context for {self.agent_name}: {len(context.get('previous_research', {}))} previous agents")
            return context

        except Exception as e:
            self.logger.error(f"Error reading research context: {str(e)}")
            return {"error": str(e), "previous_research": {}}

    def write_research_file(
        self,
        session_id: str,
        ticker: str,
        filename: str,
        content: str,
        metadata: dict[str, Any] | None = None
    ) -> str:
        """
        Write a research file to the database.
        
        Args:
            session_id: Session identifier
            ticker: Stock ticker symbol
            filename: Name of the research file
            content: Research content in markdown format
            metadata: Additional metadata for the file
            
        Returns:
            Relative path to the written file
        """
        try:
            if metadata is None:
                metadata = {}

            # Add agent-specific metadata
            metadata.update({
                "author": self.agent_name,
                "title": filename.replace(".md", "").replace("_", " ").title(),
                "topic": self._get_agent_type()
            })

            # Write file to research database
            agent_type = self._get_agent_type()
            file_path = self.research_db.write_research_file(
                session_id=session_id,
                ticker=ticker,
                agent_type=agent_type,
                filename=filename,
                content=content,
                metadata=metadata
            )

            # Return relative path from session directory
            sessions_path = self.research_db.sessions_path / session_id / ticker
            relative_path = str(file_path.relative_to(sessions_path))

            self.logger.info(f"Wrote research file: {relative_path}")
            return relative_path

        except Exception as e:
            self.logger.error(f"Error writing research file: {str(e)}")
            raise

    def add_cross_reference(
        self, session_id: str, ticker: str, source_file: str, target_file: str, relationship: str
    ) -> None:
        """
        Add a cross-reference between research files.
        
        Args:
            session_id: Session identifier
            ticker: Stock ticker symbol
            source_file: Source file path
            target_file: Target file path
            relationship: Description of relationship
        """
        try:
            self.research_db.add_cross_reference(session_id, ticker, source_file, target_file, relationship)
            self.logger.info(f"Added cross-reference: {source_file} -> {target_file} ({relationship})")
        except Exception as e:
            self.logger.error(f"Error adding cross-reference: {str(e)}")

    def format_handoff_data(
        self,
        session_id: str,
        ticker: str,
        research_files: list[str],
        summary: str,
        confidence_metrics: dict[str, Any] | None = None,
        token_usage: int = 0
    ) -> dict[str, Any]:
        """
        Format data for handoff to next agent.
        
        Args:
            session_id: Session identifier
            ticker: Stock ticker symbol
            research_files: List of research files created
            summary: Summary of research findings
            confidence_metrics: Agent confidence metrics
            token_usage: Tokens consumed during research
            
        Returns:
            Formatted handoff data dictionary
        """
        if confidence_metrics is None:
            confidence_metrics = {"confidence": 0.5, "completeness": 0.5}

        return {
            "research_files": research_files,
            "context_summary": summary,
            "cross_references": [],  # Can be populated by subclasses
            "confidence_metrics": confidence_metrics,
            "token_usage": token_usage
        }

    def _get_agent_type(self) -> str:
        """
        Determine agent type from agent name.
        
        Returns:
            Agent type string for directory structure
        """
        # Map agent names to directory types
        type_mapping = {
            "valuation_agent": "valuation",
            "strategic_agent": "strategic",
            "historian_agent": "historical",
            "synthesis_agent": "synthesis"
        }

        return type_mapping.get(self.agent_name, self.agent_name.replace("_agent", ""))

    def validate_research_context(self, context: dict[str, Any]) -> bool:
        """
        Validate that research context contains required information.
        
        Args:
            context: Research context dictionary
            
        Returns:
            True if context is valid, False otherwise
        """
        required_keys = ["session_id", "ticker", "requesting_agent"]
        return all(key in context for key in required_keys)

    def get_expertise_adjusted_depth(self, expertise_level: int) -> str:
        """
        Get research depth based on user expertise level.
        
        Args:
            expertise_level: User expertise level (1-10)
            
        Returns:
            Research depth string
        """
        if expertise_level <= 2:
            return "foundational"  # Maximum educational content
        elif expertise_level <= 4:
            return "educational"   # Detailed explanations
        elif expertise_level <= 6:
            return "intermediate"  # Balanced analysis
        elif expertise_level <= 8:
            return "advanced"      # Sophisticated analysis
        else:
            return "executive"     # Expert summaries

    def log_research_start(self, session_id: str, ticker: str, expertise_level: int) -> None:
        """Log the start of research process."""
        depth = self.get_expertise_adjusted_depth(expertise_level)
        self.logger.info(
            f"Starting {self.agent_name} research for {ticker} "
            f"(Session: {session_id}, Expertise: {expertise_level}, Depth: {depth})"
        )

    def log_research_complete(self, session_id: str, ticker: str, files_created: list[str]) -> None:
        """Log the completion of research process."""
        self.logger.info(
            f"Completed {self.agent_name} research for {ticker} "
            f"(Session: {session_id}, Files: {len(files_created)})"
        )

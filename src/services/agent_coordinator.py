"""Agent coordination service for sequential research orchestration."""

import asyncio
import logging
from typing import Any

from ..models.collaboration import AgentHandoff, AgentResult, ResearchStatus

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """Manages sequential execution of research agents with context handoffs."""

    def __init__(self):
        """Initialize the agent coordinator."""
        # Define the sequential agent execution order
        self.agent_order = [
            "valuation_agent",
            "strategic_agent",
            "historian_agent",
            "synthesis_agent"
        ]

        # Track active research sessions
        self.active_sessions: dict[str, ResearchStatus] = {}

        # Store agent handoffs for each session
        self.session_handoffs: dict[str, list[AgentHandoff]] = {}

    async def start_research_process(
        self, session_id: str, ticker: str, expertise_level: int
    ) -> str:
        """
        Start the collaborative research process for a session.
        
        Args:
            session_id: Unique session identifier
            ticker: Stock ticker symbol
            expertise_level: User expertise level (1-10)
            
        Returns:
            Research process ID (same as session_id for now)
        """
        logger.info(f"Starting research process for session {session_id}, ticker {ticker}")

        # Initialize research status
        research_status = ResearchStatus(
            session_id=session_id,
            ticker=ticker,
            status="active",
            current_agent=self.agent_order[0] if self.agent_order else None
        )

        self.active_sessions[session_id] = research_status
        self.session_handoffs[session_id] = []

        # Start the research process (non-blocking)
        asyncio.create_task(self._execute_research_workflow(session_id, ticker, expertise_level))

        return session_id

    async def get_research_status(self, session_id: str) -> dict[str, Any]:
        """
        Get current research status for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary containing research status information
        """
        if session_id not in self.active_sessions:
            return {"error": "Session not found", "session_id": session_id}

        status = self.active_sessions[session_id]
        return {
            "session_id": status.session_id,
            "ticker": status.ticker,
            "current_agent": status.current_agent,
            "agents_completed": status.agents_completed,
            "agents_failed": status.agents_failed,
            "progress_percentage": status.progress_percentage,
            "status": status.status,
            "error_message": status.error_message,
            "started_at": status.started_at.isoformat(),
            "completed_at": status.completed_at.isoformat() if status.completed_at else None
        }

    async def handle_agent_failure(self, session_id: str, agent_name: str, error: Exception) -> bool:
        """
        Handle failure of an individual agent with graceful degradation.
        
        Args:
            session_id: Session identifier
            agent_name: Name of the failed agent
            error: Exception that caused the failure
            
        Returns:
            True if recovery successful, False if critical failure
        """
        logger.error(f"Agent {agent_name} failed for session {session_id}: {str(error)}")

        if session_id not in self.active_sessions:
            return False

        status = self.active_sessions[session_id]
        status.agents_failed.append(agent_name)

        # Check if this is a critical agent (for now, all agents are considered recoverable)
        critical_agents = {"valuation_agent"}  # Valuation is most critical

        if agent_name in critical_agents:
            # Critical failure - abort the process
            status.status = "failed"
            status.error_message = f"Critical agent {agent_name} failed: {str(error)}"
            logger.error(f"Critical agent failure - aborting research for session {session_id}")
            return False

        # Non-critical failure - continue with remaining agents
        logger.warning(f"Non-critical agent {agent_name} failed - continuing research")
        return True

    async def coordinate_agent_handoff(
        self, session_id: str, source_agent: str, target_agent: str, data: dict[str, Any]
    ) -> bool:
        """
        Coordinate handoff between agents with data validation.
        
        Args:
            session_id: Session identifier
            source_agent: Agent providing the data
            target_agent: Agent receiving the data
            data: Handoff data dictionary
            
        Returns:
            True if handoff successful, False otherwise
        """
        try:
            # Create AgentHandoff object
            handoff = AgentHandoff(
                source_agent=source_agent,
                target_agent=target_agent,
                research_files=data.get("research_files", []),
                context_summary=data.get("context_summary", ""),
                cross_references=data.get("cross_references", []),
                confidence_metrics=data.get("confidence_metrics", {}),
                token_usage=data.get("token_usage", 0)
            )

            # Validate handoff integrity
            if not handoff.validate_handoff_integrity():
                logger.error(f"Handoff validation failed for {source_agent} -> {target_agent}")
                return False

            # Store handoff
            if session_id not in self.session_handoffs:
                self.session_handoffs[session_id] = []

            self.session_handoffs[session_id].append(handoff)

            # Update research status
            if session_id in self.active_sessions:
                status = self.active_sessions[session_id]
                if source_agent not in status.agents_completed:
                    status.agents_completed.append(source_agent)
                status.current_agent = target_agent

                # Update progress
                total_agents = len(self.agent_order)
                completed_agents = len(status.agents_completed)
                status.progress_percentage = (completed_agents / total_agents) * 100

            # Serialize handoff to JSON for logging/debugging
            handoff_json = handoff.model_dump_json(indent=2)
            logger.info(f"Agent handoff completed: {source_agent} -> {target_agent}")
            logger.debug(f"Handoff data: {handoff_json}")

            return True

        except Exception as e:
            logger.error(f"Error during agent handoff: {str(e)}")
            return False

    async def _execute_research_workflow(
        self, session_id: str, ticker: str, expertise_level: int
    ) -> None:
        """
        Execute the complete research workflow with sequential agents.
        
        Args:
            session_id: Session identifier
            ticker: Stock ticker symbol
            expertise_level: User expertise level
        """
        try:
            logger.info(f"Executing research workflow for {ticker}")

            # For now, we'll mock the agent execution since actual agents aren't implemented yet
            # This provides the framework for when real agents are added

            for i, agent_name in enumerate(self.agent_order):
                if session_id not in self.active_sessions:
                    logger.warning(f"Session {session_id} no longer active, stopping workflow")
                    return

                status = self.active_sessions[session_id]
                status.current_agent = agent_name

                logger.info(f"Starting {agent_name} for session {session_id}")

                # Mock agent execution (replace with actual agent calls later)
                await self._mock_agent_execution(session_id, agent_name, ticker, expertise_level)

                # Simulate handoff to next agent (except for last agent)
                if i < len(self.agent_order) - 1:
                    next_agent = self.agent_order[i + 1]

                    # Create mock handoff data
                    handoff_data = {
                        "research_files": [f"research_database/sessions/{session_id}/{ticker}/{agent_name.split('_')[0]}/analysis_v1.md"],
                        "context_summary": f"Completed comprehensive {agent_name} analysis for {ticker}. Key findings include detailed financial metrics, market positioning assessment, competitive analysis, and strategic recommendations. Analysis provides thorough foundation for {next_agent} to build upon with additional insights and specialized expertise.",
                        "cross_references": [],
                        "confidence_metrics": {"confidence": 0.8, "completeness": 0.9},
                        "token_usage": 1500
                    }

                    # Execute handoff
                    await self.coordinate_agent_handoff(session_id, agent_name, next_agent, handoff_data)

            # Mark research as completed
            if session_id in self.active_sessions:
                status = self.active_sessions[session_id]
                status.status = "completed"
                status.current_agent = None
                status.progress_percentage = 100.0
                from datetime import UTC, datetime
                status.completed_at = datetime.now(UTC)

                logger.info(f"Research workflow completed for session {session_id}")

        except Exception as e:
            logger.error(f"Error in research workflow for session {session_id}: {str(e)}")
            if session_id in self.active_sessions:
                status = self.active_sessions[session_id]
                status.status = "failed"
                status.error_message = str(e)

    async def _mock_agent_execution(
        self, session_id: str, agent_name: str, ticker: str, expertise_level: int
    ) -> AgentResult:
        """
        Mock agent execution for testing the coordination framework.
        
        This will be replaced with actual agent implementations.
        """
        # Simulate some processing time
        await asyncio.sleep(1)

        # Create mock result
        result = AgentResult(
            agent_name=agent_name,
            success=True,
            research_files_created=[f"research_database/sessions/{session_id}/{ticker}/{agent_name.split('_')[0]}/analysis_v1.md"],
            summary=f"Completed {agent_name} analysis for {ticker}",
            token_usage=1500,
            execution_time_seconds=1.0,
            confidence_score=0.85
        )

        logger.info(f"Mock {agent_name} execution completed for {ticker}")
        return result

    def get_session_handoffs(self, session_id: str) -> list[dict[str, Any]]:
        """
        Get all handoffs for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of handoff dictionaries
        """
        if session_id not in self.session_handoffs:
            return []

        return [handoff.model_dump() for handoff in self.session_handoffs[session_id]]

    def cleanup_session(self, session_id: str) -> None:
        """
        Clean up session data after research completion.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

        if session_id in self.session_handoffs:
            del self.session_handoffs[session_id]

        logger.info(f"Cleaned up session data for {session_id}")


# Global coordinator instance
_coordinator_instance: AgentCoordinator | None = None


def get_agent_coordinator() -> AgentCoordinator:
    """Get the global agent coordinator instance."""
    global _coordinator_instance
    if _coordinator_instance is None:
        _coordinator_instance = AgentCoordinator()
    return _coordinator_instance

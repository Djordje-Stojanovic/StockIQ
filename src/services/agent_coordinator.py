"""Agent coordination service for sequential research orchestration."""

import asyncio
import logging
from typing import Any

from ..agents.valuation_agent import ValuationAgent
from ..models.collaboration import AgentHandoff, AgentResult, ResearchStatus

logger = logging.getLogger(__name__)


class AgentCoordinator:
    """Manages sequential execution of research agents with context handoffs."""

    def __init__(self, enable_retries: bool = True):
        """Initialize the agent coordinator."""
        # Define the sequential agent execution order
        self.agent_order = [
            "valuation_agent",
            "strategic_agent",
            "historian_agent",
            "synthesis_agent",
        ]

        # Initialize agent instances
        self.agents = {
            "valuation_agent": ValuationAgent(),
            # Other agents will be added as they're implemented
            "strategic_agent": None,  # Placeholder for future implementation
            "historian_agent": None,  # Placeholder for future implementation
            "synthesis_agent": None,  # Placeholder for future implementation
        }

        # Track active research sessions
        self.active_sessions: dict[str, ResearchStatus] = {}

        # Store agent handoffs for each session
        self.session_handoffs: dict[str, list[AgentHandoff]] = {}

        # Track retry counts for each agent per session
        self.agent_retry_counts: dict[str, dict[str, int]] = {}

        # Maximum retries per agent
        self.max_retries = 3 if enable_retries else 0

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
            current_agent=self.agent_order[0] if self.agent_order else None,
        )

        self.active_sessions[session_id] = research_status
        self.session_handoffs[session_id] = []
        self.agent_retry_counts[session_id] = {}

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
            "completed_at": status.completed_at.isoformat() if status.completed_at else None,
        }

    async def handle_agent_failure(
        self, session_id: str, agent_name: str, error: Exception
    ) -> bool:
        """
        Handle failure of an individual agent with retry logic and graceful degradation.

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

        # Initialize retry count for this agent if not exists
        if session_id not in self.agent_retry_counts:
            self.agent_retry_counts[session_id] = {}
        if agent_name not in self.agent_retry_counts[session_id]:
            self.agent_retry_counts[session_id][agent_name] = 0

        # Get current retry count
        retry_count = self.agent_retry_counts[session_id][agent_name]

        # Check if we should retry
        if retry_count < self.max_retries:
            # Increment retry count
            self.agent_retry_counts[session_id][agent_name] += 1
            retry_count += 1

            # Calculate exponential backoff delay (1s, 2s, 4s)
            delay = 2 ** (retry_count - 1)

            logger.info(
                f"Retrying agent {agent_name} for session {session_id} "
                f"(attempt {retry_count}/{self.max_retries}) after {delay}s delay"
            )

            # Schedule retry with exponential backoff
            await asyncio.sleep(delay)

            # Attempt to retry the agent
            retry_success = await self._retry_agent(session_id, agent_name)

            if retry_success:
                logger.info(f"Agent {agent_name} succeeded on retry {retry_count}")
                # Remove from failed list if it was added
                if agent_name in status.agents_failed:
                    status.agents_failed.remove(agent_name)
                return True
            else:
                # If retry also failed, continue to check if we have more retries
                if retry_count < self.max_retries:
                    # Will retry again
                    return await self.handle_agent_failure(session_id, agent_name, error)

        # No more retries - mark as failed
        if agent_name not in status.agents_failed:
            status.agents_failed.append(agent_name)

        # Check if this is a critical agent (all agents are critical per PO requirement)
        critical_agents = {
            "valuation_agent",
            "strategic_agent",
            "historian_agent",
            "synthesis_agent",
        }

        if agent_name in critical_agents:
            # Critical failure - abort the process
            status.status = "failed"
            status.error_message = (
                f"Critical agent {agent_name} failed after {self.max_retries} retries: {str(error)}"
            )
            logger.error(
                f"Critical agent failure after all retries - aborting research for session {session_id}"
            )
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
                token_usage=data.get("token_usage", 0),
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

                # Execute agent - use real agent if available, otherwise mock
                if self.agents[agent_name] is not None:
                    result = await self._execute_real_agent(
                        session_id, agent_name, ticker, expertise_level
                    )
                else:
                    # Fall back to mock execution for unimplemented agents
                    result = await self._mock_agent_execution(
                        session_id, agent_name, ticker, expertise_level
                    )

                # Handle agent failure if needed
                if not result.success:
                    failure_handled = await self.handle_agent_failure(
                        session_id, agent_name, Exception(result.error_message or "Agent execution failed")
                    )
                    if not failure_handled:
                        # Critical failure, abort research
                        return

                # Simulate handoff to next agent (except for last agent)
                if i < len(self.agent_order) - 1:
                    next_agent = self.agent_order[i + 1]

                    # Create mock handoff data
                    handoff_data = {
                        "research_files": [
                            f"research_database/sessions/{session_id}/{ticker}/{agent_name.split('_')[0]}/analysis_v1.md"
                        ],
                        "context_summary": f"Completed comprehensive {agent_name} analysis for {ticker}. Key findings include detailed financial metrics, market positioning assessment, competitive analysis, and strategic recommendations. Analysis provides thorough foundation for {next_agent} to build upon with additional insights and specialized expertise.",
                        "cross_references": [],
                        "confidence_metrics": {"confidence": 0.8, "completeness": 0.9},
                        "token_usage": 1500,
                    }

                    # Execute handoff
                    await self.coordinate_agent_handoff(
                        session_id, agent_name, next_agent, handoff_data
                    )

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

    async def _execute_real_agent(
        self, session_id: str, agent_name: str, ticker: str, expertise_level: int
    ) -> AgentResult:
        """
        Execute a real agent with proper context handling.

        Args:
            session_id: Session identifier
            agent_name: Name of the agent to execute
            ticker: Stock ticker symbol
            expertise_level: User expertise level

        Returns:
            AgentResult from agent execution
        """
        try:
            agent = self.agents[agent_name]
            if agent is None:
                raise ValueError(f"Agent {agent_name} not implemented")

            # Prepare context from previous agents
            context = self._build_agent_context(session_id, ticker, agent_name)

            logger.info(f"Executing real agent {agent_name} for {ticker}")

            # Execute the agent's research method
            result = await agent.conduct_research(session_id, ticker, expertise_level, context)

            logger.info(
                f"Real agent {agent_name} completed for {ticker}: "
                f"Success={result.success}, Files={len(result.research_files_created)}, "
                f"Tokens={result.token_usage}, Time={result.execution_time_seconds:.1f}s"
            )

            return result

        except Exception as e:
            logger.error(f"Error executing real agent {agent_name}: {str(e)}")
            return AgentResult(
                agent_name=agent_name,
                success=False,
                summary=f"Agent {agent_name} failed during execution",
                error_message=str(e),
                execution_time_seconds=0.0,
            )

    def _build_agent_context(self, session_id: str, ticker: str, current_agent: str) -> dict[str, Any]:
        """
        Build context from previous agents for the current agent.

        Args:
            session_id: Session identifier
            ticker: Stock ticker symbol
            current_agent: Current agent name

        Returns:
            Context dictionary with previous research
        """
        context = {
            "session_id": session_id,
            "ticker": ticker,
            "requesting_agent": current_agent,
            "previous_research": {},
        }

        # Get handoffs for this session
        if session_id in self.session_handoffs:
            for handoff in self.session_handoffs[session_id]:
                context["previous_research"][handoff.source_agent] = {
                    "research_files": handoff.research_files,
                    "summary": handoff.context_summary,
                    "cross_references": handoff.cross_references,
                    "confidence_metrics": handoff.confidence_metrics,
                    "token_usage": handoff.token_usage,
                    "timestamp": handoff.handoff_timestamp.isoformat(),
                }

        return context

    async def _mock_agent_execution(
        self, session_id: str, agent_name: str, ticker: str, expertise_level: int
    ) -> AgentResult:
        """
        Mock agent execution for testing the coordination framework.

        This is used for agents that aren't implemented yet.
        """
        # Simulate some processing time
        await asyncio.sleep(1)

        # Create mock result
        result = AgentResult(
            agent_name=agent_name,
            success=True,
            research_files_created=[
                f"research_database/sessions/{session_id}/{ticker}/{agent_name.split('_')[0]}/analysis_v1.md"
            ],
            summary=f"Completed {agent_name} analysis for {ticker}",
            token_usage=1500,
            execution_time_seconds=1.0,
            confidence_score=0.85,
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

    async def _retry_agent(self, session_id: str, agent_name: str) -> bool:
        """
        Retry a failed agent execution.

        Args:
            session_id: Session identifier
            agent_name: Name of the agent to retry

        Returns:
            True if retry successful, False otherwise
        """
        try:
            logger.info(f"Retrying agent {agent_name} for session {session_id}")

            if session_id not in self.active_sessions:
                return False

            status = self.active_sessions[session_id]
            ticker = status.ticker

            # Get expertise level from first handoff or default to 5
            expertise_level = 5
            if session_id in self.session_handoffs and self.session_handoffs[session_id]:
                # Extract from context if available
                expertise_level = 5  # Default for now

            # Re-execute the agent - use real agent if available, otherwise mock
            if self.agents[agent_name] is not None:
                result = await self._execute_real_agent(
                    session_id, agent_name, ticker, expertise_level
                )
            else:
                result = await self._mock_agent_execution(
                    session_id, agent_name, ticker, expertise_level
                )

            return result.success

        except Exception as e:
            logger.error(f"Error during agent retry: {str(e)}")
            return False

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

        if session_id in self.agent_retry_counts:
            del self.agent_retry_counts[session_id]

        logger.info(f"Cleaned up session data for {session_id}")


# Global coordinator instance
_coordinator_instance: AgentCoordinator | None = None


def get_agent_coordinator() -> AgentCoordinator:
    """Get the global agent coordinator instance."""
    global _coordinator_instance
    if _coordinator_instance is None:
        _coordinator_instance = AgentCoordinator()
    return _coordinator_instance

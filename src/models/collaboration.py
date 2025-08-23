"""Inter-agent collaboration models for agent coordination."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class AgentHandoff(BaseModel):
    """Model for structured data transfer between agents."""

    source_agent: str = Field(..., description="Agent providing the data")
    target_agent: str = Field(..., description="Agent receiving the data")
    research_files: list[str] = Field(..., description="List of research file paths")
    context_summary: str = Field(..., max_length=5000, description="Condensed context for handoff")
    cross_references: list[str] = Field(
        default_factory=list, description="References to related analyses"
    )
    confidence_metrics: dict[str, Any] = Field(
        default_factory=dict, description="Agent confidence and quality metrics"
    )
    handoff_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Handoff completion time"
    )
    token_usage: int = Field(default=0, description="Tokens used in research phase")

    def validate_handoff_integrity(self) -> bool:
        """Validate handoff data integrity."""
        return (
            len(self.research_files) > 0
            and len(self.context_summary.strip()) > 100
            and self.source_agent != self.target_agent
        )


class ResearchStatus(BaseModel):
    """Model for tracking research process status."""

    session_id: str = Field(..., description="Session identifier")
    ticker: str = Field(..., description="Ticker being researched")
    current_agent: str | None = Field(None, description="Currently active agent")
    agents_completed: list[str] = Field(
        default_factory=list, description="Agents that have completed their work"
    )
    agents_failed: list[str] = Field(
        default_factory=list, description="Agents that failed during processing"
    )
    progress_percentage: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Overall progress percentage"
    )
    status: str = Field(
        default="pending", description="Overall research status"
    )  # pending, active, completed, failed
    error_message: str | None = Field(None, description="Error message if failed")
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Research start time"
    )
    completed_at: datetime | None = Field(None, description="Research completion time")


class AgentResult(BaseModel):
    """Model for agent execution results."""

    agent_name: str = Field(..., description="Name of the agent")
    success: bool = Field(..., description="Whether agent completed successfully")
    research_files_created: list[str] = Field(
        default_factory=list, description="Files created by this agent"
    )
    summary: str = Field(..., description="Summary of work completed")
    error_message: str | None = Field(None, description="Error message if failed")
    token_usage: int = Field(default=0, description="Tokens consumed")
    execution_time_seconds: float = Field(default=0.0, description="Time taken to complete")
    confidence_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Agent confidence in results"
    )
    completed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Completion timestamp"
    )

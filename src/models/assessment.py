"""Assessment-related data models."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class UserSession(BaseModel):
    """User session model for assessment and analysis."""

    model_config = ConfigDict(str_strip_whitespace=True)

    session_id: str = Field(..., description="Unique session identifier (UUID v4)")
    ticker_symbol: str = Field(
        ...,
        min_length=1,
        max_length=6,
        pattern="^[A-Z]{1,6}$",
        description="Company ticker being analyzed",
    )
    user_expertise_level: int | None = Field(
        None, ge=1, le=10, description="Calculated expertise level (1-10)"
    )
    assessment_responses: list[dict] = Field(
        default_factory=list, description="User responses to assessment questions"
    )
    report_complexity: Literal["comprehensive", "executive"] | None = Field(
        None, description="Chosen report complexity level"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Session creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    status: Literal["active", "research", "generation", "complete", "error"] = Field(
        default="active", description="Current session status"
    )
    research_database_path: str = Field(..., description="Path to session research database")


class AssessmentQuestion(BaseModel):
    """Model for assessment questions."""

    question_id: str = Field(..., description="Unique question identifier")
    question_text: str = Field(..., description="Question text")
    options: list[str] = Field(..., description="Answer options")
    category: str = Field(..., description="Question category")
    weight: float = Field(1.0, ge=0, le=10, description="Question weight for scoring")


class AssessmentResponse(BaseModel):
    """Model for user's response to assessment question."""

    question_id: str = Field(..., description="Question identifier")
    answer: str = Field(..., description="User's selected answer")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

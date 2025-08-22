"""Assessment-related data models."""

from __future__ import annotations

from datetime import UTC, datetime
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
    assessment_responses: list[AssessmentResponse] = Field(
        default_factory=list, description="User responses to assessment questions"
    )
    assessment_result: AssessmentResult | None = Field(
        None, description="Complete assessment results and analysis"
    )
    report_complexity: Literal["foundational", "educational", "intermediate", "advanced", "executive"] | None = Field(
        None, description="Chosen report complexity level based on expertise"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Session creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Last update timestamp"
    )
    status: Literal["active", "research", "generation", "complete", "error"] = Field(
        default="active", description="Current session status"
    )
    research_database_path: str = Field(..., description="Path to session research database")


class AssessmentQuestion(BaseModel):
    """Model for assessment questions."""

    id: int = Field(..., description="Question number (1-20)")
    difficulty_level: int = Field(..., ge=1, le=10, description="Target expertise level (1-10)")
    category: str = Field(
        ...,
        pattern="^(general_investing|ticker_specific|sector_expertise|analytical_sophistication)$",
        description="Question category",
    )
    question: str = Field(..., max_length=800, description="Contextually generated question text")
    options: list[str] = Field(
        ..., min_length=3, max_length=5, description="Multiple choice options"
    )
    correct_answer_index: int = Field(..., ge=0, le=4, description="Index of correct answer")
    ticker_context: str = Field(..., description="Ticker this question was generated for")
    weight: float = Field(..., gt=0, le=2.0, description="Scoring weight based on difficulty level")


class AssessmentResponse(BaseModel):
    """Model for user's response to assessment question."""

    question_id: int = Field(..., ge=1, le=20, description="Question identifier")
    selected_option: int = Field(..., ge=0, le=4, description="Index of selected option")
    correct_option: int = Field(..., ge=0, le=4, description="Index of correct answer")
    time_taken: float = Field(..., gt=0, description="Time taken in seconds")
    partial_credit: float = Field(default=0.0, ge=0.0, le=1.0, description="Partial credit awarded")


class AssessmentResult(BaseModel):
    """Model for assessment results and expertise calculation."""

    session_id: str = Field(..., description="Session identifier")
    expertise_level: int = Field(..., ge=1, le=10, description="AI-evaluated expertise level")
    report_complexity: str = Field(
        ...,
        pattern="^(foundational|educational|intermediate|advanced|executive)$",
        description="Report complexity based on expertise level mapping",
    )
    explanation: str = Field(..., description="AI-generated explanation of expertise assessment")
    ticker_context: str = Field(..., description="Ticker this assessment was conducted for")
    score_breakdown: dict = Field(
        default_factory=dict, description="Detailed score breakdown by category"
    )
    assessment_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Assessment completion timestamp"
    )

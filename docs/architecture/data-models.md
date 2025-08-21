# Data Models

## Session Management Models

**UserSession**: Pydantic model for assessment + context
```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class UserSession(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    ticker_symbol: str = Field(..., description="Company ticker being analyzed")
    user_expertise_level: int = Field(..., ge=1, le=10, description="Calculated expertise (1-10)")
    assessment_responses: List[dict] = Field(default_factory=list)
    report_complexity: str = Field(..., pattern="^(comprehensive|executive)$")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="active", pattern="^(active|research|generation|complete|error)$")
    research_database_path: str = Field(..., description="Path to session research database")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

**AgentHandoff**: Standardized data format for agent-to-agent transfers
```python
class AgentHandoff(BaseModel):
    source_agent: str = Field(..., description="Agent providing the data")
    target_agent: str = Field(..., description="Agent receiving the data")
    research_files: List[str] = Field(..., description="List of research file paths")
    context_summary: str = Field(..., max_length=5000, description="Condensed context for handoff")
    cross_references: List[str] = Field(default_factory=list)
    confidence_metrics: dict = Field(default_factory=dict)
    handoff_timestamp: datetime = Field(default_factory=datetime.utcnow)
    token_usage: int = Field(default=0, description="Tokens used in research phase")
    
    def validate_handoff_integrity(self) -> bool:
        """Validate that handoff data is complete and consistent"""
        return (
            len(self.research_files) > 0 and
            len(self.context_summary.strip()) > 100 and
            self.source_agent != self.target_agent
        )
```

**ReportMetadata**: Progress tracking and generation state
```python
class ReportMetadata(BaseModel):
    session_id: str = Field(..., description="Associated session")
    report_id: str = Field(..., description="Unique report identifier")
    generation_status: str = Field(
        default="pending",
        pattern="^(pending|generating|merging|converting|complete|error)$"
    )
    current_section: Optional[str] = Field(None, description="Currently generating section")
    sections_completed: int = Field(default=0, ge=0)
    total_sections: int = Field(..., gt=0)
    estimated_completion_time: Optional[datetime] = None
    word_count_target: int = Field(default=0, description="Target word count for expertise level")
    actual_word_count: int = Field(default=0)
    pdf_generation_attempts: int = Field(default=0, ge=0, le=3)
    error_log: List[str] = Field(default_factory=list)
    
    @property
    def progress_percentage(self) -> float:
        """Calculate completion percentage"""
        if self.total_sections == 0:
            return 0.0
        return min(100.0, (self.sections_completed / self.total_sections) * 100)
```

## Shared Research Database Structure

**Purpose:** Central repository for all agent-contributed research insights, structured as versioned markdown files with metadata

**Key Attributes:**
- file_path: str - Location of research file
- author_agent: str - Which agent created this research
- created_at: datetime - When research was contributed
- version: int - Version number for updates
- topic: str - Research topic/category
- cross_references: List[str] - Links to related research files

### Database Structure
```typescript
research_database/
├── meta/
│   ├── file_index.yaml          # Master index of all research files
│   ├── cross_references.yaml    # Links between analyses  
│   └── agent_activity.yaml      # Track agent contributions
├── valuation/
│   ├── dcf_analysis_v1.md       # DCF model and assumptions
│   ├── peer_comparison_v1.md    # Industry peer analysis
│   ├── valuation_summary_v1.md  # Key valuation insights
│   └── comments/
│       ├── strategic_critique_on_dcf.md    # Other agents' comments
│       └── historian_context_on_peers.md
├── strategic/
│   ├── competitive_moat_v1.md
│   ├── market_dynamics_v1.md
│   ├── strategic_risks_v1.md
│   └── comments/
├── historical/
│   ├── company_timeline_v1.md
│   ├── leadership_analysis_v1.md
│   ├── crisis_management_v1.md
│   └── comments/
└── synthesis/
    ├── investment_thesis_v1.md
    ├── executive_summary_v1.md
    └── sections/
        ├── introduction_v1.md
        ├── valuation_section_v1.md
        ├── strategic_section_v1.md
        └── conclusion_v1.md
```

### Research File Metadata Format
```yaml
---
title: "DCF Analysis for ASML"
author: "ValuationAgent"
created_at: "2025-08-21T10:00:00Z"
version: 1
topic: "valuation"
ticker: "ASML"
cross_references:
  - "strategic/competitive_moat_v1.md"
  - "historical/company_timeline_v1.md"
confidence_level: 0.85
data_sources:
  - "MCP Financial Data"
  - "Company 10-K filings"
  - "Industry reports"
---
```

## User Assessment

**Purpose:** Captures user responses to 20 financial expertise questions and calculates expertise level

**Key Attributes:**
- session_id: str - Unique identifier for user session
- ticker_symbol: str - Company ticker being analyzed
- questions: List[AssessmentQuestion] - The 20 expertise questions
- responses: List[AssessmentResponse] - User answers to questions
- expertise_level: int - Calculated expertise level (1-10)
- report_complexity: str - 'comprehensive' or 'executive'

### TypeScript Interface

```typescript
interface UserAssessment {
  sessionId: string;
  tickerSymbol: string;
  questions: AssessmentQuestion[];
  responses: AssessmentResponse[];
  expertiseLevel: number;
  reportComplexity: 'comprehensive' | 'executive';
  createdAt: string;
}

interface AssessmentQuestion {
  id: number;
  category: 'financial' | 'valuation' | 'strategic' | 'risk';
  question: string;
  options: string[];
  difficulty: number;
  weight: number;
}
```

## Agent Context

**Purpose:** Manages agent access to shared research database and tracks contributions

**Key Attributes:**
- agent_name: str - Identifying agent (valuation, strategic, historical, synthesis)
- current_research_focus: str - What the agent is currently researching
- contributed_files: List[str] - Files this agent has written
- accessed_files: List[str] - Files this agent has read
- private_context_size: int - Size of agent's private research context

### TypeScript Interface

```typescript
interface AgentContext {
  agentName: string;
  currentResearchFocus: string;
  contributedFiles: string[];
  accessedFiles: string[];
  privateContextSize: number;
  lastActivity: string;
}
```

"""Company Historian Agent using 2-Step GPT-5 Workflow."""

import logging
import os
from datetime import UTC, datetime
from typing import Any

from ..models.collaboration import AgentResult
from ..utils.openai_client import OpenAIClient
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class HistorianAgent(BaseAgent):
    """Company Historian Agent using 2-step GPT-5 workflow for historical analysis."""

    def __init__(self):
        """Initialize HistorianAgent with GPT-5 client."""
        super().__init__("historian_agent")
        self.openai_client = OpenAIClient()

    async def conduct_research(
        self,
        session_id: str,
        ticker: str,
        expertise_level: int,
        context: dict[str, Any] | None = None,
    ) -> AgentResult:
        """
        Conduct historical analysis using clean 2-step workflow.

        Args:
            session_id: Unique session identifier
            ticker: Stock ticker symbol
            expertise_level: User expertise level (1-10)
            context: Valuation and strategic context from previous agents

        Returns:
            AgentResult with historical research files created
        """
        start_time = datetime.now(UTC)
        self.log_research_start(session_id, ticker, expertise_level)

        try:
            # Step 1: Research with GPT-5 web search → temp_history.md
            logger.info(f"🔍 Step 1: Researching historical data for {ticker}")
            temp_md = await self._run_research_phase(session_id, ticker, expertise_level)

            # Step 2: Historical analysis → company_history.md
            logger.info(f"📊 Step 2: Creating historical analysis for {ticker}")
            history_md = await self._run_analysis_phase(
                session_id, ticker, expertise_level, temp_md, context
            )

            # Write files to research database
            files_created = await self._write_research_files(
                session_id, ticker, temp_md, history_md
            )

            # Create execution summary
            execution_time = (datetime.now(UTC) - start_time).total_seconds()
            summary = self._create_execution_summary(
                ticker, execution_time, len(temp_md), len(history_md)
            )

            logger.info(f"✅ Historical analysis completed for {ticker} in {execution_time:.1f}s")

            return AgentResult(
                agent_name=self.agent_name,
                success=True,
                research_files_created=files_created,
                summary=summary,
                error_message=None,
                token_usage=0,  # GPT-5 handles token tracking
                execution_time_seconds=execution_time,
                confidence_score=0.8,  # High confidence with real data
            )

        except Exception as e:
            logger.error(f"❌ Historical analysis failed for {ticker}: {str(e)}")
            return self._create_error_result(session_id, ticker, str(e), start_time)

    async def _run_research_phase(self, session_id: str, ticker: str, expertise_level: int) -> str:
        """Step 1: GPT-5 web search for historical company data → temp_history.md."""
        try:
            depth_config = self._get_expertise_depth_config(expertise_level)

            research_prompt = f"""
You are a company historian researcher. Using web search for {ticker}:

## PRIORITY HISTORICAL DATA TO EXTRACT:
1. **Founding Story**: When/where/who founded the company, original vision
2. **Timeline of Major Events**: IPOs, acquisitions, mergers, spin-offs, pivots
3. **Leadership Evolution**: CEOs, key executives, board changes over time
4. **Crisis Moments**: How company handled recessions, disruptions, scandals
5. **Strategic Decisions**: Major product launches, market entries/exits, pivots
6. **Financial Journey**: Revenue/profit milestones, major capital raises
7. **Cultural Evolution**: Company values, mission changes, workforce growth
8. **Technological Transitions**: Key innovations, R&D breakthroughs, patents

DATA SOURCES TO PREFER:
- Company "About" and "History" pages
- SEC filings (10-K business descriptions, proxy statements)
- Major business publications (WSJ, FT, Bloomberg archives)
- Company press releases and investor presentations
- Academic case studies and business school materials

CRITICAL: Include inline citations for EVERY historical fact.
Format: [Source: publication/document, date]

Analysis depth: {depth_config["depth_name"]} level

Target output: 3000-4000 words of dense historical facts with dates and citations.
"""

            # GPT-5-MINI with web search - using 200k TPM limit, 32k context
            temp_md = self.openai_client.respond_with_web_search(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a company historian researcher. Search for comprehensive historical data with proper citations.",
                    },
                    {"role": "user", "content": research_prompt},
                ],
                reasoning_effort="low",  # Low to save tokens for output
                verbosity="medium",  # Medium verbosity
                max_output_tokens=32000,  # 32k context for comprehensive data
            )

            logger.info(f"✅ Research phase completed: {len(temp_md)} characters with real data")
            return temp_md

        except Exception as e:
            logger.error(f"Research phase failed for {ticker}: {str(e)}")
            return f"# Historical Research Failed for {ticker}\n\nError: {str(e)}\n\nUnable to retrieve historical data."

    async def _run_analysis_phase(
        self,
        session_id: str,
        ticker: str,
        expertise_level: int,
        temp_md: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Step 2: GPT-5 historical analysis using temp_history.md → company_history.md."""
        try:
            depth_config = self._get_expertise_depth_config(expertise_level)

            # Format context from previous agents if available
            context_summary = "No previous agent context provided."
            if context:
                context_sections = []
                if "valuation" in context and "summary" in context["valuation"]:
                    context_sections.append(f"VALUATION CONTEXT:\n{context['valuation']['summary']}")
                if "strategic" in context and "summary" in context["strategic"]:
                    context_sections.append(f"STRATEGIC CONTEXT:\n{context['strategic']['summary']}")
                if context_sections:
                    context_summary = "\n\n".join(context_sections)

            analysis_prompt = f"""
You are an elite company historian creating institutional-grade historical analysis.

Using the research in temp_history.md, create a comprehensive historical narrative that:

## HISTORICAL RESEARCH DATA:
{temp_md}

## {context_summary}

## YOUR TASK - Create complete historical analysis for {ticker}:

1. **Company Evolution Timeline**
   - Founding story and original mission
   - Major milestones chronologically organized
   - Strategic pivots and their outcomes

2. **Leadership Analysis**
   - CEO succession and tenure analysis
   - Management team stability/turnover patterns
   - Board composition evolution
   - Leadership during crisis periods

3. **Crisis Management Track Record**
   - How company navigated recessions (2000, 2008, 2020)
   - Response to industry disruptions
   - Recovery from strategic mistakes
   - Regulatory/legal challenge handling

4. **Strategic Decision Patterns**
   - M&A track record (successful vs failed)
   - Market expansion decisions
   - Product portfolio evolution
   - Capital allocation history

5. **Historical Performance Context**
   - Revenue/profit growth trajectory
   - Market share evolution
   - Competitive position changes
   - Stock performance vs peers over time

6. **Predictive Historical Patterns**
   - Recurring themes in company behavior
   - Management's typical playbook
   - Historical indicators of future performance
   - Lessons from past for current strategy

## OUTPUT FORMAT (Markdown):
```markdown
# {ticker} Company History & Evolution

## Executive Summary
- **Company Age**: [Years since founding]
- **Leadership Stability**: HIGH/MODERATE/LOW
- **Crisis Management Track Record**: STRONG/ADEQUATE/WEAK
- **Strategic Consistency**: HIGH/MODERATE/LOW
- **Historical Growth Pattern**: [Characterization]

## Founding & Early Years
### The Origin Story
[Founding details with sources]

### Initial Vision & Mission
[Original business model and goals]

### Early Challenges & Pivots
[How company evolved from inception]

## Major Milestones Timeline
### [Decade 1] - Foundation Period
[Key events with dates and sources]

### [Decade 2] - Growth Phase
[Expansion milestones with sources]

### [Continue chronologically to present]
[Major events, acquisitions, product launches]

## Leadership Evolution
### CEO Succession History
[Complete CEO timeline with tenure analysis]

### Management Team Evolution
[Key executive changes and impact]

### Board Composition Changes
[Board evolution and governance shifts]

**Leadership Assessment**: [Analysis of management stability and quality]

## Crisis Management Track Record
### Financial Crisis Response (2008)
[How company navigated the crisis]

### COVID-19 Response (2020)
[Pandemic strategy and outcomes]

### Industry-Specific Challenges
[Response to disruptions, competition, regulation]

**Crisis Management Rating**: [Overall assessment with examples]

## Strategic Decision Analysis
### Successful Strategic Moves
[Major wins with outcomes and sources]

### Strategic Mistakes & Recoveries
[Failed initiatives and lessons learned]

### M&A Track Record
[Acquisition history and integration success]

### Capital Allocation History
[How management deployed capital over time]

**Strategic Consistency Score**: [Assessment with justification]

## Financial Performance Evolution
### Revenue Growth Trajectory
[Long-term growth patterns with key inflection points]

### Profitability Evolution
[Margin expansion/contraction over time]

### Market Position Changes
[Competitive position evolution]

### Stock Performance History
[Long-term returns vs market and peers]

**Performance Pattern**: [Characterization of historical performance]

## Cultural & Organizational Evolution
### Company Values Evolution
[How culture changed over time]

### Workforce Growth & Composition
[Employee count and demographic changes]

### Innovation & R&D History
[Key innovations and technology adoption]

**Organizational Assessment**: [Cultural strength and adaptation]

## Predictive Historical Patterns
### Recurring Strategic Themes
[Patterns in company behavior]

### Management Playbook Analysis
[Typical responses to challenges/opportunities]

### Future Performance Indicators
[What history suggests about future]

### Integration with Current Strategy
[How historical patterns inform current direction]

## Key Historical Lessons
[Top 5-7 insights from company history relevant to investment thesis]

## Data Sources & Citations
[List all sources from research data]
```

Report complexity: {depth_config["depth_name"]} level
Include specific dates, numbers, and citations throughout.
Output: Comprehensive historical analysis (2500-3000 words)
"""

            # GPT-5 for historical analysis - focused output
            history_md = self.openai_client.create_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an elite company historian. Focus on investment-relevant historical patterns with proper sourcing.",
                    },
                    {"role": "user", "content": analysis_prompt},
                ],
                max_tokens=16000,  # 16k context for analysis
                use_complex_model=True,  # Use GPT-5 for complex analysis
            )

            logger.info(f"✅ Historical analysis phase completed: {len(history_md)} characters")
            return history_md

        except Exception as e:
            logger.error(f"Historical analysis phase failed for {ticker}: {str(e)}")
            return f"# Historical Analysis Failed for {ticker}\n\nError: {str(e)}\n\nUnable to complete historical analysis."

    def _get_expertise_depth_config(self, expertise_level: int) -> dict:
        """Map expertise level to analysis depth configuration."""
        depth_map = {
            (1, 2): {
                "depth_name": "Foundational",
                "pages": "250-300",
                "detail": "comprehensive with educational explanations",
            },
            (3, 4): {
                "depth_name": "Educational",
                "pages": "150-200",
                "detail": "detailed with historical context",
            },
            (5, 6): {
                "depth_name": "Intermediate",
                "pages": "80-100",
                "detail": "focused historical analysis",
            },
            (7, 8): {
                "depth_name": "Advanced",
                "pages": "50-60",
                "detail": "executive-level historical insights",
            },
            (9, 10): {
                "depth_name": "Executive",
                "pages": "10-20",
                "detail": "historical summary with key implications",
            },
        }

        for level_range, config in depth_map.items():
            if level_range[0] <= expertise_level <= level_range[1]:
                return config

        return {
            "depth_name": "Intermediate",
            "pages": "80-100",
            "detail": "focused historical analysis",
        }

    async def _write_research_files(
        self, session_id: str, ticker: str, temp_md: str, history_md: str
    ) -> list[str]:
        """Write research files to database following Story 2.1 pattern."""
        try:
            research_dir = f"research_database/sessions/{session_id}/{ticker}/historical"
            files_created = []

            # Write temp_history.md (raw research with citations)
            temp_path = f"{research_dir}/temp_history.md"
            await self._write_research_file(temp_path, temp_md)
            files_created.append(temp_path)

            # Write company_history.md (complete analysis)
            history_path = f"{research_dir}/company_history.md"
            await self._write_research_file(history_path, history_md)
            files_created.append(history_path)

            logger.info(f"✅ Created {len(files_created)} historical research files for {ticker}")
            return files_created

        except Exception as e:
            logger.error(f"Failed to write historical research files for {ticker}: {str(e)}")
            return []

    async def _write_research_file(self, file_path: str, content: str) -> None:
        """Write content to research database file."""

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write content to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _create_execution_summary(
        self, ticker: str, execution_time: float, research_chars: int, history_chars: int
    ) -> str:
        """Create execution summary for agent result."""
        return f"""
Historical Analysis Complete for {ticker}:

✅ Step 1: Historical research completed ({research_chars:,} characters with real data)
✅ Step 2: Company history analysis completed ({history_chars:,} characters)
✅ Files: temp_history.md (raw research) + company_history.md (complete analysis)
✅ Framework: Chronological evolution with crisis management and leadership analysis
✅ Data: Real historical data with citations (founding to present)

Analysis completed in {execution_time:.1f} seconds using GPT-5 with web search.
Ready for final synthesis agent with complete historical context.
"""

    def _create_error_result(
        self, session_id: str, ticker: str, error_message: str, start_time: datetime
    ) -> AgentResult:
        """Create error result for failed analysis."""
        execution_time = (datetime.now(UTC) - start_time).total_seconds()

        return AgentResult(
            agent_name=self.agent_name,
            success=False,
            research_files_created=[],
            summary=f"Historical analysis failed for {ticker}: {error_message}",
            error_message=error_message,
            token_usage=0,
            execution_time_seconds=execution_time,
            confidence_score=0.0,
        )

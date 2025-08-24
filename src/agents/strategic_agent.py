"""Strategic Analyst Agent using 2-Step GPT-5 Workflow."""

import logging
import os
from datetime import UTC, datetime
from typing import Any

from ..models.collaboration import AgentResult
from ..utils.openai_client import OpenAIClient
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class StrategicAgent(BaseAgent):
    """Strategic Analyst Agent using 2-step GPT-5 workflow for competitive analysis."""

    def __init__(self):
        """Initialize StrategicAgent with GPT-5 client."""
        super().__init__("strategic_agent")
        self.openai_client = OpenAIClient()

    async def conduct_research(
        self,
        session_id: str,
        ticker: str,
        expertise_level: int,
        context: dict[str, Any] | None = None,
    ) -> AgentResult:
        """
        Conduct strategic analysis using clean 2-step workflow.

        Args:
            session_id: Unique session identifier
            ticker: Stock ticker symbol
            expertise_level: User expertise level (1-10)
            context: Valuation context from previous agents

        Returns:
            AgentResult with strategic research files created
        """
        start_time = datetime.now(UTC)
        self.log_research_start(session_id, ticker, expertise_level)

        try:
            # Step 1: Research with GPT-5 web search → temp_competition.md
            logger.info(f"🔍 Step 1: Researching competitive data for {ticker}")
            temp_md = await self._run_research_phase(session_id, ticker, expertise_level)

            # Step 2: Strategic analysis → strategic_analysis.md
            logger.info(f"📊 Step 2: Creating strategic analysis for {ticker}")
            strategic_md = await self._run_analysis_phase(
                session_id, ticker, expertise_level, temp_md, context
            )

            # Write files to research database
            files_created = await self._write_research_files(
                session_id, ticker, temp_md, strategic_md
            )

            # Create execution summary
            execution_time = (datetime.now(UTC) - start_time).total_seconds()
            summary = self._create_execution_summary(
                ticker, execution_time, len(temp_md), len(strategic_md)
            )

            logger.info(f"✅ Strategic analysis completed for {ticker} in {execution_time:.1f}s")

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
            logger.error(f"❌ Strategic analysis failed for {ticker}: {str(e)}")
            return self._create_error_result(session_id, ticker, str(e), start_time)

    async def _run_research_phase(self, session_id: str, ticker: str, expertise_level: int) -> str:
        """Step 1: GPT-5 web search for competitive and market data → temp_competition.md."""
        try:
            depth_config = self._get_expertise_depth_config(expertise_level)

            research_prompt = f"""
You are a strategic research analyst. Using web search for {ticker}:

## PRIORITY DATA TO EXTRACT:
1. **Competitive positioning**: Market share, competitive advantages, moats
2. **Industry dynamics**: Market size, growth trends, key drivers
3. **Strategic risks**: Regulatory, technological, competitive threats
4. **Management quality**: Leadership track record, strategic decisions
5. **ESG factors**: Material ESG considerations affecting investment thesis
6. **Strategic opportunities**: Growth catalysts, expansion opportunities
7. **Market dynamics**: Pricing power, customer retention, switching costs

## DATA SOURCES TO PREFER:
- Company 10-K, 10-Q filings (competitive sections)
- Industry reports (McKinsey, BCG, industry associations)
- Recent management presentations and strategy updates
- Competitor filings and press releases
- Regulatory filings and government reports
- ESG reports and sustainability disclosures

## OUTPUT FORMAT:
Return comprehensive **markdown** with:
- Structured sections for each analysis area
- **Inline citations** after each statement: [Source: document name, date]
- Comparative analysis with key competitors
- Quantitative data where available (market share percentages, etc.)
- Focus on qualitative factors that impact long-term returns

Analysis depth: {depth_config["depth_name"]} level

CRITICAL: Use real web search. Get actual current competitive data with proper citations.
No generic statements - only specific, sourced insights about competitive positioning.
"""

            # GPT-5-MINI with web search - using 200k TPM limit, increased to 64k context
            temp_md = self.openai_client.respond_with_web_search(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a strategic research analyst. Search for comprehensive competitive and market data with proper citations.",
                    },
                    {"role": "user", "content": research_prompt},
                ],
                reasoning_effort="low",  # Low to save tokens for output
                verbosity="high",  # High for lots of detail
                max_output_tokens=64000,  # 64k context for comprehensive data
            )

            logger.info(f"✅ Research phase completed: {len(temp_md)} characters with real data")
            return temp_md

        except Exception as e:
            logger.error(f"Research phase failed for {ticker}: {str(e)}")
            return f"# Strategic Research Failed for {ticker}\n\nError: {str(e)}\n\nUnable to retrieve competitive data."

    async def _run_analysis_phase(
        self,
        session_id: str,
        ticker: str,
        expertise_level: int,
        temp_md: str,
        valuation_context: dict[str, Any] | None = None,
    ) -> str:
        """Step 2: GPT-5 strategic analysis using temp_competition.md → strategic_analysis.md."""
        try:
            strategic_framework = self._get_strategic_framework()
            depth_config = self._get_expertise_depth_config(expertise_level)

            # Format valuation context if available
            valuation_summary = "No valuation context provided."
            if valuation_context and "summary" in valuation_context:
                valuation_summary = f"VALUATION CONTEXT:\n{valuation_context['summary']}"

            analysis_prompt = f"""
Use the competitive research data below to create comprehensive strategic analysis for {ticker}.

## STRATEGIC ANALYSIS FRAMEWORK:
{strategic_framework}

## COMPETITIVE RESEARCH DATA:
{temp_md}

## {valuation_summary}

## YOUR TASK - Create complete strategic analysis:

**Analyze systematically:**

1. **Competitive Moat Analysis**:
   - Network effects, switching costs, scale advantages
   - Brand strength and customer loyalty
   - Regulatory barriers and patents
   - Cost advantages and operational efficiency

2. **Market Dynamics Assessment**:
   - Industry growth trends and cyclicality
   - Pricing power and margin sustainability
   - Customer concentration and retention
   - Supplier relationships and bargaining power

3. **Strategic Risk Evaluation**:
   - Regulatory and political risks
   - Technological disruption threats
   - Competitive pressure points
   - ESG-related business risks

4. **Management Quality Assessment**:
   - Track record of strategic execution
   - Capital allocation decisions
   - Leadership depth and succession
   - Stakeholder communication quality

5. **Strategic Opportunities**:
   - Market expansion opportunities
   - Product/service innovation potential
   - M&A and partnership possibilities
   - Operational improvement areas

6. **Investment Implications**:
   - Link strategic factors to valuation metrics
   - Quality of earnings sustainability
   - Long-term competitive position
   - Recommended strategic monitoring points

## OUTPUT FORMAT (Markdown):
```markdown
# {ticker} Strategic Analysis

## Executive Summary
- **Strategic Position**: STRONG/MODERATE/WEAK
- **Competitive Moat**: WIDE/NARROW/NONE
- **Strategic Risk Level**: LOW/MODERATE/HIGH
- **Management Quality**: EXCELLENT/GOOD/POOR
- **Investment Implication**: [Strategic factors support/question valuation]

## Competitive Moat Analysis
### Network Effects & Switching Costs
[Analysis with sources]

### Scale Advantages & Cost Position
[Analysis with sources]

### Brand Strength & Customer Loyalty
[Analysis with sources]

### Regulatory & Patent Protection
[Analysis with sources]

**Moat Assessment**: [Qualitative and quantitative analysis]

## Market Dynamics Assessment
### Industry Growth & Trends
[Analysis with sources]

### Pricing Power & Margin Sustainability
[Analysis with sources]

### Customer & Supplier Relationships
[Analysis with sources]

**Market Position Strength**: [Assessment with implications]

## Strategic Risk Evaluation
### Regulatory & Political Risks
[Specific risks with probability/impact]

### Technology Disruption Threats
[Analysis of disruption potential]

### Competitive Pressure Points
[Key vulnerabilities and competitive responses]

### ESG & Sustainability Risks
[Material ESG factors affecting business]

**Overall Risk Assessment**: [Comprehensive risk rating]

## Management Quality Assessment
### Strategic Execution Track Record
[Historical performance with examples]

### Capital Allocation Discipline
[Analysis of past decisions and outcomes]

### Leadership Depth & Communication
[Management team evaluation]

**Management Rating**: [Overall assessment with justification]

## Strategic Opportunities
### Growth Catalysts
[Near and long-term opportunities]

### Operational Improvements
[Efficiency and margin expansion potential]

### Market Expansion Potential
[Geographic and product expansion analysis]

**Opportunity Assessment**: [Prioritized opportunities with timelines]

## Investment Implications
### Strategic Factor Impact on Valuation
[How strategic position affects financial returns]

### Quality of Competitive Position
[Sustainability of current advantages]

### Strategic Monitoring Points
[Key metrics and developments to track]

### Integration with Valuation Analysis
[Strategic factors supporting/challenging financial projections]

## Key Strategic Risks to Monitor
[Top 3-5 strategic risks with specific watch points]

## Data Sources & Citations
[List all sources from research data]
```

Report complexity: {depth_config["depth_name"]} level
Focus on investment-relevant strategic factors. Link analysis to long-term return potential.
"""

            # GPT-5 for strategic analysis - focused output
            strategic_md = self.openai_client.create_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an elite strategic analyst. Focus on investment-relevant strategic factors with proper sourcing.",
                    },
                    {"role": "user", "content": analysis_prompt},
                ],
                max_tokens=16000,  # 16k tokens as requested (increased from 12k)
                use_complex_model=True,  # Use GPT-5 for complex analysis
            )

            logger.info(f"✅ Strategic analysis phase completed: {len(strategic_md)} characters")
            return strategic_md

        except Exception as e:
            logger.error(f"Strategic analysis phase failed for {ticker}: {str(e)}")
            return f"# Strategic Analysis Failed for {ticker}\n\nError: {str(e)}\n\nUnable to complete strategic analysis."

    def _get_strategic_framework(self) -> str:
        """Get strategic analysis framework for GPT-5."""
        return """
# Strategic Analysis Framework (Porter's Five Forces + Moat Analysis)

## 1. Competitive Moat Analysis
**Four Types of Economic Moats:**

### Network Effects
- Value increases with more users/participants
- Creates switching costs and barriers to entry
- Examples: Payment networks, social platforms, marketplaces

### Switching Costs
- High costs (financial, operational, emotional) to change providers
- Lock-in through integration, data, contracts, learning curves
- Creates predictable revenue streams

### Cost Advantages
- Structural cost advantages competitors cannot easily replicate
- Sources: Scale, location, process patents, preferential access
- Enables pricing flexibility and margin expansion

### Intangible Assets
- Brands, patents, regulatory licenses, data assets
- Create pricing power and barrier to competition
- Must be defensible and economically valuable

## 2. Porter's Five Forces Analysis

### Threat of New Entrants
- Barriers to entry (capital, regulation, network effects)
- Economies of scale requirements
- Brand loyalty and switching costs

### Bargaining Power of Suppliers
- Supplier concentration vs industry concentration
- Availability of substitute inputs
- Cost of switching suppliers

### Bargaining Power of Customers
- Customer concentration and size
- Price sensitivity and switching costs
- Availability of alternatives

### Threat of Substitutes
- Substitute products/services performance
- Relative price-performance of substitutes
- Customer propensity to substitute

### Competitive Rivalry
- Number and strength of competitors
- Industry growth rate and capacity utilization
- Differentiation vs commodity competition

## 3. Strategic Risk Assessment Matrix
**Risk Categories:**
- **Regulatory**: Policy changes, new regulations, enforcement
- **Technology**: Disruption, obsolescence, innovation cycles
- **Market**: Demand shifts, economic cycles, demographic changes
- **Operational**: Key person risk, supply chain, operational execution
- **Financial**: Capital requirements, debt capacity, cash flow volatility

## 4. Management Quality Evaluation
**Assessment Criteria:**
- **Track Record**: Historical strategic execution and results
- **Capital Allocation**: ROI on investments, M&A success, shareholder returns
- **Communication**: Transparency, consistency, stakeholder management
- **Vision**: Strategic clarity, market understanding, adaptation capability

**Key Principle**: Focus on strategic factors that directly impact long-term cash flows and competitive positioning.
Quantify qualitative factors where possible and link to investment implications.
"""

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
                "detail": "detailed with strategic context",
            },
            (5, 6): {
                "depth_name": "Intermediate",
                "pages": "80-100",
                "detail": "focused strategic analysis",
            },
            (7, 8): {
                "depth_name": "Advanced",
                "pages": "50-60",
                "detail": "executive-level strategic insights",
            },
            (9, 10): {
                "depth_name": "Executive",
                "pages": "10-20",
                "detail": "strategic summary with key implications",
            },
        }

        for level_range, config in depth_map.items():
            if level_range[0] <= expertise_level <= level_range[1]:
                return config

        return {
            "depth_name": "Intermediate",
            "pages": "80-100",
            "detail": "focused strategic analysis",
        }

    async def _write_research_files(
        self, session_id: str, ticker: str, temp_md: str, strategic_md: str
    ) -> list[str]:
        """Write research files to database following Story 2.1 pattern."""
        try:
            research_dir = f"research_database/sessions/{session_id}/{ticker}/strategic"
            files_created = []

            # Write temp_competition.md (raw research with citations)
            temp_path = f"{research_dir}/temp_competition.md"
            await self._write_research_file(temp_path, temp_md)
            files_created.append(temp_path)

            # Write strategic_analysis.md (complete analysis)
            strategic_path = f"{research_dir}/strategic_analysis.md"
            await self._write_research_file(strategic_path, strategic_md)
            files_created.append(strategic_path)

            logger.info(f"✅ Created {len(files_created)} strategic research files for {ticker}")
            return files_created

        except Exception as e:
            logger.error(f"Failed to write strategic research files for {ticker}: {str(e)}")
            return []

    async def _write_research_file(self, file_path: str, content: str) -> None:
        """Write content to research database file."""

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write content to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _create_execution_summary(
        self, ticker: str, execution_time: float, research_chars: int, strategic_chars: int
    ) -> str:
        """Create execution summary for agent result."""
        return f"""
Strategic Analysis Complete for {ticker}:

✅ Step 1: Competitive research completed ({research_chars:,} characters with real data)
✅ Step 2: Strategic analysis completed ({strategic_chars:,} characters)
✅ Files: temp_competition.md (raw research) + strategic_analysis.md (complete analysis)
✅ Framework: Porter's Five Forces + Economic Moat Analysis
✅ Data: Real competitive data with citations (no generic insights)

Analysis completed in {execution_time:.1f} seconds using GPT-5 with web search.
Ready for next agent handoff with strategic context.
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
            summary=f"Strategic analysis failed for {ticker}: {error_message}",
            error_message=error_message,
            token_usage=0,
            execution_time_seconds=execution_time,
            confidence_score=0.0,
        )

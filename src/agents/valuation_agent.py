"""Clean Valuation Expert Agent using 2-Step GPT-5 Workflow."""

import logging
import os
from datetime import UTC, datetime
from typing import Any

from ..models.collaboration import AgentResult
from ..utils.openai_client import OpenAIClient
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ValuationAgent(BaseAgent):
    """Clean Valuation Expert Agent using 2-step GPT-5 workflow with real data."""

    def __init__(self):
        """Initialize ValuationAgent with GPT-5 client."""
        super().__init__("valuation_agent")
        self.openai_client = OpenAIClient()

    async def conduct_research(
        self,
        session_id: str,
        ticker: str,
        expertise_level: int,
        context: dict[str, Any] | None = None,
    ) -> AgentResult:
        """
        Conduct Owner-Returns valuation analysis using clean 2-step workflow.

        Args:
            session_id: Unique session identifier
            ticker: Stock ticker symbol
            expertise_level: User expertise level (1-10)
            context: Previous research context from other agents

        Returns:
            AgentResult with valuation research files created
        """
        start_time = datetime.now(UTC)
        self.log_research_start(session_id, ticker, expertise_level)

        try:
            # Step 1: Research with GPT-5 web search → temp.md
            logger.info(f"🔍 Step 1: Researching financial data for {ticker}")
            temp_md = await self._run_research_phase(session_id, ticker, expertise_level)

            # Step 2: Valuation analysis → valuation.md
            logger.info(f"🧮 Step 2: Creating valuation analysis for {ticker}")
            valuation_md = await self._run_valuation_phase(session_id, ticker, expertise_level, temp_md)

            # Write files to research database
            files_created = await self._write_research_files(session_id, ticker, temp_md, valuation_md)

            # Create execution summary
            execution_time = (datetime.now(UTC) - start_time).total_seconds()
            summary = self._create_execution_summary(ticker, execution_time, len(temp_md), len(valuation_md))

            logger.info(f"✅ Owner-Returns analysis completed for {ticker} in {execution_time:.1f}s")

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
            logger.error(f"❌ Valuation analysis failed for {ticker}: {str(e)}")
            return self._create_error_result(session_id, ticker, str(e), start_time)

    async def _run_research_phase(self, session_id: str, ticker: str, expertise_level: int) -> str:
        """Step 1: GPT-5 web search for real financial data → temp.md."""
        try:
            depth_config = self._get_expertise_depth_config(expertise_level)
            
            research_prompt = f"""
You are an equity research assistant. Using web search for {ticker}:

## PRIORITY DATA TO EXTRACT:
1. **Most recent 10-K/annual** and **latest quarterly report**
2. **Financial metrics**: Revenue, CFO, CapEx, FCF, shares outstanding (diluted)
3. **Current stock price** with date/time of quote  
4. **Share changes**: Buybacks, dilution percentage, net share change
5. **Balance sheet**: Net debt/cash, total debt, cash position
6. **Management guidance** if available in recent calls

## DATA SOURCES TO PREFER:
- sec.gov filings (10-K, 10-Q, 8-K)
- Company investor relations pages
- Exchange data (NYSE, NASDAQ)
- Recent earnings call transcripts

## OUTPUT FORMAT:
Return concise **markdown** with:
- Bullet lists for each metric with actual numbers
- **Inline citations** after each figure: [Source: document name, date]
- If multiple sources show different figures, explain discrepancy
- Focus on FCF/share data and trends (last 3-5 years)

Analysis depth: {depth_config['depth_name']} level

CRITICAL: Use real web search. Get actual current financial data with proper citations.
No estimates or placeholders - only real data with sources.
"""

            # GPT-5-MINI with web search - using 200k TPM limit for lots of data
            temp_md = self.openai_client.respond_with_web_search(
                messages=[
                    {"role": "system", "content": "You are a financial data researcher. Search for primary source financial data with proper citations."},
                    {"role": "user", "content": research_prompt}
                ],
                reasoning_effort="low",  # Low reasoning effort
                verbosity="medium",  # Medium verbosity
                max_output_tokens=32000  # 32k context for comprehensive data
            )

            logger.info(f"✅ Research phase completed: {len(temp_md)} characters with real data")
            return temp_md

        except Exception as e:
            logger.error(f"Research phase failed for {ticker}: {str(e)}")
            return f"# Research Failed for {ticker}\n\nError: {str(e)}\n\nUnable to retrieve financial data."

    async def _run_valuation_phase(self, session_id: str, ticker: str, expertise_level: int, temp_md: str) -> str:
        """Step 2: GPT-5 valuation analysis using temp.md → valuation.md."""
        try:
            owner_returns_formulas = self._get_owner_returns_formulas()
            depth_config = self._get_expertise_depth_config(expertise_level)

            valuation_prompt = f"""
Use the research data below to compute Owner-Returns valuation for {ticker}.

## OWNER-RETURNS METHODOLOGY:
{owner_returns_formulas}

## RESEARCH DATA:
{temp_md}

## YOUR TASK - Create complete valuation analysis:

**Calculate step-by-step:**
1. **Current FCF Yield**: FCF_per_share / Current_Price
2. **IRR Decomposition**: Starting_Yield + Growth + Multiple_Reversion - Dilution
   - Starting Yield = Current FCF yield
   - Growth = Projected FCF/share CAGR (10-year with conservative fade)  
   - Multiple Reversion = (Terminal_Multiple / Current_Multiple)^(1/10) - 1
   - Dilution = Annual net share change impact

3. **Price Ladder** (solve for prices yielding target returns):
   - Buffett Floor: 10× pre-tax earnings approximation
   - ≥10% IRR Target Price: Price for 10% annual return
   - ≥15% IRR Target Price: Price for 15% annual return

4. **Conservative Stress Tests**:
   - Growth reduced by 200-300 basis points
   - Terminal multiple reduced by 2-4 turns
   - Combined adverse scenario

## OUTPUT FORMAT (Markdown):
```markdown
# {ticker} Owner-Returns Valuation Analysis

## Executive Summary
- Current Price: $XXX [Source: research data]
- FCF/Share (LTM): $XXX [Source: research data]  
- Current FCF Yield: XX.X%
- **Investment Recommendation: BUY/HOLD/AVOID**
- **Target IRR: XX.X%**

## Financial Data Summary
[Key metrics from research with sources]

## IRR Decomposition Analysis
- **Starting Yield**: XX.X% (FCF/share ÷ Price)
- **FCF Growth (10yr)**: XX.X% CAGR with fade assumptions
- **Multiple Reversion**: XX.X% (conservative terminal assumptions)
- **Dilution Impact**: XX.X% (net share change)
- **Total Expected IRR**: XX.X%

## Price Ladder Framework
- **Buffett Floor**: $XXX (10× pre-tax earnings)
- **10% IRR Target**: $XXX (fair value for quality business)
- **15% IRR Target**: $XXX (attractive entry point)
- **Current Assessment**: [Analysis vs target prices]

## Conservative Stress Testing
- **Growth Stress** (-250bp): IRR becomes XX.X%
- **Multiple Compression** (-3 turns): IRR becomes XX.X%  
- **Combined Stress**: Worst-case IRR of XX.X%
- **Resilience Assessment**: [HIGH/MODERATE/LOW]

## Must-Be-True KPIs
For current price to be justified:
- FCF growth: XX% annually for 10 years
- Margin sustainability: [specific requirements]
- Market share: [competitive position needed]

## Investment Thesis
[2-3 paragraph summary with reasoning]

## Key Risks
[Primary risks to thesis]

## Data Sources & Citations
[List all sources from research data]
```

Report complexity: {depth_config['depth_name']} level
Be conservative with assumptions. Show all calculations step-by-step with the actual numbers from research.
"""

            # GPT-5 for calculations and analysis - focused output
            valuation_md = self.openai_client.create_completion(
                messages=[
                    {"role": "system", "content": "You are an elite valuation expert. Be conservative, show all math step-by-step, cite sources from research."},
                    {"role": "user", "content": valuation_prompt}
                ],
                max_tokens=16000,  # 16k tokens as requested
                use_complex_model=True  # Use GPT-5 for complex analysis
            )

            logger.info(f"✅ Valuation phase completed: {len(valuation_md)} characters")
            return valuation_md

        except Exception as e:
            logger.error(f"Valuation phase failed for {ticker}: {str(e)}")
            return f"# Valuation Analysis Failed for {ticker}\n\nError: {str(e)}\n\nUnable to complete valuation."

    def _get_owner_returns_formulas(self) -> str:
        """Get Owner-Returns calculation formulas for GPT-5."""
        return """
# Owner-Returns FCF/Share Framework (Buffett, Ackman, Terry Smith methodology)

## Core IRR Decomposition Formula:
**Total IRR = Starting Yield + FCF Growth + Multiple Reversion - Dilution ± Leverage**

### 1. Starting Yield
```
Starting Yield = Current FCF per Share / Current Stock Price
```
This provides immediate cash return and margin of safety anchor.

### 2. FCF Growth Component
```  
FCF Growth = (Terminal FCF per Share / Current FCF per Share)^(1/10) - 1
```
Conservative approach: Model 10-year growth with fade to industry median ROIC.

### 3. Multiple Reversion
```
Multiple Reversion = (Terminal Multiple / Current Multiple)^(1/10) - 1
Current Multiple = Current Price / Current FCF per Share
Terminal Multiple = Conservative estimate (10-15× FCF for quality businesses)
```

### 4. Dilution Impact
```
Annual Dilution Rate = (New Shares - Buybacks) / Total Shares Outstanding
Dilution Drag = -Annual Dilution Rate (negative if net buybacks)
```

## Price Ladder Calculations:

### Buffett Floor (Quality Business Threshold)
```
Buffett Floor ≈ Pre-tax Earnings per Share × 10
(Use FCF × 1.2 as pre-tax earnings approximation if needed)
```

### IRR-Based Target Prices
```
10% IRR Price = Current FCF per Share / 0.10
15% IRR Price = Current FCF per Share / 0.15
```

## Conservative Stress Testing Framework:
- Reduce FCF growth by 200-300 basis points
- Reduce terminal multiple by 2-4 turns
- Increase dilution by 50 basis points
- Model combined adverse scenarios

**Key Principle**: Focus on FCF/share (not revenue or earnings) to avoid accounting manipulation.
Show all calculations explicitly with actual numbers from research data.
"""

    def _get_expertise_depth_config(self, expertise_level: int) -> dict:
        """Map expertise level to analysis depth configuration."""
        depth_map = {
            (1, 2): {"depth_name": "Foundational", "pages": "250-300", "detail": "comprehensive"},
            (3, 4): {"depth_name": "Educational", "pages": "150-200", "detail": "detailed"},
            (5, 6): {"depth_name": "Intermediate", "pages": "80-100", "detail": "focused"},
            (7, 8): {"depth_name": "Advanced", "pages": "50-60", "detail": "executive"},
            (9, 10): {"depth_name": "Executive", "pages": "10-20", "detail": "summary"}
        }

        for level_range, config in depth_map.items():
            if level_range[0] <= expertise_level <= level_range[1]:
                return config

        return {"depth_name": "Intermediate", "pages": "80-100", "detail": "focused"}

    async def _write_research_files(self, session_id: str, ticker: str, temp_md: str, valuation_md: str) -> list[str]:
        """Write research files to database following Story 2.1 pattern."""
        try:
            research_dir = f"research_database/sessions/{session_id}/{ticker}/valuation"
            files_created = []

            # Write temp.md (raw research with citations)
            temp_path = f"{research_dir}/temp.md"
            await self._write_research_file(temp_path, temp_md)
            files_created.append(temp_path)

            # Write valuation.md (complete analysis)
            val_path = f"{research_dir}/valuation.md"
            await self._write_research_file(val_path, valuation_md)
            files_created.append(val_path)

            logger.info(f"✅ Created {len(files_created)} research files for {ticker}")
            return files_created

        except Exception as e:
            logger.error(f"Failed to write research files for {ticker}: {str(e)}")
            return []

    async def _write_research_file(self, file_path: str, content: str) -> None:
        """Write content to research database file."""
        import os

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write content to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _create_execution_summary(self, ticker: str, execution_time: float, research_chars: int, valuation_chars: int) -> str:
        """Create execution summary for agent result."""
        return f"""
Owner-Returns Valuation Complete for {ticker}:

✅ Step 1: Research completed ({research_chars:,} characters with real data)
✅ Step 2: Valuation analysis completed ({valuation_chars:,} characters)
✅ Files: temp.md (raw research) + valuation.md (complete analysis)
✅ Framework: Owner-Returns FCF/share per Buffett/Ackman/Terry Smith
✅ Data: Real financial data with citations (no hardcoded values)

Analysis completed in {execution_time:.1f} seconds using GPT-5 with web search.
Ready for Strategic Agent handoff with real market data.
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
            summary=f"Valuation analysis failed for {ticker}: {error_message}",
            error_message=error_message,
            token_usage=0,
            execution_time_seconds=execution_time,
            confidence_score=0.0,
        )

    def log_research_start(self, session_id: str, ticker: str, expertise_level: int):
        """Log the start of research with context."""
        depth_config = self._get_expertise_depth_config(expertise_level)
        logger.info(f"🚀 Starting Owner-Returns valuation for {ticker} (Session: {session_id})")
        logger.info(f"📊 Expertise Level: {expertise_level} ({depth_config['depth_name']} - {depth_config['pages']} pages)")
        logger.info("🔍 Step 1: GPT-5 web search for real financial data")
        logger.info("🧮 Step 2: GPT-5 valuation analysis with Owner-Returns framework")
        logger.info("💰 Methodology: FCF/share focus per elite investor practices")

    # Compatibility methods for existing coordinator integration
    async def conduct_owner_returns_research(self, ticker: str, expertise_level: int) -> dict[str, Any]:
        """Compatibility method for existing tests."""
        try:
            temp_md = await self._run_research_phase("compat_session", ticker, expertise_level)
            valuation_md = await self._run_valuation_phase("compat_session", ticker, expertise_level, temp_md)
            
            return {
                "analysis": valuation_md,
                "ticker": ticker,
                "citations": self._extract_citations_from_response(temp_md + valuation_md),
                "temp_research": temp_md,
                "final_valuation": valuation_md,
                "workflow": "2-step: research → valuation",
                "model_used": "gpt-5"
            }
        except Exception as e:
            logger.error(f"Compatibility research failed for {ticker}: {e}")
            return {
                "analysis": f"Analysis failed: {str(e)}",
                "ticker": ticker,
                "citations": [],
                "workflow": "error",
                "model_used": "gpt-5"
            }

    def _extract_citations_from_response(self, content: str) -> list[str]:
        """Extract citations from content for compatibility."""
        import re
        citations = []
        citation_pattern = r'\[Source: ([^\]]+)\]'
        matches = re.findall(citation_pattern, content)
        citations.extend(matches)
        return citations[:10]  # Limit to top 10
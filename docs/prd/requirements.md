# Requirements

## Functional

**FR1:** The system must accept ticker symbols (e.g., ASML, COST) as input through a FastAPI web interface
**FR2:** The Assessment Agent must dynamically generate exactly 20 contextual questions (2 per difficulty level 1-10) to evaluate user expertise across general investing knowledge, ticker-specific understanding, sector expertise, and analytical sophistication
**FR3:** The system must calculate user expertise level on a 1-10 scale based on assessment responses
**FR4:** The Valuation Expert agent must generate DCF models, financial ratio analysis, and quantitative valuation metrics
**FR5:** The Strategic Analyst agent must analyze competitive positioning, market dynamics, and strategic risks/opportunities  
**FR6:** The Company Historian agent must research and document complete company history from founding to present
**FR7:** The Final Report Synthesizer must integrate all agent outputs into cohesive investment recommendations with buy/sell/hold ratings and price targets
**FR8:** The system must generate 200-300 page comprehensive reports for users with expertise levels 1-5
**FR9:** The system must generate 10-20 page executive summaries for users with expertise levels 6-10
**FR10:** All reports must include professional PDF formatting with citations, charts, and institutional-grade presentation
**FR11:** The system must provide clear expected IRR calculations and investment thesis conclusions
**FR12:** Agent coordination must preserve context through sequential handoffs from assessment to specialized research agents
**FR13:** The system must continue research with partial data when individual agents fail
**FR14:** Users must receive progress updates and error notifications during long-running analysis
**FR15:** The system must provide retry mechanisms for failed API calls with user control

## Non Functional

**NFR1:** The system must complete full analysis cycles (assessment + 4 research agents) within 2-day development timeline constraints
**NFR2:** API response times must support real-time assessment question delivery and agent orchestration
**NFR3:** The system must operate entirely on local Windows 11 environment with no cloud dependencies
**NFR4:** Memory-based session storage must maintain user context throughout multi-agent workflow
**NFR5:** Agent prompts must achieve institutional-grade analysis quality that demonstrably exceeds Goldman Sachs research depth
**NFR6:** The system must integrate with MCP servers for real-time financial data access
**NFR7:** PDF generation must support professional formatting with embedded charts and financial tables
**NFR8:** The system must maintain API key security for OpenAI SDK integration
**NFR9:** Agent coordination must be fault-tolerant with graceful error handling between sequential handoffs
**NFR10:** The system must include manual testing procedures for agent coordination and report quality validation
**NFR11:** API failure scenarios must have defined graceful degradation with user notification
**NFR12:** Session data persistence must survive application restarts during development
**NFR13:** Token usage must not exceed 200,000 tokens per complete analysis cycle
**NFR14:** Report generation must complete within 10 minutes for comprehensive reports
**NFR15:** Memory usage must not exceed 2GB during report generation on Windows 11

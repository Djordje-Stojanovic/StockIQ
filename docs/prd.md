# StockIQ Product Requirements Document (PRD)

## Goals and Background Context

### Goals
- Achieve research quality that demonstrably surpasses Goldman Sachs, Morgan Stanley, and JPMorgan institutional research
- Generate 200-300 page comprehensive analyses for beginners or 10-20 pages for experts based on user knowledge assessment  
- Outperform OpenAI Deep Research, Gemini Deep Thinking, and LangChain implementations in analytical sophistication
- Create investment-grade DCF models, competitive moat analysis, and complete company histories
- Provide clear buy/sell/hold recommendations with price targets and expected IRR
- Replicate hedge fund-level research quality through 5-agent AI architecture at near-zero marginal cost

### Background Context

StockIQ addresses a fundamental capital accessibility problem in investment research. Superior research traditionally requires hiring 20+ PhD analysts or running thousands of parallel AI agents - approaches only available to well-funded institutions. Individual investors are consequently limited to shallow analysis from Reddit discussions, basic Seeking Alpha articles, or expensive Bloomberg terminals that lack institutional-grade depth.

The solution replicates capital-intensive research approaches using a 5-agent AI architecture: 1 sophisticated assessment agent evaluating user expertise through 20 questions, followed by 4 specialized research agents (Valuation Expert, Strategic Analyst, Company Historian, Final Report Synthesizer) that conduct parallel analysis equivalent to multiple PhD-level researchers. This breaks through both capital constraints and human cognitive limitations.

### Change Log
| Date | Version | Description | Author |
|------|---------|-------------|---------|
| 2025-08-21 | v1.0 | Initial PRD creation from updated brief | John (PM) |

## Requirements

### Functional

**FR1:** The system must accept ticker symbols (e.g., ASML, COST) as input through a FastAPI web interface
**FR2:** The Assessment Agent must present exactly 20 questions to evaluate user expertise across financial/valuation/strategic/risk domains
**FR3:** The system must calculate user expertise level on a 1-10 scale based on assessment responses
**FR4:** The Valuation Expert agent must generate Owner-Returns FCF/Share analysis, Price Ladder (Buffett Floor/≥10%/≥15% IRR), reverse-DCF expectations analysis, and comprehensive financial metrics using elite investor methodologies
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

### Non Functional

**NFR1:** The system must complete full analysis cycles (assessment + 4 research agents) within 2-day development timeline constraints
**NFR2:** API response times must support real-time assessment question delivery and agent orchestration
**NFR3:** The system must operate entirely on local Windows 11 environment with no cloud dependencies
**NFR4:** Memory-based session storage must maintain user context throughout multi-agent workflow
**NFR5:** Agent prompts must achieve elite investor-grade analysis quality using Owner-Returns FCF/Share methodologies that match Buffett, Ackman, Terry Smith practices rather than traditional investment bank DCF approaches
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

## User Interface Design Goals

### Overall UX Vision
Clean, professional interface that mirrors the sophistication of institutional research platforms. The user experience should feel authoritative and trustworthy, similar to Bloomberg Terminal or Goldman Sachs research portals, but simplified for single-user operation. Focus on guiding users through the assessment process and presenting complex analysis in digestible formats.

### Key Interaction Paradigms
- **Guided Assessment Flow:** Step-by-step progression through 20 expertise questions with clear progress indicators
- **Contextual Help System:** Inline explanations for financial terms and concepts during assessment
- **Report Delivery:** Simple download mechanism for PDF reports with preview capabilities
- **Session Management:** Clear indication of current processing stage and estimated completion times

### Core Screens and Views
- **Home/Ticker Input Screen:** Simple form for entering company ticker symbols with validation
- **Assessment Interface:** Multi-step questionnaire with progress tracking and question navigation
- **Processing Dashboard:** Real-time status display showing current agent activity and progress
- **Report Preview Screen:** PDF preview with download options and report metadata
- **Settings Page:** Basic configuration for API keys and user preferences

### Accessibility: None
Given the personal-use nature and 2-day development timeline, accessibility features are out of scope for MVP.

### Branding
Professional financial aesthetic with clean typography and institutional color palette (navy, gray, white). No specific corporate branding required - focus on credibility and analytical sophistication rather than consumer appeal.

### Target Device and Platforms: Web Responsive
Primary target is desktop/laptop browsers on Windows 11, with basic responsive design to support occasional tablet use during report review.

## Technical Assumptions

### Repository Structure: Monorepo
Single repository with minimal structure - agents/, api/, templates/ directories. No complex build systems or packaging.

### Service Architecture
**Direct OpenAI API calls with simple sequential orchestration.** Skip LangGraph complexity - use basic Python functions with direct OpenAI SDK calls. Each agent is a simple function that takes context and returns results.

### Testing Requirements  
**Manual testing only for MVP.** Skip automated testing infrastructure to meet 2-day timeline. Focus development time on agent prompt quality rather than test frameworks.

### Additional Technical Assumptions and Requests

**Core Technology Stack:**
- **FastAPI** - Minimal setup, auto docs, async support
- **OpenAI SDK** - Direct API calls, no wrapper frameworks  
- **Pydantic BaseModel** - Simple data validation only where needed
- **Python standard library** - Avoid unnecessary dependencies

**Agent Pattern:** Simple Python functions, not complex frameworks
```python
def assessment_agent(ticker: str, questions: List[str]) -> AssessmentResult:
    # Direct OpenAI API call with system prompt
    return structured_output
```

**Data Flow:** JSON files for configuration, simple dictionaries for agent handoffs
- No complex state management or graph workflows
- Agent results passed as simple Python dictionaries
- Context preservation through basic JSON serialization

**Frontend:** Plain HTML + minimal JavaScript
- Single page application with basic form handling
- No React, Vue, or complex frontend frameworks
- Direct API calls with fetch()

**PDF Generation:** Python `weasyprint` library
- HTML-to-PDF conversion (simpler than reportlab)
- CSS styling for professional appearance
- Skip complex charting libraries for MVP

**Configuration:** Simple .env + JSON config files
- Agent prompts in separate .txt files
- No YAML complexity, no configuration frameworks

**Error Handling:** Basic try/catch with graceful degradation
- If one agent fails, return partial results
- Simple logging to console/file

## Epic List

**Epic 1: Foundation & Core Assessment System**
Establish project infrastructure with FastAPI, implement the 20-question assessment agent, and deliver basic ticker input functionality with expertise level calculation.

**Epic 2: Research Agent Implementation**  
Build the 4 specialized research agents (Valuation Expert, Strategic Analyst, Company Historian, Final Report Synthesizer) with sequential handoff coordination and context preservation.

**Epic 3: Report Generation & PDF Output**
Create professional PDF report generation with institutional-grade formatting, adaptive content based on user expertise level (200-300 pages vs 10-20 pages), and download delivery system.

## Epic 1: Foundation & Core Assessment System

**Epic Goal:** Establish complete project foundation with FastAPI infrastructure, implement sophisticated 20-question assessment system, and deliver working ticker input with accurate expertise level calculation (1-10 scale). Users can input any company ticker, complete the assessment, and receive their expertise score with system validation.

### Story 1.1: Project Setup & FastAPI Foundation
As a developer,
I want a complete FastAPI project structure with essential configuration,
so that I have a solid foundation for implementing the assessment and research agents.

#### Acceptance Criteria
1. FastAPI application initializes with health check endpoint
2. Project structure includes agents/, api/, templates/, static/ directories
3. Environment configuration supports OpenAI API key management
4. Basic CORS and middleware configuration for local development
5. Requirements.txt includes minimal dependencies (FastAPI, OpenAI SDK, Pydantic, weasyprint)
6. Application runs locally on Windows 11 with simple startup command

### Story 1.2: Ticker Input & Validation System
As a user,
I want to enter any company ticker symbol through a clean web interface,
so that I can initiate research analysis for my chosen company.

#### Acceptance Criteria
1. Simple HTML form accepts ticker symbol input (e.g., ASML, COST, MSFT)
2. Client-side validation ensures ticker format is appropriate (letters, limited length)
3. FastAPI endpoint validates ticker and returns confirmation or error
4. Basic ticker existence validation (simple format checking for MVP)
5. Error handling for invalid tickers with clear user feedback
6. Session initialization to maintain context throughout assessment process

### Story 1.3: Assessment Agent Implementation
As a user,
I want to complete a sophisticated 20-question assessment of my financial expertise,
so that the system can adapt its analysis depth to my knowledge level.

#### Acceptance Criteria
1. Assessment agent presents exactly 20 questions covering financial/valuation/strategic/risk domains
2. Questions are presented one at a time with clear progress indication (Question 5 of 20)
3. Answer scoring system calculates expertise level on 1-10 scale with transparent logic
4. Question difficulty progresses from basic to advanced across domains
5. User can navigate back to previous questions during assessment
6. Assessment completion triggers expertise level calculation and display
7. Assessment results are saved to session context for downstream agents

### Story 1.4: Assessment Scoring & Level Determination
As a user,
I want to receive an accurate expertise level score (1-10) based on my assessment responses,
so that subsequent research analysis is appropriately calibrated to my knowledge.

#### Acceptance Criteria
1. Scoring algorithm weights questions by difficulty and domain expertise
2. Final expertise level (1-10) is calculated with clear explanation of scoring rationale
3. Score determines analysis depth: levels 1-5 trigger comprehensive reports, 6-10 trigger expert summaries
4. User receives immediate feedback on their expertise level and what it means for their report
5. Scoring results are preserved for downstream research agent coordination
6. System provides option to retake assessment if user disagrees with results

### Story 1.5: Session Management & Context Preservation
As a user,
I want my ticker selection and assessment results to be maintained throughout the process,
so that I can seamlessly progress from assessment to research without losing context.

#### Acceptance Criteria
1. Session storage maintains ticker symbol, assessment responses, and expertise level
2. User can see current session status (ticker, expertise level) on all pages
3. Session expires after reasonable timeout with clear user notification
4. Context data is formatted for easy handoff to research agents
5. Error recovery allows users to resume from where they left off if issues occur
6. Session clear functionality allows users to start fresh analysis

## Epic 2: Research Agent Implementation

**Epic Goal:** Build and integrate the 4 specialized research agents (Valuation Expert, Strategic Analyst, Company Historian, Final Report Synthesizer) with sequential coordination that preserves context from the assessment phase. Users receive comprehensive, institutional-grade analysis with clear investment recommendations and supporting evidence.

### Story 2.1: Agent Orchestration Framework
As a developer,
I want a simple sequential agent coordination system,
so that research agents can process ticker analysis in logical order with preserved context.

#### Acceptance Criteria
1. Agent coordinator accepts assessment results and ticker symbol as input
2. Sequential handoff system passes results from one agent to the next
3. Context preservation maintains user expertise level and all prior agent outputs
4. Error handling allows graceful degradation if individual agents fail
5. Progress tracking shows users which agent is currently processing
6. Agent results are structured for easy consumption by subsequent agents
7. All agent communications use simple JSON format for context transfer

### Story 2.2: Valuation Expert Agent
As a user,
I want comprehensive financial valuation analysis including DCF models and ratio analysis,
so that I have quantitative investment metrics and price targets.

#### Acceptance Criteria
1. Agent generates DCF model with detailed cash flow projections and assumptions
2. Financial ratio analysis covers profitability, liquidity, efficiency, and leverage metrics
3. Peer comparison analysis positions company against industry competitors
4. Price target calculation with upside/downside scenarios
5. Quantitative risk assessment including sensitivity analysis
6. Analysis depth adapts based on user expertise level (detailed vs summary)
7. All calculations include clear assumptions and data sources
8. Output formatted for integration into final report synthesis

### Story 2.3: Strategic Analyst Agent
As a user,
I want deep strategic analysis of competitive positioning and market dynamics,
so that I understand the company's qualitative investment merits and risks.

#### Acceptance Criteria
1. Competitive moat analysis identifies and evaluates sustainable advantages
2. Market dynamics assessment covers industry trends, growth drivers, and threats
3. Strategic risk evaluation includes regulatory, technological, and competitive risks
4. Management quality assessment based on track record and strategic decisions
5. ESG factors integration where material to investment thesis
6. Strategic opportunities identification for future growth
7. Analysis integrates with valuation metrics from previous agent
8. Recommendations link strategic factors to investment implications

### Story 2.4: Company Historian Agent
As a user,
I want complete company history from founding to present with key milestone analysis,
so that I understand the business evolution and management track record.

#### Acceptance Criteria
1. Chronological company history from founding through present day
2. Key milestone identification (IPOs, acquisitions, strategic pivots, crises)
3. Leadership evolution and management team assessment over time
4. Historical financial performance contextualized with business events
5. Crisis management evaluation (how company handled downturns, challenges)
6. Strategic decision analysis with outcomes assessment
7. Historical context integrated with current strategic analysis
8. Pattern identification for predictive insights about future performance

### Story 2.5: Final Report Synthesizer Agent
As a user,
I want all research integrated into cohesive investment thesis with clear buy/sell/hold recommendation,
so that I receive actionable investment guidance with comprehensive supporting analysis.

#### Acceptance Criteria
1. Investment thesis synthesis combines quantitative and qualitative analysis
2. Clear buy/sell/hold recommendation with conviction level
3. Price target with expected IRR calculations over investment horizon
4. Risk assessment summary with key factors and mitigation strategies
5. Executive summary appropriate for user expertise level
6. Supporting evidence cross-references all prior agent analysis
7. Alternative scenarios consideration (bull/bear case analysis)
8. Report structure optimized for subsequent PDF generation

### Story 2.6: MCP Integration for Real-Time Data
As a user,
I want current market data and recent company information integrated into analysis,
so that my research reflects the most up-to-date information available.

#### Acceptance Criteria
1. MCP server integration provides current stock price and market data
2. Recent news and earnings information included in agent analysis
3. Real-time financial metrics supplement historical analysis
4. Data freshness indicators show information currency
5. MCP error handling ensures analysis continues with available data
6. Data source attribution for all external information
7. Integration works seamlessly across all research agents

## Epic 3: Report Generation & PDF Output

**Epic Goal:** Transform research agent outputs into professional, institutional-grade PDF reports with adaptive content based on user expertise (200-300 pages for beginners, 10-20 pages for experts). Users receive polished investment reports with clear formatting, charts, and download functionality that matches Bloomberg/Goldman Sachs presentation standards.

### Story 3.1: Report Template System
As a developer,
I want flexible HTML templates that adapt content depth based on user expertise level,
so that report generation can produce appropriate analysis detail for different user knowledge levels.

#### Acceptance Criteria
1. HTML template system supports both comprehensive (200-300 pages) and executive (10-20 pages) formats
2. Template engine dynamically includes/excludes sections based on expertise level (1-5 vs 6-10)
3. Professional CSS styling mimics institutional research report aesthetics
4. Template structure accommodates all 4 research agent outputs with clear section organization  
5. Charts and financial tables are properly formatted and embedded
6. Template system includes cover page, executive summary, detailed analysis, and appendices
7. Responsive design ensures proper rendering across different PDF page sizes

### Story 3.2: PDF Generation Engine
As a user,
I want my research report converted to professional PDF format with institutional-grade presentation,
so that I receive investment analysis comparable to Goldman Sachs research quality.

#### Acceptance Criteria
1. weasyprint library generates high-quality PDFs from HTML templates
2. PDF includes proper page numbering, headers, and footers
3. Professional typography with financial industry standard fonts and spacing
4. Charts and tables render correctly in PDF format without formatting issues
5. PDF bookmarks and navigation support easy section jumping
6. File size optimization ensures reasonable download times
7. PDF metadata includes report title, company ticker, and generation date

### Story 3.3: Content Adaptation Logic
As a user,
I want my report content automatically adapted to my expertise level,
so that I receive appropriately detailed analysis without information overload or oversimplification.

#### Acceptance Criteria
1. Expertise levels 1-5 trigger comprehensive 200-300 page reports with detailed explanations
2. Expertise levels 6-10 generate focused 10-20 page executive summaries
3. Content adaptation preserves all critical analysis while adjusting detail level
4. Financial concepts include explanatory context for lower expertise levels
5. Executive summaries maintain analytical rigor while condensing presentation
6. Adaptation logic is transparent to users with clear explanation of approach
7. Both formats maintain institutional-grade analysis quality standards

### Story 3.4: Report Download & Delivery
As a user,
I want to easily download my completed investment research report,
so that I can save, share, and reference the analysis for my investment decisions.

#### Acceptance Criteria
1. Simple download button triggers PDF generation and file delivery
2. Download process includes progress indicator for large report generation
3. PDF files use clear naming convention (CompanyTicker_StockIQ_Date.pdf)
4. Error handling manages PDF generation failures with user-friendly messaging
5. Download works reliably across different browsers and Windows 11 environments
6. Generated PDF files are immediately available for local storage and sharing
7. System cleanup removes temporary files after successful download

### Story 3.5: Report Quality Assurance
As a user,
I want consistent, professional report formatting that meets institutional research standards,
so that my analysis appears credible and authoritative for investment decision-making.

#### Acceptance Criteria
1. All reports include comprehensive quality checks before PDF generation
2. Financial calculations and data are validated for accuracy and consistency
3. Report structure follows institutional research report conventions
4. Charts and visualizations are clear, properly labeled, and professionally formatted  
5. Citation and data source attribution is complete and properly formatted
6. Executive summary accurately reflects detailed analysis content
7. Investment recommendations are clearly stated with supporting rationale

### Story 3.6: Performance Optimization
As a user,
I want fast report generation that doesn't compromise analysis quality,
so that I can efficiently obtain comprehensive research without excessive waiting times.

#### Acceptance Criteria
1. PDF generation completes within reasonable time limits (under 2 minutes for comprehensive reports)
2. Memory usage is optimized for large report generation on local Windows 11 systems
3. Progress indicators keep users informed during longer processing times
4. Error recovery handles memory or processing constraints gracefully
5. Caching optimization reduces redundant processing where possible
6. System resource monitoring prevents performance degradation
7. User interface remains responsive during background report generation
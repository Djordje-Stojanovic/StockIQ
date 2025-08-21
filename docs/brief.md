# Project Brief: StockIQ

## Executive Summary

**StockIQ** is a personal AI research tool that surpasses all existing investment research standards through a 5-agent multi-specialist architecture. The tool addresses the fundamental problem that superior investment research requires capital-intensive approaches (hiring 20+ PhDs or running thousands of parallel AI agents) that are inaccessible to individual investors. StockIQ replicates hedge fund-level research quality by deploying specialized AI agents for assessment and analysis, producing 200-300 page comprehensive company analyses that beat institutional research depth while adapting output complexity to user expertise levels (from beginner-friendly comprehensive reports to expert-level valuation updates).

## Problem Statement

Current investment research falls short because the most effective approaches are capital-prohibitive. To truly understand a company like Costco, you'd need to hire 20 PhDs to analyze every thesis ever written, plus 5 PhDs following all news with second-level and first-principles thinking - exactly what hedge funds do. Or you'd need OpenAI's internal capability to run 1000 parallel deep research agents followed by 100 summarization agents. 

Without massive capital, investors are stuck with inferior options: shallow Reddit discussions, basic Seeking Alpha articles, expensive Bloomberg terminal data, or generic AI research from Gemini/OpenAI/LangChain that lacks the depth and parallel processing power needed for true institutional-grade analysis. The fundamental barrier isn't knowledge or methodology - it's the capital required to deploy research at the scale and depth that produces superior investment insights.

Research is also fundamentally limited not just by capital constraints, but by human limitations in intelligence, broad knowledge, scientific and mathematical expertise, and experience depth. Even the best-funded research teams are constrained by individual analyst capabilities.

## Proposed Solution

StockIQ replicates the capital-intensive research approach of top hedge funds using AI agents instead of expensive human teams. The system deploys a 5-agent architecture that mirrors the 20+ PhD research team scenario: 1 sophisticated assessment agents evaluate user expertise, then 4 specialized research agents (Valuation Expert, Strategic Analyst, Company Historian, Final Report Synthesizer) conduct parallel deep analysis equivalent to multiple PhD-level researchers.

Each agent operates with institutional-grade prompts and access to comprehensive data sources, producing the same depth of analysis as a fully-funded research team but at near-zero marginal cost. The result is a personal research capability that surpasses hedge fund research quality by combining the thoroughness of large human teams with AI's ability to process and synthesize information at unprecedented scale and speed, while breaking through human cognitive limitations using supersmart system prompts and advanced AI reasoning combined with massive 100+ page outputs.

**Key Differentiators:**
- **Expertise Assessment System:** 20-question evaluation determines user knowledge level (1-10) to adapt report complexity
- **Multi-Agent Specialization:** Each agent focuses on specific analysis domains for comprehensive coverage
- **Adaptive Output:** 300-page comprehensive reports for beginners, 10-20 page summaries for experts
- **Institutional-Grade Analysis:** DCF models, competitive moat analysis, complete company histories, all other usefull scientific and evidence based time tested research methods that institutions like Goldman Sachs, Morgan Stanly, JP Morgan and OpenAI/Google Deepmind use.

## Target Users

### Primary User Segment: Personal Investment Researcher

The primary (and only) user is myself - a serious individual investor who demands research quality that surpasses all existing standards. This is a personal tool designed for someone who understands that superior investment decisions require superior research, and who recognizes that current research is fundamentally limited not just by capital constraints, but by human limitations in intelligence, broad knowledge, scientific and mathematical expertise, and experience depth.

**User Profile:**
- **Current Behavior:** Manually aggregates information from multiple sources (financial statements, news, analysis reports, industry research)
- **Pain Points:** Time-intensive research process, inconsistent analysis quality, inability to achieve institutional-grade depth
- **Goals:** Make superior investment decisions based on comprehensive, unbiased analysis
- **Expertise Level:** Varies by company/sector - expert in some areas, beginner in others

**Key Characteristics:**
- Values analytical depth over speed
- Willing to invest time in comprehensive assessment process
- Seeks research that surpasses human cognitive limitations
- Understands that quality research requires systematic, multi-disciplinary approach using science and art at the same time
- Recognizes that even the best-funded research teams are constrained by individual analyst capabilities

## Goals & Success Metrics

### Business Objectives

- **Personal Research Superiority:** Achieve research quality that demonstrably surpasses Goldman Sachs, Morgan Stanley, JPMorgan institutional, Gemini Deep Research, Openai Deep Research or Langchain Open Source Deep research within 2-day MVP development
- **AI Research Dominance:** Outperform OpenAI Deep Research, Gemini Deep Thinking, and all LangChain implementations in depth, insight, and analytical sophistication
- **Human Limitation Transcendence:** Generate 200-300 page analyses with cross-disciplinary integration impossible for human teams regardless of funding or expertise for beginners or exceptionally high quality research with 10-20 pages for experts. Scaling based on users knowledge.

### User Success Metrics

- **Investment Decision Confidence:** Clear buy/sell/hold recommendations with price targets and expected IRR over the long term based on comprehensive analysis
- **Research Depth Achievement:** 200-300 page company analyses covering financial, strategic, historical, and synthesized perspectives, 10-20 pages for experts.
- **Quality Benchmark Exceeded:** Analysis quality that surpasses the best existing institutional research, AI research, and financial writing

### Key Performance Indicators (KPIs)

- **Analytical Comprehensiveness:** Complete company story from founding to present with investment thesis - Target: 100% coverage of all relevant dimensions
- **Research Processing Scale:** Multi-agent parallel analysis equivalent to 20+ PhD research team - Target: 5-agent architecture fully operational
- **Output Quality Standard:** Research that beats all existing benchmarks in depth, creativity, and insight - Target: Measurably superior to institutional research

Note: All that can be validated for example with methologies used in https://github.com/Ayanami0730/deep_research_bench - the knowledge for that is in Archon and the usage guide for archon can be found in CLAUDE.md file.

## MVP Scope

### Core Features (Must Have)

- **5-Agent Research Architecture:** 1 Assessment agents (Financial/Valuation Expert/Strategic/Risk Analyst) with 20 questions, plus 4 Research agents (Valuation Expert, Strategic Analyst, Company Historian, Final Report Synthesizer)
- **Expertise Assessment System:** Sophisticated 10-level scoring system that determines research depth and complexity based on user knowledge
- **Comprehensive Report Generation:** 200-300 page PDF reports with institutional-grade formatting, citations, and professional presentation, less for more skilled investors.
- **Real-Time Data Integration:** MCP integration for current market data, news, and comprehensive company information gathering
- **Sequential Agent Orchestration:** Smooth handoff from assessment to specialized research agents with context preservation
- **FastAPI Web Interface:** Simple ticker input system with assessment questions and report download functionality

### Out of Scope for MVP

- Database persistence (using memory-based session storage)
- Multi-user support or authentication systems
- Advanced UI/UX design beyond basic HTML/CSS
- Mobile responsiveness or cross-platform compatibility
- Real-time collaboration features
- Payment processing or monetization features

### MVP Success Criteria

Complete 2-day development cycle producing a working prototype that can take a ticker symbol (e.g., ASML), conduct full assessment + research cycle, and generate a 200-300 page comprehensive company analysis that demonstrably exceeds institutional research quality in depth, insight, and analytical sophistication.

## Post-MVP Vision

### Phase 2 Features

Advanced data acquisition capabilities including web crawling for comprehensive information gathering, enhanced agent specialization with domain-specific sub-agents (e.g., sector specialists, regulatory experts, macroeconomic analysts), and sophisticated report customization allowing for different analysis frameworks (value investing, growth investing, technical analysis integration). Implementation of advanced reasoning chains where agents can challenge each other's conclusions and engage in collaborative analysis refinement.

### Long-term Vision

Evolution into the definitive personal investment research platform that continuously learns and improves analysis quality through iterative prompt engineering and agent specialization. Development of predictive analytics capabilities that not only analyze current company state but forecast potential scenarios and their investment implications. Integration of real-time monitoring systems that can track portfolio companies buy thesis and do re-analysis when significant developments occur and the user prompts.

### Expansion Opportunities

Potential extension to "Investmetn-Finder" using similar multi-agent architecture principles which synthesizes the current database of reports to look for what is appealing at current prices. Development of macro-economic analysis capabilities that can contextualize individual company research within broader economic trends. Creation of comparative analysis features that can simultaneously analyze multiple companies or entire sectors with cross-company insights and relative positioning analysis.

## Technical Considerations

### Platform Requirements

- **Target Platforms:** Windows 11 local development
- **Browser/OS Support:** Modern browsers for web interface access
- **Performance Requirements:** Fast local processing with efficient memory management for large report generation

### Technology Preferences

- **Frontend:** Simple HTML/CSS/JS interface
- **Backend:** FastAPI with OpenAI SDK direct integration
- **Database:** JSON/.md/.yml files for configuration depending on how PM Chooses, memory-based session storage
- **Hosting/Infrastructure:** Local development environment, no cloud dependencies

### Architecture Considerations

- **Repository Structure:** Single repository with clear agent prompt separation
- **Service Architecture:** Sequential agent orchestration, simple API endpoints
- **Integration Requirements:** MCP integration for data access, basic PDF generation
- **Security/Compliance:** Local-only processing, API key management

## Constraints & Assumptions

### Constraints

- **Budget:** Personal development project with API usage costs (OpenAI, MCP services)
- **Timeline:** 2-day maximum development sprint for working MVP
- **Resources:** Solo development with focus on prompt engineering over complex coding
- **Technical:** Windows 11 local environment, simple stack limitations

### Key Assumptions

- OpenAI API access provides sufficient reasoning capability for institutional-grade analysis
- MCP integration delivers adequate real-time data for comprehensive research
- 5-agent architecture can replicate 20+ PhD research team effectiveness
- Sequential agent processing produces better results than parallel coordination
- PDF report generation meets professional presentation standards
- Assessment system accurately determines user expertise level
- Simple FastAPI interface sufficient for ticker input and report delivery
- JSON-based configuration enables rapid agent prompt iteration
- Testing strategy sufficient for MVP validation despite manual approach
- API failure recovery provides adequate reliability for personal use
- Token budget management prevents cost escalation
- Session persistence adequate for development workflow

## Risks & Open Questions

### Updated Risk Assessment

- **API Cost Escalation:** Mitigated by 200k token budget limits and monitoring
- **Quality Validation:** Addressed by manual testing checklist and agent validation
- **Data Access Limitations:** Mitigated by graceful degradation strategies
- **Agent Coordination:** Addressed by standardized handoff formats and error recovery

### Open Questions

- What specific prompting strategies will enable each agent to achieve PhD-level analytical depth?
- How can we validate that 200-300 page outputs maintain quality throughout rather than padding with filler content?
- What MCP server configurations will provide optimal financial data access for comprehensive analysis?
- How will assessment questions accurately differentiate expertise levels to ensure proper analysis depth?

### Areas Needing Further Research

- Institutional research report analysis to identify specific quality markers and analytical frameworks
- Advanced prompting techniques for maintaining consistency across multi-agent workflows
- PDF generation libraries that support professional-grade formatting with charts and tables
- MCP server capabilities and limitations for financial data access

## Appendices

### A. Research Summary

**Brainstorming Findings:**
- Multi-agent architecture identified as core differentiator over single-agent approaches
- 2-day development timeline validated as achievable with focused execution
- 5-agent system design: 1 Assessment (Financial/Valuation/Strategic/Risk) + 4 Research (Valuation Expert, Strategic Analyst, Company Historian, Final Report Synthesizer)
- Technical stack simplified to FastAPI + OpenAI SDK + MCP integration for rapid development
- Assessment system with 10-level expertise scoring enables adaptive analysis depth

**Competitive Analysis Findings:**
- Blue ocean opportunity: No existing competitor offers expertise assessment + adaptive output combination
- Strategic positioning as 'Investment Bank Quality Research for Everyone' addresses accessibility gap
- OpenAI Deep Research, Gemini Deep Thinking lack investment-specific focus and adaptive capabilities
- Investment banks provide quality benchmark but have insurmountable accessibility barriers
- Market fragmentation creates opportunity for specialized, superior solution

### B. Stakeholder Input

Single stakeholder (personal use) with clear requirements: Create research tool that surpasses all existing standards through AI agent architecture replicating capital-intensive research approaches at near-zero marginal cost.

### C. References

- StockIQ Brainstorming Session - Complete Results (Archon Document ID: 374e2ce5-4369-43ed-91b3-e1cdb8db71ee)
- StockIQ Competitive Analysis Report (Archon Document ID: 4914e9dd-40ed-4b2f-b15b-e0dda51731c1)
- Archon MCP Server Documentation (via mcp__archon__perform_rag_query and mcp__archon__search_code_examples)
- CLAUDE.md project guidelines and KISS principles
